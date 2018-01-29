
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema

OSM_PATH = "ex_cwUTsyRdYdwX3NxTMws7UE6r5QERA.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        dict_attribs = element.attrib
        node_attribs["id"] = element.attrib["id"]
        node_attribs["lat"] = element.attrib["lat"]
        node_attribs["lon"] = element.attrib["lon"]
        node_attribs["user"] = element.attrib["user"]
        node_attribs["uid"] = element.attrib["uid"]
        node_attribs["version"] = element.attrib["version"]
        node_attribs["changeset"] = element.attrib["changeset"]
        node_attribs["timestamp"] = element.attrib["timestamp"]
        

        for child_tag in element:
            childAttrib = {}
            # if the child tag has the tag name "tag":
            if child_tag.tag == "tag":
                tag_attribs = child_tag.attrib
                
                # see if there is a problem character. If no problem character is present, proceed.
                match = PROBLEMCHARS.search(tag_attribs["k"])
        
                if match is None:
                    #create a dict for each child_tag
                    childAttrib["id"] = element.attrib["id"]
                        
                    #if there is a colon in the tag "k" value:
                    colonMatch = re.search(":", tag_attribs["k"])
                    if colonMatch is not None:
                        
                        #if there are more than one colon:
                        numberOfColons = len(re.findall(":", tag_attribs["k"]))
                        if numberOfColons > 1:
                            kValueList = re.split(":", tag_attribs["k"], maxsplit = 1)
                            
                            # characters after the first colon are the key value for childAttrib dictionary
                            childAttrib["key"] = kValueList[1]
                            
                            childAttrib["value"] = tag_attribs["v"]
    
                            # characters before the first ":" are the type value for childAttrib dictionary
                            childAttrib["type"] = kValueList[0]
                            
                        else:
                            kValueList = re.split(":", tag_attribs["k"], maxsplit = 1)
                            childAttrib["key"] = kValueList[1]
                            childAttrib["value"] = tag_attribs["v"]
                            childAttrib["type"] = kValueList[0]
                            
                    else:
                        childAttrib["key"] = tag_attribs["k"]
                        childAttrib["value"] = tag_attribs["v"]
                        childAttrib["type"] = "regular"
                        
                        
                    #add the dict to "tags" list
                    tags.append(childAttrib)
                    
                # if there WAS a problem character in "k" attrib, skip the secondary tag    
                else:
                    break
            else:
                break
        return {'node': node_attribs, 'node_tags': tags}
        
#------------------------------------------------------------------------------------------------------    
    elif element.tag == 'way':
        numPos = 0
        dict_attribs = element.attrib
        way_attribs["id"] = element.attrib["id"]
        way_attribs["user"] = element.attrib["user"]
        way_attribs["uid"] = element.attrib["uid"]
        way_attribs["version"] = element.attrib["version"]
        way_attribs["changeset"] = element.attrib["changeset"]
        way_attribs["timestamp"] = element.attrib["timestamp"]
        
        # print way_attribs
        for child_tag in element:
            childAttrib = {}
            # if the child tag has the tag name "tag":
            if child_tag.tag == "tag":
                tag_attribs = child_tag.attrib
                # see if there is a problem character. If no problem character is present, proceed.
                match = PROBLEMCHARS.search(tag_attribs["k"])
        
                if match is None:
                    #create a dict for each child_tag
                    childAttrib["id"] = dict_attribs["id"]
                        
                    #if there is a colon in the tag "k" value:
                    colonMatch = re.search(":", tag_attribs["k"])
                    if colonMatch is not None:
                        
                        #if there are more than one colon:
                        numberOfColons = len(re.findall(":", tag_attribs["k"]))
                        if numberOfColons > 1:
                            kValueList = re.split(":", tag_attribs["k"], maxsplit = 1)
                            # characters after the first colon are the key value for childAttrib dictionary
                            childAttrib["key"] = kValueList[1]
                            
                            childAttrib["value"] = tag_attribs["v"]
                            
                            # characters before the first ":" are the type value for childAttrib dictionary
                            childAttrib["type"] = kValueList[0]
                            
                        else:
                            kValueList = re.split(":", tag_attribs["k"], maxsplit = 1)
                            childAttrib["key"] = kValueList[1]
                            childAttrib["value"] = tag_attribs["v"]
                            childAttrib["type"] = kValueList[0]
                    else:
                        childAttrib["key"] = tag_attribs["k"]
                        childAttrib["value"] = tag_attribs["v"]
                        childAttrib["type"] = "regular"
                        
                    #add the dict to "tags" list
                    tags.append(childAttrib)
            elif child_tag.tag == "nd":
                nd_attribs = child_tag.attrib
                childAttrib["id"] = way_attribs["id"]
                childAttrib["node_id"] = nd_attribs["ref"]
                childAttrib["position"] = numPos
                numPos = numPos + 1
                way_nodes.append(childAttrib)   
                
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
        

# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()


        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    
    process_map(OSM_PATH, validate=True)
