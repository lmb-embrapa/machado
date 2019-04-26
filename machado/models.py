# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.
from django.db import models

from machado.decorators import machadoFeatureMethods, machadoPubMethods


class Acquisition(models.Model):
    acquisition_id = models.BigAutoField(primary_key=True)
    assay = models.ForeignKey(
        "Assay", on_delete=models.DO_NOTHING, related_name="Acquisition_assay_Assay"
    )
    protocol = models.ForeignKey(
        "Protocol",
        on_delete=models.DO_NOTHING,
        related_name="Acquisition_protocol_Protocol",
        blank=True,
        null=True,
    )
    channel = models.ForeignKey(
        "Channel",
        on_delete=models.DO_NOTHING,
        related_name="Acquisition_channel_Channel",
        blank=True,
        null=True,
    )
    acquisitiondate = models.DateTimeField(blank=True, null=True)
    name = models.TextField(unique=True, blank=True, null=True)
    uri = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "acquisition"


class AcquisitionRelationship(models.Model):
    acquisition_relationship_id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(
        Acquisition,
        on_delete=models.DO_NOTHING,
        related_name="AcquisitionRelationship_subject_Acquisition",
    )
    type = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="AcquisitionRelationship_type_Cvterm",
    )
    object = models.ForeignKey(
        Acquisition,
        on_delete=models.DO_NOTHING,
        related_name="AcquisitionRelationship_object_Acquisition",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "acquisition_relationship"
        unique_together = (("subject", "object", "type", "rank"),)


class Acquisitionprop(models.Model):
    acquisitionprop_id = models.BigAutoField(primary_key=True)
    acquisition = models.ForeignKey(
        Acquisition,
        on_delete=models.DO_NOTHING,
        related_name="Acquisitionprop_acquisition_Acquisition",
    )
    type = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="Acquisitionprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "acquisitionprop"
        unique_together = (("acquisition", "type", "rank"),)


class Analysis(models.Model):
    analysis_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    program = models.CharField(max_length=255)
    programversion = models.CharField(max_length=255)
    algorithm = models.CharField(max_length=255, blank=True, null=True)
    sourcename = models.CharField(max_length=255, blank=True, null=True)
    sourceversion = models.CharField(max_length=255, blank=True, null=True)
    sourceuri = models.TextField(blank=True, null=True)
    timeexecuted = models.DateTimeField()

    class Meta:
        db_table = "analysis"
        unique_together = (("program", "programversion", "sourcename"),)


class AnalysisCvterm(models.Model):
    analysis_cvterm_id = models.BigAutoField(primary_key=True)
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.DO_NOTHING,
        related_name="AnalysisCvterm_analysis_Analysis",
    )
    cvterm = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="AnalysisCvterm_cvterm_Cvterm",
    )
    is_not = models.BooleanField()
    rank = models.IntegerField()

    class Meta:
        db_table = "analysis_cvterm"
        unique_together = (("analysis", "cvterm", "rank"),)


class AnalysisDbxref(models.Model):
    analysis_dbxref_id = models.BigAutoField(primary_key=True)
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.DO_NOTHING,
        related_name="AnalysisDbxref_analysis_Analysis",
    )
    dbxref = models.ForeignKey(
        "Dbxref",
        on_delete=models.DO_NOTHING,
        related_name="AnalysisDbxref_dbxref_Dbxref",
    )
    is_current = models.BooleanField()

    class Meta:
        db_table = "analysis_dbxref"
        unique_together = (("analysis", "dbxref"),)


class AnalysisPub(models.Model):
    analysis_pub_id = models.BigAutoField(primary_key=True)
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.DO_NOTHING,
        related_name="AnalysisPub_analysis_Analysis",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="AnalysisPub_pub_Pub"
    )

    class Meta:
        db_table = "analysis_pub"
        unique_together = (("analysis", "pub"),)


class AnalysisRelationship(models.Model):
    analysis_relationship_id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(
        Analysis,
        on_delete=models.DO_NOTHING,
        related_name="AnalysisRelationship_subject_Analysis",
    )
    object = models.ForeignKey(
        Analysis,
        on_delete=models.DO_NOTHING,
        related_name="AnalysisRelationship_object_Analysis",
    )
    type = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="AnalysisRelationship_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "analysis_relationship"
        unique_together = (("subject", "object", "type", "rank"),)


class Analysisfeature(models.Model):
    analysisfeature_id = models.BigAutoField(primary_key=True)
    feature = models.ForeignKey(
        "Feature",
        on_delete=models.DO_NOTHING,
        related_name="Analysisfeature_feature_Feature",
    )
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.DO_NOTHING,
        related_name="Analysisfeature_analysis_Analysis",
    )
    rawscore = models.FloatField(blank=True, null=True)
    normscore = models.FloatField(blank=True, null=True)
    significance = models.FloatField(blank=True, null=True)
    identity = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "analysisfeature"
        unique_together = (("feature", "analysis"),)


class Analysisfeatureprop(models.Model):
    analysisfeatureprop_id = models.BigAutoField(primary_key=True)
    analysisfeature = models.ForeignKey(
        Analysisfeature,
        on_delete=models.DO_NOTHING,
        related_name="Analysisfeatureprop_analysisfeature_Analysisfeature",
    )
    type = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="Analysisfeatureprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "analysisfeatureprop"
        unique_together = (("analysisfeature", "type", "rank"),)


class Analysisprop(models.Model):
    analysisprop_id = models.BigAutoField(primary_key=True)
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.DO_NOTHING,
        related_name="Analysisprop_analysis_Analysis",
    )
    type = models.ForeignKey(
        "Cvterm", on_delete=models.DO_NOTHING, related_name="Analysisprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "analysisprop"
        unique_together = (("analysis", "type", "rank"),)


class Arraydesign(models.Model):
    arraydesign_id = models.BigAutoField(primary_key=True)
    manufacturer = models.ForeignKey(
        "Contact",
        on_delete=models.DO_NOTHING,
        related_name="Arraydesign_manufacturer_Contact",
    )
    platformtype = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="Arraydesign_platformtype_Cvterm",
    )
    substratetype = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="Arraydesign_substratetype_Cvterm",
        blank=True,
        null=True,
    )
    protocol = models.ForeignKey(
        "Protocol",
        on_delete=models.DO_NOTHING,
        related_name="Arraydesign_protocol_Protocol",
        blank=True,
        null=True,
    )
    dbxref = models.ForeignKey(
        "Dbxref",
        on_delete=models.DO_NOTHING,
        related_name="Arraydesign_dbxref_Dbxref",
        blank=True,
        null=True,
    )
    name = models.TextField(unique=True)
    version = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    array_dimensions = models.TextField(blank=True, null=True)
    element_dimensions = models.TextField(blank=True, null=True)
    num_of_elements = models.IntegerField(blank=True, null=True)
    num_array_columns = models.IntegerField(blank=True, null=True)
    num_array_rows = models.IntegerField(blank=True, null=True)
    num_grid_columns = models.IntegerField(blank=True, null=True)
    num_grid_rows = models.IntegerField(blank=True, null=True)
    num_sub_columns = models.IntegerField(blank=True, null=True)
    num_sub_rows = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "arraydesign"


class Arraydesignprop(models.Model):
    arraydesignprop_id = models.BigAutoField(primary_key=True)
    arraydesign = models.ForeignKey(
        Arraydesign,
        on_delete=models.DO_NOTHING,
        related_name="Arraydesignprop_arraydesign_Arraydesign",
    )
    type = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="Arraydesignprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "arraydesignprop"
        unique_together = (("arraydesign", "type", "rank"),)


class Assay(models.Model):
    assay_id = models.BigAutoField(primary_key=True)
    arraydesign = models.ForeignKey(
        Arraydesign,
        on_delete=models.DO_NOTHING,
        related_name="Assay_arraydesign_Arraydesign",
    )
    protocol = models.ForeignKey(
        "Protocol",
        on_delete=models.DO_NOTHING,
        related_name="Assay_protocol_Protocol",
        blank=True,
        null=True,
    )
    assaydate = models.DateTimeField(blank=True, null=True)
    arrayidentifier = models.TextField(blank=True, null=True)
    arraybatchidentifier = models.TextField(blank=True, null=True)
    operator = models.ForeignKey(
        "Contact", on_delete=models.DO_NOTHING, related_name="Assay_operator_Contact"
    )
    dbxref = models.ForeignKey(
        "Dbxref",
        on_delete=models.DO_NOTHING,
        related_name="Assay_dbxref_Dbxref",
        blank=True,
        null=True,
    )
    name = models.TextField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "assay"


class AssayBiomaterial(models.Model):
    assay_biomaterial_id = models.BigAutoField(primary_key=True)
    assay = models.ForeignKey(
        Assay, on_delete=models.DO_NOTHING, related_name="AssayBiomaterial_assay_Assay"
    )
    biomaterial = models.ForeignKey(
        "Biomaterial",
        on_delete=models.DO_NOTHING,
        related_name="AssayBiomaterial_biomaterial_Biomaterial",
    )
    channel = models.ForeignKey(
        "Channel",
        on_delete=models.DO_NOTHING,
        related_name="AssayBiomaterial_channel_Channel",
        blank=True,
        null=True,
    )
    rank = models.IntegerField()

    class Meta:
        db_table = "assay_biomaterial"
        unique_together = (("assay", "biomaterial", "channel", "rank"),)


class AssayProject(models.Model):
    assay_project_id = models.BigAutoField(primary_key=True)
    assay = models.ForeignKey(
        Assay, on_delete=models.DO_NOTHING, related_name="AssayProject_assay_Assay"
    )
    project = models.ForeignKey(
        "Project",
        on_delete=models.DO_NOTHING,
        related_name="AssayProject_project_Project",
    )

    class Meta:
        db_table = "assay_project"
        unique_together = (("assay", "project"),)


class Assayprop(models.Model):
    assayprop_id = models.BigAutoField(primary_key=True)
    assay = models.ForeignKey(
        Assay, on_delete=models.DO_NOTHING, related_name="Assayprop_assay_Assay"
    )
    type = models.ForeignKey(
        "Cvterm", on_delete=models.DO_NOTHING, related_name="Assayprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "assayprop"
        unique_together = (("assay", "type", "rank"),)


class Biomaterial(models.Model):
    biomaterial_id = models.BigAutoField(primary_key=True)
    taxon = models.ForeignKey(
        "Organism",
        on_delete=models.DO_NOTHING,
        related_name="Biomaterial_taxon_Organism",
        blank=True,
        null=True,
    )
    biosourceprovider = models.ForeignKey(
        "Contact",
        on_delete=models.DO_NOTHING,
        related_name="Biomaterial_biosourceprovider_Contact",
        blank=True,
        null=True,
    )
    dbxref = models.ForeignKey(
        "Dbxref",
        on_delete=models.DO_NOTHING,
        related_name="Biomaterial_dbxref_Dbxref",
        blank=True,
        null=True,
    )
    name = models.TextField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "biomaterial"


class BiomaterialDbxref(models.Model):
    biomaterial_dbxref_id = models.BigAutoField(primary_key=True)
    biomaterial = models.ForeignKey(
        Biomaterial,
        on_delete=models.DO_NOTHING,
        related_name="BiomaterialDbxref_biomaterial_Biomaterial",
    )
    dbxref = models.ForeignKey(
        "Dbxref",
        on_delete=models.DO_NOTHING,
        related_name="BiomaterialDbxref_dbxref_Dbxref",
    )

    class Meta:
        db_table = "biomaterial_dbxref"
        unique_together = (("biomaterial", "dbxref"),)


class BiomaterialRelationship(models.Model):
    biomaterial_relationship_id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(
        Biomaterial,
        on_delete=models.DO_NOTHING,
        related_name="BiomaterialRelationship_subject_Biomaterial",
    )
    type = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="BiomaterialRelationship_type_Cvterm",
    )
    object = models.ForeignKey(
        Biomaterial,
        on_delete=models.DO_NOTHING,
        related_name="BiomaterialRelationship_object_Biomaterial",
    )

    class Meta:
        db_table = "biomaterial_relationship"
        unique_together = (("subject", "object", "type"),)


class BiomaterialTreatment(models.Model):
    biomaterial_treatment_id = models.BigAutoField(primary_key=True)
    biomaterial = models.ForeignKey(
        Biomaterial,
        on_delete=models.DO_NOTHING,
        related_name="BiomaterialTreatment_biomaterial_Biomaterial",
    )
    treatment = models.ForeignKey(
        "Treatment",
        on_delete=models.DO_NOTHING,
        related_name="BiomaterialTreatment_treatment_Treatment",
    )
    unittype = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="BiomaterialTreatment_unittype_Cvterm",
        blank=True,
        null=True,
    )
    value = models.FloatField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "biomaterial_treatment"
        unique_together = (("biomaterial", "treatment"),)


