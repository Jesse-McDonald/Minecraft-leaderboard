from os import walk
import requests
import os
from json import *
from urllib.request import *
import urllib
from time import sleep
import pickle
from mojang import API
api = API()
def save_obj(obj, name ):
	with open('obj/'+ name + '.pkl', 'wb') as f:
		pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
	with open('obj/' + name + '.pkl', 'rb') as f:
		return pickle.load(f)
players=[]
try:
	uuids=load_obj("uuid")
except:
	uuids={}
stats=dict()
class StatPare:
	def __init__(self,name,value):
			self.name=name
			self.value=value
	def __str__(self):
			return str(self.name)+": "+str(self.value)
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
			if uuid in uuids and uuids[uuid]!=uuid:
				self.name=uuids[uuid]
			else:
				self.name=uuid_api_official(uuid)
				uuids[uuid]=self.name
				save_obj(uuids,"uuid")

			self.uuid=uuid
			self.stats=dict()
			if self.name=="Useful Minecraft Resources":
				print(uuid)
			#print(page)
			print("Name: "+self.name)
			
	def mcuuid(self,uuid):
			i=0
			while(self.name=="Useful Minecraft Resources" and i<5):
				page = urlopen(Request("http://mcuuid.net/?q="+uuid,headers={'User-Agent' : "Magic Browser"}))
				page=str(page.read());
				start=page.find("<h3 id=\"results_username\">")
				start=page.find(">",start)
				end=page.find("</h3>")
				self.name=page[start+4:end]
				#page=page[0:start]+page[end+5:-1]
				sleep(2)
				i+=1
				print("index: "+str(i))
			if i>=5:
				self.name="[MISSING] UUID= "+uuid
				
	def namemc(self, uuid):
			try:
			
	
				while True:
					page = urlopen(Request("http://namemc.com/profile/"+uuid,headers={'User-Agent' : "Magic Browser"}))
					page=str(page.read());
					
			
					start=page.find("<h1")
					end=page.find("</h1>")
					start=page.find(">",start)
					
					self.name=page[start:end]
					#print(self.name)
					self.name=self.name[self.name.find('>')+1:]
					#print (len(self.name))
					if len(self.name)>1:
						break
					sleep(10)
					#print(self.name)
					#page=page[0:start]+page[end+5:-1]
			except:
				self.mcuuid(uuid)
			sleep(5)


	def __str__(self):
			return self.name
			
def uuid_api_official(uuid):
		try:
			name = api.get_username(uuid.replace("-",""))
			#print(name)
			return name		
		except Exception as e:
			print("Exception while looking up UUID: "+uuid+"\n Skipped ")
			return uuid

def uuid_api(uuid):
		try:
			page = requests.get("https://sessionserver.mojang.com/session/minecraft/profile/"+uuid.replace("-",""))
			page=page.json()
			name=""
			lastTime=-1
			for line in page:
				#print (line)
				time=0
				if "changedToAt" in line:
					time=line["changedToAt"]
				if time>lastTime:
					#print(line)
					name=line["name"]
					lastTime=time
			return name		
		except Exception as e:
			print("Exception while looking up UUID: "+uuid+"\n Skipped ")
			return uuid

def extract(path,name):
	if(".json" in name):
			player=Player(name[0:name.find('.')])
			if(len(player.name)>2):
				players.append(player);
				stringin=open (path,'r')
				jsonIn=loads(stringin.read())["stats"]
				players[-1].stats={}
				for key in jsonIn.keys():
					holdString=key;
					for subkey in jsonIn[key].keys():
						tmpstr=subkey.replace("minecraft","")
						players[-1].stats[(holdString+tmpstr).replace(':','.')]=jsonIn[key][subkey]


	
def dirin(mypath):
	for (dirpath, dirnames, filenames) in walk(mypath):
		for path in dirnames:
				dirin(dirpath+'/'+path)
		for path in filenames:
				extract(dirpath+'/'+path,path)

		break
	
path=input("Path directory to be checked: ")
print("looking up UUID's, this can take quite some time")
dirin(path)
print("Creating top and bottom summary list")
fullStats=dict()
for player in players:
	for key in player.stats:
				#for i in stats:
				if (key in fullStats):
					fullStats[key].append(StatPare(player.name,player.stats[key]))
				else:
					fullStats[key]=[]
					fullStats[key].append(StatPare(player.name,player.stats[key]))
		

				if (key in stats):
					if key in globalStats:
						globalStats[key]+=player.stats[key]
					else:
						globalStats[key]=player.stats[key];
					stats[key].max(player.stats[key],player.name)
					stats[key].min(player.stats[key],player.name)
				else:
					stats[key]=Stat(key,player.stats[key],player.name)
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
print("Writing total for each stat")
index=0
statList=[]
for key in globalStats:
	file.write("\n"+str(key)+": "+str(globalStats[key]))
	statList.append(key)
statList.sort(key=lambda x: x,reverse=False)
for stat in statList:
	index+=1
print(statList)
file.close()

print("writing comprehensive summary of each stat")
for key in fullStats:
	fullStats[key].sort(key=lambda x: x.value,reverse=True)
	#print(key)
	if not os.path.exists(path+"/full"):
		os.makedirs(path+"/full")
	file=open(path+"/full/"+key+".txt",'w+')
	c=0
	total=0
	file.write(key+"\n");
	for p in fullStats[key]:
		c+=1
		file.write(str(c)+": "+str(p)+"\n")
		total+=p.value
	file.write("Total "+ str(total))
	file.close()
print("Finished writing comprehensive summary, it is avaliable in "+path+"\\full")
save_obj(uuids,"uuid")
save_obj(players,"players")
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

