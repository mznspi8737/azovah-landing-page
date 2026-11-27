import json, sys
W=json.load(open(sys.argv[1])); OFF=0.5; FPS=30
def at(word, after):
    for s,e,w in W:
        if s>=after-0.3 and w.strip().lower().startswith(word.lower()): return s
    raise Exception(word)
def endbefore(t): return max(e for s,e,w in W if s<t)
L={'s1':[('Oi',0),('E',3.4)],
   's2':[('Olha',6),('Olha',10.8),('Somando',19.4),('E',21.4)],
   's3':[('Agora',25.7),('Se',27.5),('A',31.4),('Um',35.3)],
   's4':[('Com',38.6),('Quando',42),('isso',46.4)],
   's6':[('Mas',49.6),('Com',51.7),('e',56.3)],
   's7':[('No',62),('ciclos',64.8)],
   's5':[('E',70.4),('Calcule',72.9)]}
H={'let':[('H',11.8),('E',13.1),('L',14.4),('E',15.7),('N',17.0),('A',18.4)],'sete':('7',30.5),'oito':('8',34.4),'hl':('como',44.6),
   'vira':('vira',54.8),'pelo':('pelo',59.1),'feat':[('mapa',63.3),('ciclos',64.8),('ano',65.5),('compat',66.4),('calend',68.0)]}
order=['s1','s2','s3','s4','s6','s7','s5']
starts={k:[at(w,t) for w,t in v] for k,v in L.items()}
allst=sorted(x for v in starts.values() for x in v); total_end=W[-1][1]
def lend(x):
    nx=[y for y in allst if y>x]; return endbefore(nx[0]) if nx else total_end
bounds=[0.0]
for a,b in zip(order,order[1:]): bounds.append((lend(starts[a][-1])+starts[b][0])/2+OFF)
bounds.append(total_end+OFF+0.7); bounds=[round(b*FPS)/FPS for b in bounds]
M={}
for i,k in enumerate(order):
    b0=bounds[i]; M[k]=dict(cues=[[x+OFF-b0, lend(x)+OFF-b0] for x in starts[k]], dur=round(bounds[i+1]-b0,4), t0=b0)
def rel(k,wt): return at(*wt)+OFF-M[k]['t0']
M['s2']['let']=[rel('s2',x) for x in H['let']]
M['s3']['sete']=rel('s3',H['sete']); M['s3']['oito']=rel('s3',H['oito'])
M['s4']['hl']=rel('s4',H['hl']); M['s6']['vira']=rel('s6',H['vira']); M['s6']['pelo']=rel('s6',H['pelo'])
M['s7']['feat']=[rel('s7',x) for x in H['feat']]
M['s8']=dict(cues=[],dur=6.0,t0=bounds[-1])
json.dump(M,open('/home/claude/reels/v2/meta.json','w'))
for k in order: print(k,M[k]['dur'],[[round(a,1),round(b,1)] for a,b in M[k]['cues']])
print([round(x,1) for x in M['s2']['let']],[round(x,1) for x in M['s7']['feat']],round(M['s3']['sete'],1),round(M['s6']['vira'],1))