class Biomaterialprop(models.Model):
    biomaterialprop_id = models.BigAutoField(primary_key=True)
    biomaterial = models.ForeignKey(
        Biomaterial,
        on_delete=models.DO_NOTHING,
        related_name="Biomaterialprop_biomaterial_Biomaterial",
    )
    type = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="Biomaterialprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "biomaterialprop"
        unique_together = (("biomaterial", "type", "rank"),)


class CellLine(models.Model):
    cell_line_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    uniquename = models.CharField(max_length=255)
    organism = models.ForeignKey(
        "Organism",
        on_delete=models.DO_NOTHING,
        related_name="CellLine_organism_Organism",
    )
    timeaccessioned = models.DateTimeField()
    timelastmodified = models.DateTimeField()

    class Meta:
        db_table = "cell_line"
        unique_together = (("uniquename", "organism"),)


class CellLineCvterm(models.Model):
    cell_line_cvterm_id = models.BigAutoField(primary_key=True)
    cell_line = models.ForeignKey(
        CellLine,
        on_delete=models.DO_NOTHING,
        related_name="CellLineCvterm_cell_line_CellLine",
    )
    cvterm = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="CellLineCvterm_cvterm_Cvterm",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="CellLineCvterm_pub_Pub"
    )
    rank = models.IntegerField()

    class Meta:
        db_table = "cell_line_cvterm"
        unique_together = (("cell_line", "cvterm", "pub", "rank"),)


class CellLineCvtermprop(models.Model):
    cell_line_cvtermprop_id = models.BigAutoField(primary_key=True)
    cell_line_cvterm = models.ForeignKey(
        CellLineCvterm,
        on_delete=models.DO_NOTHING,
        related_name="CellLineCvtermprop_cell_line_cvterm_CellLineCvterm",
    )
    type = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="CellLineCvtermprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "cell_line_cvtermprop"
        unique_together = (("cell_line_cvterm", "type", "rank"),)


class CellLineDbxref(models.Model):
    cell_line_dbxref_id = models.BigAutoField(primary_key=True)
    cell_line = models.ForeignKey(
        CellLine,
        on_delete=models.DO_NOTHING,
        related_name="CellLineDbxref_cell_line_CellLine",
    )
    dbxref = models.ForeignKey(
        "Dbxref",
        on_delete=models.DO_NOTHING,
        related_name="CellLineDbxref_dbxref_Dbxref",
    )
    is_current = models.BooleanField()

    class Meta:
        db_table = "cell_line_dbxref"
        unique_together = (("cell_line", "dbxref"),)


class CellLineFeature(models.Model):
    cell_line_feature_id = models.BigAutoField(primary_key=True)
    cell_line = models.ForeignKey(
        CellLine,
        on_delete=models.DO_NOTHING,
        related_name="CellLineFeature_cell_line_CellLine",
    )
    feature = models.ForeignKey(
        "Feature",
        on_delete=models.DO_NOTHING,
        related_name="CellLineFeature_feature_Feature",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="CellLineFeature_pub_Pub"
    )

    class Meta:
        db_table = "cell_line_feature"
        unique_together = (("cell_line", "feature", "pub"),)


class CellLineLibrary(models.Model):
    cell_line_library_id = models.BigAutoField(primary_key=True)
    cell_line = models.ForeignKey(
        CellLine,
        on_delete=models.DO_NOTHING,
        related_name="CellLineLibrary_cell_line_CellLine",
    )
    library = models.ForeignKey(
        "Library",
        on_delete=models.DO_NOTHING,
        related_name="CellLineLibrary_library_Library",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="CellLineLibrary_pub_Pub"
    )

    class Meta:
        db_table = "cell_line_library"
        unique_together = (("cell_line", "library", "pub"),)


class CellLinePub(models.Model):
    cell_line_pub_id = models.BigAutoField(primary_key=True)
    cell_line = models.ForeignKey(
        CellLine,
        on_delete=models.DO_NOTHING,
        related_name="CellLinePub_cell_line_CellLine",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="CellLinePub_pub_Pub"
    )

    class Meta:
        db_table = "cell_line_pub"
        unique_together = (("cell_line", "pub"),)


class CellLineRelationship(models.Model):
    cell_line_relationship_id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(
        CellLine,
        on_delete=models.DO_NOTHING,
        related_name="CellLineRelationship_subject_CellLine",
    )
    object = models.ForeignKey(
        CellLine,
        on_delete=models.DO_NOTHING,
        related_name="CellLineRelationship_object_CellLine",
    )
    type = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="CellLineRelationship_type_Cvterm",
    )

    class Meta:
        db_table = "cell_line_relationship"
        unique_together = (("subject", "object", "type"),)


class CellLineSynonym(models.Model):
    cell_line_synonym_id = models.BigAutoField(primary_key=True)
    cell_line = models.ForeignKey(
        CellLine,
        on_delete=models.DO_NOTHING,
        related_name="CellLineSynonym_cell_line_CellLine",
    )
    synonym = models.ForeignKey(
        "Synonym",
        on_delete=models.DO_NOTHING,
        related_name="CellLineSynonym_synonym_Synonym",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="CellLineSynonym_pub_Pub"
    )
    is_current = models.BooleanField()
    is_internal = models.BooleanField()

    class Meta:
        db_table = "cell_line_synonym"
        unique_together = (("synonym", "cell_line", "pub"),)


class CellLineprop(models.Model):
    cell_lineprop_id = models.BigAutoField(primary_key=True)
    cell_line = models.ForeignKey(
        CellLine,
        on_delete=models.DO_NOTHING,
        related_name="CellLineprop_cell_line_CellLine",
    )
    type = models.ForeignKey(
        "Cvterm", on_delete=models.DO_NOTHING, related_name="CellLineprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "cell_lineprop"
        unique_together = (("cell_line", "type", "rank"),)


class CellLinepropPub(models.Model):
    cell_lineprop_pub_id = models.BigAutoField(primary_key=True)
    cell_lineprop = models.ForeignKey(
        CellLineprop,
        on_delete=models.DO_NOTHING,
        related_name="CellLinepropPub_cell_lineprop_CellLineprop",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="CellLinepropPub_pub_Pub"
    )

    class Meta:
        db_table = "cell_lineprop_pub"
        unique_together = (("cell_lineprop", "pub"),)


class Chadoprop(models.Model):
    chadoprop_id = models.BigAutoField(primary_key=True)
    type = models.ForeignKey(
        "Cvterm", on_delete=models.DO_NOTHING, related_name="Chadoprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "chadoprop"
        unique_together = (("type", "rank"),)


class Channel(models.Model):
    channel_id = models.BigAutoField(primary_key=True)
    name = models.TextField(unique=True)
    definition = models.TextField()

    class Meta:
        db_table = "channel"


class Contact(models.Model):
    contact_id = models.BigAutoField(primary_key=True)
    type = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="Contact_type_Cvterm",
        blank=True,
        null=True,
    )
    name = models.CharField(unique=True, max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "contact"


class ContactRelationship(models.Model):
    contact_relationship_id = models.BigAutoField(primary_key=True)
    type = models.ForeignKey(
        "Cvterm",
        on_delete=models.DO_NOTHING,
        related_name="ContactRelationship_type_Cvterm",
    )
    subject = models.ForeignKey(
        Contact,
        on_delete=models.DO_NOTHING,
        related_name="ContactRelationship_subject_Contact",
    )
    object = models.ForeignKey(
        Contact,
        on_delete=models.DO_NOTHING,
        related_name="ContactRelationship_object_Contact",
    )

    class Meta:
        db_table = "contact_relationship"
        unique_together = (("subject", "object", "type"),)


class Contactprop(models.Model):
    contactprop_id = models.BigAutoField(primary_key=True)
    contact = models.ForeignKey(
        Contact, on_delete=models.DO_NOTHING, related_name="Contactprop_contact_Contact"
    )
    type = models.ForeignKey(
        "Cvterm", on_delete=models.DO_NOTHING, related_name="Contactprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "contactprop"
        unique_together = (("contact", "type", "rank"),)


class Control(models.Model):
    control_id = models.BigAutoField(primary_key=True)
    type = models.ForeignKey(
        "Cvterm", on_delete=models.DO_NOTHING, related_name="Control_type_Cvterm"
    )
    assay = models.ForeignKey(
        Assay, on_delete=models.DO_NOTHING, related_name="Control_assay_Assay"
    )
    tableinfo = models.ForeignKey(
        "Tableinfo",
        on_delete=models.DO_NOTHING,
        related_name="Control_tableinfo_Tableinfo",
    )
    row_id = models.IntegerField()
    name = models.TextField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "control"


class Cv(models.Model):
    cv_id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    definition = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "cv"


class Cvprop(models.Model):
    cvprop_id = models.BigAutoField(primary_key=True)
    cv = models.ForeignKey(Cv, on_delete=models.DO_NOTHING, related_name="Cvprop_cv_Cv")
    type = models.ForeignKey(
        "Cvterm", on_delete=models.DO_NOTHING, related_name="Cvprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "cvprop"
        unique_together = (("cv", "type", "rank"),)


class Cvterm(models.Model):
    cvterm_id = models.BigAutoField(primary_key=True)
    cv = models.ForeignKey(Cv, on_delete=models.DO_NOTHING, related_name="Cvterm_cv_Cv")
    name = models.CharField(max_length=1024)
    definition = models.TextField(blank=True, null=True)
    dbxref = models.ForeignKey(
        "Dbxref", on_delete=models.DO_NOTHING, related_name="Cvterm_dbxref_Dbxref"
    )
    is_obsolete = models.IntegerField()
    is_relationshiptype = models.IntegerField()

    class Meta:
        db_table = "cvterm"
        unique_together = (("name", "cv", "is_obsolete"),)


class CvtermDbxref(models.Model):
    cvterm_dbxref_id = models.BigAutoField(primary_key=True)
    cvterm = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="CvtermDbxref_cvterm_Cvterm"
    )
    dbxref = models.ForeignKey(
        "Dbxref", on_delete=models.DO_NOTHING, related_name="CvtermDbxref_dbxref_Dbxref"
    )
    is_for_definition = models.IntegerField()

    class Meta:
        db_table = "cvterm_dbxref"
        unique_together = (("cvterm", "dbxref"),)


class CvtermRelationship(models.Model):
    cvterm_relationship_id = models.BigAutoField(primary_key=True)
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="CvtermRelationship_type_Cvterm",
    )
    subject = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="CvtermRelationship_subject_Cvterm",
    )
    object = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="CvtermRelationship_object_Cvterm",
    )

    class Meta:
        db_table = "cvterm_relationship"
        unique_together = (("subject", "object", "type"),)


class Cvtermpath(models.Model):
    cvtermpath_id = models.BigAutoField(primary_key=True)
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Cvtermpath_type_Cvterm",
        blank=True,
        null=True,
    )
    subject = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Cvtermpath_subject_Cvterm"
    )
    object = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Cvtermpath_object_Cvterm"
    )
    cv = models.ForeignKey(
        Cv, on_delete=models.DO_NOTHING, related_name="Cvtermpath_cv_Cv"
    )
    pathdistance = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "cvtermpath"
        unique_together = (("subject", "object", "type", "pathdistance"),)


class Cvtermprop(models.Model):
    cvtermprop_id = models.BigAutoField(primary_key=True)
    cvterm = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Cvtermprop_cvterm_Cvterm"
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Cvtermprop_type_Cvterm"
    )
    value = models.TextField()
    rank = models.IntegerField()

    class Meta:
        db_table = "cvtermprop"
        unique_together = (("cvterm", "type", "value", "rank"),)


class Cvtermsynonym(models.Model):
    cvtermsynonym_id = models.BigAutoField(primary_key=True)
    cvterm = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Cvtermsynonym_cvterm_Cvterm"
    )
    synonym = models.CharField(max_length=1024)
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Cvtermsynonym_type_Cvterm",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "cvtermsynonym"
        unique_together = (("cvterm", "synonym"),)


