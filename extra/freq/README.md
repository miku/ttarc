# TikTokVoc

Fetch top 1000 english nouns by frequency from tags endpoint.

* [https://www.tiktok.com/node/share/tag/frequency](https://www.tiktok.com/node/share/tag/frequency)

```
$ jq -rc '[.body.challengeData.posts, .body.challengeData.views, .body.challengeData.challengeName] | @tsv' \
     $HOME/.cache/ttfetchtag/20200424/* | column -t | sort -k2,2 -nr
...
5586252  55969054241  art
4241452  21044914816  army
3504589  17849893726  cat
4221658  16937328607  baby
1492482  15299673232  artist
699942   12249371774  basketball
948817   12069669853  act
1374938  11544963520  amazing
1133376  10860957744  boyfriend
1450227  10850729725  beauty
...
```
