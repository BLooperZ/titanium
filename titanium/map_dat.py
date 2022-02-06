#!/usr/bin/env python3

import binascii
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract data from Compedia games.')
    parser.add_argument('fname', help='data file to extract')

    args = parser.parse_args()

    with open(args.fname, 'rb') as f:
        start_header = f.read(21)
        size = ord(f.read(1))
        rest_header = f.read(6)
        print(binascii.hexlify(start_header, sep=' '), size, binascii.hexlify(rest_header, sep=' '))


        for i in range(size):
            ln = int.from_bytes(f.read(2), byteorder='big', signed=False)
            fname = f.read(ln)
            padding = f.read(49 - ln)
            assert set(padding) == {0}, padding
            print(i, ln, fname)

        sep = f.read(1)
        print('SEP', sep)

        maybe_type = ord(f.read(1))
        assert maybe_type == 7
        num_pcx = int.from_bytes(f.read(2), byteorder='little', signed=False)
        rest = f.read(6)

        print('\nINBETWEEN', maybe_type, num_pcx, binascii.hexlify(rest, sep=' '), '\n')

        pos = f.tell()

        for i in range(num_pcx):
            ln = ord(f.read(1))
            fname = f.read(ln)
            padding = f.read(58 - ln)
            print(i, ln, fname, binascii.hexlify(padding, sep=' '))
            assert fname.endswith(b'.pcx')

        print('DIFF POS', f.tell() - pos)

        maybe_type = ord(f.read(1))
        assert maybe_type == 1
        num_flc = int.from_bytes(f.read(2), byteorder='little', signed=False)
        rest = f.read(6)
        print('\nINBETWEEN', maybe_type, num_flc, binascii.hexlify(rest, sep=' '), '\n')

        for i in range(num_flc):
            ln = ord(f.read(1))
            fname = f.read(ln)
            padding = f.read(49 - ln)
            print(i, ln, fname, binascii.hexlify(padding, sep=' '))
            assert fname.endswith(b'.flc')

        maybe_type = ord(f.read(1))
        assert maybe_type == 3
        num_voc = int.from_bytes(f.read(2), byteorder='little', signed=False)
        rest = f.read(6)
        print('\nINBETWEEN', maybe_type, num_voc, binascii.hexlify(rest, sep=' '), '\n')
        for i in range(num_voc):
            ln = ord(f.read(1))
            fname = f.read(ln)
            padding = f.read(40 - ln)
            print(i, ln, fname, binascii.hexlify(padding, sep=' '))
            assert fname.endswith(b'.voc')


        # print(f.read())