class Db(models.Model):
    db_id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    urlprefix = models.CharField(max_length=255, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "db"


class Dbprop(models.Model):
    dbprop_id = models.BigAutoField(primary_key=True)
    db = models.ForeignKey(Db, on_delete=models.DO_NOTHING, related_name="Dbprop_db_Db")
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Dbprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "dbprop"
        unique_together = (("db", "type", "rank"),)


class Dbxref(models.Model):
    dbxref_id = models.BigAutoField(primary_key=True)
    db = models.ForeignKey(Db, on_delete=models.DO_NOTHING, related_name="Dbxref_db_Db")
    accession = models.CharField(max_length=1024)
    version = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "dbxref"
        unique_together = (("db", "accession", "version"),)


class Dbxrefprop(models.Model):
    dbxrefprop_id = models.BigAutoField(primary_key=True)
    dbxref = models.ForeignKey(
        Dbxref, on_delete=models.DO_NOTHING, related_name="Dbxrefprop_dbxref_Dbxref"
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Dbxrefprop_type_Cvterm"
    )
    value = models.TextField()
    rank = models.IntegerField()

    class Meta:
        db_table = "dbxrefprop"
        unique_together = (("dbxref", "type", "rank"),)


class Eimage(models.Model):
    eimage_id = models.BigAutoField(primary_key=True)
    eimage_data = models.TextField(blank=True, null=True)
    eimage_type = models.CharField(max_length=255)
    image_uri = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "eimage"


class Element(models.Model):
    element_id = models.BigAutoField(primary_key=True)
    feature = models.ForeignKey(
        "Feature",
        on_delete=models.DO_NOTHING,
        related_name="Element_feature_Feature",
        blank=True,
        null=True,
    )
    arraydesign = models.ForeignKey(
        Arraydesign,
        on_delete=models.DO_NOTHING,
        related_name="Element_arraydesign_Arraydesign",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Element_type_Cvterm",
        blank=True,
        null=True,
    )
    dbxref = models.ForeignKey(
        Dbxref,
        on_delete=models.DO_NOTHING,
        related_name="Element_dbxref_Dbxref",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "element"
        unique_together = (("feature", "arraydesign"),)


class ElementRelationship(models.Model):
    element_relationship_id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(
        Element,
        on_delete=models.DO_NOTHING,
        related_name="ElementRelationship_subject_Element",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="ElementRelationship_type_Cvterm",
    )
    object = models.ForeignKey(
        Element,
        on_delete=models.DO_NOTHING,
        related_name="ElementRelationship_object_Element",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "element_relationship"
        unique_together = (("subject", "object", "type", "rank"),)


class Elementresult(models.Model):
    elementresult_id = models.BigAutoField(primary_key=True)
    element = models.ForeignKey(
        Element,
        on_delete=models.DO_NOTHING,
        related_name="Elementresult_element_Element",
    )
    quantification = models.ForeignKey(
        "Quantification",
        on_delete=models.DO_NOTHING,
        related_name="Elementresult_quantification_Quantification",
    )
    signal = models.FloatField()

    class Meta:
        db_table = "elementresult"
        unique_together = (("element", "quantification"),)


class ElementresultRelationship(models.Model):
    elementresult_relationship_id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(
        Elementresult,
        on_delete=models.DO_NOTHING,
        related_name="ElementresultRelationship_subject_Elementresult",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="ElementresultRelationship_type_Cvterm",
    )
    object = models.ForeignKey(
        Elementresult,
        on_delete=models.DO_NOTHING,
        related_name="ElementresultRelationship_object_Elementresult",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "elementresult_relationship"
        unique_together = (("subject", "object", "type", "rank"),)


class Environment(models.Model):
    environment_id = models.BigAutoField(primary_key=True)
    uniquename = models.TextField(unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "environment"


class EnvironmentCvterm(models.Model):
    environment_cvterm_id = models.BigAutoField(primary_key=True)
    environment = models.ForeignKey(
        Environment,
        on_delete=models.DO_NOTHING,
        related_name="EnvironmentCvterm_environment_Environment",
    )
    cvterm = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="EnvironmentCvterm_cvterm_Cvterm",
    )

    class Meta:
        db_table = "environment_cvterm"
        unique_together = (("environment", "cvterm"),)


class Expression(models.Model):
    expression_id = models.BigAutoField(primary_key=True)
    uniquename = models.TextField(unique=True)
    md5checksum = models.CharField(max_length=32, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "expression"


class ExpressionCvterm(models.Model):
    expression_cvterm_id = models.BigAutoField(primary_key=True)
    expression = models.ForeignKey(
        Expression,
        on_delete=models.DO_NOTHING,
        related_name="ExpressionCvterm_expression_Expression",
    )
    cvterm = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="ExpressionCvterm_cvterm_Cvterm",
    )
    rank = models.IntegerField()
    cvterm_type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="ExpressionCvterm_cvterm_type_Cvterm",
    )

    class Meta:
        db_table = "expression_cvterm"
        unique_together = (("expression", "cvterm", "rank", "cvterm_type"),)


class ExpressionCvtermprop(models.Model):
    expression_cvtermprop_id = models.BigAutoField(primary_key=True)
    expression_cvterm = models.ForeignKey(
        ExpressionCvterm,
        on_delete=models.DO_NOTHING,
        related_name="ExpressionCvtermprop_expression_cvterm_ExpressionCvterm",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="ExpressionCvtermprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "expression_cvtermprop"
        unique_together = (("expression_cvterm", "type", "rank"),)


class ExpressionImage(models.Model):
    expression_image_id = models.BigAutoField(primary_key=True)
    expression = models.ForeignKey(
        Expression,
        on_delete=models.DO_NOTHING,
        related_name="ExpressionImage_expression_Expression",
    )
    eimage = models.ForeignKey(
        Eimage,
        on_delete=models.DO_NOTHING,
        related_name="ExpressionImage_eimage_Eimage",
    )

    class Meta:
        db_table = "expression_image"
        unique_together = (("expression", "eimage"),)


class ExpressionPub(models.Model):
    expression_pub_id = models.BigAutoField(primary_key=True)
    expression = models.ForeignKey(
        Expression,
        on_delete=models.DO_NOTHING,
        related_name="ExpressionPub_expression_Expression",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="ExpressionPub_pub_Pub"
    )

    class Meta:
        db_table = "expression_pub"
        unique_together = (("expression", "pub"),)


class Expressionprop(models.Model):
    expressionprop_id = models.BigAutoField(primary_key=True)
    expression = models.ForeignKey(
        Expression,
        on_delete=models.DO_NOTHING,
        related_name="Expressionprop_expression_Expression",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Expressionprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "expressionprop"
        unique_together = (("expression", "type", "rank"),)


@machadoFeatureMethods()
class Feature(models.Model):
    feature_id = models.BigAutoField(primary_key=True)
    dbxref = models.ForeignKey(
        Dbxref,
        on_delete=models.DO_NOTHING,
        related_name="Feature_dbxref_Dbxref",
        blank=True,
        null=True,
    )
    organism = models.ForeignKey(
        "Organism",
        on_delete=models.DO_NOTHING,
        related_name="Feature_organism_Organism",
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    uniquename = models.TextField()
    residues = models.TextField(blank=True, null=True)
    seqlen = models.BigIntegerField(blank=True, null=True)
    md5checksum = models.CharField(max_length=32, blank=True, null=True)
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Feature_type_Cvterm"
    )
    is_analysis = models.BooleanField()
    is_obsolete = models.BooleanField()
    timeaccessioned = models.DateTimeField()
    timelastmodified = models.DateTimeField()

    class Meta:
        db_table = "feature"
        unique_together = (("organism", "uniquename", "type"),)


class FeatureContact(models.Model):
    feature_contact_id = models.BigAutoField(primary_key=True)
    feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="FeatureContact_feature_Feature",
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.DO_NOTHING,
        related_name="FeatureContact_contact_Contact",
    )

    class Meta:
        db_table = "feature_contact"
        unique_together = (("feature", "contact"),)


class FeatureCvterm(models.Model):
    feature_cvterm_id = models.BigAutoField(primary_key=True)
    feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="FeatureCvterm_feature_Feature",
    )
    cvterm = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="FeatureCvterm_cvterm_Cvterm"
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="FeatureCvterm_pub_Pub"
    )
    is_not = models.BooleanField()
    rank = models.IntegerField()

    class Meta:
        db_table = "feature_cvterm"
        unique_together = (("feature", "cvterm", "pub", "rank"),)


class FeatureCvtermDbxref(models.Model):
    feature_cvterm_dbxref_id = models.BigAutoField(primary_key=True)
    feature_cvterm = models.ForeignKey(
        FeatureCvterm,
        on_delete=models.DO_NOTHING,
        related_name="FeatureCvtermDbxref_feature_cvterm_FeatureCvterm",
    )
    dbxref = models.ForeignKey(
        Dbxref,
        on_delete=models.DO_NOTHING,
        related_name="FeatureCvtermDbxref_dbxref_Dbxref",
    )

    class Meta:
        db_table = "feature_cvterm_dbxref"
        unique_together = (("feature_cvterm", "dbxref"),)


class FeatureCvtermPub(models.Model):
    feature_cvterm_pub_id = models.BigAutoField(primary_key=True)
    feature_cvterm = models.ForeignKey(
        FeatureCvterm,
        on_delete=models.DO_NOTHING,
        related_name="FeatureCvtermPub_feature_cvterm_FeatureCvterm",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="FeatureCvtermPub_pub_Pub"
    )

    class Meta:
        db_table = "feature_cvterm_pub"
        unique_together = (("feature_cvterm", "pub"),)


class FeatureCvtermprop(models.Model):
    feature_cvtermprop_id = models.BigAutoField(primary_key=True)
    feature_cvterm = models.ForeignKey(
        FeatureCvterm,
        on_delete=models.DO_NOTHING,
        related_name="FeatureCvtermprop_feature_cvterm_FeatureCvterm",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="FeatureCvtermprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "feature_cvtermprop"
        unique_together = (("feature_cvterm", "type", "rank"),)


class FeatureDbxref(models.Model):
    feature_dbxref_id = models.BigAutoField(primary_key=True)
    feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="FeatureDbxref_feature_Feature",
    )
    dbxref = models.ForeignKey(
        Dbxref, on_delete=models.DO_NOTHING, related_name="FeatureDbxref_dbxref_Dbxref"
    )
    is_current = models.BooleanField()

    class Meta:
        db_table = "feature_dbxref"
        unique_together = (("feature", "dbxref"),)


class FeatureExpression(models.Model):
    feature_expression_id = models.BigAutoField(primary_key=True)
    expression = models.ForeignKey(
        Expression,
        on_delete=models.DO_NOTHING,
        related_name="FeatureExpression_expression_Expression",
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="FeatureExpression_feature_Feature",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="FeatureExpression_pub_Pub"
    )

    class Meta:
        db_table = "feature_expression"
        unique_together = (("expression", "feature", "pub"),)


class FeatureExpressionprop(models.Model):
    feature_expressionprop_id = models.BigAutoField(primary_key=True)
    feature_expression = models.ForeignKey(
        FeatureExpression,
        on_delete=models.DO_NOTHING,
        related_name="FeatureExpressionprop_feature_expression_FeatureExpression",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="FeatureExpressionprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "feature_expressionprop"
        unique_together = (("feature_expression", "type", "rank"),)


class FeatureGenotype(models.Model):
    feature_genotype_id = models.BigAutoField(primary_key=True)
    feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="FeatureGenotype_feature_Feature",
    )
    genotype = models.ForeignKey(
        "Genotype",
        on_delete=models.DO_NOTHING,
        related_name="FeatureGenotype_genotype_Genotype",
    )
    chromosome = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="FeatureGenotype_chromosome_Feature",
        blank=True,
        null=True,
    )
    rank = models.IntegerField()
    cgroup = models.IntegerField()
    cvterm = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="FeatureGenotype_cvterm_Cvterm",
    )

    class Meta:
        db_table = "feature_genotype"
        unique_together = (
            ("feature", "genotype", "cvterm", "chromosome", "rank", "cgroup"),
        )


class FeaturePhenotype(models.Model):
    feature_phenotype_id = models.BigAutoField(primary_key=True)
    feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="FeaturePhenotype_feature_Feature",
    )
    phenotype = models.ForeignKey(
        "Phenotype",
        on_delete=models.DO_NOTHING,
        related_name="FeaturePhenotype_phenotype_Phenotype",
    )

    class Meta:
        db_table = "feature_phenotype"
        unique_together = (("feature", "phenotype"),)


class FeaturePub(models.Model):
    feature_pub_id = models.BigAutoField(primary_key=True)
    feature = models.ForeignKey(
        Feature, on_delete=models.DO_NOTHING, related_name="FeaturePub_feature_Feature"
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="FeaturePub_pub_Pub"
    )

    class Meta:
        db_table = "feature_pub"
        unique_together = (("feature", "pub"),)


