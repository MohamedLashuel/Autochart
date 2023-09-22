import random
import pdb
import copy

def match(*args, default = None):
    if len(args) == 0: return None

    for arg in args:
        if arg[0]: return arg[1]

    return default

def matchVal(var, *args, default = None):
    if len(args) == 0:
        return None

    for arg in args:
        if arg[0] == var: return arg[1]

    return default

def twoBoolEvaluate(bool_1, bool_2, outcomes):
    assert len(outcomes) == 4
    
    match (bool_1, bool_2):
        case (False, False):
            result = outcomes[0]
        case (True, False):
            result = outcomes[1]
        case (False, True):
            result = outcomes[2]
        case (True, True):
            result = outcomes[3]
    if result == 'DIE': assert False
    return result

def numberGrab(string, index):
    typecheck([string, str], [index, int])
    assert string[index].isdigit()
    
    number_length = 1
    
    while index + number_length < len(string) and string[index : index + number_length + 1].isdigit():
        number_length += 1

    result = int(string[index : index + number_length])

    return result

def blowup(reason):
    print(reason)
    assert False

def find_all(a_str, sub):
    # Code I stole from stack overflow to find all substring matches as a list
    start = 0
    results = []
    while True:
        start = a_str.find(sub, start)
        if start == -1: return results
        results.append(start)
        start += len(sub) # use start += 1 to find overlapping matches

def unset(st):
    if len(st) != 1: return None
    for item in st: return st
    
def weightedChoice(items, *item_weights):
    weights = [1 for item in items]

    for pair in item_weights: 
        try:
            weight_index = items.index(pair[0])
        except ValueError:
            pass
        else:
            weights[weight_index] = pair[1]

    choice = random.choices(items, weights = weights)[0]

    return choice

def dictAddKeyVal(dic, seq): dic[seq[0]] = seq[1]