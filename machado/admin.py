from django.contrib import admin

from .models import Acquisition
from .models import AcquisitionRelationship
from .models import Acquisitionprop
from .models import Analysis
from .models import AnalysisCvterm
from .models import AnalysisDbxref
from .models import AnalysisPub
from .models import AnalysisRelationship
from .models import Analysisfeature
from .models import Analysisfeatureprop
from .models import Analysisprop
from .models import Arraydesign
from .models import Arraydesignprop
from .models import Assay
from .models import AssayBiomaterial
from .models import AssayProject
from .models import Assayprop
from .models import Biomaterial
from .models import BiomaterialDbxref
from .models import BiomaterialRelationship
from .models import BiomaterialTreatment
from .models import Biomaterialprop
from .models import CellLine
from .models import CellLineCvterm
from .models import CellLineCvtermprop
from .models import CellLineDbxref
from .models import CellLineFeature
from .models import CellLineLibrary
from .models import CellLinePub
from .models import CellLineRelationship
from .models import CellLineSynonym
from .models import CellLineprop
from .models import CellLinepropPub
from .models import Chadoprop
from .models import Channel
from .models import Contact
from .models import ContactRelationship
from .models import Contactprop
from .models import Control
from .models import Cv
from .models import Cvprop
from .models import Cvterm
from .models import CvtermDbxref
from .models import CvtermRelationship
from .models import Cvtermpath
from .models import Cvtermprop
from .models import Cvtermsynonym
from .models import Db
from .models import Dbprop
from .models import Dbxref
from .models import Dbxrefprop
from .models import Eimage
from .models import Element
from .models import ElementRelationship
from .models import Elementresult
from .models import ElementresultRelationship
from .models import Environment
from .models import EnvironmentCvterm
from .models import Expression
from .models import ExpressionCvterm
from .models import ExpressionCvtermprop
from .models import ExpressionImage
from .models import ExpressionPub
from .models import Expressionprop
from .models import Feature
from .models import FeatureContact
from .models import FeatureCvterm
from .models import FeatureCvtermDbxref
from .models import FeatureCvtermPub
from .models import FeatureCvtermprop
from .models import FeatureDbxref
from .models import FeatureExpression
from .models import FeatureExpressionprop
from .models import FeatureGenotype
from .models import FeaturePhenotype
from .models import FeaturePub
from .models import FeaturePubprop
from .models import FeatureRelationship
from .models import FeatureRelationshipPub
from .models import FeatureRelationshipprop
from .models import FeatureRelationshippropPub
from .models import FeatureSynonym
from .models import Featureloc
from .models import FeaturelocPub
from .models import Featuremap
from .models import FeaturemapContact
from .models import FeaturemapDbxref
from .models import FeaturemapOrganism
from .models import FeaturemapPub
from .models import Featuremapprop
from .models import Featurepos
from .models import Featureposprop
from .models import Featureprop
from .models import FeaturepropPub
from .models import Featurerange
from .models import Genotype
from .models import Genotypeprop
from .models import Library
from .models import LibraryContact
from .models import LibraryCvterm
from .models import LibraryDbxref
from .models import LibraryExpression
from .models import LibraryExpressionprop
from .models import LibraryFeature
from .models import LibraryFeatureprop
from .models import LibraryPub
from .models import LibraryRelationship
from .models import LibraryRelationshipPub
from .models import LibrarySynonym
from .models import Libraryprop
from .models import LibrarypropPub
from .models import Magedocumentation
from .models import Mageml
from .models import NdExperiment
from .models import NdExperimentAnalysis
from .models import NdExperimentContact
from .models import NdExperimentDbxref
from .models import NdExperimentGenotype
from .models import NdExperimentPhenotype
from .models import NdExperimentProject
from .models import NdExperimentProtocol
from .models import NdExperimentPub
from .models import NdExperimentStock
from .models import NdExperimentStockDbxref
from .models import NdExperimentStockprop
from .models import NdExperimentprop
from .models import NdGeolocation
from .models import NdGeolocationprop
from .models import NdProtocol
from .models import NdProtocolReagent
from .models import NdProtocolprop
from .models import NdReagent
from .models import NdReagentRelationship
from .models import NdReagentprop
from .models import Organism
from .models import OrganismCvterm
from .models import OrganismCvtermprop
from .models import OrganismDbxref
from .models import OrganismPub
from .models import OrganismRelationship
from .models import Organismprop
from .models import OrganismpropPub
from .models import Phendesc
from .models import Phenotype
from .models import PhenotypeComparison
from .models import PhenotypeComparisonCvterm
from .models import PhenotypeCvterm
from .models import Phenotypeprop
from .models import Phenstatement
from .models import Phylonode
from .models import PhylonodeDbxref
from .models import PhylonodeOrganism
from .models import PhylonodePub
from .models import PhylonodeRelationship
from .models import Phylonodeprop
from .models import Phylotree
from .models import PhylotreePub
from .models import Phylotreeprop
from .models import Project
from .models import ProjectAnalysis
from .models import ProjectContact
from .models import ProjectDbxref
from .models import ProjectFeature
from .models import ProjectPub
from .models import ProjectRelationship
from .models import ProjectStock
from .models import Projectprop
from .models import Protocol
from .models import Protocolparam
from .models import Pub
from .models import PubDbxref
from .models import PubRelationship
from .models import Pubauthor
from .models import PubauthorContact
from .models import Pubprop
from .models import Quantification
from .models import QuantificationRelationship
from .models import Quantificationprop
from .models import Stock
from .models import StockCvterm
from .models import StockCvtermprop
from .models import StockDbxref
from .models import StockDbxrefprop
from .models import StockFeature
from .models import StockFeaturemap
from .models import StockGenotype
from .models import StockLibrary
from .models import StockPub
from .models import StockRelationship
from .models import StockRelationshipCvterm
from .models import StockRelationshipPub
from .models import Stockcollection
from .models import StockcollectionDb
from .models import StockcollectionStock
from .models import Stockcollectionprop
from .models import Stockprop
from .models import StockpropPub
from .models import Study
from .models import StudyAssay
from .models import Studydesign
from .models import Studydesignprop
from .models import Studyfactor
from .models import Studyfactorvalue
from .models import Studyprop
from .models import StudypropFeature
from .models import Synonym
from .models import Tableinfo
from .models import Treatment

