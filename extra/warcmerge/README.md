# warcmerge

Concatenate the many small WARC files written by ttarc (wget) into fewer,
larger ones (default: ~1GB), e.g. for upload to archive.org. Only needs
Python 3 and its standard library.

wget gzips every WARC record as a separate gzip member, so byte-level
concatenation produces a valid WARC file. Input files are never split, and they
are processed in filename order, which for ttarc means chronological order.

```
$ python3 warcmerge.py -n data/ttarc                      # dry run, show plan
$ python3 warcmerge.py -o /data/merged data/ttarc         # 1G files, *.warc.gz
$ python3 warcmerge.py -r -s 500M -p '*.warc.gz' -o /data/merged /data/ttarc
```

Output files are named `ttarc-merged-00000.warc.gz` and so on (change the
prefix with `--prefix`). A `manifest.tsv` in the output directory lists
output file, input file, bytes copied and input size for each input.

Notes:

* Gzipped inputs are checked before merging. A truncated file (e.g. from an
  interrupted crawl) would corrupt every record after it in the output, so
  only its complete records are copied. Use `--no-check` to skip the check.
* Each input starts with its own `warcinfo` record, so the merged files
  contain several `warcinfo` records. The WARC format allows this.
* The `.cdx` files from wget are not merged, because their offsets no longer
  match. Build new indexes from the merged files if you need them.
