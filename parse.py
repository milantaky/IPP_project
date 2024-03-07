# IPP project 1 - Parser
# Author: Milan Takac - xtakac09

import sys
import argparse
import xml.etree.ElementTree as ET
import re

def checkArgs():
    if len(sys.argv) > 2:
        if sys.argv[1] == '--help' or sys.argv[1] == '-h':
            sys.exit(10)
    
    arguments = argparse.ArgumentParser(prog='parse.py', description='This code parses IPPcode24 to XML form to be interpreted by interpreter.php.Usage: python3.10 parse.py < input > output')
    args = arguments.parse_args()

def checkHeader():
    header = input().strip()
    while header == '' or header[0] == '#':
        header = input().strip()

    header = header.split('#', 1)
    if header[0].strip().lower() != '.ippcode24':
        sys.exit(21)

def sanitizeLine(line):
    if len(line) == 0: return []
    readLine = line.split('#', 1)
    readLine = line.strip().split(' ', -1)
    readLine = list(filter(lambda x: x != '', readLine))    # Zbaveni se pripadnych bilych znaku v listu
    readLine = removeComments(readLine)
    return readLine

def removeComments(line):
    newList = []
    for item in line:
        if '#' in item:
            if item[0] == '#' or item == '#': return newList
            else:
                item = item.split('#', 1)
                newList.append(item[0])
                break
        else: newList.append(item)
    return newList

def checkInstructionArgsCount(line):
    instruction = line[0].lower()
    numOfArgs = len(line)

    if instruction not in ('createframe', 'pushframe', 'popframe', 'return', 'break', 'defvar', 'call', 'pushs', 'pops', 'write', 'label', 'jump', 'dprint', 'exit', 'move', 'int2char', 'strlen', 'type', 'read', 'not', 'add', 'sub', 'mul', 'idiv', 'lt', 'gt', 'eq', 'and', 'or', 'stri2int', 'concat', 'getchar', 'setchar', 'jumpifeq', 'jumpifneq'): 
        if instruction == '.ippcode24': 
            print('Header duplicate', file=sys.stderr)
            sys.exit(23)
        print('Invalid instruction name', file=sys.stderr)
        sys.exit(22)

    match numOfArgs:
        case 1:
            if instruction in ('createframe', 'pushframe', 'popframe', 'return', 'break'):                  # Bez argumentu
                writeInstructionToXML(instruction, None)
            else:
                print('Invalid instruction name or usage', file=sys.stderr)
                sys.exit(23)
        case 2:
            if instruction in ('defvar', 'call', 'pushs', 'pops', 'write', 'label', 'jump', 'dprint', 'exit'):      # S 1 argumentem
                writeInstructionToXML(instruction, line[1:])
            else:
                print('Invalid instruction name or usage', file=sys.stderr)
                sys.exit(23)
        case 3:
            if instruction in ('move', 'int2char', 'strlen', 'type', 'read', 'not'):      # Se 2 argumenty
                writeInstructionToXML(instruction, line[1:])
            else:
                print('Invalid instruction name or usage', file=sys.stderr)
                sys.exit(23)
        case 4:
            if instruction in ('add', 'sub', 'mul', 'idiv', 'lt', 'gt', 'eq', 'and', 'or', 'stri2int', 'concat', 'getchar', 'setchar', 'jumpifeq', 'jumpifneq'):      # Se 3 argumenty
                writeInstructionToXML(instruction, line[1:])
            else:
                print('Invalid instruction name or usage', file=sys.stderr)
                sys.exit(23)
        case _:
            print('Too many arguments in instruction', file=sys.stderr)
            sys.exit(23)

def writeInstructionToXML(name, args):
    global orderNum
    global xmlRoot
    instruction = ET.Element('instruction', order=str(orderNum), opcode=name.upper())
    xmlRoot.append(instruction)
    orderNum += 1

    args = checkArguments(name, args)  # Pokud chyba v argumentech, dal to nedojde

    if args != None and len(args) > 0:
        for index, arg in enumerate(args):
            argumentElement = ET.Element('arg' + str(index + 1), type=str(arg[0]))
            argumentElement.text = arg[1]
            instruction.append(argumentElement)

