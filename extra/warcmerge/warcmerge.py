#!/usr/bin/env python3
"""
Concatenate many small WARC files into fewer, larger ones (default: ~1GB).

WARC files are sequences of records, and wget writes gzipped WARCs with one
gzip member per record, so plain byte concatenation yields a valid WARC file.
Input files are never split; a new output file is started once adding the next
input would exceed the target size.

    $ python warcmerge.py data/ttarc
    $ python warcmerge.py -p '*.warc.gz' -s 1G -o /tmp/merged data/ttarc

Gzipped inputs are checked first: a truncated file (e.g. from an interrupted
crawl) would corrupt everything after it in the output, so only its complete
records are copied and the partial record at the end is dropped. Files with no
complete record are skipped.

Next to the WARC files, a manifest.tsv (output, input, bytes copied, input
size) is written to the output directory. Only the Python standard library is
used.
"""

import argparse
import os
import pathlib
import re
import sys
import zlib

BUFSIZE = 16 * 1024 * 1024
CHECK_BUFSIZE = 1024 * 1024


def parse_size(s):
    """Parse a human readable size like 1G, 500M, 1073741824 into bytes."""
    m = re.fullmatch(r"(?i)\s*(\d+(?:\.\d+)?)\s*([kmgt]?)i?b?\s*", s)
    if not m:
        raise argparse.ArgumentTypeError("invalid size: {}".format(s))
    num, unit = m.groups()
    exp = {"": 0, "k": 1, "m": 2, "g": 3, "t": 4}[unit.lower()]
    return int(float(num) * 1024**exp)


def warc_suffix(path):
    name = path.name
    if name.endswith(".warc.gz"):
        return ".warc.gz"
    if name.endswith(".warc"):
        return ".warc"
    return None


def valid_gzip_length(path):
    """Return the number of bytes at the start of path that consist of
    complete gzip members. For an intact file this is the file size; for a
    truncated file (e.g. an interrupted crawl) it is the offset just after the
    last complete record."""
    offset, consumed = 0, 0
    d = zlib.decompressobj(31)
    with open(path, "rb") as f:
        while True:
            chunk = f.read(CHECK_BUFSIZE)
            if not chunk:
                break
            while chunk:
                try:
                    d.decompress(chunk)
                except zlib.error:
                    return offset
                if d.eof:
                    rest = d.unused_data
                    offset += consumed + len(chunk) - len(rest)
                    consumed, chunk = 0, rest
                    d = zlib.decompressobj(31)
                else:
                    consumed += len(chunk)
                    chunk = b""
    return offset


def copy_n(src, dst, n):
    """Copy exactly n bytes from src to dst."""
    while n > 0:
        buf = src.read(min(BUFSIZE, n))
        if not buf:
            raise IOError("unexpected end of file: {}".format(src.name))
        dst.write(buf)
        n -= len(buf)


def plan_batches(files, max_size):
    """Group (path, length) pairs (in order) into batches not exceeding
    max_size bytes; a single file larger than max_size gets its own batch."""
    batches, current, current_size = [], [], 0
    for f, size in files:
        if current and current_size + size > max_size:
            batches.append(current)
            current, current_size = [], 0
        current.append((f, size))
        current_size += size
    if current:
        batches.append(current)
    return batches


