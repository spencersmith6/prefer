import json
import pandas
import numpy
import re
import ast
import argparse


def cleanFields(entry, fields_to_keep):
    # Remove apostrophes and double quotes from all fields
    clean_entry = {}
    for key in entry.keys():
        if key in fields_to_keep:
            try:
                clean_entry[key] = re.sub("['\"]", '', str(entry[key]))
            except TypeError:
                pass
    return clean_entry


def getFields(datapath, fieldname):
    with open(datapath+fieldname) as f:
        data = f.read()
    return data.split(',')


def getData(datapath, filename):
    with open(datapath+filename) as f:
        data = f.readlines()
    return data

def buildSQL(dict_data):
    return str(dict_data).replace("'", '"').replace('imUrl', 'imurl')

def writeOut(to_paste, datapath, outFile):
    with open(datapath + outFile, 'w') as f:
        f.write(to_paste)



def main(args):
    raw_data = getData(args.datapath, args.filename)
    fields_to_keep = getFields(args.datapath, args.fieldname)
    dict_data = [cleanFields(ast.literal_eval(i), fields_to_keep) for i in raw_data]
    to_paste = buildSQL(dict_data)
    writeOut(to_paste, args.datapath, args.outfile)
    print 'Finished'



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-filename", help="JSON File Name")
    parser.add_argument("-datapath", help="Path to Data Directory")
    parser.add_argument("-outfile", help="Filename to Write Out To")
    parser.add_argument('-fieldname', help="Filename containing comma seperated list of fields to keep")
    args = parser.parse_args()
    main(args)