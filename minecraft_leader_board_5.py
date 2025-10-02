from os import walk
import requests
import os
import io

from json import *
from urllib.request import *
import urllib
from time import sleep
import pickle
from mojang import API
from math import *
from PIL import Image
import sys
api = API()
def mkdir(path):
	if not os.path.exists(path):
		os.makedirs(path)
def save_obj(obj, name ):
	with open('cache/'+ name + '.pkl', 'wb') as f:
		pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
	with open('cache/' + name + '.pkl', 'rb') as f:
		return pickle.load(f)
players=[]
try:
	uuids=load_obj("uuid")
except:
	uuids={}
stats=dict()
class StatPair:
	def __init__(self,player,value):
			self.player=player
			self.value=value
	def __str__(self):
			return str(self.player.name)+": "+str(self.value)
class Stat:
	def __init__(self,name,value,player):
			self.name=name
			self.minPlr=[player]
			self.maxPlr=[player]
			self.maxV=value
			self.minV=value
	def min(self,other,name):
			if(self.minV>other):
				self.minV=other
				self.minPlr=[name]

			elif self.minV==other:
				self.minPlr.append(name)

	def max(self,other,name):
				if(self.maxV<other):
					self.maxV=other
					self.maxPlr=[name]

				elif self.maxV==other:
					self.maxPlr.append(name)
	def __str__(self):
			return "Most:	"+self.name+": "+str(self.maxV)+" "+str(self.maxPlr)+"\nLeast: "+self.name+": "+str(self.minV)+" "+str(self.minPlr)
		
#stats.append(Stat("generic",0,"none"))
globalStats =dict()
class Player:
	def __init__(self,uuid):
			print("UUID: "+uuid,end=" ");
			self.score=0;
			self.name="Useful Minecraft Resources"
			self.uuid=uuid
			self.stat_ranks=[]
			if uuid in uuids and uuids[uuid]!=uuid:
				self.name=uuids[uuid]
			else:
				self.name, face=uuid_api_official(uuid)
				self.hasFace = not face is None
				if self.hasFace:
					face.save("cache/faces/"+self.name+".png")
				uuids[uuid]=self.name
				save_obj(uuids,"uuid")

			self.uuid=uuid
			self.stats=dict()
			if self.name=="Useful Minecraft Resources":
				print(uuid)
			#print(page)
			print("Name: "+str(self.name))

	def __str__(self):
			return self.name

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
def uuid_api_official(uuid):
		try:
			profile = api.get_profile(uuid.replace("-",""))
			name = profile.name
			#print(name)
			face = get_face(profile.skin_url)
			return name, face
		except Exception as e:
			print("Exception while looking up UUID: "+uuid+"\n Skipped ")
			return uuid, None

def extract(path,name):
	try:
		if(".json" in name):
			player=Player(name[0:name.find('.')])
			if((not player.name is None) and len(player.name)>2):
				players.append(player);
				stringin=open (path,'r')
				jsonIn=loads(stringin.read())["stats"]
				players[-1].stats={}
				for key in jsonIn.keys():
					holdString=key;
					for subkey in jsonIn[key].keys():
						tmpstr=subkey.replace("minecraft","")
						players[-1].stats[(holdString+tmpstr).replace(':','.')]=jsonIn[key][subkey]
	except Exception as e:
		try:
			extract_legacy(path,name)
		except Exception:
			raise e
def extract_legacy(path,name):
	if(".json" in name):
			player=Player(name[0:name.find('.')])
			if((not player.name is None) and len(player.name)>2):
				players.append(player);
				stringin=open (path,'r')
				jsonIn=loads(stringin.read())
				players[-1].stats={}
				for key in jsonIn.keys():
					if "stat." in key:
						#holdString="";
						#tmpstr=key.replace("minecraft","")
						players[-1].stats[(key).replace(':','.')]=jsonIn[key]
	
def dirin(mypath):
	for (dirpath, dirnames, filenames) in walk(mypath):
		#for path in dirnames:
		#		dirin(dirpath+'/'+path)
		for path in filenames:
				extract(dirpath+'/'+path,path)

		break