def main():
    parser = argparse.ArgumentParser(
        description="Concatenate WARC files into larger WARC files.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("dir", type=pathlib.Path, help="directory containing WARC files")
    parser.add_argument("-p", "--pattern", default="*.warc.gz", help="glob pattern for input files")
    parser.add_argument("-r", "--recursive", action="store_true", help="search for files recursively")
    parser.add_argument("-o", "--output-dir", type=pathlib.Path, default=pathlib.Path("warcmerge-output"),
                        help="output directory, will be created if necessary")
    parser.add_argument("-s", "--size", type=parse_size, default=parse_size("1G"),
                        help="target maximum size per output file, e.g. 500M, 1G")
    parser.add_argument("--prefix", default="ttarc-merged", help="output filename prefix")
    parser.add_argument("-n", "--dry-run", action="store_true", help="only print what would be done")
    parser.add_argument("-f", "--force", action="store_true", help="overwrite existing output files")
    parser.add_argument("--no-check", action="store_true",
                        help="do not check gzip integrity of inputs (faster, but truncated inputs corrupt the output)")
    args = parser.parse_args()

    if not args.dir.is_dir():
        parser.error("not a directory: {}".format(args.dir))

    output_dir = args.output_dir.resolve()
    glob = args.dir.rglob if args.recursive else args.dir.glob
    files = sorted(
        (p for p in glob(args.pattern) if p.is_file() and output_dir not in p.resolve().parents),
        key=lambda p: (p.name, str(p)),
    )
    if not files:
        print("no files matching {} in {}".format(args.pattern, args.dir), file=sys.stderr)
        sys.exit(1)

    # Mixing compressed and uncompressed WARCs in one file would be invalid.
    suffixes = {warc_suffix(p) for p in files}
    if None in suffixes:
        bad = [str(p) for p in files if warc_suffix(p) is None][:5]
        parser.error("files do not end in .warc or .warc.gz: {}".format(", ".join(bad)))
    if len(suffixes) > 1:
        parser.error("found both .warc and .warc.gz files, use --pattern to select one kind")
    suffix = suffixes.pop()

    # Determine how many bytes of each file to copy.
    sized = []
    for i, p in enumerate(files, 1):
        size = p.stat().st_size
        if suffix == ".warc.gz" and not args.no_check:
            print("checking [{}/{}] {}".format(i, len(files), p), file=sys.stderr, end="\r")
            valid = valid_gzip_length(p)
            if valid == 0:
                print("\nskipping, no complete record: {}".format(p), file=sys.stderr)
                continue
            if valid < size:
                print("\ntruncated, using first {} of {} bytes: {}".format(valid, size, p), file=sys.stderr)
            size = valid
        sized.append((p, size))
    if suffix == ".warc.gz" and not args.no_check:
        print(file=sys.stderr)
    if not sized:
        print("no usable input files", file=sys.stderr)
        sys.exit(1)

    batches = plan_batches(sized, args.size)
    width = max(5, len(str(len(batches))))
    names = ["{}-{:0{}d}{}".format(args.prefix, i, width, suffix) for i in range(len(batches))]

    total = sum(size for _, size in sized)
    print("{} files, {:.1f} MB -> {} output file(s) in {}".format(
        len(sized), total / 1024**2, len(batches), output_dir), file=sys.stderr)

    if args.dry_run:
        for name, batch in zip(names, batches):
            size = sum(size for _, size in batch)
            print("{}\t{} files\t{:.1f} MB".format(name, len(batch), size / 1024**2))
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = output_dir / "manifest.tsv"
    if not args.force:
        existing = [n for n in names + [manifest.name] if (output_dir / n).exists()]
        if existing:
            parser.error("output exists (use --force to overwrite): {}".format(", ".join(existing[:5])))

    with open(manifest, "w") as mf:
        for name, batch in zip(names, batches):
            target = output_dir / name
            tmp = target.with_name(target.name + ".tmp")
            with open(tmp, "wb") as dst:
                for p, size in batch:
                    with open(p, "rb") as src:
                        copy_n(src, dst, size)
                dst.flush()
                os.fsync(dst.fileno())
            os.replace(tmp, target)
            for p, size in batch:
                mf.write("{}\t{}\t{}\t{}\n".format(name, p, size, p.stat().st_size))
            mf.flush()
            print("{}\t{} files\t{:.1f} MB".format(
                target, len(batch), target.stat().st_size / 1024**2), file=sys.stderr)


if __name__ == "__main__":
    main()