class FeaturePubprop(models.Model):
    feature_pubprop_id = models.BigAutoField(primary_key=True)
    feature_pub = models.ForeignKey(
        FeaturePub,
        on_delete=models.DO_NOTHING,
        related_name="FeaturePubprop_feature_pub_FeaturePub",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="FeaturePubprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "feature_pubprop"
        unique_together = (("feature_pub", "type", "rank"),)


class FeatureRelationship(models.Model):
    objects = None
    feature_relationship_id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="FeatureRelationship_subject_Feature",
    )
    object = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="FeatureRelationship_object_Feature",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="FeatureRelationship_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "feature_relationship"
        unique_together = (("subject", "object", "type", "rank"),)


class FeatureRelationshipPub(models.Model):
    feature_relationship_pub_id = models.BigAutoField(primary_key=True)
    feature_relationship = models.ForeignKey(
        FeatureRelationship,
        on_delete=models.DO_NOTHING,
        related_name="FeatureRelationshipPub_feature_relationship_FeatureRelationship",
    )
    pub = models.ForeignKey(
        "Pub",
        on_delete=models.DO_NOTHING,
        related_name="FeatureRelationshipPub_pub_Pub",
    )

    class Meta:
        db_table = "feature_relationship_pub"
        unique_together = (("feature_relationship", "pub"),)


class FeatureRelationshipprop(models.Model):
    feature_relationshipprop_id = models.BigAutoField(primary_key=True)
    feature_relationship = models.ForeignKey(
        FeatureRelationship,
        on_delete=models.DO_NOTHING,
        related_name="FeatureRelationshipprop_feature_relationship_FeatureRelationship",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="FeatureRelationshipprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "feature_relationshipprop"
        unique_together = (("feature_relationship", "type", "rank"),)


class FeatureRelationshippropPub(models.Model):
    feature_relationshipprop_pub_id = models.BigAutoField(primary_key=True)
    feature_relationshipprop = models.ForeignKey(
        FeatureRelationshipprop,
        on_delete=models.DO_NOTHING,
        related_name="FeatureRelationshippropPub_feature_relationshipprop_FeatureRelationshipprop",
    )
    pub = models.ForeignKey(
        "Pub",
        on_delete=models.DO_NOTHING,
        related_name="FeatureRelationshippropPub_pub_Pub",
    )

    class Meta:
        db_table = "feature_relationshipprop_pub"
        unique_together = (("feature_relationshipprop", "pub"),)


class FeatureSynonym(models.Model):
    feature_synonym_id = models.BigAutoField(primary_key=True)
    synonym = models.ForeignKey(
        "Synonym",
        on_delete=models.DO_NOTHING,
        related_name="FeatureSynonym_synonym_Synonym",
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="FeatureSynonym_feature_Feature",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="FeatureSynonym_pub_Pub"
    )
    is_current = models.BooleanField()
    is_internal = models.BooleanField()

    class Meta:
        db_table = "feature_synonym"
        unique_together = (("synonym", "feature", "pub"),)


class Featureloc(models.Model):
    featureloc_id = models.BigAutoField(primary_key=True)
    feature = models.ForeignKey(
        Feature, on_delete=models.DO_NOTHING, related_name="Featureloc_feature_Feature"
    )
    srcfeature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="Featureloc_srcfeature_Feature",
        blank=True,
        null=True,
    )
    fmin = models.BigIntegerField(blank=True, null=True)
    is_fmin_partial = models.BooleanField()
    fmax = models.BigIntegerField(blank=True, null=True)
    is_fmax_partial = models.BooleanField()
    strand = models.SmallIntegerField(blank=True, null=True)
    phase = models.IntegerField(blank=True, null=True)
    residue_info = models.TextField(blank=True, null=True)
    locgroup = models.IntegerField()
    rank = models.IntegerField()

    class Meta:
        db_table = "featureloc"
        unique_together = (("feature", "locgroup", "rank"),)


class FeaturelocPub(models.Model):
    featureloc_pub_id = models.BigAutoField(primary_key=True)
    featureloc = models.ForeignKey(
        Featureloc,
        on_delete=models.DO_NOTHING,
        related_name="FeaturelocPub_featureloc_Featureloc",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="FeaturelocPub_pub_Pub"
    )

    class Meta:
        db_table = "featureloc_pub"
        unique_together = (("featureloc", "pub"),)


class Featuremap(models.Model):
    featuremap_id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    unittype = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Featuremap_unittype_Cvterm",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "featuremap"


class FeaturemapContact(models.Model):
    featuremap_contact_id = models.BigAutoField(primary_key=True)
    featuremap = models.ForeignKey(
        Featuremap,
        on_delete=models.DO_NOTHING,
        related_name="FeaturemapContact_featuremap_Featuremap",
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.DO_NOTHING,
        related_name="FeaturemapContact_contact_Contact",
    )

    class Meta:
        db_table = "featuremap_contact"
        unique_together = (("featuremap", "contact"),)


class FeaturemapDbxref(models.Model):
    featuremap_dbxref_id = models.BigAutoField(primary_key=True)
    featuremap = models.ForeignKey(
        Featuremap,
        on_delete=models.DO_NOTHING,
        related_name="FeaturemapDbxref_featuremap_Featuremap",
    )
    dbxref = models.ForeignKey(
        Dbxref,
        on_delete=models.DO_NOTHING,
        related_name="FeaturemapDbxref_dbxref_Dbxref",
    )
    is_current = models.BooleanField()

    class Meta:
        db_table = "featuremap_dbxref"


class FeaturemapOrganism(models.Model):
    featuremap_organism_id = models.BigAutoField(primary_key=True)
    featuremap = models.ForeignKey(
        Featuremap,
        on_delete=models.DO_NOTHING,
        related_name="FeaturemapOrganism_featuremap_Featuremap",
    )
    organism = models.ForeignKey(
        "Organism",
        on_delete=models.DO_NOTHING,
        related_name="FeaturemapOrganism_organism_Organism",
    )

    class Meta:
        db_table = "featuremap_organism"
        unique_together = (("featuremap", "organism"),)


class FeaturemapPub(models.Model):
    featuremap_pub_id = models.BigAutoField(primary_key=True)
    featuremap = models.ForeignKey(
        Featuremap,
        on_delete=models.DO_NOTHING,
        related_name="FeaturemapPub_featuremap_Featuremap",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="FeaturemapPub_pub_Pub"
    )

    class Meta:
        db_table = "featuremap_pub"


class Featuremapprop(models.Model):
    featuremapprop_id = models.BigAutoField(primary_key=True)
    featuremap = models.ForeignKey(
        Featuremap,
        on_delete=models.DO_NOTHING,
        related_name="Featuremapprop_featuremap_Featuremap",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Featuremapprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "featuremapprop"
        unique_together = (("featuremap", "type", "rank"),)


class Featurepos(models.Model):
    featurepos_id = models.BigAutoField(primary_key=True)
    featuremap = models.ForeignKey(
        Featuremap,
        on_delete=models.DO_NOTHING,
        related_name="Featurepos_featuremap_Featuremap",
    )
    feature = models.ForeignKey(
        Feature, on_delete=models.DO_NOTHING, related_name="Featurepos_feature_Feature"
    )
    map_feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="Featurepos_map_feature_Feature",
    )
    mappos = models.FloatField()

    class Meta:
        db_table = "featurepos"


class Featureposprop(models.Model):
    featureposprop_id = models.BigAutoField(primary_key=True)
    featurepos = models.ForeignKey(
        Featurepos,
        on_delete=models.DO_NOTHING,
        related_name="Featureposprop_featurepos_Featurepos",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Featureposprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "featureposprop"
        unique_together = (("featurepos", "type", "rank"),)


class Featureprop(models.Model):
    featureprop_id = models.BigAutoField(primary_key=True)
    feature = models.ForeignKey(
        Feature, on_delete=models.DO_NOTHING, related_name="Featureprop_feature_Feature"
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Featureprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "featureprop"
        unique_together = (("feature", "type", "rank"),)


class FeaturepropPub(models.Model):
    featureprop_pub_id = models.BigAutoField(primary_key=True)
    featureprop = models.ForeignKey(
        Featureprop,
        on_delete=models.DO_NOTHING,
        related_name="FeaturepropPub_featureprop_Featureprop",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="FeaturepropPub_pub_Pub"
    )

    class Meta:
        db_table = "featureprop_pub"
        unique_together = (("featureprop", "pub"),)


class Featurerange(models.Model):
    featurerange_id = models.BigAutoField(primary_key=True)
    featuremap = models.ForeignKey(
        Featuremap,
        on_delete=models.DO_NOTHING,
        related_name="Featurerange_featuremap_Featuremap",
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="Featurerange_feature_Feature",
    )
    leftstartf = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="Featurerange_leftstartf_Feature",
    )
    leftendf = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="Featurerange_leftendf_Feature",
        blank=True,
        null=True,
    )
    rightstartf = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="Featurerange_rightstartf_Feature",
        blank=True,
        null=True,
    )
    rightendf = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="Featurerange_rightendf_Feature",
    )
    rangestr = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "featurerange"


class Genotype(models.Model):
    genotype_id = models.BigAutoField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    uniquename = models.TextField(unique=True)
    description = models.TextField(blank=True, null=True)
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Genotype_type_Cvterm"
    )

    class Meta:
        db_table = "genotype"


class Genotypeprop(models.Model):
    genotypeprop_id = models.BigAutoField(primary_key=True)
    genotype = models.ForeignKey(
        Genotype,
        on_delete=models.DO_NOTHING,
        related_name="Genotypeprop_genotype_Genotype",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Genotypeprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "genotypeprop"
        unique_together = (("genotype", "type", "rank"),)


class Library(models.Model):
    library_id = models.BigAutoField(primary_key=True)
    organism = models.ForeignKey(
        "Organism",
        on_delete=models.DO_NOTHING,
        related_name="Library_organism_Organism",
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    uniquename = models.TextField()
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Library_type_Cvterm"
    )
    is_obsolete = models.IntegerField()
    timeaccessioned = models.DateTimeField()
    timelastmodified = models.DateTimeField()

    class Meta:
        db_table = "library"
        unique_together = (("organism", "uniquename", "type"),)


class LibraryContact(models.Model):
    library_contact_id = models.BigAutoField(primary_key=True)
    library = models.ForeignKey(
        Library,
        on_delete=models.DO_NOTHING,
        related_name="LibraryContact_library_Library",
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.DO_NOTHING,
        related_name="LibraryContact_contact_Contact",
    )

    class Meta:
        db_table = "library_contact"
        unique_together = (("library", "contact"),)


class LibraryCvterm(models.Model):
    library_cvterm_id = models.BigAutoField(primary_key=True)
    library = models.ForeignKey(
        Library,
        on_delete=models.DO_NOTHING,
        related_name="LibraryCvterm_library_Library",
    )
    cvterm = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="LibraryCvterm_cvterm_Cvterm"
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="LibraryCvterm_pub_Pub"
    )

    class Meta:
        db_table = "library_cvterm"
        unique_together = (("library", "cvterm", "pub"),)


class LibraryDbxref(models.Model):
    library_dbxref_id = models.BigAutoField(primary_key=True)
    library = models.ForeignKey(
        Library,
        on_delete=models.DO_NOTHING,
        related_name="LibraryDbxref_library_Library",
    )
    dbxref = models.ForeignKey(
        Dbxref, on_delete=models.DO_NOTHING, related_name="LibraryDbxref_dbxref_Dbxref"
    )
    is_current = models.BooleanField()

    class Meta:
        db_table = "library_dbxref"
        unique_together = (("library", "dbxref"),)


class LibraryExpression(models.Model):
    library_expression_id = models.BigAutoField(primary_key=True)
    library = models.ForeignKey(
        Library,
        on_delete=models.DO_NOTHING,
        related_name="LibraryExpression_library_Library",
    )
    expression = models.ForeignKey(
        Expression,
        on_delete=models.DO_NOTHING,
        related_name="LibraryExpression_expression_Expression",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="LibraryExpression_pub_Pub"
    )

    class Meta:
        db_table = "library_expression"
        unique_together = (("library", "expression"),)


