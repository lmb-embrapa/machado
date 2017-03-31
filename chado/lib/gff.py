from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Cv, Cvprop, Cvterm, CvtermDbxref, Cvtermprop, CvtermRelationship, Cvtermsynonym, Feature, Featureloc, FeatureDbxref, FeatureRelationship, FeatureSynonym, Featureprop, FeatureCvterm,  Organism
from chado.lib.dbxref import *
import re

def check_parent(gff3line):
# receive a line from tbx.fetch and return if has a Parent attribute
        parent = 0
        try:
            fields = gff3line.attributes.split(";")
            for field in fields:
                attribute = field.split("=")
                if(attribute[0] == "Parent"):
                    parent = 1
            return parent

        except ObjectDoesNotExist:

            return parent



def get_attribute(gff3line, name):
# receive a line from tbx.fetch and retreive one of the attribute fields (name)
        result = ""
        try:
            fields = gff3line.attributes.split(";")
            for field in fields:
                attribute = field.split("=")
                if(attribute[0] == name):
                    result = attribute[1]
            return result

        except ObjectDoesNotExist:

            return result



