from autochart.noteobj import *
from autochart.inpnote import *

def processTxt(filename: str) -> list[str]:
    with open(filename, 'r') as file:
        # Strip to chop off the \n at the end
        return [line.strip() for line in file] 

def injectChart(chart, dest_text, meter):
    # Get the section for the meter we're working on
    meter_line = dest_text.index(f"#METER:{meter};")

    chart_start = dest_text.index('#NOTES:', meter_line)
    chart_end = dest_text.index(';', chart_start)

    dest_text = dest_text[:(chart_start + 1)] + chart + dest_text[chart_end:]

    return dest_text

def writeTxt(filename, text):
    with open(filename, 'w') as file:
		file.write(text)

def measureToText(measure):
    beat_text = [beat.toText() for beat in measure]

    return '\n'.join(beat_text) + '\n' 

def measuresToText(measures):
    measure_text = [measureToText(measure) for measure in measures]

    result = ',\n'.join(measure_text)

    return result[0:-1] # Cut off last newline

def listToText(lst):
    result = ''

    for item in lst: result += (item + '\n')

    return result

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