def checkArguments(name, args):
    numOfArgs = 0
    check = None
    if name not in ('createframe', 'pushframe', 'popframe', 'return', 'break'): numOfArgs = len(args)

    match numOfArgs:
        case 0:
            return None
        case 1:
            if name in ('defvar', 'pops'):                                          # <var>
                check = [isVar(args[0])]
            elif name in ('pushs', 'write', 'exit', 'dprint'):                      # <symb>
                check = [isSymb(args[0])]
            else:                                                                   # <label>                   'call', 'label', 'jump'
                check = [isLabel(args[0])]
        case 2:
            if name in ('move', 'int2char', 'strlen', 'type', 'not'):               # <var><symb>
                check = [isVar(args[0]), isSymb(args[1])]
            else:                                                                   # <var><type>               'read'
                check = [isVar(args[0]), isType(args[1])]
        case 3:
            if name in ('jumpifeq', 'jumpifneq'):                                   # <label><symb1><symb2>
                check = [isLabel(args[0]), isSymb(args[1]), isSymb(args[2])]
            else:                                                                   # <var><symb1><symb2>       'add', 'sub', 'mul', 'idiv', 'lt', 'gt', 'eq', 'and', 'or', 'stri2int', 'concat', 'getchar', 'setchar'
                check = [isVar(args[0]), isSymb(args[1]), isSymb(args[2])]

        # 4 ani default neni potreb, to je osetreno ve funkci checkInstructionArgsCount
    if False in check:
        print('Incorrect argument:', args , file=sys.stderr)
        sys.exit(23)
    return check

# promenna GF/LF/TF@..., zacina specialnim znakem, nebo pismenem
def isVar(arg):
    if '@' not in arg: return False

    saved = arg
    arg = arg.split('@', 1)
    if arg[0] not in ('GF', 'LF', 'TF'): return False
    
    if isValidName(arg[1]): return ['var', saved]
    return False

# konstanta int,bool,...@..
# muze byt i promenna
def isSymb(arg):
    if '@' not in arg: return False
    var = isVar(arg)
    if var != False: return var

    arg = arg.split('@', 1)
    match arg[0]:
        case 'int':
            if isValidNum(arg[1]): return ['int', arg[1]]
            else: return False
        case 'bool':
            if arg[1] in ('true', 'false'): return ['bool', arg[1]]
            else: return False
        case 'string':
            arg[1] = checkString(arg[1])
            if arg[1] == False: 
                print('Lexical error in string: Wrong usage of \\', file=sys.stderr)
                sys.exit(23)
            return ['string', arg[1]]                               
        case 'nil':
            if arg[1] == 'nil': return ['nil', arg[1]]
            else: return False
        case _:
            return False

# Kontroluje cislo -> oct, dec, hex
def isValidNum(num):
    try:
        x = int(num, 0)
    except:
        return False
    return True

# Pro citelnost
def isLabel(arg):
    if isValidName(arg): return ['label', arg]
    else: return False

def isType(arg):
    if arg in ('int', 'string', 'bool'): return ['type', arg]
    else: return False

def isValidName(name):
    # Je potreba udelat to pro prvni zvlast
    if name[0] not in ('_', '-', '$', '&', '%', '*', '!', '?') and not name[0].isalpha(): return False

    for letter in name:
        if letter not in ('_', '-', '$', '&', '%', '*', '!', '?') and not letter.isalnum(): return False
    return True

def checkString(str):
    badEsc = re.findall('\\\\\d\d\D|\\\\\d\D|\\\\\D|\\\\$', str)
    if len(badEsc) > 0: return False

    str = str.replace('&', '&amp;')
    str = str.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
    return str

#=================================================================================================================

# Kontrola argumentu
checkArgs()
checkHeader()

# Hlavicka a zakladni tag
xmlRoot = ET.Element('program', language='IPPcode24')
orderNum = 1

# Zpracovani radku souboru ze vstupu
for line in sys.stdin:
    readLine = sanitizeLine(line)
    if len(readLine) == 0: continue
    checkInstructionArgsCount(readLine)

print('<?xml version="1.0" encoding="UTF-8"?>')
tree = ET.ElementTree(xmlRoot)
ET.dump(tree)