from django.core.exceptions import ObjectDoesNotExist
from chado.models import Project


def get_project(project_name):

    try:
        project = Project.objects.get(name=project_name)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist('%s not registered.'
                                 % project_name)
    return project


def get_set_project(project_name):
    try:
        project = Project.objects.get(name=project_name)
    except ObjectDoesNotExist:
        project = Project.objects.create(name=project_name)
        project.save()
    return (project)
