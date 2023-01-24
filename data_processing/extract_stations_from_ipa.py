#!/usr/bin/env python3
# This script converts train data files, such as 'trains' from IPA, into a list
# of train stations.
import argparse
import json
import locale
import sys


if __name__ == '__main__':
    argpar = argparse.ArgumentParser()
    argpar.add_argument('trains_file', nargs='+', help='file with train data')
    argpar.add_argument('-o', '--output', type=argparse.FileType('w'),
                        default=sys.stdout)

    args = argpar.parse_args()

    stations = set()
    for path in args.trains_file:
        with open(path, 'r') as f:
            trains = json.load(f)['trains']
            for train in trains:
                stations.update(train['stations'])

    # In case the system locale isn't set up correctly, this might be helpful.
    # locale.setlocale(locale.LC_COLLATE, "pl_PL.UTF-8")
    for s in sorted(stations, key=locale.strxfrm):
        if s != "":
            print(s, file=args.output)

    args.output.close()
