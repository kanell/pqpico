import ConfigParser

cparser = ConfigParser.ConfigParser()
cparser.read('../parameters.ini')
iniSections = cparser.sections()

parameters = {}

for sec in iniSections:
    print('--[ '+sec+' ]--')
    for opt in cparser.options(sec):
            value = cparser.get(sec,opt)
        print('    '+opt+' : '+value)
        parameters[opt] = value

print(parameters)
