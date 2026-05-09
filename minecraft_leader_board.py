import argparse
import requests
import os
import io
from os import walk
from mojang import API
from PIL import Image
import shutil
import json
from collections import defaultdict
from pathlib import Path
import urllib.parse


verbosity_level=None
api = API()

## utils

def mkdir(path):
	if not os.path.exists(path):
		os.makedirs(path)
		
def rmdir(path):
	if os.path.isdir(path):
		shutil.rmtree(path)		
		
def load_json(path):
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)
def load_file(path):
	with open(path, "r", encoding="utf-8") as f:
		return f.read()
		
def save_json(path, data):
	with open(path, "w", encoding="utf-8") as f:
		json.dump(data, f, indent="\t", ensure_ascii=False)
		

def flatten_dict(d, parent_key="", sep="."):

	items = {}

	for k, v in d.items():
		new_key = f"{parent_key}{sep}{k}" if parent_key else k

		if isinstance(v, dict):
			items.update(flatten_dict(v, new_key, sep=sep))
		else:
			items[new_key] = v

	return items
## API

def uuid_api_official(uuid, doFaces):
		try:
			profile = api.get_profile(uuid.replace("-",""))
			name = profile.name
			#print(name)
			if doFaces:
				face = get_face(profile.skin_url)
			else:
				face = None
			return name, face
		except Exception as e:
			if verbosity_level > -1: print("Exception while looking up UUID: "+uuid+"\n\t Skipped ") 
			raise 
			return None, None
			
			
def get_face(skin_uri, out_size = 8) -> Image.Image:
	r = requests.get(skin_uri, timeout=10)
	r.raise_for_status()
	skin_bytes = r.content	
	skin = Image.open(io.BytesIO(skin_bytes)).convert("RGBA")
	face = skin.crop((8, 8, 16, 16))  # 8x8
	try:
		hat = skin.crop((40, 8, 48, 16))

		if any(px[3] != 0 for px in hat.getdata()):
			face = face.copy()
			face = Image.alpha_composite(face, hat)
	except Exception:
		pass
	face = face.resize((out_size, out_size), resample=Image.NEAREST)
	return face	

## output


class Output:
	"""
	A simple output writer supporting filesystem, zip, and tar.gz outputs.

	compression:
		- "zip" -> writes to {path}/output.zip
		- "tar" -> writes to {path}/output.tar.gz
		- "none" -> writes to {path}/output/
	"""

	def __init__(self, path, name, compression=None):
		if compression is None:
			compression="none"
		self.base_path = Path(path)

		self.zip_file = None
		self.tar_file = None
	
		if "zip" in compression:
			import zipfile
			self.base_path.mkdir(parents=True, exist_ok=True)
			self.archive_path = self.base_path / (name+".zip")
			self.zip_file = zipfile.ZipFile(self.archive_path, "w", zipfile.ZIP_DEFLATED)
			self.compression="zip"
		elif "t" in compression:
			import tarfile
			self.base_path.mkdir(parents=True, exist_ok=True)
			self.archive_path = self.base_path / (name+".tar.gz")
			self.tar_file = tarfile.open(self.archive_path, "w:gz")
			self.compression="tar"
		else:
			self.base_path = self.base_path / name
			self.base_path.mkdir(parents=True, exist_ok=True)
			self.compression="none"

	def write(self, relative_path, data):

		if isinstance(data, str):
			data = data.encode("utf-8")

		relative_path = Path(relative_path).as_posix().lstrip("/")

		if self.compression == "none":
			full_path = self.base_path / relative_path
			full_path.parent.mkdir(parents=True, exist_ok=True)
			with open(full_path, "wb") as f:
				f.write(data)

		elif self.compression == "zip":
			self.zip_file.writestr(relative_path, data)
			import zipfile 
		elif self.compression == "tar":
			import tarfile
	
			info = tarfile.TarInfo(name=relative_path)
			info.size = len(data)
			self.tar_file.addfile(info, io.BytesIO(data))
			
	def copy_path(self, src_path, dest_path=None):
		src_path = Path(src_path)

		if dest_path is None:
			dest_path = src_path.name
		else:
			dest_path = str(dest_path)

		dest_path = Path(dest_path).as_posix().lstrip("/")

		self.write(dest_path, src_path.read_bytes())
			
	def close(self):
		if self.zip_file:
			self.zip_file.close()
		if self.tar_file:
			self.tar_file.close()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc, tb):
		self.close()


		
