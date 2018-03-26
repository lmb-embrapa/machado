"""Remove phylotree."""

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from machado.models import Phylotree, Phylonode, PhylonodeOrganism


class Command(BaseCommand):
    """Remove phylotree."""

    help = 'Remove Phylotree (CASCADE)'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--name", help="phylotree.name", required=True,
                            type=str)

    def handle(self, name: str, **options):
        """Execute the main function."""
        try:
            self.stdout.write('Deleting {} and every child record (CASCADE)'
                              .format(name))

            phylotree = Phylotree.objects.get(name=name)
            phylonode_ids = list(Phylonode.objects.filter(
                phylotree=phylotree).values_list('phylonode_id', flat=True))
            PhylonodeOrganism.objects.filter(
                phylonode_id__in=phylonode_ids).delete()
            Phylonode.objects.filter(phylotree=phylotree).delete()
            phylotree.delete()

            self.stdout.write(self.style.SUCCESS('Done'))
        except ObjectDoesNotExist:
            raise CommandError(
                'Cannot remove {} (not registered)'.format(name))