class LibraryExpressionprop(models.Model):
    library_expressionprop_id = models.BigAutoField(primary_key=True)
    library_expression = models.ForeignKey(
        LibraryExpression,
        on_delete=models.DO_NOTHING,
        related_name="LibraryExpressionprop_library_expression_LibraryExpression",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="LibraryExpressionprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "library_expressionprop"
        unique_together = (("library_expression", "type", "rank"),)


class LibraryFeature(models.Model):
    library_feature_id = models.BigAutoField(primary_key=True)
    library = models.ForeignKey(
        Library,
        on_delete=models.DO_NOTHING,
        related_name="LibraryFeature_library_Library",
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="LibraryFeature_feature_Feature",
    )

    class Meta:
        db_table = "library_feature"
        unique_together = (("library", "feature"),)


class LibraryFeatureprop(models.Model):
    library_featureprop_id = models.BigAutoField(primary_key=True)
    library_feature = models.ForeignKey(
        LibraryFeature,
        on_delete=models.DO_NOTHING,
        related_name="LibraryFeatureprop_library_feature_LibraryFeature",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="LibraryFeatureprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "library_featureprop"
        unique_together = (("library_feature", "type", "rank"),)


class LibraryPub(models.Model):
    library_pub_id = models.BigAutoField(primary_key=True)
    library = models.ForeignKey(
        Library, on_delete=models.DO_NOTHING, related_name="LibraryPub_library_Library"
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="LibraryPub_pub_Pub"
    )

    class Meta:
        db_table = "library_pub"
        unique_together = (("library", "pub"),)


class LibraryRelationship(models.Model):
    library_relationship_id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(
        Library,
        on_delete=models.DO_NOTHING,
        related_name="LibraryRelationship_subject_Library",
    )
    object = models.ForeignKey(
        Library,
        on_delete=models.DO_NOTHING,
        related_name="LibraryRelationship_object_Library",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="LibraryRelationship_type_Cvterm",
    )

    class Meta:
        db_table = "library_relationship"
        unique_together = (("subject", "object", "type"),)


class LibraryRelationshipPub(models.Model):
    library_relationship_pub_id = models.BigAutoField(primary_key=True)
    library_relationship = models.ForeignKey(
        LibraryRelationship,
        on_delete=models.DO_NOTHING,
        related_name="LibraryRelationshipPub_library_relationship_LibraryRelationship",
    )
    pub = models.ForeignKey(
        "Pub",
        on_delete=models.DO_NOTHING,
        related_name="LibraryRelationshipPub_pub_Pub",
    )

    class Meta:
        db_table = "library_relationship_pub"
        unique_together = (("library_relationship", "pub"),)


class LibrarySynonym(models.Model):
    library_synonym_id = models.BigAutoField(primary_key=True)
    synonym = models.ForeignKey(
        "Synonym",
        on_delete=models.DO_NOTHING,
        related_name="LibrarySynonym_synonym_Synonym",
    )
    library = models.ForeignKey(
        Library,
        on_delete=models.DO_NOTHING,
        related_name="LibrarySynonym_library_Library",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="LibrarySynonym_pub_Pub"
    )
    is_current = models.BooleanField()
    is_internal = models.BooleanField()

    class Meta:
        db_table = "library_synonym"
        unique_together = (("synonym", "library", "pub"),)


class Libraryprop(models.Model):
    libraryprop_id = models.BigAutoField(primary_key=True)
    library = models.ForeignKey(
        Library, on_delete=models.DO_NOTHING, related_name="Libraryprop_library_Library"
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Libraryprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "libraryprop"
        unique_together = (("library", "type", "rank"),)


class LibrarypropPub(models.Model):
    libraryprop_pub_id = models.BigAutoField(primary_key=True)
    libraryprop = models.ForeignKey(
        Libraryprop,
        on_delete=models.DO_NOTHING,
        related_name="LibrarypropPub_libraryprop_Libraryprop",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="LibrarypropPub_pub_Pub"
    )

    class Meta:
        db_table = "libraryprop_pub"
        unique_together = (("libraryprop", "pub"),)


class Magedocumentation(models.Model):
    magedocumentation_id = models.BigAutoField(primary_key=True)
    mageml = models.ForeignKey(
        "Mageml",
        on_delete=models.DO_NOTHING,
        related_name="Magedocumentation_mageml_Mageml",
    )
    tableinfo = models.ForeignKey(
        "Tableinfo",
        on_delete=models.DO_NOTHING,
        related_name="Magedocumentation_tableinfo_Tableinfo",
    )
    row_id = models.IntegerField()
    mageidentifier = models.TextField()

    class Meta:
        db_table = "magedocumentation"


class Mageml(models.Model):
    mageml_id = models.BigAutoField(primary_key=True)
    mage_package = models.TextField()
    mage_ml = models.TextField()

    class Meta:
        db_table = "mageml"


class NdExperiment(models.Model):
    nd_experiment_id = models.BigAutoField(primary_key=True)
    nd_geolocation = models.ForeignKey(
        "NdGeolocation",
        on_delete=models.DO_NOTHING,
        related_name="NdExperiment_nd_geolocation_NdGeolocation",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="NdExperiment_type_Cvterm"
    )

    class Meta:
        db_table = "nd_experiment"


class NdExperimentAnalysis(models.Model):
    nd_experiment_analysis_id = models.BigAutoField(primary_key=True)
    nd_experiment = models.ForeignKey(
        NdExperiment,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentAnalysis_nd_experiment_NdExperiment",
    )
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentAnalysis_analysis_Analysis",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentAnalysis_type_Cvterm",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "nd_experiment_analysis"


class NdExperimentContact(models.Model):
    nd_experiment_contact_id = models.BigAutoField(primary_key=True)
    nd_experiment = models.ForeignKey(
        NdExperiment,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentContact_nd_experiment_NdExperiment",
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentContact_contact_Contact",
    )

    class Meta:
        db_table = "nd_experiment_contact"


class NdExperimentDbxref(models.Model):
    nd_experiment_dbxref_id = models.BigAutoField(primary_key=True)
    nd_experiment = models.ForeignKey(
        NdExperiment,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentDbxref_nd_experiment_NdExperiment",
    )
    dbxref = models.ForeignKey(
        Dbxref,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentDbxref_dbxref_Dbxref",
    )

    class Meta:
        db_table = "nd_experiment_dbxref"


class NdExperimentGenotype(models.Model):
    nd_experiment_genotype_id = models.BigAutoField(primary_key=True)
    nd_experiment = models.ForeignKey(
        NdExperiment,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentGenotype_nd_experiment_NdExperiment",
    )
    genotype = models.ForeignKey(
        Genotype,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentGenotype_genotype_Genotype",
    )

    class Meta:
        db_table = "nd_experiment_genotype"
        unique_together = (("nd_experiment", "genotype"),)


class NdExperimentPhenotype(models.Model):
    nd_experiment_phenotype_id = models.BigAutoField(primary_key=True)
    nd_experiment = models.ForeignKey(
        NdExperiment,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentPhenotype_nd_experiment_NdExperiment",
    )
    phenotype = models.ForeignKey(
        "Phenotype",
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentPhenotype_phenotype_Phenotype",
    )

    class Meta:
        db_table = "nd_experiment_phenotype"
        unique_together = (("nd_experiment", "phenotype"),)


class NdExperimentProject(models.Model):
    nd_experiment_project_id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(
        "Project",
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentProject_project_Project",
    )
    nd_experiment = models.ForeignKey(
        NdExperiment,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentProject_nd_experiment_NdExperiment",
    )

    class Meta:
        db_table = "nd_experiment_project"
        unique_together = (("project", "nd_experiment"),)


class NdExperimentProtocol(models.Model):
    nd_experiment_protocol_id = models.BigAutoField(primary_key=True)
    nd_experiment = models.ForeignKey(
        NdExperiment,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentProtocol_nd_experiment_NdExperiment",
    )
    nd_protocol = models.ForeignKey(
        "NdProtocol",
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentProtocol_nd_protocol_NdProtocol",
    )

    class Meta:
        db_table = "nd_experiment_protocol"


class NdExperimentPub(models.Model):
    nd_experiment_pub_id = models.BigAutoField(primary_key=True)
    nd_experiment = models.ForeignKey(
        NdExperiment,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentPub_nd_experiment_NdExperiment",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="NdExperimentPub_pub_Pub"
    )

    class Meta:
        db_table = "nd_experiment_pub"
        unique_together = (("nd_experiment", "pub"),)


class NdExperimentStock(models.Model):
    nd_experiment_stock_id = models.BigAutoField(primary_key=True)
    nd_experiment = models.ForeignKey(
        NdExperiment,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentStock_nd_experiment_NdExperiment",
    )
    stock = models.ForeignKey(
        "Stock",
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentStock_stock_Stock",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentStock_type_Cvterm",
    )

    class Meta:
        db_table = "nd_experiment_stock"


class NdExperimentStockDbxref(models.Model):
    nd_experiment_stock_dbxref_id = models.BigAutoField(primary_key=True)
    nd_experiment_stock = models.ForeignKey(
        NdExperimentStock,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentStockDbxref_nd_experiment_stock_NdExperimentStock",
    )
    dbxref = models.ForeignKey(
        Dbxref,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentStockDbxref_dbxref_Dbxref",
    )

    class Meta:
        db_table = "nd_experiment_stock_dbxref"


class NdExperimentStockprop(models.Model):
    nd_experiment_stockprop_id = models.BigAutoField(primary_key=True)
    nd_experiment_stock = models.ForeignKey(
        NdExperimentStock,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentStockprop_nd_experiment_stock_NdExperimentStock",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentStockprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "nd_experiment_stockprop"
        unique_together = (("nd_experiment_stock", "type", "rank"),)


class NdExperimentprop(models.Model):
    nd_experimentprop_id = models.BigAutoField(primary_key=True)
    nd_experiment = models.ForeignKey(
        NdExperiment,
        on_delete=models.DO_NOTHING,
        related_name="NdExperimentprop_nd_experiment_NdExperiment",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="NdExperimentprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "nd_experimentprop"
        unique_together = (("nd_experiment", "type", "rank"),)


class NdGeolocation(models.Model):
    nd_geolocation_id = models.BigAutoField(primary_key=True)
    description = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    geodetic_datum = models.CharField(max_length=32, blank=True, null=True)
    altitude = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "nd_geolocation"


class NdGeolocationprop(models.Model):
    nd_geolocationprop_id = models.BigAutoField(primary_key=True)
    nd_geolocation = models.ForeignKey(
        NdGeolocation,
        on_delete=models.DO_NOTHING,
        related_name="NdGeolocationprop_nd_geolocation_NdGeolocation",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="NdGeolocationprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "nd_geolocationprop"
        unique_together = (("nd_geolocation", "type", "rank"),)


class NdProtocol(models.Model):
    nd_protocol_id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="NdProtocol_type_Cvterm"
    )

    class Meta:
        db_table = "nd_protocol"


class NdProtocolReagent(models.Model):
    nd_protocol_reagent_id = models.BigAutoField(primary_key=True)
    nd_protocol = models.ForeignKey(
        NdProtocol,
        on_delete=models.DO_NOTHING,
        related_name="NdProtocolReagent_nd_protocol_NdProtocol",
    )
    reagent = models.ForeignKey(
        "NdReagent",
        on_delete=models.DO_NOTHING,
        related_name="NdProtocolReagent_reagent_NdReagent",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="NdProtocolReagent_type_Cvterm",
    )

    class Meta:
        db_table = "nd_protocol_reagent"


class NdProtocolprop(models.Model):
    nd_protocolprop_id = models.BigAutoField(primary_key=True)
    nd_protocol = models.ForeignKey(
        NdProtocol,
        on_delete=models.DO_NOTHING,
        related_name="NdProtocolprop_nd_protocol_NdProtocol",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="NdProtocolprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "nd_protocolprop"
        unique_together = (("nd_protocol", "type", "rank"),)


class NdReagent(models.Model):
    nd_reagent_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=80)
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="NdReagent_type_Cvterm"
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="NdReagent_feature_Feature",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "nd_reagent"


class NdReagentRelationship(models.Model):
    nd_reagent_relationship_id = models.BigAutoField(primary_key=True)
    subject_reagent = models.ForeignKey(
        NdReagent,
        on_delete=models.DO_NOTHING,
        related_name="NdReagentRelationship_subject_reagent_NdReagent",
    )
    object_reagent = models.ForeignKey(
        NdReagent,
        on_delete=models.DO_NOTHING,
        related_name="NdReagentRelationship_object_reagent_NdReagent",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="NdReagentRelationship_type_Cvterm",
    )

    class Meta:
        db_table = "nd_reagent_relationship"


class NdReagentprop(models.Model):
    nd_reagentprop_id = models.BigAutoField(primary_key=True)
    nd_reagent = models.ForeignKey(
        NdReagent,
        on_delete=models.DO_NOTHING,
        related_name="NdReagentprop_nd_reagent_NdReagent",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="NdReagentprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "nd_reagentprop"
        unique_together = (("nd_reagent", "type", "rank"),)


class Organism(models.Model):
    organism_id = models.BigAutoField(primary_key=True)
    abbreviation = models.CharField(max_length=255, blank=True, null=True)
    genus = models.CharField(max_length=255)
    species = models.CharField(max_length=255)
    common_name = models.CharField(max_length=255, blank=True, null=True)
    infraspecific_name = models.CharField(max_length=1024, blank=True, null=True)
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Organism_type_Cvterm",
        blank=True,
        null=True,
    )
    comment = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "organism"
        unique_together = (("genus", "species", "type", "infraspecific_name"),)


class OrganismCvterm(models.Model):
    organism_cvterm_id = models.BigAutoField(primary_key=True)
    organism = models.ForeignKey(
        Organism,
        on_delete=models.DO_NOTHING,
        related_name="OrganismCvterm_organism_Organism",
    )
    cvterm = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="OrganismCvterm_cvterm_Cvterm"
    )
    rank = models.IntegerField()
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="OrganismCvterm_pub_Pub"
    )

    class Meta:
        db_table = "organism_cvterm"
        unique_together = (("organism", "cvterm", "pub"),)


class OrganismCvtermprop(models.Model):
    organism_cvtermprop_id = models.BigAutoField(primary_key=True)
    organism_cvterm = models.ForeignKey(
        OrganismCvterm,
        on_delete=models.DO_NOTHING,
        related_name="OrganismCvtermprop_organism_cvterm_OrganismCvterm",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="OrganismCvtermprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "organism_cvtermprop"
        unique_together = (("organism_cvterm", "type", "rank"),)


class OrganismDbxref(models.Model):
    organism_dbxref_id = models.BigAutoField(primary_key=True)
    organism = models.ForeignKey(
        Organism,
        on_delete=models.DO_NOTHING,
        related_name="OrganismDbxref_organism_Organism",
    )
    dbxref = models.ForeignKey(
        Dbxref, on_delete=models.DO_NOTHING, related_name="OrganismDbxref_dbxref_Dbxref"
    )

    class Meta:
        db_table = "organism_dbxref"
        unique_together = (("organism", "dbxref"),)


class OrganismPub(models.Model):
    organism_pub_id = models.BigAutoField(primary_key=True)
    organism = models.ForeignKey(
        Organism,
        on_delete=models.DO_NOTHING,
        related_name="OrganismPub_organism_Organism",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="OrganismPub_pub_Pub"
    )

    class Meta:
        db_table = "organism_pub"
        unique_together = (("organism", "pub"),)


class OrganismRelationship(models.Model):
    organism_relationship_id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(
        Organism,
        on_delete=models.DO_NOTHING,
        related_name="OrganismRelationship_subject_Organism",
    )
    object = models.ForeignKey(
        Organism,
        on_delete=models.DO_NOTHING,
        related_name="OrganismRelationship_object_Organism",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="OrganismRelationship_type_Cvterm",
    )
    rank = models.IntegerField()

    class Meta:
        db_table = "organism_relationship"
        unique_together = (("subject", "object", "type", "rank"),)


class Organismprop(models.Model):
    organismprop_id = models.BigAutoField(primary_key=True)
    organism = models.ForeignKey(
        Organism,
        on_delete=models.DO_NOTHING,
        related_name="Organismprop_organism_Organism",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Organismprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "organismprop"
        unique_together = (("organism", "type", "rank"),)


class OrganismpropPub(models.Model):
    organismprop_pub_id = models.BigAutoField(primary_key=True)
    organismprop = models.ForeignKey(
        Organismprop,
        on_delete=models.DO_NOTHING,
        related_name="OrganismpropPub_organismprop_Organismprop",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="OrganismpropPub_pub_Pub"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "organismprop_pub"
        unique_together = (("organismprop", "pub"),)


class Phendesc(models.Model):
    phendesc_id = models.BigAutoField(primary_key=True)
    genotype = models.ForeignKey(
        Genotype, on_delete=models.DO_NOTHING, related_name="Phendesc_genotype_Genotype"
    )
    environment = models.ForeignKey(
        Environment,
        on_delete=models.DO_NOTHING,
        related_name="Phendesc_environment_Environment",
    )
    description = models.TextField()
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Phendesc_type_Cvterm"
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="Phendesc_pub_Pub"
    )

    class Meta:
        db_table = "phendesc"
        unique_together = (("genotype", "environment", "type", "pub"),)


class Phenotype(models.Model):
    phenotype_id = models.BigAutoField(primary_key=True)
    uniquename = models.TextField(unique=True)
    name = models.TextField(blank=True, null=True)
    observable = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Phenotype_observable_Cvterm",
        blank=True,
        null=True,
    )
    attr = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Phenotype_attr_Cvterm",
        blank=True,
        null=True,
    )
    value = models.TextField(blank=True, null=True)
    cvalue = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Phenotype_cvalue_Cvterm",
        blank=True,
        null=True,
    )
    assay = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Phenotype_assay_Cvterm",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "phenotype"


class PhenotypeComparison(models.Model):
    phenotype_comparison_id = models.BigAutoField(primary_key=True)
    genotype1 = models.ForeignKey(
        Genotype,
        on_delete=models.DO_NOTHING,
        related_name="PhenotypeComparison_genotype1_Genotype",
    )
    environment1 = models.ForeignKey(
        Environment,
        on_delete=models.DO_NOTHING,
        related_name="PhenotypeComparison_environment1_Environment",
    )
    genotype2 = models.ForeignKey(
        Genotype,
        on_delete=models.DO_NOTHING,
        related_name="PhenotypeComparison_genotype2_Genotype",
    )
    environment2 = models.ForeignKey(
        Environment,
        on_delete=models.DO_NOTHING,
        related_name="PhenotypeComparison_environment2_Environment",
    )
    phenotype1 = models.ForeignKey(
        Phenotype,
        on_delete=models.DO_NOTHING,
        related_name="PhenotypeComparison_phenotype1_Phenotype",
    )
    phenotype2 = models.ForeignKey(
        Phenotype,
        on_delete=models.DO_NOTHING,
        related_name="PhenotypeComparison_phenotype2_Phenotype",
        blank=True,
        null=True,
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="PhenotypeComparison_pub_Pub"
    )
    organism = models.ForeignKey(
        Organism,
        on_delete=models.DO_NOTHING,
        related_name="PhenotypeComparison_organism_Organism",
    )

    class Meta:
        db_table = "phenotype_comparison"
        unique_together = (
            (
                "genotype1",
                "environment1",
                "genotype2",
                "environment2",
                "phenotype1",
                "pub",
            ),
        )


class PhenotypeComparisonCvterm(models.Model):
    phenotype_comparison_cvterm_id = models.BigAutoField(primary_key=True)
    phenotype_comparison = models.ForeignKey(
        PhenotypeComparison,
        on_delete=models.DO_NOTHING,
        related_name="PhenotypeComparisonCvterm_phenotype_comparison_PhenotypeComparison",
    )
    cvterm = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="PhenotypeComparisonCvterm_cvterm_Cvterm",
    )
    pub = models.ForeignKey(
        "Pub",
        on_delete=models.DO_NOTHING,
        related_name="PhenotypeComparisonCvterm_pub_Pub",
    )
    rank = models.IntegerField()

    class Meta:
        db_table = "phenotype_comparison_cvterm"
        unique_together = (("phenotype_comparison", "cvterm"),)


class PhenotypeCvterm(models.Model):
    phenotype_cvterm_id = models.BigAutoField(primary_key=True)
    phenotype = models.ForeignKey(
        Phenotype,
        on_delete=models.DO_NOTHING,
        related_name="PhenotypeCvterm_phenotype_Phenotype",
    )
    cvterm = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="PhenotypeCvterm_cvterm_Cvterm",
    )
    rank = models.IntegerField()

    class Meta:
        db_table = "phenotype_cvterm"
        unique_together = (("phenotype", "cvterm", "rank"),)


