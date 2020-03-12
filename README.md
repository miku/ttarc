# TikTok archiver (ttarc)

Inspiration: *tiktok-feed* by [CorentinB](https://github.com/CorentinB/).

Minimalistic TikTok archival tool using
[https://m.tiktok.com/node/share/trending](https://m.tiktok.com/node/share/trending).

Collects the trending JSON document and linked (mp4) video clips and puts the
into [WARC via
wget](https://www.archiveteam.org/index.php?title=Wget_with_WARC_output) (1.14
or higher).

```
$ ttarc
$ ls -lah
...
ttarc-trending-20200312214721.cdx
ttarc-trending-20200312214721.warc
...
```

This can be put into cron, e.g. to be run every 5 minutes - which would
accumulate 5GB per day, or 150GB per month or video content.

```cron
*/5 * * * * /usr/local/bin/ttarc -P /tmp/ttarc -log /tmp/ttarc/ttarc.log
```

## Usage

```
Usage of ttarc:
  -P string
        output directory (default ".")
  -b    ignore wget errors, just log them
  -f string
        basename for warc file (default "ttarc-trending-20200312224313")
  -log string
        log to stdout, if empty
  -ua string
        user agent (default "Mozilla/5.0 (Windows NT 10.0; ... )
  -verbose
        be verbose
  -version
        show version and exit
```
