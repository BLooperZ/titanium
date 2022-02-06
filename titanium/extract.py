#!/usr/bin/env python3

import io
import os
import pathlib
import argparse

from struct import Struct
from typing import IO, Iterator, Tuple

UINT32LE = Struct('<I')

def read_file_header(stream: IO[bytes]) -> Tuple[bytes, int, int]:
    header_size = ord(stream.read(1))
    header = stream.read(header_size - 1)
    fat_offset = UINT32LE.unpack(header[-4:])[0]

    stream.seek(fat_offset, io.SEEK_SET)
    return header, header_size, fat_offset


def read_file_table(stream: IO[bytes]) -> Iterator[bytes]:
    while True:
        size_bytes = stream.read(1)
        if not size_bytes:
            break

        size = ord(size_bytes)
        yield stream.read(size - 1)


def read_file_entry(entry: bytes):
    start = entry[:3]
    assert set(start) == {0}, start
    offset = UINT32LE.unpack(entry[3:7])[0]
    offset2 = UINT32LE.unpack(entry[7:11])[0]
    assert offset == offset2, (offset, offset2)
    fsize = UINT32LE.unpack(entry[11:15])[0]
    unk1 = UINT32LE.unpack(entry[15:19])[0]
    unk2 = UINT32LE.unpack(entry[19:23])[0]
    fname, fdir, empty = entry[23:].split(b'\0')
    fname = fname.decode('ascii')
    fdir = fdir.decode('ascii')
    assert empty == b''
    return (offset, fsize, unk1, unk2, fname, fdir)


def extract_all(stream: IO[bytes]) -> None:
    _header, header_size, fat_offset = read_file_header(stream)
    stream.seek(fat_offset, io.SEEK_SET)
    files = [read_file_entry(entry) for entry in read_file_table(stream)]

    stream.seek(header_size, io.SEEK_SET)
    for offset, size, unk1, unk2, fname, fdir in files:
        if stream.tell() != offset:
            print('WARNING: UNUSED DATA from {offset} of size {size}'.format(offset=stream.tell(), size=offset - stream.tell()))
            stream.seek(offset, io.SEEK_SET)
            exit(1)
        print(offset, size, unk1, unk2, fname, fdir)

        fdir = pathlib.Path(fdir.replace(':', '_'))
        assert fdir.relative_to('.'), fdir
        yield offset, unk1, unk2, fname, fdir, stream.read(size)

    assert stream.tell() == fat_offset, (stream.tell(), fat_offset)
    return files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract data from Compedia games.')
    parser.add_argument('fname', help='data file to extract')

    args = parser.parse_args()

    with open(args.fname, 'rb') as data_file:
        num_files = 0
        for offset, unk1, unk2, fname, fdir, content in extract_all(data_file):
            os.makedirs(fdir, exist_ok=True)
            with open(fdir / fname, 'wb') as out:
                out.write(content)
            num_files += 1
        print('Extracted {num} files'.format(num=num_files))
