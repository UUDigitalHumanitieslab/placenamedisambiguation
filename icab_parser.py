import argparse
import os
import sys
import xml.etree.ElementTree as ET


def parseArguments(sysArgs):
    parser = argparse.ArgumentParser(
        description='Extract text only from I-CAB corpus. Produces txt files with the plain text')

    parser.add_argument(
        '--dir',
        dest='root_dir', required=True,
        help="The root directory that your input files are in")

    parser.add_argument(
        '--ext',
        dest='extension', default=".txt",
        help="The extension of the files to be included. Defaults to '.txt'.")

    parser.add_argument(
        '--out',
        dest='output_folder', default=".txt",
        help="The directory where to write the output. Has to exist / will not be created.")

    parsedArgs = parser.parse_args()

    return parsedArgs


def main(sysArgs):
    args = parseArguments(sysArgs)

    for folder, subs, files in os.walk(args.root_dir):
        for filename in files:
            if filename.endswith(args.extension):
                text = extract_text(os.path.join(folder, filename))
                new_name = filename.replace(args.extension, '.txt')
                print("extracting '{}' to '{}'".format(os.path.join(folder, filename), os.path.join(args.output_folder, new_name)))
                write_to_file(args.output_folder, new_name, text)


def extract_text(icab_file_path):    
    tree = ET.parse(icab_file_path)
    root = tree.getroot()

    for child in root:
        if (child.tag == 'TEXT'):
            return child.text


def write_to_file(folder, filename, text):
    with open(os.path.join(folder, filename), "w") as outfile:
        outfile.write(text)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
