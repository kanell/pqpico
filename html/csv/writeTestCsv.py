import csv

def writecsv():
    with open('data.csv','wb') as csvfile:
        datawriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        datawriter.writerow(['spam'] * 5)


import timeit


print(timeit.repeat('writecsv()','from __main__ import writecsv', number = 1000))