class Phenotypeprop(models.Model):
    phenotypeprop_id = models.BigAutoField(primary_key=True)
    phenotype = models.ForeignKey(
        Phenotype,
        on_delete=models.DO_NOTHING,
        related_name="Phenotypeprop_phenotype_Phenotype",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Phenotypeprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "phenotypeprop"
        unique_together = (("phenotype", "type", "rank"),)


class Phenstatement(models.Model):
    phenstatement_id = models.BigAutoField(primary_key=True)
    genotype = models.ForeignKey(
        Genotype,
        on_delete=models.DO_NOTHING,
        related_name="Phenstatement_genotype_Genotype",
    )
    environment = models.ForeignKey(
        Environment,
        on_delete=models.DO_NOTHING,
        related_name="Phenstatement_environment_Environment",
    )
    phenotype = models.ForeignKey(
        Phenotype,
        on_delete=models.DO_NOTHING,
        related_name="Phenstatement_phenotype_Phenotype",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Phenstatement_type_Cvterm"
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="Phenstatement_pub_Pub"
    )

    class Meta:
        db_table = "phenstatement"
        unique_together = (("genotype", "phenotype", "environment", "type", "pub"),)


class Phylonode(models.Model):
    phylonode_id = models.BigAutoField(primary_key=True)
    phylotree = models.ForeignKey(
        "Phylotree",
        on_delete=models.DO_NOTHING,
        related_name="Phylonode_phylotree_Phylotree",
    )
    parent_phylonode = models.ForeignKey(
        "self",
        on_delete=models.DO_NOTHING,
        related_name="Phylonode_parent_phylonode_self",
        blank=True,
        null=True,
    )
    left_idx = models.IntegerField()
    right_idx = models.IntegerField()
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Phylonode_type_Cvterm",
        blank=True,
        null=True,
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="Phylonode_feature_Feature",
        blank=True,
        null=True,
    )
    label = models.CharField(max_length=255, blank=True, null=True)
    distance = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "phylonode"
        unique_together = (("phylotree", "left_idx"), ("phylotree", "right_idx"))


class PhylonodeDbxref(models.Model):
    phylonode_dbxref_id = models.BigAutoField(primary_key=True)
    phylonode = models.ForeignKey(
        Phylonode,
        on_delete=models.DO_NOTHING,
        related_name="PhylonodeDbxref_phylonode_Phylonode",
    )
    dbxref = models.ForeignKey(
        Dbxref,
        on_delete=models.DO_NOTHING,
        related_name="PhylonodeDbxref_dbxref_Dbxref",
    )

    class Meta:
        db_table = "phylonode_dbxref"
        unique_together = (("phylonode", "dbxref"),)


class PhylonodeOrganism(models.Model):
    phylonode_organism_id = models.BigAutoField(primary_key=True)
    phylonode = models.ForeignKey(
        Phylonode,
        on_delete=models.DO_NOTHING,
        related_name="PhylonodeOrganism_phylonode_Phylonode",
    )
    organism = models.ForeignKey(
        Organism,
        on_delete=models.DO_NOTHING,
        related_name="PhylonodeOrganism_organism_Organism",
    )

    class Meta:
        db_table = "phylonode_organism"


class PhylonodePub(models.Model):
    phylonode_pub_id = models.BigAutoField(primary_key=True)
    phylonode = models.ForeignKey(
        Phylonode,
        on_delete=models.DO_NOTHING,
        related_name="PhylonodePub_phylonode_Phylonode",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="PhylonodePub_pub_Pub"
    )

    class Meta:
        db_table = "phylonode_pub"
        unique_together = (("phylonode", "pub"),)


class PhylonodeRelationship(models.Model):
    phylonode_relationship_id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(
        Phylonode,
        on_delete=models.DO_NOTHING,
        related_name="PhylonodeRelationship_subject_Phylonode",
    )
    object = models.ForeignKey(
        Phylonode,
        on_delete=models.DO_NOTHING,
        related_name="PhylonodeRelationship_object_Phylonode",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="PhylonodeRelationship_type_Cvterm",
    )
    rank = models.IntegerField(blank=True, null=True)
    phylotree = models.ForeignKey(
        "Phylotree",
        on_delete=models.DO_NOTHING,
        related_name="PhylonodeRelationship_phylotree_Phylotree",
    )

    class Meta:
        db_table = "phylonode_relationship"
        unique_together = (("subject", "object", "type"),)


class Phylonodeprop(models.Model):
    phylonodeprop_id = models.BigAutoField(primary_key=True)
    phylonode = models.ForeignKey(
        Phylonode,
        on_delete=models.DO_NOTHING,
        related_name="Phylonodeprop_phylonode_Phylonode",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Phylonodeprop_type_Cvterm"
    )
    value = models.TextField()
    rank = models.IntegerField()

    class Meta:
        db_table = "phylonodeprop"
        unique_together = (("phylonode", "type", "value", "rank"),)


