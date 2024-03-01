# python3.10 parse.py < file.txt

import sys
import argparse
import xml.etree.ElementTree as ET

noArg = ('createframe', 'pushframe', 'popframe', 'return', 'break')
oneArg = ('defvar', 'call', 'pushs', 'pops', 'write', 'label', 'jump', 'dprint')
twoArgs = ()
threeArgs = ()

orderNum = 1

def checkArgs():
    if len(sys.argv) > 2:
        if sys.argv[1] == '--help' or sys.argv[1] == '-h':
            sys.exit(10)

def writeInstructionToXML(name, args):
    global orderNum
    global xmlRoot
    instruction = ET.Element('instruction', order=str(orderNum), opcode=name.upper())
    xmlRoot.append(instruction)
    orderNum += 1
    # print("pisu", name)
    # for arg in args:
    #     print(arg)

def checkInstructionArgsCount(line):
    instruction = line[0].lower()
    numOfArgs = len(line)

    match numOfArgs:
        case 1:
            if instruction in noArg:
                print(instruction)
                writeInstructionToXML(instruction, None)
            else:
                print('Invalid instruction name', file=sys.stderr)
                sys.exit(22)

            # match instruction:
            #     case 'createframe':
            #         print('createframe')
            #     case 'pushframe':
            #         print('pushframe')
            #     case 'popframe':
            #         print('popframe')
            #     case 'return':
            #         print('return')
            #     case 'break':
            #         print('break')
            #     case _:
            #         print('Invalid instruction name', file=sys.stderr)
            #         sys.exit(22)
                
        case 2:
            print('pojebal2')
        case 3:
            print('pojebal3')
        case 4:
            print('pojebal4')
        case _:
            print('Too many arguments in instruction', file=sys.stderr)
            sys.exit(22)

def isVar():
    print('yup')

def isSymb():
    print('yup')

#=================================================================================================================

# Kontrola argumentu
checkArgs()
arguments = argparse.ArgumentParser(prog='parse.py', description='IPPcode24 to XML parser')
args = arguments.parse_args()

# Kontrola hlavicky -> .IPPcode24
header = input()
if header.lower() != '.ippcode24':
    sys.exit(21)

# TODO Vytvorit XML hlavicku
xmlRoot = ET.Element('program', language='IPPcode24')
# print(xmlRoot)

# Zpracovani radku souboru ze vstupu
for line in sys.stdin:   
    readLine = line.strip().split(' ', -1)
    print(readLine)
    checkInstructionArgsCount(readLine)
    # writeInstructionToXML(line) ???


tree = ET.ElementTree(xmlRoot)
tree.write('klok.xml')




print("POHODINDA!")