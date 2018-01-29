import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

#OSMFILE = "sample.osm2"
OSMFILE = "ex_cwUTsyRdYdwX3NxTMws7UE6r5QERA.osm"

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

mapping = {
"Rd": "Road", 
"W": "West",
"E": "East",
"S": "South",
"N": "North",
"W ": "West",
"E ": "East",
"S ": "South",
"N ": "Norht",
" W": "West",
" E": "East",
" S": "South",
" N": "Norht",
"avenue" : "Avenue",
"Ave": "Avenue",
"Ave.": "Avenue",
"Aveneu": "Avenue",
"Avene": "Avenue",
"street": "Street", 
"ST": "Street",
"St.": "Street",  
"St" : "Street",
"st" : "Street",
"Steet" : "Street" 
}


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def update_name(osmfile):
    osm_file = open(osmfile, "r+")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    name = tag.attrib['v']
                    #1 Find if the street name ends with any of the keys in "mapping",
                    m = street_type_re.search(name) # Pulling out the endname of the streetname
                    if m:
                        street_type = m.group() # Pulled out endnames of the streets
                        if street_type in mapping.keys():
                            #2 If it does, the endname should be changed to the key's value
                            tag.attrib['v'] = name.replace(street_type, mapping[street_type])
    osm_file.close()



update_name(OSMFILE)







