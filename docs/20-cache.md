# Cache

Rendered search pages are cached on disk and cleared automatically by
`rebuild_search_index`. There is nothing to enable and no cache to clear by
hand — the only setup is the cache directory and its permissions.

## Settings

`machado-startproject` writes these into `.env`, commented out. The defaults
work; uncomment only what you need to change.

| Variable | Default | Purpose |
|---|---|---|
| `CACHE_DIR` | `cache` beside `manage.py` | Where the cache files are written |
| `CACHE_MAX_ENTRIES` | `1000000` | Effectively no limit. Django's own default is 300, and every write past the limit deletes a third of the cache |
| `CACHE_TIMEOUT` | `3600` | How long the JBrowse API views stay cached, in seconds. Does not affect search pages, which are cleared by `rebuild_search_index` rather than by time |

## Directory permissions

The directory is written by Apache and cleared by `rebuild_search_index`, so
both need write access. If Django creates it, it will be mode `0700` and
owned by whichever of the two ran first — so create it explicitly:

```bash
sudo install -d -o www-data -g www-data -m 2775 /var/cache/machado
sudo usermod -aG www-data $USER   # so you can run rebuild_search_index too
```

Then set it in `.env`:

```
CACHE_DIR=/var/cache/machado
```

## Apache

Under mod_wsgi the application runs as the Apache user — `www-data` on
Debian/Ubuntu — unless `WSGIDaemonProcess` sets `user=`. That is the user
that must own the cache directory above. See [Web server](18-webserver.md).

A cache directory left inside the project tree (the default) will not be
writable by Apache if the project is owned by another user, so on a
production install set `CACHE_DIR` to a path outside it.
