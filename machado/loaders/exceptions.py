# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Loaders exceptions."""


class ImportingError(Exception):
    """Handles importing errors with contextual metadata."""

    def __init__(self, message, file=None, line=None, field=None, context=None):
        """Initialize ImportingError with contextual details."""
        self.message = message
        self.file = file
        self.line = line
        self.field = field
        self.context = context
        super().__init__(self.message)

    def __str__(self):
        """Return string representation of the importing error."""
        msg = self.message
        if self.file:
            msg = f"File: {self.file} - {msg}"
        if self.line:
            msg = f"Line {self.line}: {msg}"
        if self.field:
            msg = f"Field '{self.field}': {msg}"
        if self.context:
            msg = f"({self.context}) {msg}"
        return msg
