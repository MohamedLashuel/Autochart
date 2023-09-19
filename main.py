from printplus import *

from noteobj import *
from inout import *
from inpnote import *

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-i', '--input_file', help = 'File to use as input', 
    default = 'input.txt')
parser.add_argument('-o', '--output_file', help = 'File to use as output', default = 'output.txt')
parser.add_argument('-j', '--inject_file', help = 'File to inject to (must be ssc)', default = None)
parser.add_argument('-m', '--meter', help = 'Meter of the injected chart', default = None,
    type = int)
parser.add_argument('-p', '--pdb', help = 'Use pdb', action = 'store_true')

args = parser.parse_args()

if args.pdb: pdb.set_trace()

def convertToSSC(input_file, output_file):
    input_text = processTxt(input_file)

    phrases = processLines(input_text)

    measures = unpackPhrases(phrases)

    measure_text = measuresToText(measures)

    writeTxt(output_file, measure_text)

def injectSSCToChart(input_file, inject_file, meter):
    input_text = processTxt(input_file)

    destination_text = processTxt(inject_file)

    injected_list = injectChart(input_text, destination_text, meter)

    injected_text = listToText(injected_list)

    writeTxt(inject_file, injected_text)
    
if args.inject_file:
    injectSSCToChart(args.input_file, args.inject_file, args.meter)
else:
    convertToSSC(args.input_file, args.output_file)