admin.site.register(Acquisition)
admin.site.register(AcquisitionRelationship)
admin.site.register(Acquisitionprop)
admin.site.register(Analysis)
admin.site.register(AnalysisCvterm)
admin.site.register(AnalysisDbxref)
admin.site.register(AnalysisPub)
admin.site.register(AnalysisRelationship)
admin.site.register(Analysisfeature)
admin.site.register(Analysisfeatureprop)
admin.site.register(Analysisprop)
admin.site.register(Arraydesign)
admin.site.register(Arraydesignprop)
admin.site.register(Assay)
admin.site.register(AssayBiomaterial)
admin.site.register(AssayProject)
admin.site.register(Assayprop)
admin.site.register(Biomaterial)
admin.site.register(BiomaterialDbxref)
admin.site.register(BiomaterialRelationship)
admin.site.register(BiomaterialTreatment)
admin.site.register(Biomaterialprop)
admin.site.register(CellLine)
admin.site.register(CellLineCvterm)
admin.site.register(CellLineCvtermprop)
admin.site.register(CellLineDbxref)
admin.site.register(CellLineFeature)
admin.site.register(CellLineLibrary)
admin.site.register(CellLinePub)
admin.site.register(CellLineRelationship)
admin.site.register(CellLineSynonym)
admin.site.register(CellLineprop)
admin.site.register(CellLinepropPub)
admin.site.register(Chadoprop)
admin.site.register(Channel)
admin.site.register(Contact)
admin.site.register(ContactRelationship)
admin.site.register(Contactprop)
admin.site.register(Control)
admin.site.register(Cv)
admin.site.register(Cvprop)
admin.site.register(Cvterm)
admin.site.register(CvtermDbxref)
admin.site.register(CvtermRelationship)
admin.site.register(Cvtermpath)
admin.site.register(Cvtermprop)
admin.site.register(Cvtermsynonym)
admin.site.register(Db)
admin.site.register(Dbprop)
admin.site.register(Dbxref)
admin.site.register(Dbxrefprop)
admin.site.register(Eimage)
admin.site.register(Element)
admin.site.register(ElementRelationship)
admin.site.register(Elementresult)
admin.site.register(ElementresultRelationship)
admin.site.register(Environment)
admin.site.register(EnvironmentCvterm)
admin.site.register(Expression)
admin.site.register(ExpressionCvterm)
admin.site.register(ExpressionCvtermprop)
admin.site.register(ExpressionImage)
admin.site.register(ExpressionPub)
admin.site.register(Expressionprop)
admin.site.register(Feature)
admin.site.register(FeatureContact)
admin.site.register(FeatureCvterm)
admin.site.register(FeatureCvtermDbxref)
admin.site.register(FeatureCvtermPub)
admin.site.register(FeatureCvtermprop)
admin.site.register(FeatureDbxref)
admin.site.register(FeatureExpression)
admin.site.register(FeatureExpressionprop)
admin.site.register(FeatureGenotype)
admin.site.register(FeaturePhenotype)
admin.site.register(FeaturePub)
admin.site.register(FeaturePubprop)
admin.site.register(FeatureRelationship)
admin.site.register(FeatureRelationshipPub)
admin.site.register(FeatureRelationshipprop)
admin.site.register(FeatureRelationshippropPub)
admin.site.register(FeatureSynonym)
admin.site.register(Featureloc)
admin.site.register(FeaturelocPub)
admin.site.register(Featuremap)
admin.site.register(FeaturemapContact)
admin.site.register(FeaturemapDbxref)
admin.site.register(FeaturemapOrganism)
admin.site.register(FeaturemapPub)
admin.site.register(Featuremapprop)
admin.site.register(Featurepos)
admin.site.register(Featureposprop)
admin.site.register(Featureprop)
admin.site.register(FeaturepropPub)
admin.site.register(Featurerange)
admin.site.register(Genotype)
admin.site.register(Genotypeprop)
admin.site.register(Library)
admin.site.register(LibraryContact)
admin.site.register(LibraryCvterm)
admin.site.register(LibraryDbxref)
admin.site.register(LibraryExpression)
admin.site.register(LibraryExpressionprop)
admin.site.register(LibraryFeature)
admin.site.register(LibraryFeatureprop)
admin.site.register(LibraryPub)
admin.site.register(LibraryRelationship)
admin.site.register(LibraryRelationshipPub)
admin.site.register(LibrarySynonym)
admin.site.register(Libraryprop)
admin.site.register(LibrarypropPub)
admin.site.register(Magedocumentation)
admin.site.register(Mageml)
admin.site.register(NdExperiment)
admin.site.register(NdExperimentAnalysis)
admin.site.register(NdExperimentContact)
admin.site.register(NdExperimentDbxref)
admin.site.register(NdExperimentGenotype)
admin.site.register(NdExperimentPhenotype)
admin.site.register(NdExperimentProject)
admin.site.register(NdExperimentProtocol)
admin.site.register(NdExperimentPub)
admin.site.register(NdExperimentStock)
admin.site.register(NdExperimentStockDbxref)
admin.site.register(NdExperimentStockprop)
admin.site.register(NdExperimentprop)
admin.site.register(NdGeolocation)
admin.site.register(NdGeolocationprop)
admin.site.register(NdProtocol)
admin.site.register(NdProtocolReagent)
admin.site.register(NdProtocolprop)
admin.site.register(NdReagent)
admin.site.register(NdReagentRelationship)
admin.site.register(NdReagentprop)
admin.site.register(Organism)
admin.site.register(OrganismCvterm)
admin.site.register(OrganismCvtermprop)
admin.site.register(OrganismDbxref)
admin.site.register(OrganismPub)
admin.site.register(OrganismRelationship)
admin.site.register(Organismprop)
admin.site.register(OrganismpropPub)
admin.site.register(Phendesc)
admin.site.register(Phenotype)
admin.site.register(PhenotypeComparison)
admin.site.register(PhenotypeComparisonCvterm)
admin.site.register(PhenotypeCvterm)
admin.site.register(Phenotypeprop)
admin.site.register(Phenstatement)
admin.site.register(Phylonode)
admin.site.register(PhylonodeDbxref)
admin.site.register(PhylonodeOrganism)
admin.site.register(PhylonodePub)
admin.site.register(PhylonodeRelationship)
admin.site.register(Phylonodeprop)
admin.site.register(Phylotree)
admin.site.register(PhylotreePub)
admin.site.register(Phylotreeprop)
admin.site.register(Project)
admin.site.register(ProjectAnalysis)
admin.site.register(ProjectContact)
admin.site.register(ProjectDbxref)
admin.site.register(ProjectFeature)
admin.site.register(ProjectPub)
admin.site.register(ProjectRelationship)
admin.site.register(ProjectStock)
admin.site.register(Projectprop)
admin.site.register(Protocol)
admin.site.register(Protocolparam)
admin.site.register(Pub)
admin.site.register(PubDbxref)
admin.site.register(PubRelationship)
admin.site.register(Pubauthor)
admin.site.register(PubauthorContact)
admin.site.register(Pubprop)
admin.site.register(Quantification)
admin.site.register(QuantificationRelationship)
admin.site.register(Quantificationprop)
admin.site.register(Stock)
admin.site.register(StockCvterm)
admin.site.register(StockCvtermprop)
admin.site.register(StockDbxref)
admin.site.register(StockDbxrefprop)
admin.site.register(StockFeature)
admin.site.register(StockFeaturemap)
admin.site.register(StockGenotype)
admin.site.register(StockLibrary)
admin.site.register(StockPub)
admin.site.register(StockRelationship)
admin.site.register(StockRelationshipCvterm)
admin.site.register(StockRelationshipPub)
admin.site.register(Stockcollection)
admin.site.register(StockcollectionDb)
admin.site.register(StockcollectionStock)
admin.site.register(Stockcollectionprop)
admin.site.register(Stockprop)
admin.site.register(StockpropPub)
admin.site.register(Study)
admin.site.register(StudyAssay)
admin.site.register(Studydesign)
admin.site.register(Studydesignprop)
admin.site.register(Studyfactor)
admin.site.register(Studyfactorvalue)
admin.site.register(Studyprop)
admin.site.register(StudypropFeature)
admin.site.register(Synonym)
admin.site.register(Tableinfo)
admin.site.register(Treatment)
