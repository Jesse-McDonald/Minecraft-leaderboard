from os import walk
import os
from json import *
from urllib.request import *
from time import sleep
import pickle
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
          return "Most:  "+self.name+": "+str(self.maxV)+" "+str(self.maxPlr)+"\nLeast: "+self.name+": "+str(self.minV)+" "+str(self.minPlr)
#stats.append(Stat("generic",0,"none"))
globalStats =dict()
class Player:
     def __init__(self,uuid):
          self.score=0;
          self.name="Useful Minecraft Resources"
          if uuid in uuids:
               self.name=uuids[uuid]
          else:
               self.namemc(uuid)
               uuids[uuid]=self.name
               save_obj(uuids,"uuid")

                    
               
          self.uuid=uuid
          self.stats=dict()
          if self.name=="Useful Minecraft Resources":
               print(uuid)
          #print(page)
          print(self.name)
                    
     def mcuuid(self,uuid):
          i=0
          while(self.name=="Useful Minecraft Resources" and i<5):
               page = urlopen(Request("http://mcuuid.net/?q="+uuid,headers={'User-Agent' : "Magic Browser"}))
               page=str(page.read());
               start=page.find("<h3>")
               end=page.find("</h3>")
               self.name=page[start+4:end]
               #page=page[0:start]+page[end+5:-1]
               sleep(2)
               i+=1
               print(i)
          if i>=5:
               self.name="[MISSING] UUID= "+uuid
               
     def namemc(self, uuid):
          try:
               page = urlopen(Request("http://namemc.com/profile/"+uuid,headers={'User-Agent' : "Magic Browser"}))
               page=str(page.read());
               #print(page)
	 
               start=page.find("<h1 translate=\"no\">")              
               end=page.find("</h1>")
               self.name=page[start:end]
               #print(self.name)
               self.name=self.name[self.name.find('>')+1:]
   
               #print(self.name)
               #page=page[0:start]+page[end+5:-1]
          except:
               self.mcuuid(uuid)
          sleep(5)


     def __str__(self):
          return self.name
def extract(path,name):
     if(".json" in name):
          players.append(Player(name[0:name.find('.')]));
          stringin=open (path,'r')
          jsonIn=stringin.read()
          players[-1].stats=dict(loads(jsonIn))
     
     
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
          if key[0:5]=="stat.":
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
file=open(path+"\Leader Board.txt",'w')
for key in stats:
     #print (stats[key])
     file.write("\n"+str(stats[key]))
print("wrote summary to "+path+"\\Leader Board.txt")
file.close()
print("Writing names of all players")
file=open(path+"/Names.txt",'w')
for player in players:

     file.write("\n"+str(player))

file.close()
file=open(path+"/total.txt",'w')
print("Writing total for each stat")
for key in globalStats:
    file.write("\n"+str(key)+": "+str(globalStats[key]))
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
    for p in fullStats[key]:
        c+=1
        file.write(str(c)+": "+str(p)+"\n")
        total+=p.value
    file.write("Total "+ str(total))
    file.close()
print("Finished writing comprehensive summary, it is avaliable in"+path+"\\full")
save_obj(uuids,"uuid")
save_obj(players,"players")
