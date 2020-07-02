# TikTok archiver (ttarc)

NOTE: As of 2020-04-23 5PM CET, the trending [endpoint](https://m.tiktok.com/node/share/trending) returns an empty list only. Hence, as is, this program does not fetch any data.

----

[![Go Report Card](https://goreportcard.com/badge/github.com/miku/ttarc)](https://goreportcard.com/report/github.com/miku/ttarc)

Inspiration: *tiktok-feed* by [CorentinB](https://github.com/CorentinB/).

Minimalistic TikTok archival tool using
[https://m.tiktok.com/node/share/trending](https://m.tiktok.com/node/share/trending).

Collects the trending JSON document and linked (mp4) video clips and puts them
into [WARC via
wget](https://www.archiveteam.org/index.php?title=Wget_with_WARC_output) (1.14
or higher).

![](static/pix.png)


## Install

```
$ go get github.com/miku/cmd/ttarc/...
```

> or use some [Linux packages](https://github.com/miku/ttarc/releases) (there's
> an [armhf](https://askubuntu.com/a/518182/5079) [version](https://github.com/miku/ttarc/releases/download/v0.1.1/ttarc_0.1.1_armhf.deb) for an SBC)

## Run

```
$ ttarc
$ ls -lah
...
ttarc-trending-20200312214721.cdx
ttarc-trending-20200312214721.warc
...
```

This can be put into cron, e.g. to be run every 15 minutes.

```cron
*/15 * * * * /usr/local/bin/ttarc -P /tmp/ttarc -log /tmp/ttarc/ttarc.log
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

## TODO

* [ ] broader scope
* [ ] optimal tile
* [ ] save user profiles, e.g. [anna](https://www.tiktok.com/node/share/user/@anna)
* [ ] the [discover](https://www.tiktok.com/node/share/discover) list
* [ ] cycle through top 5000 english words and make a [frequency](https://www.tiktok.com/node/share/tag/frequency) list
* [ ] video id, [6840824663585639686](https://www.tiktok.com/@lzz03/video/6840824663585639686)

## Stills

[Extracted](extra/videostills.py) via
[warcio](https://github.com/webrecorder/warcio),
[ffmpeg](https://www.ffmpeg.org/) and [imagemagick](https://imagemagick.org/).

![](static/output10.png)

