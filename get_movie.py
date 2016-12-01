import json
import urllib2
import pymongo
import yaml
from watson_developer_cloud import ToneAnalyzerV3
from configuration import USERNAME, PASSWORD, KEY, PORT, ADDRESS
from watson_api import WATSON

conn = pymongo.MongoClient(ADDRESS)              # Mongo Stuff
conn.admin.authenticate(USERNAME, PASSWORD)
db = conn.admin
rec = db.movie
tone_analyzer = None


def dump_to_json(file_name, object_name):
    with open(file_name, "w") as f:
        f.write(json.dumps(object_name))


def get_senti():
    global tone_analyzer
    if tone_analyzer is None:
        try:
            tone_analyzer = ToneAnalyzerV3(**WATSON)
        except:
            print "Watson's out of coverage"
    return tone_analyzer


def get_movie(movie_name):
    api_end = "http://www.omdbapi.com/?t=%s&y=&plot=short&r=json" % movie_name.replace(' ','+')
    page = rec.find_one({'Title': {'$regex': movie_name, '$options': "$i"}})
    found = page is not None
    if found:
        del page['_id']
    else:
        try:
            page = eval(urllib2.urlopen(api_end).read())
        except:
            return {}
    dump_to_json('movie.json', page)
    if not found:
        insert_to_mongo()
    return page


def senti_analysis(movie_name):
    movie_in_db = rec.find_one({"Title": {'$regex': movie_name, '$options': "$i"}})
    analyzer = get_senti()
    if analyzer is None:
        return {}
    return analyzer.tone(text=movie_in_db['Plot'])


def insert_to_mongo():
    f = open('movie.json', 'r').read()        # All json files used are temporary!
    parsed_json = yaml.safe_load(f)
    try:
        rec.insert(parsed_json)
    except:
        pass
