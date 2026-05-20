from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import cache_page
from django.conf import settings
from machado.models import Feature, Featureloc, FeatureRelationship
from machado.loaders.common import retrieve_organism

try:
    CACHE_TIMEOUT = settings.CACHE_TIMEOUT
except AttributeError:
    CACHE_TIMEOUT = 60 * 60


@cache_page(CACHE_TIMEOUT)
def jbrowse_global(request):
    """Provide API endpoint to view JBrowse global settings."""
    return JsonResponse([{"featureDensity": 0.02}], safe=False)


@cache_page(CACHE_TIMEOUT)
def jbrowse_refseqs(request):
    """Provide API endpoint to JBrowse refSeqs.json."""
    organism = request.GET.get("organism")
    sotype = request.GET.get("soType")

    queryset = Feature.objects.filter(is_obsolete=0)
    if organism is not None:
        queryset = queryset.filter(organism=retrieve_organism(organism))
    if sotype is not None:
        queryset = queryset.filter(type__cv__name="sequence", type__name=sotype)

    queryset = queryset.only("seqlen", "uniquename")

    data = []
    for obj in queryset:
        data.append({"name": obj.uniquename, "start": 1, "end": obj.seqlen})
    return JsonResponse(data, safe=False)


@cache_page(CACHE_TIMEOUT)
def jbrowse_names(request):
    """Provide API endpoint to JBrowse names."""
    queryset = (
        Feature.objects.filter(is_obsolete=0)
        .exclude(name=None)
        .exclude(uniquename=None)
    )

    organism = request.GET.get("organism")
    if organism is not None:
        queryset = queryset.filter(organism=retrieve_organism(organism))

    equals = request.GET.get("equals")
    startswith = request.GET.get("startswith")
    if startswith is not None:
        queryset = queryset.filter(uniquename__startswith=startswith)
    elif equals is not None:
        queryset = queryset.filter(uniquename=equals)

    data = []
    for obj in queryset:
        try:
            location = Featureloc.objects.get(feature_id=obj.feature_id)
            ref = (
                Feature.objects.filter(feature_id=location.srcfeature_id)
                .values_list("uniquename", flat=True)
                .first()
            )
            loc_data = {
                "ref": ref,
                "start": location.fmin,
                "end": location.fmax,
                "type": obj.type.name,
                "tracks": [],
                "objectName": obj.uniquename,
            }
        except ObjectDoesNotExist:
            loc_data = None

        data.append({"name": obj.name, "location": loc_data})
    return JsonResponse(data, safe=False)


@cache_page(CACHE_TIMEOUT)
def jbrowse_features(request, refseq):
    """Provide API endpoint to view JBrowse features."""
    organism = request.GET.get("organism")
    org_obj = None
    if organism is not None:
        org_obj = retrieve_organism(organism)

    refseq_feature_obj = Feature.objects.filter(
        uniquename=refseq, organism=org_obj
    ).first()
    if not refseq_feature_obj:
        return JsonResponse({"features": []})

    soType = request.GET.get("soType")
    start = request.GET.get("start", 1)
    end = request.GET.get("end")

    features_locs = Featureloc.objects.filter(srcfeature=refseq_feature_obj)
    if end is not None:
        features_locs = features_locs.filter(fmin__lte=end)
    features_locs = features_locs.filter(fmax__gte=start)
    features_ids = features_locs.values_list("feature_id", flat=True)

    features = Feature.objects.filter(feature_id__in=features_ids, is_obsolete=0)
    if soType is not None:
        features = features.filter(type__cv__name="sequence", type__name=soType)

    # Serialize
    data = []
    for obj in features:
        # Get location
        try:
            loc = Featureloc.objects.get(
                feature_id=obj.feature_id, srcfeature_id=refseq_feature_obj.feature_id
            )
            f_start = loc.fmin
            f_end = loc.fmax
            f_strand = loc.strand
        except ObjectDoesNotExist:
            f_start = 1
            f_end = obj.seqlen
            f_strand = None

        if not soType:
            f_start = 1
            f_end = obj.seqlen

        # Get subfeatures
        subfeatures = []
        relationship = FeatureRelationship.objects.filter(
            subject_id=obj.feature_id, type__name="part_of", type__cv__name="sequence"
        )
        for rel in relationship:
            rel_feature_id = rel.object_id
            try:
                sub_loc = Featureloc.objects.get(
                    feature_id=rel_feature_id,
                    srcfeature_id=refseq_feature_obj.feature_id,
                )
                sub_type = (
                    Feature.objects.filter(feature_id=rel_feature_id)
                    .values_list("type__name", flat=True)
                    .first()
                )
                subfeatures.append(
                    {
                        "type": sub_type,
                        "start": sub_loc.fmin,
                        "end": sub_loc.fmax,
                        "strand": sub_loc.strand,
                        "phase": sub_loc.phase,
                    }
                )
            except ObjectDoesNotExist:
                pass

        feat_data = {
            "uniqueID": obj.uniquename,
            "accession": obj.uniquename,
            "name": obj.name,
            "type": obj.type.name,
            "start": f_start,
            "end": f_end,
            "strand": f_strand,
            "subfeatures": subfeatures,
            "seq": obj.residues,
            "display": obj.get_display(),
        }
        data.append(feat_data)

    return JsonResponse({"features": data})