## Main functions
def init_players(rootpath,uuids, doFaces):
	ret={}
	for filename in os.listdir(rootpath):
		path = os.path.join(rootpath, filename)
		if os.path.isfile(path):
			print(path)
			if(".json" in filename):
				source=""
				uuid=filename[0:filename.find('.')]
				if uuid in uuids and (not doFaces or os.path.exists("cache/faces/"+uuids[uuid]+".png")):
					name=uuids[uuid]
					source="cached"
				else:
					name, face = uuid_api_official(uuid,doFaces)
					if face:
						face.save("cache/faces/"+name+".png")
					source="fetched"	
				if name is None or len(name)<2:
					continue
				if verbosity_level > 0: 
					print(uuid+": "+name+" - "+source) 
				uuids[uuid]=name
				save_json("cache/uuid.json",uuids, )
				ret[uuid]={"name":name}
	return ret
				
				
def extract(path,uuid,players,trylegacy=True):
	try:
		player=players[uuid]
		file=load_json(path+"/"+uuid+".json")["stats"]
		file=flatten_dict(file)
		for key in list(file.keys()):
			repkey=key.replace("minecraft:","").replace("..",".")
			file[repkey]=file.pop(key)
		player["stats"]=file
	except Exception as e:
		if trylegacy:
			try:
				extract_legacy(path,uuid)
			except Exception:
				raise e
		else: 
			raise e
def extract_legacy(path,uuid,player):
	player=players["uuid"]
	file=load_json(path+"/"+uuid+".json")
	stats={}
	for key in file:
		if "stat." in key:
			stats[key]=file[key]
	player["stats"]=stats		

def apply_mapping(mapping,players):
	for key in mapping:
		for player in players.values():
			if key in player["stats"]:
				player["stats"][mapping[key]]=player["stats"].pop(key)
				
def generate_custom(custom,players):
	for key in custom:
		for player in players.values():
			sum=0
			count=0
			maxV=None
			minV=None
			for target in custom[key]["stats"]:
				if target in player["stats"]:
					if count ==0:
						maxV=player["stats"][target]
						minV=player["stats"][target]
					else:
						maxV=max(maxV,player["stats"][target])
						minV=min(minV,player["stats"][target])
					count+=1
					sum+=player["stats"][target]
			customstat=0
			if custom[key]["op"]=="sum":
				customstat=sum	
			elif custom[key]["op"]=="d_avg":
				customstat=sum/count
			elif custom[key]["op"]=="f_avg":
				customstat=sum/len(custom[key]["stats"])
			elif custom[key]["op"]=="min":	
				customstat=minV
			elif custom[key]["op"]=="max":
				customstat=maxV		
			
			if customstat!=0:
				player["stats"][key]=customstat 
def fullStats(players):
	stats= defaultdict(list)
	for player in players.values():
		for stat in player["stats"]:
			stats[stat].append({"name":player["name"],"amount":player["stats"][stat]})
	for stat in stats.values():
		stat.sort(reverse=True, key=lambda x: x["amount"])
		
	return stats

