from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from chado.models import Project
from chado.lib.project import get_project
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Create new project'

    def add_arguments(self, parser):
        parser.add_argument("--name",
                            help="project name",
                            required=True,
                            type=str)
        parser.add_argument("--description",
                            help="project description",
                            required=False,
                            type=str)

    def handle(self, *args, **options):
        project_name = options['name']

        try:
            project = get_project(project_name)
            if (project is not None):
                self.stdout.write(self.style.ERROR('%s already registered!'
                                                 % project.name))
#                raise IntegrityError('Project %s already registered!'
#                                     % project.name)
        except ObjectDoesNotExist:
            project = Project.objects.create(name=options['name'],
                                             description=options['descri'
                                             'ption'])
            project.save()
            self.stdout.write(self.style.SUCCESS('%s registered'
                                                 % project.name))
