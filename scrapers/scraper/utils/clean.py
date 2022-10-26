import argparse
import json
import logging
from os import environ
import os
from os.path import join, dirname
import sys
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

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class CliDiaperCleaner(object):

    def __init__(self, dir, fname, fall):
        self.dir = dir
        self.fname = fname
        self.fall = fall
        self.cleaner = DiaperCleaner()

    def _process_file(self, fname):
        logger.info(f" {bcolors.OKGREEN}[+]{bcolors.ENDC} In {fname}")
        result = []
        items = []
        not_diaper = 0
        missing_data = 0
        with open(fname, 'r') as fp:
            items = json.load(fp)
            for item in items:
                try:
                    result.append(self.cleaner.enhance(item))
                except NotDiaperException:
                    not_diaper += 1
                    logger.debug(f" {bcolors.FAIL}[!]{bcolors.ENDC} Not a Diaper found - {item}")
                except MissingDataException as e:
                    missing_data += 1
                    logger.debug(f" {bcolors.FAIL}[!]{bcolors.ENDC} Missing data from diaper - {e.missing_fields} - {item}")
        splited = fname.split(".")
        fout = f"{splited[0]}.cleaned.{splited[1]}"
        with open(fout, 'w') as fp:
            json.dump(result, fp, indent=2)
        if self.fall and result:
            with open(self.fall, 'a') as fp:
                # fp.write(",".join([ str(r) for r in result[0].keys()]) + "\n")
                for r in result:
                    fp.write(",".join([ f'"{str(r)}"' for r in r.values()]) + "\n")
        results = len(items)
        ignored = len(items) - len(result)
        logger.info(f" {bcolors.OKBLUE}[+]{bcolors.ENDC} Out {fout}")
        logger.info(f" {bcolors.OKBLUE}[+]{bcolors.ENDC} Summary:")
        logger.info(f" {bcolors.OKBLUE}[+]{bcolors.ENDC} \t - total: {len(items)}")
        logger.info(f" {bcolors.OKBLUE}[+]{bcolors.ENDC} \t - ignored: {ignored}")
        return results, ignored, not_diaper, missing_data

    def process(self):
        results, ignored, not_diaper, missing_data = 0, 0, 0, 0
        if self.dir:
            for root, _, files in os.walk(self.dir):
                for name in files:
                    if 'cleaned' not in name:
                        _results, _ignored, _not_diaper, _missing_data = self._process_file(join(root, name))
                        results += _results
                        ignored += _ignored
                        not_diaper += _not_diaper
                        missing_data += _missing_data
        else:
            results, ignored, not_diaper, missing_data = self._process_file(self.fname)
        logger.info(f" {bcolors.HEADER}[+]{bcolors.ENDC} Summary:")
        logger.info(f" {bcolors.HEADER}[+]{bcolors.ENDC} \t - ignored: {ignored} (missing_data: {missing_data}, not_diaper: {not_diaper})")
        logger.info(f" {bcolors.HEADER}[+]{bcolors.ENDC} \t - results: {results- ignored}")
        logger.info(f" {bcolors.HEADER}[+]{bcolors.ENDC} \t - total: {results} (results + ignored)")
        return results, ignored



def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-d', '--dir', type=str, default=DIR_DATA, help="Specify input directory")
    parser.add_argument('-f', '--file', type=str, default=None, help="Specify input file")
    parser.add_argument('-O', '--output', type=str, default=None, help="Specify output CSV file")
    args = parser.parse_args()
    c = CliDiaperCleaner(args.dir, args.file, args.output)
    c.process()

if __name__ == '__main__':
    main()