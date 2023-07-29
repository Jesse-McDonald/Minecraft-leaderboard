# Minecraft-leaderboard
This program will navigate to the stats folder of a Minecraft world, once there it will collect the UUID’s of all players recorded there and lookup the corresponding user name from a server.
After that the program analyzes each stat for the single player who did the best and worst at all stats
This collection of stats is then output in a text file, as are the names,
The program also creates an offline name UUID database to query instead of the server and saves several objects using pickle in case anyone wants to open and examine them later.
As of version 2.0 the program also exports a directory with a full summary of each stat in its own file.
