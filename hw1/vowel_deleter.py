import sys

vowel_symbols = "AEIOU"
other_symbols = "BCDFGHJKLMNPQRSTVWXYZ_"
sys.stdout.write("0\n")
for v in vowel_symbols:
    sys.stdout.write("(0 (0 \"%s\" *e*))\n" % s)
for s in other_symbols:
    sys.stdout.write("(0 (0 \"%s\" \"%s\"))\n" % (s, s))


