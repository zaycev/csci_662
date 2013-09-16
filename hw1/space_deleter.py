import sys

vovel_symbols = "_"
all_symbols = "AEIOBCDFGHJKLMNPQRSTUVWXYZ"
sys.stdout.write("0\n")
for v in vovel_symbols:
    sys.stdout.write("(0 (0 \"%s\" *e*))\n" % v)
for s in all_symbols:
    sys.stdout.write("(0 (0 \"%s\" \"%s\"))\n" % (s, s))