class Phylotree(models.Model):
    phylotree_id = models.BigAutoField(primary_key=True)
    dbxref = models.ForeignKey(
        Dbxref, on_delete=models.DO_NOTHING, related_name="Phylotree_dbxref_Dbxref"
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Phylotree_type_Cvterm",
        blank=True,
        null=True,
    )
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.DO_NOTHING,
        related_name="Phylotree_analysis_Analysis",
        blank=True,
        null=True,
    )
    comment = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "phylotree"


class PhylotreePub(models.Model):
    phylotree_pub_id = models.BigAutoField(primary_key=True)
    phylotree = models.ForeignKey(
        Phylotree,
        on_delete=models.DO_NOTHING,
        related_name="PhylotreePub_phylotree_Phylotree",
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="PhylotreePub_pub_Pub"
    )

    class Meta:
        db_table = "phylotree_pub"
        unique_together = (("phylotree", "pub"),)


class Phylotreeprop(models.Model):
    phylotreeprop_id = models.BigAutoField(primary_key=True)
    phylotree = models.ForeignKey(
        Phylotree,
        on_delete=models.DO_NOTHING,
        related_name="Phylotreeprop_phylotree_Phylotree",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Phylotreeprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "phylotreeprop"
        unique_together = (("phylotree", "type", "rank"),)


class Project(models.Model):
    project_id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "project"


class ProjectAnalysis(models.Model):
    project_analysis_id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.DO_NOTHING,
        related_name="ProjectAnalysis_project_Project",
    )
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.DO_NOTHING,
        related_name="ProjectAnalysis_analysis_Analysis",
    )
    rank = models.IntegerField()

    class Meta:
        db_table = "project_analysis"
        unique_together = (("project", "analysis"),)


class ProjectContact(models.Model):
    project_contact_id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.DO_NOTHING,
        related_name="ProjectContact_project_Project",
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.DO_NOTHING,
        related_name="ProjectContact_contact_Contact",
    )

    class Meta:
        db_table = "project_contact"
        unique_together = (("project", "contact"),)


class ProjectDbxref(models.Model):
    project_dbxref_id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.DO_NOTHING,
        related_name="ProjectDbxref_project_Project",
    )
    dbxref = models.ForeignKey(
        Dbxref, on_delete=models.DO_NOTHING, related_name="ProjectDbxref_dbxref_Dbxref"
    )
    is_current = models.BooleanField()

    class Meta:
        db_table = "project_dbxref"
        unique_together = (("project", "dbxref"),)


class ProjectFeature(models.Model):
    project_feature_id = models.BigAutoField(primary_key=True)
    feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="ProjectFeature_feature_Feature",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.DO_NOTHING,
        related_name="ProjectFeature_project_Project",
    )

    class Meta:
        db_table = "project_feature"
        unique_together = (("feature", "project"),)


class ProjectPub(models.Model):
    project_pub_id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(
        Project, on_delete=models.DO_NOTHING, related_name="ProjectPub_project_Project"
    )
    pub = models.ForeignKey(
        "Pub", on_delete=models.DO_NOTHING, related_name="ProjectPub_pub_Pub"
    )

    class Meta:
        db_table = "project_pub"
        unique_together = (("project", "pub"),)


class ProjectRelationship(models.Model):
    project_relationship_id = models.BigAutoField(primary_key=True)
    subject_project = models.ForeignKey(
        Project,
        on_delete=models.DO_NOTHING,
        related_name="ProjectRelationship_subject_project_Project",
    )
    object_project = models.ForeignKey(
        Project,
        on_delete=models.DO_NOTHING,
        related_name="ProjectRelationship_object_project_Project",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="ProjectRelationship_type_Cvterm",
    )

    class Meta:
        db_table = "project_relationship"
        unique_together = (("subject_project", "object_project", "type"),)


class ProjectStock(models.Model):
    project_stock_id = models.BigAutoField(primary_key=True)
    stock = models.ForeignKey(
        "Stock", on_delete=models.DO_NOTHING, related_name="ProjectStock_stock_Stock"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.DO_NOTHING,
        related_name="ProjectStock_project_Project",
    )

    class Meta:
        db_table = "project_stock"
        unique_together = (("stock", "project"),)


class Projectprop(models.Model):
    projectprop_id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(
        Project, on_delete=models.DO_NOTHING, related_name="Projectprop_project_Project"
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Projectprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "projectprop"
        unique_together = (("project", "type", "rank"),)


class Protocol(models.Model):
    protocol_id = models.BigAutoField(primary_key=True)
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Protocol_type_Cvterm"
    )
    pub = models.ForeignKey(
        "Pub",
        on_delete=models.DO_NOTHING,
        related_name="Protocol_pub_Pub",
        blank=True,
        null=True,
    )
    dbxref = models.ForeignKey(
        Dbxref,
        on_delete=models.DO_NOTHING,
        related_name="Protocol_dbxref_Dbxref",
        blank=True,
        null=True,
    )
    name = models.TextField(unique=True)
    uri = models.TextField(blank=True, null=True)
    protocoldescription = models.TextField(blank=True, null=True)
    hardwaredescription = models.TextField(blank=True, null=True)
    softwaredescription = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "protocol"


class Protocolparam(models.Model):
    protocolparam_id = models.BigAutoField(primary_key=True)
    protocol = models.ForeignKey(
        Protocol,
        on_delete=models.DO_NOTHING,
        related_name="Protocolparam_protocol_Protocol",
    )
    name = models.TextField()
    datatype = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Protocolparam_datatype_Cvterm",
        blank=True,
        null=True,
    )
    unittype = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Protocolparam_unittype_Cvterm",
        blank=True,
        null=True,
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "protocolparam"


@machadoPubMethods()
class Pub(models.Model):
    pub_id = models.BigAutoField(primary_key=True)
    title = models.TextField(blank=True, null=True)
    volumetitle = models.TextField(blank=True, null=True)
    volume = models.CharField(max_length=255, blank=True, null=True)
    series_name = models.CharField(max_length=255, blank=True, null=True)
    issue = models.CharField(max_length=255, blank=True, null=True)
    pyear = models.CharField(max_length=255, blank=True, null=True)
    pages = models.CharField(max_length=255, blank=True, null=True)
    miniref = models.CharField(max_length=255, blank=True, null=True)
    uniquename = models.TextField(unique=True)
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Pub_type_Cvterm"
    )
    is_obsolete = models.NullBooleanField()
    publisher = models.CharField(max_length=255, blank=True, null=True)
    pubplace = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "pub"


class PubDbxref(models.Model):
    pub_dbxref_id = models.BigAutoField(primary_key=True)
    pub = models.ForeignKey(
        Pub, on_delete=models.DO_NOTHING, related_name="PubDbxref_pub_Pub"
    )
    dbxref = models.ForeignKey(
        Dbxref, on_delete=models.DO_NOTHING, related_name="PubDbxref_dbxref_Dbxref"
    )
    is_current = models.BooleanField()

    class Meta:
        db_table = "pub_dbxref"
        unique_together = (("pub", "dbxref"),)


class PubRelationship(models.Model):
    pub_relationship_id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(
        Pub, on_delete=models.DO_NOTHING, related_name="PubRelationship_subject_Pub"
    )
    object = models.ForeignKey(
        Pub, on_delete=models.DO_NOTHING, related_name="PubRelationship_object_Pub"
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="PubRelationship_type_Cvterm"
    )

    class Meta:
        db_table = "pub_relationship"
        unique_together = (("subject", "object", "type"),)


class Pubauthor(models.Model):
    pubauthor_id = models.BigAutoField(primary_key=True)
    pub = models.ForeignKey(
        Pub, on_delete=models.DO_NOTHING, related_name="Pubauthor_pub_Pub"
    )
    rank = models.IntegerField()
    editor = models.NullBooleanField()
    surname = models.CharField(max_length=100)
    givennames = models.CharField(max_length=100, blank=True, null=True)
    suffix = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "pubauthor"
        unique_together = (("pub", "rank"),)


class PubauthorContact(models.Model):
    pubauthor_contact_id = models.BigAutoField(primary_key=True)
    contact = models.ForeignKey(
        Contact,
        on_delete=models.DO_NOTHING,
        related_name="PubauthorContact_contact_Contact",
    )
    pubauthor = models.ForeignKey(
        Pubauthor,
        on_delete=models.DO_NOTHING,
        related_name="PubauthorContact_pubauthor_Pubauthor",
    )

    class Meta:
        db_table = "pubauthor_contact"
        unique_together = (("contact", "pubauthor"),)


class Pubprop(models.Model):
    pubprop_id = models.BigAutoField(primary_key=True)
    pub = models.ForeignKey(
        Pub, on_delete=models.DO_NOTHING, related_name="Pubprop_pub_Pub"
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Pubprop_type_Cvterm"
    )
    value = models.TextField()
    rank = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "pubprop"
        unique_together = (("pub", "type", "rank"),)


class Quantification(models.Model):
    quantification_id = models.BigAutoField(primary_key=True)
    acquisition = models.ForeignKey(
        Acquisition,
        on_delete=models.DO_NOTHING,
        related_name="Quantification_acquisition_Acquisition",
    )
    operator = models.ForeignKey(
        Contact,
        on_delete=models.DO_NOTHING,
        related_name="Quantification_operator_Contact",
        blank=True,
        null=True,
    )
    protocol = models.ForeignKey(
        Protocol,
        on_delete=models.DO_NOTHING,
        related_name="Quantification_protocol_Protocol",
        blank=True,
        null=True,
    )
    analysis = models.ForeignKey(
        Analysis,
        on_delete=models.DO_NOTHING,
        related_name="Quantification_analysis_Analysis",
    )
    quantificationdate = models.DateTimeField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    uri = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "quantification"
        unique_together = (("name", "analysis"),)


class QuantificationRelationship(models.Model):
    quantification_relationship_id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(
        Quantification,
        on_delete=models.DO_NOTHING,
        related_name="QuantificationRelationship_subject_Quantification",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="QuantificationRelationship_type_Cvterm",
    )
    object = models.ForeignKey(
        Quantification,
        on_delete=models.DO_NOTHING,
        related_name="QuantificationRelationship_object_Quantification",
    )

    class Meta:
        db_table = "quantification_relationship"
        unique_together = (("subject", "object", "type"),)


class Quantificationprop(models.Model):
    quantificationprop_id = models.BigAutoField(primary_key=True)
    quantification = models.ForeignKey(
        Quantification,
        on_delete=models.DO_NOTHING,
        related_name="Quantificationprop_quantification_Quantification",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Quantificationprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "quantificationprop"
        unique_together = (("quantification", "type", "rank"),)


class Stock(models.Model):
    stock_id = models.BigAutoField(primary_key=True)
    dbxref = models.ForeignKey(
        Dbxref,
        on_delete=models.DO_NOTHING,
        related_name="Stock_dbxref_Dbxref",
        blank=True,
        null=True,
    )
    organism = models.ForeignKey(
        Organism,
        on_delete=models.DO_NOTHING,
        related_name="Stock_organism_Organism",
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    uniquename = models.TextField()
    description = models.TextField(blank=True, null=True)
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Stock_type_Cvterm"
    )
    is_obsolete = models.BooleanField()

    class Meta:
        db_table = "stock"
        unique_together = (("organism", "uniquename", "type"),)


class StockCvterm(models.Model):
    stock_cvterm_id = models.BigAutoField(primary_key=True)
    stock = models.ForeignKey(
        Stock, on_delete=models.DO_NOTHING, related_name="StockCvterm_stock_Stock"
    )
    cvterm = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="StockCvterm_cvterm_Cvterm"
    )
    pub = models.ForeignKey(
        Pub, on_delete=models.DO_NOTHING, related_name="StockCvterm_pub_Pub"
    )
    is_not = models.BooleanField()
    rank = models.IntegerField()

    class Meta:
        db_table = "stock_cvterm"
        unique_together = (("stock", "cvterm", "pub", "rank"),)


