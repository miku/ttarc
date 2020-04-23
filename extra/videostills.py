# Take a list of WARC files, containing video/mp4 content, extract one image from each.
import argparse
import base64
import hashlib
import tempfile
import os
import sys

from warcio.archiveiterator import ArchiveIterator

from gluish.utils import shellout

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("f", nargs="*", metavar="FILE", help="files")
    parser.add_argument("-p", "--prefix", default="stills-")
    args = parser.parse_args()

    # Note the seen payload digests.
    seen = set()

    for fn in args.f:
        with open(fn, "rb") as stream:
            for record in ArchiveIterator(stream):
                if record.rec_type != "response":
                    continue
                rh = record.rec_headers
                hh = record.http_headers
                if hh.get("Content-Type") not in ("video/mp4",):
                    continue

                payload_digest = rh.get("WARC-Payload-Digest")
                if not payload_digest:
                    continue

                hv = payload_digest.split(':')[1]
                if hv in seen:
                    continue
                seen.add(hv)

                with tempfile.NamedTemporaryFile(delete=False) as tf:
                    data = record.raw_stream.read()
                    tf.write(data)

                dst = "{}{}.jpg".format(args.prefix, hv)
                if os.path.exists(dst):
                    continue
                # Generate a still.
                # ffmpeg -ss 1 -i  -t 00:04 Linus-Torvalds-Nvidia_%03d.png
                output = shellout(""" ffmpeg -hide_banner -loglevel panic -y -ss 1 -i {video} -vframes 1 -f image2 {output} """, video=tf.name)
                # output = shellout(""" ffmpeg -hide_banner -loglevel panic -y -ss 1 -i {video} -vframes 1 -s 480x300 -f image2 {output} """, video=tf.name)
                os.rename(output, dst)
                os.remove(tf.name) # remove extracted video

                # sha1 = hashlib.sha1(data)
                # print(
                #     "{}\tsha1:{}".format(
                #         rh.get("WARC-Payload-Digest"),
                #         base64.b32encode(sha1.digest()).decode("utf-8"),
                #     )
                # )
                # print(record.rec_headers.get_header('WARC-Target-URI')[:50] + "...")
                # for attr in ['content_stream', 'content_type', 'digest_checker', 'format', 'http_headers', 'length', 'payload_length', 'raw_stream', 'rec_headers', 'rec_type']:
                #     print(attr, '=>', getattr(record, attr))
