from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections
import LNEx as lnex
import unicodedata, os, json
import requests, Geohash
from elasticsearch import Elasticsearch
import collections,operator
from collections import defaultdict
import xlrd

dname = "chennai"
geohash_fname = "_Data/"+dname+"_geohashes_8prec.json"
geohash_dict = defaultdict(bool)
if os.path.isfile(geohash_fname):
    print "returning cached file..."
    with open(geohash_fname) as f:
        geohash_dict = json.load(f)
    print len(geohash_dict.keys()), "geohashes"
else:
    print "Geohash File is not in folder"

def flooded(lat, lon):
    geohash = Geohash.encode(lon,lat, precision=8)
    if geohash_dict.get(geohash) is not None:
        return geohash_dict[geohash]
    else:
        return "No Satellite Data!"

def prepare_data(gaz_name):
    #geo_info = init_using_files()
    gaz_name=gaz_name.lower()
    geo_info = init_using_elasticindex(gaz_name)
    #print geo_info
    all_geo_points = prepare_geo_points(gaz_name, geo_info)

    with open("_Data/"+gaz_name+"_all_geo_points.json", "w") as f:
        json.dump(all_geo_points, f)

def init_using_elasticindex(gaz_name):

    lnex.elasticindex(conn_string='localhost:9200', index_name="photon")
    if gaz_name=="chennai":
    	# chennai flood bounding box
    	bb = [12.74, 80.066986084, 13.2823848224, 80.3464508057]
    elif gaz_name=="houston":
	#houston bb
	bb = [29.4778611958,-95.975189209,30.1463147381,-94.8889160156]
    print bb
    return lnex.initialize(bb, augment=True)

def strip_non_ascii(s):

    if isinstance(s, unicode):
        nfkd = unicodedata.normalize('NFKD', s)
        return str(nfkd.encode('ASCII', 'ignore').decode('ASCII'))
    else:
        return s


def get_all_tweets_and_annotations(gaz_name):

    #with open("_Data/Brat_Annotations/houston/Houston_annotations_with_time.json") as f:
    #    data = json.load(f)
    all_tweets_and_annotations = list()
    print gaz_name
    #keys = list()
    with open("_Data/Brat_Annotations/"+gaz_name+"/"+gaz_name.title()+"FloodRelief_C.json") as c:
        for line in c:
            d=json.loads(line)
	    if gaz_name=="houston":

            	text=d["_source"]["tweet"]["text"]
		time=d["_source"]["date"]
		k=d["_source"]["tweet"]["id"]
	    else:
		text=d["tweet"]["text"]
		time=d["date"]
		k=d["tweet"]["id"]
            text=strip_non_ascii(text)
            all_tweets_and_annotations.append((text, k, time))

    return all_tweets_and_annotations

