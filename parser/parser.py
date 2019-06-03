import argparse
import os
import sys
import xml.etree.ElementTree as ET
import html

###
#  Input validation
###
def route(input):
    parts = input.split('#')
    for index in range(len(parts)):
        part = parts[index]
        is_last = index == len(parts) - 1

        if not part:
            raise argparse.ArgumentTypeError(
            "route '{}' may not contain empty elements.".format(input))

        if not is_last and '[' in part:
            raise argparse.ArgumentTypeError(
            "route '{}' may only contain an attribute in the last element.".format(input))

    return input


def dir(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(
            "Path '{}' is not a directory".format(path))
    return path


def extension(input):
    if input.startswith("."):
        return input
    else:
        return ".{}".format(input)


def parseArguments(sysArgs):
    parser = argparse.ArgumentParser(
        description='Extract text only from I-CAB corpus. Produces txt files with the plain text.')

    parser.add_argument(
        '--dir',
        dest='root_dir',
        required=True,
        type=dir,
        help="The root directory that your input files are in.")

    parser.add_argument(
        '--ext',
        dest='extension',
        type=extension,
        default=".xml",
        help="The extension of the files to be included. Defaults to '.xml'.")

    parser.add_argument(
        '--out',
        dest='output_folder',
        required=True,
        type=dir,
        help="The directory where to write the output. Has to exist / will not be created.")

    parser.add_argument(
        '--route_to_content',
        dest='route',
        help="""The route (i.e. path) to the node the textual content needs to be extracted from. 
                To extract the content from all 'content' nodes that are direct children of 'parent', 
                provide 'parent#content'. If the content is in an attribute, you can do: 
                'tagname[attributename]' (note that these are only allowed in the last element of the route).

                A route cannot contain empty elements (i.e. ## is not allowed), but you can provide wildcards.
                If, for example, you need to extract text from a node 'text' that lives in 'sibling1' and 'sibling2',
                which are both direct children of 'parent', you can provide 'parent#*#text'.
                
                Beware of namespaces! If a namespace applies to the tag you want to extract, you should add 
                it to the tagname. For example: '{http://any.namespace.you/need}tagname'. 
                
                More info and examples in the README""",
        type=route)

    parsedArgs = parser.parse_args()

    return parsedArgs

###
# Do the work
###
def main(sysArgs):
    args = parseArguments(sysArgs)

    print(args)

    for folder, subs, files in os.walk(args.root_dir):
        for filename in files:
            if filename.endswith(args.extension):
                text = extract_text(os.path.join(folder, filename), args.route)
                new_name = filename.replace(args.extension, '.txt')
                print("extracting '{}' to '{}'".format(os.path.join(
                    folder, filename), os.path.join(args.output_folder, new_name)))
                write_to_file(args.output_folder, new_name, text)


def extract_text(file_path, route_to_text):
    # first unescape HTML if it is present
    with open(file_path, 'r') as file:
        xml = file.read()
    html_unescaped = html.unescape(xml)
    root = ET.fromstring(html_unescaped)

    return collect_text(root, route_to_text)


def collect_text(xml, route_to_text):
    # if the route contains the root tag we need to skip it
    skip_first = xml.tag == route_to_text.split('#')[0]

    route = parse_route(route_to_text, skip_first)
    nodes_with_text = xml.findall(route['query'])

    text = []

    for node in nodes_with_text:
        if not route['attr'] is None:
            text.append(node.attrib[route['attr']])
        else:
            text.append(node.text)

    return ' '.join(text)


def parse_route(route, skip_first):
    '''
    Parses a route of format 'node#childnode#childnode[attribute]'
    into XPATH query

    actual = xml.findall(".//child/contentnode[@content]")
    actual = xml.findall(".//child/contentnode")

    '''
    tags = route.split('#')

    if skip_first:
        tags.pop(0)

    xpath_query = "./"
    attribute = None

    for i in range(len(tags)):
        tag = tags[i]
        if '[' in tag:
            tag_attribute = tag.split('[')
            tag = tag_attribute[0]
            attribute = tag_attribute[1][:-1]

        xpath_query = "{}/{}".format(xpath_query, tag)

        if not attribute is None:
            xpath_query = "{}[@{}]".format(xpath_query, attribute)

    return {'query': xpath_query, 'attr': attribute}


def write_to_file(folder, filename, text):
    with open(os.path.join(folder, filename), "w") as outfile:
        outfile.write(text)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