class StockCvtermprop(models.Model):
    stock_cvtermprop_id = models.BigAutoField(primary_key=True)
    stock_cvterm = models.ForeignKey(
        StockCvterm,
        on_delete=models.DO_NOTHING,
        related_name="StockCvtermprop_stock_cvterm_StockCvterm",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="StockCvtermprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "stock_cvtermprop"
        unique_together = (("stock_cvterm", "type", "rank"),)


class StockDbxref(models.Model):
    stock_dbxref_id = models.BigAutoField(primary_key=True)
    stock = models.ForeignKey(
        Stock, on_delete=models.DO_NOTHING, related_name="StockDbxref_stock_Stock"
    )
    dbxref = models.ForeignKey(
        Dbxref, on_delete=models.DO_NOTHING, related_name="StockDbxref_dbxref_Dbxref"
    )
    is_current = models.BooleanField()

    class Meta:
        db_table = "stock_dbxref"
        unique_together = (("stock", "dbxref"),)


class StockDbxrefprop(models.Model):
    stock_dbxrefprop_id = models.BigAutoField(primary_key=True)
    stock_dbxref = models.ForeignKey(
        StockDbxref,
        on_delete=models.DO_NOTHING,
        related_name="StockDbxrefprop_stock_dbxref_StockDbxref",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="StockDbxrefprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "stock_dbxrefprop"
        unique_together = (("stock_dbxref", "type", "rank"),)


class StockFeature(models.Model):
    stock_feature_id = models.BigAutoField(primary_key=True)
    feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="StockFeature_feature_Feature",
    )
    stock = models.ForeignKey(
        Stock, on_delete=models.DO_NOTHING, related_name="StockFeature_stock_Stock"
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="StockFeature_type_Cvterm"
    )
    rank = models.IntegerField()

    class Meta:
        db_table = "stock_feature"
        unique_together = (("feature", "stock", "type", "rank"),)


class StockFeaturemap(models.Model):
    stock_featuremap_id = models.BigAutoField(primary_key=True)
    featuremap = models.ForeignKey(
        Featuremap,
        on_delete=models.DO_NOTHING,
        related_name="StockFeaturemap_featuremap_Featuremap",
    )
    stock = models.ForeignKey(
        Stock, on_delete=models.DO_NOTHING, related_name="StockFeaturemap_stock_Stock"
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="StockFeaturemap_type_Cvterm",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "stock_featuremap"
        unique_together = (("featuremap", "stock", "type"),)


class StockGenotype(models.Model):
    stock_genotype_id = models.BigAutoField(primary_key=True)
    stock = models.ForeignKey(
        Stock, on_delete=models.DO_NOTHING, related_name="StockGenotype_stock_Stock"
    )
    genotype = models.ForeignKey(
        Genotype,
        on_delete=models.DO_NOTHING,
        related_name="StockGenotype_genotype_Genotype",
    )

    class Meta:
        db_table = "stock_genotype"
        unique_together = (("stock", "genotype"),)


class StockLibrary(models.Model):
    stock_library_id = models.BigAutoField(primary_key=True)
    library = models.ForeignKey(
        Library,
        on_delete=models.DO_NOTHING,
        related_name="StockLibrary_library_Library",
    )
    stock = models.ForeignKey(
        Stock, on_delete=models.DO_NOTHING, related_name="StockLibrary_stock_Stock"
    )

    class Meta:
        db_table = "stock_library"
        unique_together = (("library", "stock"),)


class StockPub(models.Model):
    stock_pub_id = models.BigAutoField(primary_key=True)
    stock = models.ForeignKey(
        Stock, on_delete=models.DO_NOTHING, related_name="StockPub_stock_Stock"
    )
    pub = models.ForeignKey(
        Pub, on_delete=models.DO_NOTHING, related_name="StockPub_pub_Pub"
    )

    class Meta:
        db_table = "stock_pub"
        unique_together = (("stock", "pub"),)


class StockRelationship(models.Model):
    stock_relationship_id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(
        Stock,
        on_delete=models.DO_NOTHING,
        related_name="StockRelationship_subject_Stock",
    )
    object = models.ForeignKey(
        Stock,
        on_delete=models.DO_NOTHING,
        related_name="StockRelationship_object_Stock",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="StockRelationship_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "stock_relationship"
        unique_together = (("subject", "object", "type", "rank"),)


class StockRelationshipCvterm(models.Model):
    stock_relationship_cvterm_id = models.BigAutoField(primary_key=True)
    stock_relationship = models.ForeignKey(
        StockRelationship,
        on_delete=models.DO_NOTHING,
        related_name="StockRelationshipCvterm_stock_relationship_StockRelationship",
    )
    cvterm = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="StockRelationshipCvterm_cvterm_Cvterm",
    )
    pub = models.ForeignKey(
        Pub,
        on_delete=models.DO_NOTHING,
        related_name="StockRelationshipCvterm_pub_Pub",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "stock_relationship_cvterm"


class StockRelationshipPub(models.Model):
    stock_relationship_pub_id = models.BigAutoField(primary_key=True)
    stock_relationship = models.ForeignKey(
        StockRelationship,
        on_delete=models.DO_NOTHING,
        related_name="StockRelationshipPub_stock_relationship_StockRelationship",
    )
    pub = models.ForeignKey(
        Pub, on_delete=models.DO_NOTHING, related_name="StockRelationshipPub_pub_Pub"
    )

    class Meta:
        db_table = "stock_relationship_pub"
        unique_together = (("stock_relationship", "pub"),)


class Stockcollection(models.Model):
    stockcollection_id = models.BigAutoField(primary_key=True)
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Stockcollection_type_Cvterm"
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.DO_NOTHING,
        related_name="Stockcollection_contact_Contact",
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    uniquename = models.TextField()

    class Meta:
        db_table = "stockcollection"
        unique_together = (("uniquename", "type"),)


class StockcollectionDb(models.Model):
    stockcollection_db_id = models.BigAutoField(primary_key=True)
    stockcollection = models.ForeignKey(
        Stockcollection,
        on_delete=models.DO_NOTHING,
        related_name="StockcollectionDb_stockcollection_Stockcollection",
    )
    db = models.ForeignKey(
        Db, on_delete=models.DO_NOTHING, related_name="StockcollectionDb_db_Db"
    )

    class Meta:
        db_table = "stockcollection_db"
        unique_together = (("stockcollection", "db"),)


class StockcollectionStock(models.Model):
    stockcollection_stock_id = models.BigAutoField(primary_key=True)
    stockcollection = models.ForeignKey(
        Stockcollection,
        on_delete=models.DO_NOTHING,
        related_name="StockcollectionStock_stockcollection_Stockcollection",
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.DO_NOTHING,
        related_name="StockcollectionStock_stock_Stock",
    )

    class Meta:
        db_table = "stockcollection_stock"
        unique_together = (("stockcollection", "stock"),)


class Stockcollectionprop(models.Model):
    stockcollectionprop_id = models.BigAutoField(primary_key=True)
    stockcollection = models.ForeignKey(
        Stockcollection,
        on_delete=models.DO_NOTHING,
        related_name="Stockcollectionprop_stockcollection_Stockcollection",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Stockcollectionprop_type_Cvterm",
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "stockcollectionprop"
        unique_together = (("stockcollection", "type", "rank"),)


class Stockprop(models.Model):
    stockprop_id = models.BigAutoField(primary_key=True)
    stock = models.ForeignKey(
        Stock, on_delete=models.DO_NOTHING, related_name="Stockprop_stock_Stock"
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Stockprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "stockprop"
        unique_together = (("stock", "type", "rank"),)


class StockpropPub(models.Model):
    stockprop_pub_id = models.BigAutoField(primary_key=True)
    stockprop = models.ForeignKey(
        Stockprop,
        on_delete=models.DO_NOTHING,
        related_name="StockpropPub_stockprop_Stockprop",
    )
    pub = models.ForeignKey(
        Pub, on_delete=models.DO_NOTHING, related_name="StockpropPub_pub_Pub"
    )

    class Meta:
        db_table = "stockprop_pub"
        unique_together = (("stockprop", "pub"),)


class Study(models.Model):
    study_id = models.BigAutoField(primary_key=True)
    contact = models.ForeignKey(
        Contact, on_delete=models.DO_NOTHING, related_name="Study_contact_Contact"
    )
    pub = models.ForeignKey(
        Pub,
        on_delete=models.DO_NOTHING,
        related_name="Study_pub_Pub",
        blank=True,
        null=True,
    )
    dbxref = models.ForeignKey(
        Dbxref,
        on_delete=models.DO_NOTHING,
        related_name="Study_dbxref_Dbxref",
        blank=True,
        null=True,
    )
    name = models.TextField(unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "study"


class StudyAssay(models.Model):
    study_assay_id = models.BigAutoField(primary_key=True)
    study = models.ForeignKey(
        Study, on_delete=models.DO_NOTHING, related_name="StudyAssay_study_Study"
    )
    assay = models.ForeignKey(
        Assay, on_delete=models.DO_NOTHING, related_name="StudyAssay_assay_Assay"
    )

    class Meta:
        db_table = "study_assay"
        unique_together = (("study", "assay"),)


class Studydesign(models.Model):
    studydesign_id = models.BigAutoField(primary_key=True)
    study = models.ForeignKey(
        Study, on_delete=models.DO_NOTHING, related_name="Studydesign_study_Study"
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "studydesign"


class Studydesignprop(models.Model):
    studydesignprop_id = models.BigAutoField(primary_key=True)
    studydesign = models.ForeignKey(
        Studydesign,
        on_delete=models.DO_NOTHING,
        related_name="Studydesignprop_studydesign_Studydesign",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Studydesignprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "studydesignprop"
        unique_together = (("studydesign", "type", "rank"),)


class Studyfactor(models.Model):
    studyfactor_id = models.BigAutoField(primary_key=True)
    studydesign = models.ForeignKey(
        Studydesign,
        on_delete=models.DO_NOTHING,
        related_name="Studyfactor_studydesign_Studydesign",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="Studyfactor_type_Cvterm",
        blank=True,
        null=True,
    )
    name = models.TextField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "studyfactor"


class Studyfactorvalue(models.Model):
    studyfactorvalue_id = models.BigAutoField(primary_key=True)
    studyfactor = models.ForeignKey(
        Studyfactor,
        on_delete=models.DO_NOTHING,
        related_name="Studyfactorvalue_studyfactor_Studyfactor",
    )
    assay = models.ForeignKey(
        Assay, on_delete=models.DO_NOTHING, related_name="Studyfactorvalue_assay_Assay"
    )
    factorvalue = models.TextField(blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "studyfactorvalue"


class Studyprop(models.Model):
    studyprop_id = models.BigAutoField(primary_key=True)
    study = models.ForeignKey(
        Study, on_delete=models.DO_NOTHING, related_name="Studyprop_study_Study"
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Studyprop_type_Cvterm"
    )
    value = models.TextField(blank=True, null=True)
    rank = models.IntegerField()

    class Meta:
        db_table = "studyprop"
        unique_together = (("study", "type", "rank"),)


class StudypropFeature(models.Model):
    studyprop_feature_id = models.BigAutoField(primary_key=True)
    studyprop = models.ForeignKey(
        Studyprop,
        on_delete=models.DO_NOTHING,
        related_name="StudypropFeature_studyprop_Studyprop",
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.DO_NOTHING,
        related_name="StudypropFeature_feature_Feature",
    )
    type = models.ForeignKey(
        Cvterm,
        on_delete=models.DO_NOTHING,
        related_name="StudypropFeature_type_Cvterm",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "studyprop_feature"
        unique_together = (("studyprop", "feature"),)


class Synonym(models.Model):
    synonym_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Synonym_type_Cvterm"
    )
    synonym_sgml = models.CharField(max_length=255)

    class Meta:
        db_table = "synonym"
        unique_together = (("name", "type"),)


class Tableinfo(models.Model):
    tableinfo_id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=30)
    primary_key_column = models.CharField(max_length=30, blank=True, null=True)
    is_view = models.IntegerField()
    view_on_table_id = models.BigIntegerField(blank=True, null=True)
    superclass_table_id = models.BigIntegerField(blank=True, null=True)
    is_updateable = models.IntegerField()
    modification_date = models.DateField()

    class Meta:
        db_table = "tableinfo"


class Treatment(models.Model):
    treatment_id = models.BigAutoField(primary_key=True)
    rank = models.IntegerField()
    biomaterial = models.ForeignKey(
        Biomaterial,
        on_delete=models.DO_NOTHING,
        related_name="Treatment_biomaterial_Biomaterial",
    )
    type = models.ForeignKey(
        Cvterm, on_delete=models.DO_NOTHING, related_name="Treatment_type_Cvterm"
    )
    protocol = models.ForeignKey(
        Protocol,
        on_delete=models.DO_NOTHING,
        related_name="Treatment_protocol_Protocol",
        blank=True,
        null=True,
    )
    name = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "treatment"
