import ConfigParser

cparser = ConfigParser.ConfigParser()
cparser.read('../parameters.ini')
iniSections = cparser.sections()

parameters = {}

for section in iniSections:
    print('--[ '+section+' ]--')
    for opt in cparser.options(section):
        value = cparser.get(section,opt)
        print('    '+opt+' : '+value)
        parameters[opt] = value

print(parameters)