if __name__=="__main__":	
	if len(sys.argv)>1:
		path=sys.argv[1]
	else:
		path=input("Path directory to be checked: ")
	print("looking up UUID's, this can take quite some time")
	dirin(path)
	path+="/summary"
	
	mkdir("cache")
	mkdir("cache/faces")
	mkdir(path)
	mkdir(path+"/full")
	mkdir(path+"/full/stat")
	mkdir(path+"/full/player")
	mkdir(path+"/json")
	mkdir(path+"/json/stat")
	mkdir(path+"/json/player")
	mkdir(path+"/html")
	mkdir(path+"/html/stat")
	mkdir(path+"/html/player")
	print("Creating top and bottom summary list")
	fullStats=dict()
	for player in players:
		for key in player.stats:
					#for i in stats:
					if (key in fullStats):
						fullStats[key].append(StatPair(player,player.stats[key]))
					else:
						fullStats[key]=[]
						fullStats[key].append(StatPair(player,player.stats[key]))
			

					if not (key in stats):
						stats[key]=Stat(key,player.stats[key],player.name)
					else:
						stats[key].max(player.stats[key],player.name)
						stats[key].min(player.stats[key],player.name)
					if key in globalStats:
						globalStats[key]+=player.stats[key]
					else:
						globalStats[key]=player.stats[key];
	save_obj(uuids,"uuid")				
	file=open(path+"/Leader Board.txt",'w')
	for key in stats:
		#print (stats[key])
		file.write("\n"+str(stats[key]))
	print("wrote summary to "+path+"/Leader Board.txt")
	file.close()
	print("Writing names of all players")
	file=open(path+"/Names.txt",'w')
	playerList=[]
	for player in players:
		file.write("\n"+str(player))
	players.sort(key=lambda x: x.name,reverse=False)
	file.close()
	file=open(path+"/total.txt",'w')
	jsonfile=open(path+"/json/leaderboard.json",'w')
	jsonfile.write("[");
	print("Writing total for each stat")
	index=0
	statList=[]
	first=True
	for key in globalStats:
		if first:
			first=False
		else:
			jsonfile.write(',')
		stat=stats[key]
		file.write("\n"+str(key)+": "+str(globalStats[key]))
		jsonfile.write('{"name":"'+str(key)+
			'","total":'+str(globalStats[key])+
			',"max":{\"amount\":'+str(stat.maxV)+
				',\"players\":'+str(stat.maxPlr).replace("'",'"')+
			'},"min":{\"amount\":'+str(stat.minV)+
				',\"players\":'+str(stat.minPlr).replace("'",'"')+
		'}}')

		statList.append(key)
	statList.sort(key=lambda x: x,reverse=False)
	for stat in statList:
		index+=1
	#print(statList)
	jsonfile.write("]");
	file.close()
	jsonfile.close()
	if len(sys.argv)>2:
		title=sys.argv[2]
	else:
		title=input("HTML Title: ")
	print("writing comprehensive summary of each stat")
	
	for key in fullStats:
		fullStats[key].sort(key=lambda x: x.value,reverse=True)
		#print(key)
		file=open(path+"/full/stat/"+key+".txt",'w+')
		jsonfile=open(path+"/json/stat/"+key+".json",'w+')
		htmlfile=open(path+"/html/stat/"+key+".html",'w+')
		jsonfile.write("[")
		total=0
		c=0
		for p in fullStats[key]:
			total+=p.value
			c+=1
		descrip=f"Total: {total}"
		for i,p in enumerate(fullStats[key][0:10]):
			descrip+=f"\n{i+1}: {p.player.name}: {p.value} ({round(p.value/max(total,1)*100)}%)"
		if c>10:
			descrip+="\n..."
		htmlfile.write(f"""<!DOCTYPE html>
		<html>
			<head>
				
				<title>{title} | {key}</title>
				<link rel="stylesheet" href="../statsStyle.css">
				<link rel="stylesheet" href="../darkmode.css">
				<link rel="stylesheet" href="../statsDarkmode.css">
				<meta property="og:title" content="{title} | {key}">
				<meta property="og:description" content="{descrip}">
				<meta property="og:type" content="website">
			</head>
			<body>
			<h1><a href="../">All Stats</a> &gt {key} <radio>
		  <input type="radio" onchange="activateLightMode()" name="toggle" id="saneMode" checked>
		  <label for="saneMode" class="sanemode" title="Light Mode"></label>
		  <input type="radio" onchange="activateDarkMode()"   name="toggle" id="darkMode">
		  <label for="darkMode" class="darkmode" title="Dark Mode"></label> 
		  <input type="radio" onchange="activateAmoledMode()" name="toggle" id="amoledMode"> 
		  <label for="amoledMode" class="amoledmode" title="AMOLED Mode"></label>
			</radio></h1>
			<span class="total" id="total">Total: {total}</span>
			<input type="text" id="searchInput" placeholder="Filter by Username">
			<ul id="listContainer">
					<li class="list-item header"><span class='rank'>Rank</span><span class='name'>Username</span><span class='number'>Raw Stat</span><span class='percentage'>% of Total</span><div class='progress-bar header'> Distribution</div></li>
	""")

		file.write(key+"\n");
		first=True
		for i,p in enumerate(fullStats[key]):
			if first:
				first=False
			else:
				jsonfile.write(',')
			file.write(str(c)+": "+str(p)+"\n")
			
			jsonfile.write('{"\"name\"":"'+str(p.player.name)+'","\"amount\"":'+str(p.value)+"}")
			htmlfile.write(f"<li class='list-item'><span class='rank'>#{i+1}</span><span class='name'><a class='profile_link' href='../player/{p.player.name}.html'><img class='inline_face' src='../faces/{p.player.name}.png'>{p.player.name}</a></span><span class='number'>{p.value}</span><span class='percentage'>{round(p.value/max(total,1)*100)}%</span><div class='progress-bar'</div><div class='progress-bar-fill' style='width: {p.value/max(total,1)*100}%;'</div></li>\n")
			
			
			p.player.stat_ranks.append((i, p.value/max(total,1)*100, p.value, len(fullStats[key]), key))
		file.write("Total "+ str(total))
		htmlfile.write("""</ul>
		<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
		<script src="../statsScript.js"></script>
		</body>
	</html>
		""")
		jsonfile.write("]")
		htmlfile.close()
		file.close()
		jsonfile.close()
	
	print("Finished writing comprehensive summary, it is available in "+path+"\\full")
	print("Working on individual player files")
	
	for player in players:
		
		file=open(path+"/full/player/"+player.name+".txt",'w+')
		jsonfile=open(path+"/json/player/"+player.name+".json",'w+')
		htmlfile=open(path+"/html/player/"+player.name+".html",'w+')
		jsonfile.write("{")
		jsonfile.write('"name":'+player.name+",")
		jsonfile.write('"stats":{')
		#print(player.stat_ranks)
		player.stat_ranks.sort(key=lambda x: x[1]*x[3]/100-x[0],reverse=True)#percentage*competition rewards stats with a large percentage and a large number of players competing for it (30% of 30 is 9)  while lowering large percentage solos (100% of 1 is 1).  then -rank downgrades stats where the player was not the top while still leaving the number 1-3 mostly untouched.  In theory as competition increases, players are less likely to get high percentages unless they are standouts
		descrip=f"Top Stats:\n"
		for i,stat in enumerate(player.stat_ranks[0:min(len(player.stat_ranks),10)]):
			descrip+=f"#{stat[0]+1} in {stat[4].replace('minecraft.','').replace('.',' ').replace('_',' ')}: {stat[2]} ({round(stat[1])}%)\n"
		if len(player.stat_ranks)>10:
			descrip+="\n..."

		htmlfile.write(f"""<!DOCTYPE html>
		<html>
			<head>
				
				<title>{title} | {player.name}</title>
				<link rel="icon" type="image/png" href="../faces/{player.uuid}.png">
				<link rel="stylesheet" href="../playerStyle.css">
				<link rel="stylesheet" href="../darkmode.css">
				<link rel="stylesheet" href="../statsDarkmode.css">
				<meta property="og:title" content="{title} | {player.name}">
				<meta property="og:description" content="{descrip}">
				<meta property="og:type" content="website">
			</head>
			<body>
			<h1><a href="../">All Stats</a> &gt <img class='inline_face' src='../faces/{player.uuid}.png'> {player.name} <radio>
		  <input type="radio" onchange="activateLightMode()" name="toggle" id="saneMode" checked>
		  <label for="saneMode" class="sanemode" title="Light Mode"></label>
		  <input type="radio" onchange="activateDarkMode()"   name="toggle" id="darkMode">
		  <label for="darkMode" class="darkmode" title="Dark Mode"></label> 
		  <input type="radio" onchange="activateAmoledMode()" name="toggle" id="amoledMode"> 
		  <label for="amoledMode" class="amoledmode" title="AMOLED Mode"></label>
			</radio></h1>
			<input type="text" id="searchInput" placeholder="Filter by Stat">
			<ul id="listContainer">
					<li class="list-item header"><span class='GWR'>Achivement</span><span class='name'>Stat</span><span class='rank'>Rank</span><span class='number'>Raw Stat</span><span class='percentage'>% of Total</span></li>
	""")

		file.write("stat, rank, value, (percentage) \n");
		first=True
		for i,stat in enumerate(player.stat_ranks):
			if first:
				first=False
			else:
				jsonfile.write(',')
			file.write(stat[4]+": #"+str(stat[0]+1)+", "+str(stat[2])+"("+str(round(stat[1]))+"%)\n")
			# rank[0], percentage[1], value[2], comp[3], name[4]
			jsonfile.write('{"\"name\"":"'+str(stat[4])+'","\"amount\"":'+str(stat[2])+',"rank":'+str(stat[0]+1)+',"GWR":'+str(i+1)+',"percentage":'+str(stat[1])+"}")
			htmlfile.write(f"<li class='list-item'><span class='GWR'>{i+1}:</span><span class='name'><a class='stat_link' href='../stat/{stat[4]}.html'>{stat[4]}</a></span><span class='rank'>#{stat[0]+1}</span><span class='number'>{stat[2]}</span><span class='percentage'>{round(stat[1])}%</span></li>\n")
			
			
		htmlfile.write("""</ul>
		<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
		<script src="../playerScript.js"></script>
		</body>
	</html>
		""")
		jsonfile.write("}}")
		htmlfile.close()
		file.close()
		jsonfile.close()
	print("Finished Player Files")
	print("Working on comprehensive csv")
	file=open(path+"/stats.csv","w")
	header="Player Name"
	for stat in statList:
		header+=","+stat
	file.write(header+"\n")
	for player in players:
		line=player.name
		for stat in statList:
			if stat in player.stats:
				line+=","+str(player.stats[stat])
			else:
				line+=",0"
		file.write(line+"\n")
	file.close()
	print("Finished")

