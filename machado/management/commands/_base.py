# Copyright 2026 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

import os
from django.core.management.base import CommandError
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.utils import IntegrityError
from machado.models import History
from machado.loaders.exceptions import ImportingError


class HistoryCommandMixin:
    """Mixin to automatically handle History logging for management commands.

    Logs start, success, and data-related failures.
    """

    def execute(self, *args, **options):
        """Execute the command and record history logs."""
        history_id = os.environ.get("MACHADO_HISTORY_ID")
        if history_id:
            try:
                history_obj = History.objects.get(pk=int(history_id))
            except (History.DoesNotExist, ValueError):
                history_obj = History()
        else:
            history_obj = History()

        # Get the command name from the module path
        command_name = self.__class__.__module__.split(".")[-1]

        # Capture parameters
        params = str(options)

        history_obj.start(command=command_name, params=params, pid=os.getpid())

        try:
            output = super().execute(*args, **options)
            history_obj.success()
            return output
        except (
            ImportingError,
            ObjectDoesNotExist,
            MultipleObjectsReturned,
            IntegrityError,
            CommandError,
        ) as e:
            error_msg = str(e)
            # Log to history
            history_obj.failure(stderr=error_msg)

            # Inform user through terminal with styling
            self.stdout.write(self.style.ERROR(f"ERROR: {error_msg}"))

            # Re-raise as CommandError if it's not already one, or just re-raise
            if not isinstance(e, CommandError):
                raise CommandError(e)
            raise e
        except Exception as e:
            # Log ALL failures to history, including unexpected ones
            error_msg = str(e)
            history_obj.failure(stderr=error_msg)
            self.stdout.write(self.style.ERROR(f"CRITICAL ERROR: {error_msg}"))
            raise e
