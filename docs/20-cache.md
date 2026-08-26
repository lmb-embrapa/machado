# Cache

Two different things are cached, on two different schedules.

| What | Expires | Invalidated by |
|---|---|---|
| The search page (`/find/`) | never | `rebuild_search_index` |
| The JBrowse API views | after `CACHE_TIMEOUT` (1 hour by default) | time only |

The search page is cached because it is expensive to assemble: eleven facet
aggregates over a multi-million-row index. On a 7.5M-feature corpus it takes
about 4.2s to build and 0.013s to serve from cache.

It never expires on its own because it does not need to. The corpus is
read-only between index rebuilds, so a rendered page stays correct until the
index changes — and `rebuild_search_index` clears the cache itself, both when
it starts (the old index is being replaced) and when it finishes.

## You must configure a shared cache backend

This is the one part that is not optional.

Django's default is `LocMemCache`, which is **per-process**.
`rebuild_search_index` runs in a different process from the web workers, so
with `LocMemCache` its `cache.clear()` cannot reach what they have cached.
Because search pages never expire on their own, the result is that **stale
search results are served indefinitely** after loading new data — until the
web server is restarted.

`LocMemCache` also holds only 300 entries by default and starts from empty in
every worker, so it caches far less than you would expect.

## Recommended configuration

`FileBasedCache` needs no extra server and is the only built-in backend that
compresses what it stores. These pages compress about 130× — a 1.8MB search
page occupies roughly 36KB on disk.

Add to `settings.py`:

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/var/cache/machado",
        "TIMEOUT": None,          # search pages are invalidated by events, not time
        "OPTIONS": {"MAX_ENTRIES": 1000000},
    }
}
```

### `MAX_ENTRIES` is not optional either

Leaving it out does not mean "no limit" — it means **300**, and every write
past that deletes a third of the cache. Set it high enough that it never
triggers in practice.

### Directory permissions

The cache directory is written by the web server and cleared by
`rebuild_search_index`. If those run as different users, clearing fails with
a permission error. Either run the command as the web server's user, or give
both a shared group with group-write on the directory:

```bash
sudo install -d -o www-data -g machado -m 2775 /var/cache/machado
```

Django creates the directory mode `0700` if it does not exist, which is
owner-only — so create it yourself if two users need it.

## Alternative: `DatabaseCache`

Also serverless, and immune to the permission problem above because both
processes reach it through the database. The tradeoff is size: it
base64-encodes what it stores instead of compressing, so the same 1.8MB page
becomes about 2.4MB rather than 36KB — roughly 150× more storage for
identical content.

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "machado_cache_table",
        "TIMEOUT": None,
        "OPTIONS": {"MAX_ENTRIES": 50000},
    }
}
```

```bash
python manage.py createcachetable
```

Note this writes to the database, so it is incompatible with making the
database read-only after going live.

## Clearing the cache manually

`rebuild_search_index` already clears it, so this is only needed after
changing templates, settings, or anything else the cache cannot know about:

```bash
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

## What the search page cache is keyed on

The URL path, the query string, and whether the visitor is logged in.

Anonymous visitors and authenticated users never share an entry: an
anonymous visitor has private organisms filtered out of results and facet
counts, so serving one audience the other's page would disclose data.
Nothing finer is needed — visibility depends on being logged in, never on
*which* user, so all authenticated users share a single entry.

Query strings are normalised, so ticking the same facets in a different
order reuses one entry rather than storing several copies of the same page.

Only `GET` requests and only successful (200) responses are stored, so an
error page is never served to everyone until the next rebuild.

The export endpoint (`/export/`) is deliberately not cached: it is
unpaginated, so a single response can be the entire result set.
