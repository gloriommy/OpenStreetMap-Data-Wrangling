import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "ex_cwUTsyRdYdwX3NxTMws7UE6r5QERA.osm"
#OSMFILE = "sample.osm2"

#reg expression that will find 5 digit postal code
fiveDigitPostcode = re.compile('[0-9]{5}', re.IGNORECASE)

def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")


def changePostcode(osmfile):
    osm_file = open(osmfile, "r+")
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postcode(tag):
                    postcode = tag.attrib['v'] 
                    match = fiveDigitPostcode.search(postcode)
                    if match is not None:
                        #change postal code to just a 5 digit number.
                        tag.attrib['v'] = match.group()
    osm_file.close()

        
changePostcode(OSMFILE)










