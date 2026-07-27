# JBrowse (optional)

The [JBrowse](https://jbrowse.org) software renders genomic tracks from Chado using the machado API.

## Installing JBrowse

Before installing JBrowse you should probably have BioPerl installed in your system (tested in Ubuntu 20.04):

```bash
sudo apt install bioperl
```

Then install JBrowse following the [official instructions](https://jbrowse.org/docs/installation.html).

In Ubuntu 20.04, install some prerequisites:

```bash
sudo apt install build-essential zlib1g-dev curl
```

Also Node.js is needed:

```bash
curl -sL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

Finally, proceed with JBrowse installation:

```bash
wget https://github.com/GMOD/jbrowse/releases/download/1.16.12-release/JBrowse-1.16.12.zip
unzip JBrowse-1.16.12.zip
sudo mv JBrowse-1.16.12 /var/www/html/jbrowse
cd /var/www/html
sudo chown `whoami` jbrowse
cd jbrowse
./setup.sh  # don't do sudo ./setup.sh
```

## Configuring JBrowse

The machado source contains the directory `extras`. Copy the file `extras/trackList.json.sample` to the JBrowse data directory, inside a subdirectory with the name of the organism (e.g. `/var/www/html/jbrowse/data/Arabidopsis thaliana`) and rename it to `trackList.json`. This directory structure will enable machado to embed JBrowse in its pages.

```bash
mkdir -p "/var/www/html/jbrowse/data/Arabidopsis thaliana"
cp extras/trackList.json.sample "/var/www/html/jbrowse/data/Arabidopsis thaliana/trackList.json"
```

Edit the file `trackList.json` to set the **organism** name you have loaded to the database.

**In case you have WSGI apache module configured and running**, change the `baseUrl` variable in `trackList.json` to refer to the proper address:

```
"baseUrl": "http://localhost/MYGENOME/api/jbrowse"
```

- Repeat the steps above for as many other organisms as you may have loaded to the database.
- Remember to restart the Apache server after the modifications.

## machado API

**In case you don't have the WSGI module installed under Apache** (and did not change the `baseUrl` variable in `trackList.json`), start the machado API framework:

```bash
python manage.py runserver
```

Once the server is running, go to your browser and open your JBrowse instance (e.g. `http://localhost/jbrowse/?data=data/Arabidopsis%20thaliana`).

## machado Settings

The `settings.py` file should contain these variables in order to have the JBrowse visualization embedded in the feature page. Don't forget to restart Apache to make the settings changes up to date.

```python
MACHADO_JBROWSE_URL = 'http://localhost/jbrowse'
MACHADO_JBROWSE_TRACKS = 'ref_seq,gene,transcripts,CDS,SNV'
MACHADO_JBROWSE_OFFSET = 1200
```

- `MACHADO_JBROWSE_URL` — the base URL to the JBrowse installation. The URL must contain the protocol (i.e. `http` or `https`).
- `MACHADO_JBROWSE_TRACKS` — the name of the tracks to be displayed (`ref_seq,gene,transcripts,CDS,SNV` if not set).
- `MACHADO_JBROWSE_OFFSET` — the number of bp upstream and downstream of the feature (1000 if not set).

## Use Reference from FASTA File (optional)

If the reference sequences are really long (>200 Mbp), there may be memory issues during the loading process and JBrowse may take too long to render the tracks. To avoid this, follow instructions to create and use an indexed FASTA file as source for the reference sequences — see the [JBrowse tutorial](https://jbrowse.org/docs/tutorial.html).

Follow the steps below.

Put the genome's assembly FASTA file into your JBrowse organism's `data/seq` directory (for example: `/var/www/html/jbrowse/data/Glycine max/data/seq/Gmax.fa`), change to this directory, and run:

```bash
samtools faidx Gmax.fa
```

A `Gmax.fa.fai` indexed FASTA file will be created.

Now, modify your default `trackList.json` file. You need to make two modifications — first replace the `refSeqs` entry line (probably the second line of the file) with:

```json
"refSeqs" : "data/seq/Gmax.fa.fai",
```

And then change the reference sequence track code chunk:

```json
{
    "category" : "1. Reference sequence",
    "faiUrlTemplate" : "data/seq/Gmax.fa.fai",
    "key" : "Reference sequence",
    "label" : "ref_seq",
    "seqType" : "dna",
    "storeClass" : "JBrowse/Store/SeqFeature/IndexedFasta",
    "type" : "SequenceTrack",
    "urlTemplate" : "data/seq/Gmax.fa",
    "useAsRefSeqStore" : 1
}
```

- The code above should replace all code from the "1. Reference sequence" category track code chunk.
- Make sure `urlTemplate` points to the FASTA file path, not the `.fai` indexed one.

Now restart the Apache daemon for changes to take effect:

```bash
systemctl restart apache2
```