class Converter():
	def __init__(self,table):
		self.table=table
		
	def __call__(self, stat, amount):
		if stat in self.table:
			rule=self.table[stat]
			if rule["type"]=="item":
				stack=rule["stackSize"]
				working=amount
				unit=""
				if working>(256*256*128):
					working/=(256*256*128)
					unit="TCSU"
				else:	
					if working>stack and stack > 1 and unit=="":
						unit="S"
						working/=stack
					if working>27 and unit=="S":
						unit="SB"
						working/=27
					if working>54 and unit=="SB":
						unit="DC"
						working/=54
				return str(round(working,1))+" "+unit
			elif rule["type"]=="time":
				seconds=rule["seconds"]
				working=amount*seconds
				unit="s"
				if working>60 and unit=="s":
					unit="m"
					working/=60
				if working>60 and unit=="m":	
					unit="H"
					working/=60	
				if working>24 and unit=="H":	
					unit="D"
					working/=24
				if working>365 and unit=="D":
					unit="Y"
					working/=365
				elif working>30 and unit=="D":	
					unit="M"
					working/=30
				elif working>7 and unit=="D":
					unit="W"
					working/=7
				return str(round(working,1))+" "+unit
					
			elif rule["type"]=="distance":
				meter=rule["meter"]
				working=amount*meter
				unit=""
				maxed=""
				if amount==2**31-1:
					maxed=" (maxed)"
				if working>1000 and unit=="":
					unit="k"
					working/=1000
				if working>1000 and unit=="k":
					unit="M"
					working/=1000
				if working>1000 and unit=="M":
					unit="G"
					working/=1000
				if working>1000 and unit=="G":
					unit="T"
					working/=1000
				return str(round(working,1))+" "+unit+"m"+maxed

		working=amount
		unit=""
		maxed=""
		if amount==2**31-1:
			maxed=" (maxed)"
		if working>1000 and unit=="":
			unit="k"
			working/=1000
		if working>1000 and unit=="k":
			unit="M"
			working/=1000
		if working>1000 and unit=="M":
			unit="B"
			working/=1000
		if working>1000 and unit=="B":
			unit="T"
			working/=1000		
		return str(round(working,1))+" "+unit+maxed
## Driver

