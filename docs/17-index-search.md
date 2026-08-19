# Index and Search

## PostgreSQL Full-Text Search

Machado uses the native **full-text search capabilities of PostgreSQL** to provide fast, reliable search and faceted navigation without requiring any external search services. All search indexes are stored within the main database.



```bash
MACHADO_VALID_TYPES=gene,mRNA,polypeptide
```

If `MACHADO_VALID_TYPES` is not explicitly set in the settings, the default is `['gene', 'mRNA', 'polypeptide']`.

## Indexing the Data

The search system relies on a denormalized "materialized" index table to guarantee fast responses. After loading data into the Chado database, you must build the search index to make the new records searchable:

```bash
python manage.py rebuild_search_index
```

> **Note:** It is necessary to run `rebuild_search_index` whenever additional data is loaded into the database or when you wish to refresh the search facets.

Rebuilding the index queries the underlying database tables and batch-inserts the records into the search index. You can control the batch size to tune performance:

```bash
# Process 5,000 records at a time
python manage.py rebuild_search_index --batch-size 5000
```

### Resuming an interrupted rebuild

A full rebuild over millions of features takes hours. If it is interrupted,
re-run with `--resume` to continue from where it stopped:

```bash
python manage.py rebuild_search_index --resume
```

`--resume` skips features already present in the index and does not clear it.
It assumes `MACHADO_VALID_TYPES` has not changed since the interrupted run; if
you changed that setting, use `--restart` to rebuild from scratch.

| Flag | Effect |
|---|---|
| *(none)* | Clear the index and rebuild everything (default) |
| `--restart` | Same as the default, stated explicitly |
| `--resume` | Continue an interrupted run |
| `--batch-size N` | Features per chunk (default 2000) |
| `--max-features N` | Stop after N features, for benchmarking |

`search_vector` is a PostgreSQL generated column, so no separate tsvector
update step runs after indexing: it is maintained by the database itself and
must not be assigned directly.

## Search Features

The PostgreSQL search backend supports advanced search queries natively using "websearch" syntax:

* `gene kinase` — searches for documents containing both words
* `"receptor kinase"` — searches for the exact phrase
* `kinase -receptor` — searches for "kinase" but excludes documents containing "receptor"
* `kinase OR receptor` — searches for either word

All exported data (TSV or FASTA) from the search page is unlimited; PostgreSQL handles exporting the full result set regardless of its size.
