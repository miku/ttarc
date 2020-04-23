SHELL := /bin/bash

output.png: stills
	montage -geometry +0+0 -tile 8x $$(identify stills-* | grep "720x1280" | awk '{print $$1}' | head -64) $@
	convert -resize 10\% output.png output10.png

.PHONY: stills
stills:
	# Extract single frame image from embedded videos.
	python videostills.py --prefix stills- $$(find . -name "*warc.gz" -or -name "*warc")

.PHONY: clean
clean:
	rm -f stills-*jpg
	rm -f clean
	rm -f output*.png
