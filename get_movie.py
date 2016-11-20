import json,urllib2
import pymongo
import yaml

conn = pymongo.MongoClient('localhost')              #Mongo Stuff
conn.admin.authenticate('root','themenwhopause')
db = conn.admin
rec = db.movie

def get_movie(movie_name):
	movie_name = movie_name.replace(' ','+')
	print "movie_name",movie_name
	api_end = "http://www.omdbapi.com/?t=%s&y=&plot=short&r=json" %(movie_name)
	
	movie_in_db = rec.find_one({"Title":{'$regex':movie_name,'$options':"$i"}})
	print movie_in_db

	if(movie_in_db != None):
		print "Movie found in mongo!"			#First search for entry in MOngo, if not found, go online!
		return movie_in_db
	else:		
		print "Movie not in mongo, fetching..."
		try:
			page = eval(urllib2.urlopen(api_end).read())
			print "Page found"
		except:
			print "Error 404"
		with open('movie.json','w') as f:
			f.write(json.dumps(page))	
		return insert_to_mongo(movie_name)

def insert_to_mongo(movie_name):
	f = open('movie.json','r').read()		#All json files used are temporary!	
	parsed_json = yaml.safe_load(f)
	try:
		rec.insert(parsed_json)
		print 'Inserted into mongo!'
		return parsed_json
	except:
		print"Can't insert into mongo"	






