# python3.10 parse.py < file.txt

import argparse
import sys

if len(sys.argv) > 2:
    if sys.argv[1] == '--help' or sys.argv[1] == '-h':
        sys.exit(10)

arguments = argparse.ArgumentParser(
                                    prog='parse.py',
                                    description='IPPcode24 to XML parser')
args = arguments.parse_args()

# kontrola hlavicky
header = input()
if header.lower() != '.ippcode24':
    sys.exit(21)

# zpracovani radku souboru ze vstupu
for line in sys.stdin:   
    readLine = line.strip().split(' ', -1)
    print(readLine)







print("Hello, world!")
