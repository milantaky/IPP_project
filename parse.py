# python3.10 parse.py < file.txt

import sys
import argparse
import xml.etree.ElementTree as ET

# noArg = ('createframe', 'pushframe', 'popframe', 'return', 'break')
# oneArg = ('defvar', 'call', 'pushs', 'pops', 'write', 'label', 'jump', 'dprint')
# twoArgs = ()
# threeArgs = ()

orderNum = 1

def checkArgs():
    if len(sys.argv) > 2:
        if sys.argv[1] == '--help' or sys.argv[1] == '-h':
            sys.exit(10)

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
        else: 
            newList.append(item)
    return newList

def checkInstructionArgsCount(line):
    instruction = line[0].lower()
    numOfArgs = len(line)

    match numOfArgs:
        case 1:
            if instruction in ('createframe', 'pushframe', 'popframe', 'return', 'break'):                  # Bez argumentu
                print(instruction)
                writeInstructionToXML(instruction, None)
            else:
                print('Invalid instruction name or usage', file=sys.stderr)
                sys.exit(22)
        case 2:
            if instruction in ('defvar', 'call', 'pushs', 'pops', 'write', 'label', 'jump', 'dprint'):      # S 1 argumentem
                writeInstructionToXML(instruction, line[1:])
            else:
                print('Invalid instruction name or usage', file=sys.stderr)
                sys.exit(22)
        case 3:
            if instruction in ('move', 'int2char', 'strlen', 'type', 'read'):      # Se 2 argumenty
                writeInstructionToXML(instruction, line[1:])
            else:
                print('Invalid instruction name or usage', file=sys.stderr)
                sys.exit(22)
        case 4:
            if instruction in ('add', 'sub', 'mul', 'idiv', 'lt', 'gt', 'eq', 'and', 'or', 'not', 'stri2int', 'concat', 'getchar', 'setchar', 'jumpifeq', 'jumpifneq'):      # Se 3 argumenty
                writeInstructionToXML(instruction, line[1:])
            else:
                print('Invalid instruction name or usage', file=sys.stderr)
                sys.exit(22)
        case _:
            print('Too many arguments in instruction', file=sys.stderr)
            sys.exit(22)

def writeInstructionToXML(name, args):
    global orderNum
    global xmlRoot
    instruction = ET.Element('instruction', order=str(orderNum), opcode=name.upper())
    xmlRoot.append(instruction)
    orderNum += 1

    args = checkArguments(name, args)  # Pokud chyba v argumentech, dal to nedojde

    if args != None and len(args) > 0:
        for index, arg in enumerate(args):   
            print(index, arg)
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
            if name in ('defvar', 'pops'):                      # <var>
                check = [isVar(args[0])]
                if False in check:
                    print('Incorrect argument:', args , file=sys.stderr)  
                    sys.exit(22)
                else: 
                    print("OK")
            elif name in ('pushs', 'write', 'exit', 'dprint'):  # <symb>
                check = [isSymb(args[0])]
                if False in check:
                    print('Incorrect argument:', args , file=sys.stderr)  
                    sys.exit(22)
                else: 
                    print("OK")
            else:                                               # <label>                   'call', 'label', 'jump'  
                check = [isLabel(args[0])]
                if False in check:   
                    print('Incorrect argument:', args , file=sys.stderr)  
                    sys.exit(22)
                else: 
                    print("OK")
        case 2:
            if name in ('move', 'int2char', 'strlen', 'type'):  # <var><symb>
                check = [isVar(args[0]), isSymb(args[1])]
                if False in check:
                    print('Incorrect argument:', args , file=sys.stderr)  
                    sys.exit(22)
                else: 
                    print("OK")
            else:                                               # <var><type>               'read'
                check = [isVar(args[0]), isType(args[1])]
                if False in check:
                    print('Incorrect argument:', args , file=sys.stderr)  
                    sys.exit(22)
                else: 
                    print("OK")

        case 3:
            if name in ('jumpifeq', 'jumpifneq'):               # <label><symb1><symb2>
                check = [isLabel(args[0]), isSymb(args[1]), isSymb(args[2])]
                if False in check:
                    print('Incorrect argument:', args , file=sys.stderr)  
                    sys.exit(22)
                else: 
                    print("OK")
            else:                                               # <var><symb1><symb2>       'add', 'sub', 'mul', 'idiv', 'lt', 'gt', 'eq', 'and', 'or', 'not', 'stri2int', 'concat', 'getchar', 'setchar'
                check = [isVar(args[0]), isSymb(args[1]), isSymb(args[2])]
                if False in check:
                    print('Incorrect argument:', args , file=sys.stderr)  
                    sys.exit(22)
                else: 
                    print("OK")

        # 4 ani default neni potreb, to je osetreno ve funkci checkInstructionArgsCount
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
            return ['string', arg[1]]                                 #! ?????????????????????
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
        print('tu')
        return False
    return True

# Pro citelnost
def isLabel(arg):
    if isValidName(arg): return ['label', arg]

def isType(arg):
    if arg in ('int', 'string', 'bool'): return ['type', arg] 

def isValidName(name):
    # Je potreba udelat to pro prvni zvlast
    if name[0] not in ('_', '-', '$', '&', '%', '*', '!', '?') and not name[0].isalpha(): return False

    for letter in name:
        if letter not in ('_', '-', '$', '&', '%', '*', '!', '?') and not letter.isalnum(): return False
    return True

#TODO
def checkString():
    print("TODO")

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
    readLine = sanitizeLine(line)
    if len(readLine) == 0: continue
    print(readLine)
    checkInstructionArgsCount(readLine)
    # writeInstructionToXML(line) ???


tree = ET.ElementTree(xmlRoot)
# tree.write('test.xml')
ET.dump(tree)




print("POHODINDA!")