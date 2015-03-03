import csv

def writecsv():
    with open('data.csv','wb') as csvfile:
        datawriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        datawriter.writerow(['spam'] * 5)

