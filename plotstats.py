from datetime import time
import pandas as pd
import plotly.express as px
import csv
  
times = []
names = []

loopt =[]
loopn =[]

with open('ftimes.csv','r') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    for row in lines:
        times.append(row[0])
        names.append(row[1])

with open('ltimes.csv','r') as loopfile:
    lines = csv.reader(loopfile,delimiter=',')
    for row in lines:
        loopt.append(row[0])
        loopn.append(row[1])


df = pd.read_csv('stats.csv')

def makefig(stat,df):
    newfig = px.line(df, x = 'time', y = [stat], title='Time vs Usage%')
    for elem in range(1,len(names)):
        if elem % 2 == 0:
            continue
        else:
            newfig.add_vline(x=times[elem],line_width=3, line_dash="dash", line_color="green")
            newfig.add_annotation(x=times[elem],y=100-elem,text=names[elem])

    for elem in range(1,len(loopt)):
        newfig.add_vline(x=loopt[elem],line_width=2, line_dash="dash",line_color="orange")
        if elem < 3:
            newfig.add_annotation(x=loopt[elem],y=100-(elem+1),text=loopn[elem])
    return newfig

CPU0 = makefig('CPU',df)
CPU0.show()
CPU1 = makefig('CPU.1',df)
CPU1.show()
CPU2 = makefig('CPU.2',df)
CPU2.show()
CPU3 = makefig('CPU.3',df)
CPU3.show()
CPU4 = makefig('CPU.4',df)
CPU4.show()
CPU5 = makefig('CPU.5',df)
CPU5.show()
Mem = makefig('Memory%',df)
Mem.show()






