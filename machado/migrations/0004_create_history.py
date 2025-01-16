# Copyright 2018 by Embrapa.  All rights reserved.
#
# This code is part of the machado distribution and governed by its
# license. Please see the LICENSE.txt and README.md files that should
# have been included as part of this package for licensing information.

"""Create database from chado default_schema.sql."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("machado", "0001_initial"),
        ("machado", "0002_add_index"),
        ("machado", "0003_add_multispecies"),
    ]

    operations = [
        migrations.CreateModel(
            name="History",
            fields=[
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("command", models.CharField(max_length=255)),
                ("params", models.TextField(blank=True, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("exit_code", models.IntegerField(blank=True, null=True)),
            ],
            options={
                "db_table": "history",
            },
        )
    ]
