alp = "AEIOBCDFGHJKLMNPQRSTUVWXYZ"
kb = [
    "QWERTYUIOP[",
    "ASDFGHJKL;",
    "ZXCVBNM,."
]

def get_nn(c):
    for i in xrange(0, len(kb)):
        for j in xrange(0, len(kb[i])):
            if kb[i][j] == c:
                nn = []
                if j > 0:
                    nn.append(kb[i][j - 1])
                if j < len(kb[i]) - 1:
                    nn.append(kb[i][j + 1])
                if i != 2:
                    nn.append(kb[i + 1][j])
                    if j > 0:
                        nn.append(kb[i + 1][j - 1])
                if i != 0:
                    nn.append(kb[i - 1][j])
                    if j > 0:
                        nn.append(kb[i - 1][j])
                return list(set([n for n in nn if n in alp]))
            

import sys

sys.stdout.write("0\n")

for ch in alp:
    sys.stdout.write("(0 (1 \"%s\" \"%s\")\n" % (ch, ch))
sys.stdout.write("(0 (1 \"_\" \"_\")\n")

for ch in alp:
    sys.stdout.write("(1 (2 \"%s\" \"%s\")\n" % (ch, ch))
sys.stdout.write("(1 (2 \"_\" \"_\")\n")
sys.stdout.write("(1 (0 *e* *e*)\n")

for ch in alp:
    typos = get_nn(ch)
    prob = 1.0 / len(typos)
    for tp in typos:
        sys.stdout.write("(2 (0 \"%s\" \"%s\" %.4f)\n" % (ch, tp, prob))
sys.stdout.write("(2 (0 \"_\" \"V\")\n")