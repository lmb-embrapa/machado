Data loading
============

The Chado schema heavily relies on **Ontologies** to integrate different datasets.
Therefore it must be the first to load.

Inside the extras directory, there's a file named sample.tar.gz that might be helpful.
It contains a few small FASTA and GFF files, together with a README file with examples of command lines.


.. toctree::
   :maxdepth: 2
   :titlesonly:

   Ontologies <load_ontologies>
   Taxonomy <load_taxonomy>
   Organism <insert_organism>
   Publication <load_publication>
   FASTA <load_fasta>
   GFF <load_gff>
   Feature additional info<load_feature_annotation>
   Blast <load_blast>
   InterproScan <load_interproscan>
   OrthoMCL <load_orthomcl>
   RNA-seq <load_rnaseq>
   Coexpression <load_coexpression>