def prepare_geo_points(gaz_name, geo_info):
    os.environ['NO_PROXY']='127.0.0.1'
    all_geo_points = list()
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    count=0
    for tweet in get_all_tweets_and_annotations(gaz_name):
        txt='http://127.0.0.1:8089/classify?text="'+tweet[0]+'"'

        r=requests.get(txt)
	print r.content
        if r.content=="shelter_matching":
            cl="shelter_matching"
            i='/static/shelter.png'
        elif r.content=="infrastructure_need":
            cl="infrastructure_need"
            i='/static/utility_infrastructure'
        else:
            cl="rescue_match"
            i='/static/medical_need.png'
        for ln in lnex.extract(tweet[0]):
            if ln[0].lower() == gaz_name.lower():
                continue
            ln_offsets = ln[1]
            geoinfo = [geo_info[x] for x in ln[3]]
            if len(geoinfo) == 0:
                continue
            for geopoint in geoinfo:
                lat = geopoint["geo_item"]["point"]["lat"]
                lon = geopoint["geo_item"]["point"]["lon"]
                marked_tweet = tweet[0][:ln_offsets[0]] + "<mark>" + tweet[0][ln_offsets[0]:ln_offsets[1]] + "</mark>" + tweet[0][ln_offsets[1]:]
                try:
                    description = """   <table>
                                            <tr>
                                                <td colspan="2">marked_tweet</td>
                                            </tr>
                                        </table> """
                    description = description.replace("marked_tweet", marked_tweet)
                    marker_icon = "marker"
                    fl=flooded(lat,lon)
                    print str(fl)
                    if str(fl)=='True':
                        fld='True'
                    else:
                        fld='False'
		    es.index(index=gaz_name+'-tweets', doc_type='people', id=count, body={"type": "Feature", "geometry": {"type": "Point","coordinates": [lon, lat]}, "properties": { "description": description, "icon": marker_icon,"id":tweet[1],"tweet":tweet[0],"timestamp":tweet[2],"class":cl,"URL":i,"Flood":fld}})
                    all_geo_points.append({"type": "Feature", "geometry": {"type": "Point","coordinates": [lon, lat]}, "properties": { "description": description, "icon": marker_icon,"id":tweet[1],"tweet":tweet[0],"timestamp":tweet[2],"class":cl,"URL":i,"Flood":fld}})
		    count=count+1
                except Exception as e:
                    print e
                    print "ERROR:>>> ", marked_tweet
                    exit()
    #es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    #for i in range(len(all_geo_points)):
	#es.index(index='some_try', doc_type='people', id=i, body=all_geo_points[i])

    return {"type": "FeatureCollection", "features": all_geo_points}

def prepare_data_events(gaz_name):
    gaz_name=gaz_name.lower()
    if gaz_name=="chennai":
        # chennai flood bounding box
        bb = [12.74, 80.066986084, 13.2823848224, 80.3464508057]
    elif gaz_name=="houston":
        #houston bb
        bb = [29.4778611958,-95.975189209,30.1463147381,-94.8889160156]
    p_points=list()
    h=search_index(bb)
    x=0
    count=0
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    for match in h:
	if 'name' in match:
		print match["name"]
		if 'default' in match["name"]:
			x=1
			c=match["name"]['default'].encode('ascii','ignore')
		elif 'en' in match["name"]:
			x=2
			c=match["name"]['en'].encode('ascii','ignore')
		elif 'fr' in match["name"]:
			x=3
			c=match["name"]['fr'].encode('ascii','ignore')
		elif 'alt' in match["name"]:
			x=4
			c=match["name"]['alt'].encode('ascii','ignore')
		elif 'old' in match["name"]:
			x=5
			c=match["name"]['old'].encode('ascii','ignore')
		else:
			x=6
			c=match["name"]['loc'].encode('ascii','ignore')
	elif 'city' in match:
		x=7
		c=match["city"]['default'].encode('ascii','ignore')
	else:
		x=8
		c=match["country"]['default'].encode('ascii','ignore')
	lat=match["coordinate"]["lat"]
	lon=match["coordinate"]["lon"]
	k=match["osm_key"].encode('ascii','ignore')
	v=match["osm_value"].encode('ascii','ignore')
	if ((v=='animal_shelter') or (v=='bus_station') or (v=='shelter')or (k=='shop')):
		cls="shelter_matching"
	elif ((k=='man_made' and v=='pipeline') or (k=='power' and v=='line') or (k=='power' and v=='plant') or (k=='man_made' and v=='communications_tower')or(k=='building' and v=='transformer_tower') or (k=='building' and v=='service') or (k=='power' and v=='minor_line') or (k=='power' and v=='substation') or (k=='craft' and v=='electrician') or (k=='craft' and v=='scaffolder')):
		cls="infrastructure_need"
	elif ((v=='fire_station') or (v=='police') or (v=='post_office') or (v=='rescue_station') or (v=='hospital') or (v=='ambulance_station') or (v=='medical_supply') or (v=='clinic') or (v=='doctors') or (v=='social_facility') or (v=='blood_donation') or (v=='pharmacy') or (v=='nursing_home')):
		cls="rescue_match"
	else:
		continue
	fl=flooded(lat,lon)
	if str(fl)=='True':
		fl='True'
	else:
		fl='False'
		p_points.append({"type": "Feature", "geometry": {"type": "Point","coordinates": [lon, lat]}, "properties": { "name": c, "key": k, "value":v, "class":cls,"number":'2',"Flood":fl}}) 
		es.index(index=gaz_name+'1', doc_type='locs', id=count, body={"type": "Feature", "geometry": {"type": "Point","coordinates": [lon, lat]}, "properties": { "name": c, "key": k, "value":v, "class":cls,"number":'2',"Flood":fl}})
		count=count+1

    p_points_data={"type": "FeatureCollection", "features": p_points}