def main(input_dir=None,web=None, jsonA=None, text=None, clean = False, compression=None, html_title="Leaderboard", legacy_mode="auto", output=None, verbosity=1):
#verbosity: 2, prompt for missing args
#           1, no prompts
#           0, no progress
#          -1, no warnings
	global verbosity_level
	if verbosity < 2 and input_dir is None:
		raise ValueError("no input directory provided, but silent is set")
	if  verbosity > 1:
		if input_dir is None:
			input_dir=input("Path to Stats Dir: ")
		if web is None:
			choice=input("Create website?(Y/n) ")
			web= not("n" in  choice or "N" in choice)
		if web is None:
			choice=input("Create JSON api?(Y/n) ")
			jsonA= not("n" in  choice or "N" in choice)
		if text is None:
			choice=input("Create text files?(Y/n) ")
			text= not("n" in  choice or "N" in choice)	
			
	if output is None:
		output = input_dir+"/output"
		
	verbosity_level=verbosity
	
	convert=Converter(load_json("conversions.json"))
	custom_stats=load_json("custom.json")

	
		
	if clean: 
		rmdir("cache") 
	mkdir("cache")
	if web:
		mkdir("cache/faces")
		
	try:
		uuids=load_json("cache/uuid.json")
	except:
		uuids={}
	if  verbosity > 0:
		print("Loading players...")
	players=init_players(input_dir, uuids, web)
	for uuid in players:
		if legacy_mode == "true":
			extract_legacy(input_dir,uuid,players)
		else:
			extract(input_dir,uuid,players)
	conversions=load_json("conversions.json")
	mapping=load_json("mappings.json")
	
	if  verbosity > 0:
		print("Applying Custom Mappings...")	
	apply_mapping(mapping, players)
	
	if  verbosity > 0:
		print("Calculating Custom Stats...")
	generate_custom(custom_stats, players)
	
	if  verbosity > 0:
		print("Generating Leader board...")
	stats = fullStats(players)
	
	totals = {}
	statsindexed=defaultdict(dict)
	
	if  verbosity > 0:
		print("Indexing...")
	for stat in stats:
		stats[stat].sort(reverse=True, key=lambda x: x["amount"])
		for i,v in enumerate(stats[stat]):
			v["rank"]=i+1
			statsindexed[stat][v["name"]]=v	
	
	if  verbosity > 0:
		print("Calculating Totals...")		
	for stat in stats:
		totals[stat]=sum(x["amount"] for x in stats[stat])
	
	if  verbosity > 0:
		print("Clearing the Air...")	
	for stat in list(totals.keys()):
		if totals[stat]==0:
			del stats[stat]
	
	if  verbosity > 0:
		print("Silently Judging...")
	for player in players.values():
		pstats=[]
		count=0
		ranks=0
		weighted=0
		for stat in player["stats"]:
			if totals[stat]==0:
				continue

			pstat={
				"amount":player["stats"][stat],
				"rank":statsindexed[stat][player["name"]]["rank"] ,
				"stat":stat,
			}
			pstat["imp_rating"] = pstat["amount"] / totals[stat] * len(stats[stat]) - statsindexed[stat][player["name"]]["rank"]
			#percentage completed * competition - rank
			pstats.append(pstat)
			count+=1
			ranks+=statsindexed[stat][player["name"]]["rank"]
			weighted+=pstat["amount"] / totals[stat] * len(stats[stat])
		player["stats"]=sorted(pstats, reverse=True, key=lambda x: x["imp_rating"])
		player["avg_rank"]= ranks/count
		player["weight"]=weighted
		player["avg_weight"]=weighted/count
		
		
		for i, stat in enumerate(player["stats"]):
			stat["imp_rank"]=i+1
	
	if  verbosity > 0:
		print("Loudly Judging...")
	leaderboard=[]
	for stat in stats:
		min_val=min(item["amount"] for item in stats[stat])
		max_val=max(item["amount"] for item in stats[stat])
		max_val_conv=convert(stat,max_val)
		min_val_conv=convert(stat,min_val)
		leaderboard.append({
				"name":stat,
				"total":convert(stat,totals[stat]),
				"max":{"amount":max_val_conv,"players":[item["name"] for item in stats[stat] if item["amount"] == max_val]},
				"min":{"amount":min_val_conv,"players":[item["name"] for item in stats[stat] if item["amount"] == min_val]}
			})
	if  verbosity > 0:
		print("Exporting:")
	mkdir(output)
	
	if web:
		if  verbosity > 0:
			print("\tWeb:")
		stat_template=load_file("webtemplate/stat.html")
		stat_line_template=load_file("webtemplate/stat_line.html")
		stat_summary_template=load_file("webtemplate/stat_summary_line.html")
		player_template=load_file("webtemplate/player.html")
		player_line_template=load_file("webtemplate/player_line.html")
		player_summary_template=load_file("webtemplate/player_summary_line.html")
		mainpage=load_file("webtemplate/index.html")

		with Output(output, "web", compression) as webout:
			if  verbosity > 0:
				print("\t\tplayers...")
			for player in players.values():
				webout.copy_path("cache/faces/"+player["name"]+".png","faces/"+player["name"]+".png")
				
				htmlstats=""
				for stat in player["stats"]:
					pstat=(
						player_line_template
						.replace("{{Stat Name}}",stat["stat"])
						.replace("{{competition}}",str(len(stats[stat["stat"]])))
						.replace("{{Stat Name safe}}",urllib.parse.quote(stat["stat"]))
						.replace("{{Stat rank}}",str(stat["rank"]))
						.replace("{{Stat impv}}",str(stat["imp_rating"]))
						.replace("{{Stat impr}}",str(stat["imp_rank"]))
						.replace("{{Stat amount}}",str(stat["amount"]))
						.replace("{{Stat conv}}",str(convert(stat["stat"],stat["amount"])))
						.replace("{{Stat percent}}",str(round(stat["amount"]/totals[stat["stat"]]*100)))
					)
					htmlstats+=pstat
				htmlsummary=""
				for stat in player["stats"][:10]:
					pstat=(
						player_summary_template
						.replace("{{Stat Name}}",stat["stat"].replace("."," "))
						.replace("{{rank}}",str(stat["rank"]))
						.replace("{{Stat impv}}",str(stat["imp_rating"]))
						.replace("{{Stat impr}}",str(stat["imp_rank"]))
						.replace("{{amount}}",str(stat["amount"]))
						.replace("{{Stat percent}}",str(round(stat["amount"]/totals[stat["stat"]]*100)))
					)
					htmlsummary+=pstat
				htmlout=(
					player_template
					.replace("{{name}}",player["name"])
					.replace("{{stat line}}",htmlstats)
					.replace("{{stat summary line}}",htmlsummary)
					.replace("{{avg_rank}}",str(round(player["avg_rank"])))
					.replace("{{stat weight}}",str(round(player["weight"])))
					.replace("{{avg stat weight}}",str(round(player["avg_weight"],2)))
					.replace("{{html title}}",html_title)
				)
					
				webout.write("player/"+player["name"]+".html",htmlout)
			if  verbosity > 0:
				print("\t\tstats...")	
			for stat in stats:
				htmlstats=""
				for player in stats[stat]:
				
					pstat=(
						stat_line_template
						.replace("{{stat rank}}",str(statsindexed[stat][player["name"]]["rank"]))
						.replace("{{player name}}",player["name"])
						.replace("{{raw}}",str(player["amount"]))
						.replace("{{amount conv}}",str(convert(stat,statsindexed[stat][player["name"]]["amount"])))
						.replace("{{percentage rounded}}",str(round(player["amount"]/totals[stat]*100)))
						.replace("{{percentage}}",str(player["amount"]/totals[stat]*100))
					)
					htmlstats+=pstat
				htmlsummary=""
				for player in stats[stat][:10]:
					pstat=(
						stat_summary_template
						.replace("{{player name}}",player["name"])
						.replace("{{rank}}",str(statsindexed[stat][player["name"]]["rank"]))
						.replace("{{amount}}",str(statsindexed[stat][player["name"]]["amount"]))
						.replace("{{percentage rounded}}",str(round(statsindexed[stat][player["name"]]["amount"]/totals[stat]*100)))
						.replace("{{percentage}}",str(statsindexed[stat][player["name"]]["amount"]/totals[stat]*100))
					)
					htmlsummary+=pstat	
				htmlout=(
					stat_template
					.replace("{{stat summary line}}",htmlsummary)
					.replace("{{stat Name}}",stat)
					.replace("{{total}}",str(convert(stat,totals[stat])))
					.replace("{{raw total}}",str(totals[stat]))
					.replace("{{stat list}}",htmlstats)
					.replace("{{html title}}",html_title)
				)
				webout.write("stat/"+stat+".html",htmlout)
			if  verbosity > 0:
				print("\t\tstatic...")
					
			htmlout=(mainpage
				.replace("{{Title}}",html_title)
			)
			webout.write("index.html", htmlout)
			webout.write("leaderboard.json",json.dumps(leaderboard))
			for (dirpath, dirnames, filenames) in walk("webstatic"):
				for file in filenames:
					webout.copy_path(dirpath+"/"+file)
	if jsonA:
		if  verbosity > 0:
				print("\twJSON:")
		with Output(output, "api", compression)	as apiout: 
			if  verbosity > 0:
				print("\t\tplayers...")
			for player in players.values():

				jsonstats={}
				for stat in player["stats"]:
					jsonstats[stat["stat"]]={
						"name":stat["stat"],
						"competition":len(stats[stat["stat"]])),
						"rank":stat["rank"],
						"impv":stat["imp_rating"],
						"impr":stat["imp_rank"],
						"amount":stat["amount"],
						"amount_converted":convert(stat["stat"],stat["amount"]),
						"percent":stat["amount"]/totals[stat["stat"]]*100
					}
	

				jsonout={
					"name":player["name"])
					"stats":jsonstats,
					"avg_rank":player["avg_rank"],
					"weight":player["weight"]
				

				}
					
				apiout.write("player/"+player["name"]+".json",json.dumps(jsonout))
			if  verbosity > 0:
				print("\t\tstats...")	
			for stat in stats:
				jsonstats={}
				for player in stats[stat]:
				
					jsonstats[player["name"]]={
						"rank":statsindexed[stat][player["name"]]["rank"],
						"name":,player["name"],
						"raw":player["amount"],
						"amount_converted":convert(stat,statsindexed[stat][player["name"]]["amount"]),
						"percentage":player["amount"]/totals[stat]*100
					}
				jsonout={
					"stat":stat,
					"total":convert(stat,totals[stat]),
					"total":totals[stat],
					"players":jsonstats
				}
				apiout.write("stat/"+stat+".json",json.dumps(jsonout))
			if  verbosity > 0:
				print("\t\tleaderboard...")
					
			apiout.write("leaderboard.json",json.dumps(leaderboard))

	if text:
		if  verbosity > 0:
			print("\twtext:")

		with Output(output, "text", compression) as textout: 
			if  verbosity > 0:
				print("\t\tplayers...")
			for player in players.values():
				textstats=""
				for stat in player["stats"]:
					pstat=", ".join((
						stat["stat"],
						str(stat["imp_rank"]),
						str(stat["amount"]),
						str(stat["rank"]),
						str(round(stat["amount"]/totals[stat["stat"]]*100)),
						str(len(stats[stat["stat"]]))
					))
					textstats+=pstat+"\n"
				
				textout=""+player["name"]+\
					"| avg rank: "+round(player["avg_rank"])+\
					"| weight: "+round(player["weight"])+\
					"| avg weight: "+round(player["avg_weight"],2)+\
					"\n\nachievement, stat name, amount, rank, percent, competition\n"+textstats

				)
				
				textout.write("player/"+player["name"]+".txt",textout)
			if  verbosity > 0:
				print("\t\tstats...")	
			for stat in stats:
				textstats=""
				for player in stats[stat]:
					pstat=", ".join((
						statsindexed[stat][player["name"]]["rank"],
						player["name"],
						player["amount"],
						player["amount"]/totals[stat]*100,
					))
					textstats+=pstat
					
				textout=""+stat+" Total: "+ str(totals[stat])+\
					"\n\nrank, player, amount, percent\n"+textstats
				
				textout.write("stat/"+stat+".txt",textout)
			if  verbosity > 0:
				print("\t\tleaderbaord...")
					
			leaderboardtxt=""
			for stat in leaderboard:
				leaderboardtxt+=stat["name"]+ ": "+ str(stat["total"])+"\n"+\
					"\tmax: "+str(stat["max"]["amount"])+" "+str(stat["max"]["players"])+"\n"+\
					"\tmin: "+str(stat["min"]["amount"])+" "+str(stat["min"]["players"])+"\n\n"
			
			textout.write("leaderboard.json",json.dumps(leaderboard))
			#todo change leaderboard out

	if clean: 
		rmdir("cache") 
	if  verbosity > 0:
		print("Done:")

def parse_args():
	parser = argparse.ArgumentParser()

	parser.add_argument('-i', '--input_dir', required=True, type=str)
	parser.add_argument('-w', '--web', action='store_true')
	parser.add_argument('-t', '--txt', action='store_true')
	parser.add_argument('-j', '--json', action='store_true')
	parser.add_argument('-c', '--clean_cache', action='store_true')
	parser.add_argument('-z', '--compress', choices=['tgz', 'zip'])
	parser.add_argument('-html', '--html_title', default="Leaderboard", type=str)
	parser.add_argument('-l', '--legacy_mode', type=str, default='auto')
	parser.add_argument('-o', '--output', type=str)

	args = parser.parse_args()
	
	return args
if __name__=="__main__":
	args=parse_args()
	main(input_dir=args.input_dir,web=args.web, jsonA=args.json, text=args.txt, clean = args.clean_cache, compression=args.compress, html_title=args.html_title, legacy_mode=args.legacy_mode, output=args.output, verbosity=1)
