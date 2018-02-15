import re
import os
import sys

try:
    file = sys.argv[1]
except IndexError:
    raise IndexError("you should provide a file path.")

#file = '/home/m357764/workspace/YOURPROJECT/src/chado-1.31/schemas/1.31/default_schema.sql'
with open(file) as myfile:
    data = myfile.read()

output = os.path.basename(file)

regex = re.compile(
    r"^(?:CREATE( OR REPLACE)?)\s(\S+)\s(?:[^;']|(?:'[^']+'))+;\s*$",
    re.MULTILINE)

for m in regex.finditer(data):
    #print(m.group(0))
    out = open(m.group(2) + '_' + output, 'a')
    out.write(m.group(0))
    out.write("\n")
    out.close()


