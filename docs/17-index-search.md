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

Rebuilding also clears the page cache, which is what makes newly loaded data
visible on the search page. See
[Page cache](01-installation.md#page-cache) for its one requirement, a
writable cache directory.

Rebuilding the index walks the features in chunks: for each chunk it issues a
fixed, small number of queries for all the related data the chunk needs, then
bulk-inserts that chunk's rows. `--batch-size` sets the size of that chunk, so
it controls both how many rows are inserted at once *and* how many features
each prefetch query covers — every `IN` list in the prefetch grows with it.

The default of 2000 is a deliberate compromise: larger chunks mean fewer
round-trips but bigger `IN` lists and more memory held per chunk, so raise it
only if you have measured a benefit on your data.

```bash
# Smaller chunks: more round-trips, less memory per chunk
python manage.py rebuild_search_index --batch-size 500
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

In the web interface, the "Resume interrupted run" checkbox on the Rebuild
Search Index form is the on/off switch for this same behaviour: leaving it
unchecked is the `--restart` behaviour (the default), and checking it is
`--resume`.

> **`--resume` is additive only.** It indexes only features whose `feature_id`
> is **above the highest `feature_id` already in the index**. That makes it the
> right tool for continuing an interrupted run, and the wrong tool for
> everything else:
>
> * It will **not** refresh data attached to features that are already indexed.
>   Loaders such as `load_similarity`, `load_feature_annotation`,
>   `load_orthomcl` and either `load_coexpression_*` command attach new data
>   to *pre-existing* features, whose `feature_id`s are below the watermark;
>   `--resume` skips them and their index rows stay stale. Use `--restart`
>   after any such load.
> * It will **not** remove index rows for features that have since been deleted
>   or marked obsolete. Only `--restart` clears those.
>
> The web form's warning text covers only the first, more common failure
> mode; this page is the canonical, complete reference for both.

| Flag | Effect |
|---|---|
| *(none)* | Clear the index and rebuild everything (default) |
| `--restart` | Same as the default, stated explicitly |
| `--resume` | Continue an interrupted run (additive only, see above) |
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
