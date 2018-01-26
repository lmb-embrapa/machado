"""project library."""
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Project


def get_project(project_name):
    """Retrieve project object."""
    try:
        project = Project.objects.get(name=project_name)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist('%s not registered.'
                                 % project_name)
    return project
