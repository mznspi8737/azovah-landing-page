# Versão narrada (Roberta) do "Conhece-te": cenas no tempo da fala
import sys, os, subprocess
sys.path.insert(0, '/home/claude/film'); import film as Fm
from PIL import Image
Fm.OUT = '/home/claude/film/out_narr'; os.makedirs(Fm.OUT, exist_ok=True)
B = [0, 8.0, 11.7, 16.2, 20.2, 23.0, 38.1, 44.0, 53.0]
Fm.ITEM_T = [x - 23.0 for x in (24.6, 27.2, 29.8, 32.4, 34.9)]
fns = [Fm.c1, Fm.c2, Fm.c3, Fm.c4, Fm.c5, Fm.c6, Fm.c7, Fm.c8]
Fm.SC = [(f'n{i+1}', fns[i], round(B[i + 1] - B[i], 4)) for i in range(8)]
if __name__ == '__main__':
    for i in map(int, sys.argv[1:]): Fm.render(i)