def search_index(bb):
    '''Retrieves the location names from the elastic index using the given
    bounding box'''

    connections.create_connection(hosts=["localhost:9200"], timeout=60)

    phrase_search = [Q({"filtered": {
        "filter": {
            "geo_bounding_box": {
                        "coordinate": {
                            "bottom_left": {
                                "lat": bb[0],
                                "lon": bb[1]
                            },
                            "top_right": {
                                "lat": bb[2],
                                "lon": bb[3]
                            }
                        }
                        }
        },
        "query": {
            "match_all": {}
        }
    }
    })]

    #to search with a scroll
    e_search = Search(index="photon").query(Q('bool', must=phrase_search))

    try:
        res = e_search.scan()
    except BaseException:
        raise

    return res

def prepare_crowd_source(gaz_name):
    geo_info=init_using_elasticindex(gaz_name)
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    data = xlrd.open_workbook("other_resources.xlsx")
    sheet_no = data.sheet_by_index(0)
    x=[]
    y=[]
    crowd_data=[]
    count=0
    for i in range(sheet_no.nrows):
        if i >= 1:
            x.append(sheet_no.cell(i, 0).value)
            y.append(sheet_no.cell(i, 1).value)
    for text,cls in zip(x,y):
	text=strip_non_ascii(text)
	print text,cls
	for ln in lnex.extract(text):
            if ln[0].lower() == gaz_name.lower():
                continue
            ln_offsets = ln[1]
            geoinfo = [geo_info[x] for x in ln[3]]
            if len(geoinfo) == 0:
                continue
            for geopoint in geoinfo:
                lat = geopoint["geo_item"]["point"]["lat"]
                lon = geopoint["geo_item"]["point"]["lon"]
                marked_tweet = text[:ln_offsets[0]] + "<mark>" + text[ln_offsets[0]:ln_offsets[1]] + "</mark>" + text[ln_offsets[1]:]
                try:
                    description = """   <table>
                                            <tr>
                                                <td colspan="2">marked_tweet</td>
                                            </tr>
                                        </table> """
                    description = description.replace("marked_tweet", marked_tweet)
                    marker_icon = "marker"
                    fl=flooded(lat,lon)
                    print str(fl)
                    if str(fl)=='True':
                        fld='True'
		    else:
                        fld='False'
		    es.index(index=gaz_name+'-crowd', doc_type='crowd', id=count, body={"type": "Feature", "geometry": {"type": "Point","coordinates": [lon, lat]}, "properties": { "description": description, "icon": marker_icon,"tweet":text,"class":cls,"Flood":fld}})
		    crowd_data.append({"type": "Feature", "geometry": {"type": "Point","coordinates": [lon, lat]}, "properties": { "description": description, "icon": marker_icon,"tweet":text,"class":cls,"Flood":fld}})
		    count=count+1
                except Exception as e:
                    print e
                    print "ERROR:>>> ", marked_tweet
                    exit()

if __name__ == "__main__":
    #prepare_data("houston")
    #prepare_data_events("houston")
    prepare_crowd_source("chennai")
    #prepare_data("chennai")
    prepare_data_events("chennai")
