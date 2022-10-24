import argparse
import json
from os import environ
import os
from os.path import join, dirname
from dotenv import load_dotenv

from scraper.clean_data import DiaperCleaner, MissingDataException, NotDiaperException



class bcolors:
   HEADER = '\033[95m'
   OKBLUE = '\033[94m'
   OKGREEN = '\033[92m'
   WARNING = '\033[93m'
   FAIL = '\033[91m'
   ENDC = '\033[0m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'

dotenv_path = join(dirname(__file__), '.env')
try:
    load_dotenv(dotenv_path)
except Exception as e:
    raise Exception(f" {bcolors.FAIL}[-]{bcolors.ENDC} Can't locate .env file")

DIR_DATA = environ.get("DIR_DATA")


class CliDiaperCleaner(object):

    def __init__(self, dir, fname):
        self.dir = dir
        self.fname = fname
        self.cleaner = DiaperCleaner()

    def _process_file(self, fname):
        print(f" {bcolors.OKGREEN}[+]{bcolors.ENDC} In {fname}")
        result = []
        items = []
        with open(fname, 'r') as fp:
            items = json.load(fp)
            for item in items:
                try:
                    result.append(self.cleaner.enhance(item))
                except NotDiaperException:
                    print(f" {bcolors.FAIL}[!]{bcolors.ENDC} Not a Diaper found - {item}")
                except MissingDataException:
                    print(f" {bcolors.FAIL}[!]{bcolors.ENDC} Missing data from diaper - {item}")
        splited = fname.split(".")
        fout = f"{splited[0]}.cleaned.{splited[1]}"
        with open(fout, 'w') as fp:
            json.dump(result, fp, indent=2)
        print(f" {bcolors.OKBLUE}[+]{bcolors.ENDC} Out {fout}")
        print(f" {bcolors.OKBLUE}[+]{bcolors.ENDC} Summary:")
        print(f" {bcolors.OKBLUE}[+]{bcolors.ENDC} \t - total: {len(items)}")
        print(f" {bcolors.OKBLUE}[+]{bcolors.ENDC} \t - ignored: {len(items) - len(result)}")

    def process(self):
        if self.dir:
            for root, _, files in os.walk(self.dir):
                for name in files:
                    if 'cleaned' not in name:
                        self._process_file(join(root, name))
        else:
            self._process_file(self.fname)



def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--dir', type=str, default=DIR_DATA, help="Specify input directory")
    parser.add_argument('-f', '--file', type=str, default=None, help="Specify input file")
    args = parser.parse_args()
    c = CliDiaperCleaner(args.dir, args.file)
    c.process()

if __name__ == '__main__':
    main()