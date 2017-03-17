#!/usr/bin/env python

import sys,re
from argparse import ArgumentParser

def main(argv):
    parser = ArgumentParser(prog='fixChadoModel.py',
                            description='fix Chado model created by: python manage.py inspectdb')
    parser.add_argument("--input", type=str, required=True, help="model in")
    args = parser.parse_args()

    fin = open(args.input,"r")
    model = open('models.py',"w")
    admin = open('admin.py',"w")

    modelClasses = list()

    # create models.py file
    for line in fin:
        if line.startswith('class'):
            m1 = re.match(r'class (\w+)\(.+',line)
            modelClass = m1.group(1)
            modelClasses.append(modelClass)
            #print(modelClass)
        elif 'models.DO_NOTHING' in line:
            m2 = re.match(r'\s+(\w+) = models.ForeignKey\(\'*(\w+)',line)
            modelField = m2.group(1)
            modelExtRef = m2.group(2)
            line = line.replace('models.DO_NOTHING',"related_name=\'%s_%s_%s\'" % (modelClass,modelField,modelExtRef))
            line = line.replace(', unique=True','')

        model.write(line)

    # create admin.py file

    admin.write("from django.contrib import admin\n\n")
    for modelClass in modelClasses:
        admin.write("from .models import %s\n" % modelClass)
    admin.write("\n")
    for modelClass in modelClasses:
        admin.write("admin.site.register(%s)\n" % modelClass)


    fin.close()
    model.close()
    admin.close()

if __name__ == "__main__":
    main(sys.argv)
