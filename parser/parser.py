import argparse
import os
import sys

from bs4 import BeautifulSoup

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
                "route_to_content '{}' may not contain empty elements.".format(input))

        if not is_last and '[' in part:
            raise argparse.ArgumentTypeError(
                "route_to_content '{}' may only contain an attribute in the last element.".format(input))

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
        description='Extract textual content from XML or HTML to plain text files.')

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
        required=True,
        help="""The route (i.e. path) to the node the textual content needs to be extracted from.
                To extract the content from all 'content' nodes that are direct children of 'parent',
                provide 'parent#content'. If the content is in an attribute, you can do:
                'tagname[attributename]' (note that these are only allowed in the last element of the route).

                A route cannot contain empty elements (i.e. ## is not allowed), but you can provide wildcards.
                If, for example, you need to extract text from a node 'text' that lives in 'sibling1' and 'sibling2',
                which are both direct children of 'parent', you can provide 'parent#*#text'.                

                More info and examples in the README""",
        type=route)

    parsedArgs = parser.parse_args()

    return parsedArgs


def fatal(message):
    print(message)
    sys.exit(1)

###
# Do the work
###


def main(sysArgs):
    args = parseArguments(sysArgs)

    for folder, subs, files in os.walk(args.root_dir):
        for filename in files:
            if filename.endswith(args.extension):
                new_name = filename.replace(args.extension, '.txt')
                
                if not os.path.exists(os.path.join(args.output_folder, new_name)):
                    print("Processing '{}'".format(filename))
                    text = extract_text(os.path.join(folder, filename), args.route)
                    write_to_file(args.output_folder, new_name, text)


def extract_text(file_path, route_to_text):
    '''
    Extract the desired text content from a file containing HTML or XML.
    '''
    try:
        with open(file_path, 'r') as file:
            soup = BeautifulSoup(file, features="html.parser")
    except UnicodeDecodeError as e:
        print("Error when decoding '{}' More info: {}".format(file_path, e))
        exit(1)

    return collect_text(soup, route_to_text)


def collect_text(soup, route_to_text):
    '''
    Collect the text content from a BeautifulSoup instance based on a route.
    '''
    parsed_route = parse_route(route_to_text)

    try:
        elements = soup.select(parsed_route['query'])
    except SyntaxError:
        fatal("Your route contains invalid syntax. Please review it and try again.")

    return get_text(elements, parsed_route['attr'])


def get_text(elements, attribute):
    '''
    Get the text from a set of HTML or XML elements.

    Keyword arguments:
        elements -- The set of elements containg the text content.
        attribute -- The name of the attribute (of an element) that contains the text content. 
            Can be 'None' if the text is not in an attribute.
    '''
    text = []

    for elem in elements:
        if not attribute is None:
            text.append(elem.attrs[attribute])
        else:
            text.append(elem.text)

    return ' '.join(text)


def parse_route(route):
    '''
    Parses a route of format 'node#childnode#subchildnode[attribute]'
    into a CSS Selector (e.g. 'node childnode subchildnode[attribute]')
    '''
    tags = route.split('#')

    query = None
    attribute = None

    for i in range(len(tags)):
        tag = tags[i]
        if '[' in tag:
            tag_attribute = tag.split('[')
            tag = tag_attribute[0]
            attribute = tag_attribute[1][:-1]

        if query is None:
            query = tag
        else:
            query = "{} {}".format(query, tag)

        if not attribute is None:
            query = "{}[{}]".format(query, attribute)

    return {'query': query, 'attr': attribute}


def write_to_file(folder, filename, text):
    with open(os.path.join(folder, filename), "w") as outfile:
        outfile.write(text)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
