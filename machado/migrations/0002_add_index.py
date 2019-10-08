# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Create database from chado default_schema.sql."""
from django.db import migrations, models


class Migration(migrations.Migration):
    """Migration."""
    dependencies = [('machado','0001_initial')]

    operations = [
        migrations.RunSQL('create index on analysis using btree (program);'),
        migrations.RunSQL('create index on analysis using btree (programversion);'),
        migrations.RunSQL('create index on analysis using btree (sourcename);'),
        migrations.RunSQL('create index on analysisfeature using btree (rawscore);'),
        migrations.RunSQL('create index on analysisfeature using btree (normscore);'),
        migrations.RunSQL('create index on analysisfeature using btree (significance);'),
        migrations.RunSQL('create index on analysisfeature using btree (identity);'),
        migrations.RunSQL('create index on feature using btree (type_id, is_obsolete, feature_id);'),
        migrations.RunSQL('create index on featureprop using btree (value);'),
    ]
