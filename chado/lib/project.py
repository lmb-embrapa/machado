from django.core.exceptions import ObjectDoesNotExist
from chado.models import Project, ProjectDbxref, ProjectFeature


def get_project(project_name):

    try:
        project = Project.objects.get(name=project_name)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist('%s not registered.'
                                 % project_name)
    return project


def get_set_project_dbxref(dbxref, project):

    try:
        project_dbxref = ProjectDbxref.objects.get(project=project,
                                                   dbxref=dbxref)
    except ObjectDoesNotExist:
        # will always set iscurrent to True... change this in the future if it
        # may. Check the field REMARKS in the table to see what this is about
        project_dbxref = ProjectDbxref.objects.create(project=project,
                                                      dbxref=dbxref,
                                                      is_current=True)
        project_dbxref.save()
    return project_dbxref


def get_set_project_feature(feature, project):

    try:
        project_feature = ProjectFeature.objects.get(project=project,
                                                     feature=feature)
    except ObjectDoesNotExist:
        project_feature = ProjectFeature.objects.create(project=project,
                                                        feature=feature)
        project_feature.save()
    return project_feature


def get_set_project(project_name):
    try:
        project = Project.objects.get(name=project_name)
    except ObjectDoesNotExist:
        project = Project.objects.create(name=project_name)
        project.save()
    return (project)
