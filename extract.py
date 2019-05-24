from jinja2 import Environment, FileSystemLoader
import os
import sys
import argparse
import requests
import json

from geocoding import Geocoder
from config import MULTI_NER_URL

# Input validation
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


def language(input):
    if input.lower() not in ['nl', 'en', 'it']:
        raise argparse.ArgumentTypeError(
            "Language should be one of 'en', 'nl', 'it'.")
    return input.lower()


def parseArguments(sysArgs):
    parser = argparse.ArgumentParser(
        description='Extract named entities all files in a folder')

    parser.add_argument(
        '--dir',
        dest='root_dir', required=True, type=dir,
        help="The root directory that your input files are in")

    parser.add_argument(
        '--ext',
        dest='extension', default=".txt", type=extension,
        help="The extension of the files to be included. Defaults to '.txt'.")

    parser.add_argument(
        '--out',
        dest='output_dir', required=True, type=dir,
        help="The directory where you want your output to be printed")

    parser.add_argument(
        '--language',
        dest='language', default='en', type=language,
        help="The language of your corpus. Defaults to 'en'")

    parsedArgs = parser.parse_args()

    return parsedArgs


# Do the work
def extract_entities(title, text, language):
    body = {
        "title": title,
        "text": text,
        "configuration": {
            "language": language,
            "context_length": 3,
            "leading_ner_packages": [
                "stanford",
                "spotlight"
            ],
            "other_packages_min": 4
        }
    }

    r = requests.get(MULTI_NER_URL, json=body)

    if 400 <= r.status_code < 500:
        fatal("Something seems to be wrong with this script. Please contact Digital Humanities Lab with these details: 'status code: {}'".format(r.status_code))
    if 500 <= r.status_code < 600:
        fatal("Something is wrong with the multiNER service. Please contact Digital Humanities Lab with these details: 'status code: {}'".format(r.status_code))

    return r.json()


def add_geocodes(args, entities):
    g = Geocoder(entities['text']['entities'], args.language)

    try:
        g.geocode_locations()
    except requests.exceptions.ConnectionError as e:
        fatal(
            "Could not connect to one of the geocoding services. Details: {}".format(e))


def collect_data(args):
    for folder, subs, files in os.walk(args.root_dir):
        for filename in files:
            if filename.endswith(args.extension):
                with open(os.path.join(folder, filename), 'r') as src:
                    text = src.read()
                    print("extracting entities from '{}'".format(filename))
                    entities = extract_entities('test', text, args.language)

                    print("adding geocodes to locations from '{}'".format(filename))
                    add_geocodes(args, entities)

                    export(args, filename, text, entities)
                    print("results for '{}' exported".format(filename))


# Entry point
def main(sysArgs):
    check_env_var("GEONAMES_USERNAME")
    check_env_var("GOOGLE_API_KEY")

    args = parseArguments(sysArgs)
    collect_data(args)


# Output / Export
def export(args, current_filename, text, entities):
    # save json
    new_name = current_filename.replace(args.extension, '.json')
    write_to_file(args.output_dir, new_name, entities)

    # save html
    html_name = current_filename.replace(args.extension, '.html')
    write_html_version(args.output_dir, html_name, text, entities)


def write_to_file(folder, filename, entities):
    with open(os.path.join(folder, filename), "w") as outfile:
        outfile.write(json.dumps(entities))


def write_html_version(folder, filename, text, entities):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('results.html')
    text = text.replace('\r', '').replace('\n', ' ').replace('"', '\'')
    output_from_parsed_template = template.render(entities=entities, text=text)

    with open(os.path.join(folder, filename), "w") as fh:
        fh.write(output_from_parsed_template)

# Helpers
def check_env_var(var_name):
    if not var_name in os.environ:
        fatal("{0} is not present as an environment variable. Please export it with a command like this: 'export {0}=<value>'.".format(var_name))


def fatal(details):
    print(details)
    exit()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
