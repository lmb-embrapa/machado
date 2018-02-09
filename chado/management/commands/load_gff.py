"""Load GFF file."""

from chado.loaders.common import Validator
from chado.loaders.exceptions import ImportingError
from chado.loaders.feature import FeatureLoader
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm
import os
import pysam


class Command(BaseCommand):
    """Load GFF file."""

    help = 'Load GFF3 file indexed with tabix.'

    def add_arguments(self, parser):
        """Define the arguments."""
        parser.add_argument("--gff",
                            help="GFF3 genome file indexed with tabix"
                            "(see http://www.htslib.org/doc/tabix.html)",
                            required=True,
                            type=str)
        parser.add_argument("--organism", help="Species name (eg. Homo "
                            "sapiens, Mus musculus)",
                            required=True,
                            type=str)
        parser.add_argument("--description", help="DB Description",
                            required=False, type=str)
        parser.add_argument("--url", help="DB URL", required=False, type=str)
        parser.add_argument("--cpu", help="Number of threads", default=1,
                            type=int)

    def handle(self, *args, **options):
        """Execute the main function."""
        verbosity = 1
        if options.get('verbosity'):
            verbosity = options.get('verbosity')

        if verbosity > 0:
            self.stdout.write('Preprocessing')

        Validator().validate(options.get('gff'))

        # retrieve only the file name
        filename = os.path.basename(options.get('gff'))
        try:
            feature_file = FeatureLoader(
                filename=filename,
                organism=options.get('organism'),
                url=options.get('url'),
                description=options.get('description'))

            cpu = options.get('cpu')
            pool = ThreadPoolExecutor(max_workers=cpu)
            tasks = list()

            # Load the GFF3 file
            with open(options['gff']) as tbx_file:
                # print(str(tbx_file.name))
                tbx = pysam.TabixFile(tbx_file.name)
                for row in tbx.fetch(parser=pysam.asGTF()):
                    tasks.append(pool.submit(
                        feature_file.store_tabix_feature, row))

            if verbosity > 0:
                self.stdout.write('Loading features')
            for task in tqdm(as_completed(tasks), total=len(tasks)):
                if task.result():
                    raise(task.result())

        except ImportingError as e:
            raise CommandError(e)

        finally:
            if verbosity > 0:
                self.stdout.write('Loading relationships')
            feature_file.store_relationships()

            if feature_file.ignored_attrs is not None:
                self.stdout.write(
                    self.style.WARNING('Ignored attrs: {}'.format(
                        feature_file.ignored_attrs)))

        self.stdout.write(self.style.SUCCESS('Done'))
