import argparse
from preprocessing.functions import anonymize
parser = argparse.ArgumentParser(description='Anonimizar dataset')
parser.add_argument("source", help="nome do arquivo a ser anonimizado.")
parser.add_argument("dest", help="nome do arquivo anonimizado.")
args = parser.parse_args()

if __name__ == '__main__':
    anonymize(args.source, args.dest)
