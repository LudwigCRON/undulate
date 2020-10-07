#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import stat


def exist_and_bloc(path):
    return os.path.exists(path) and stat.S_ISBLK(os.stat(path).st_mode)


def exist_and_character(path):
    return os.path.exists(path) and stat.S_ISCHR(os.stat(path).st_mode)


def exist_and_dir(path):
    return os.path.exists(path) and os.path.isdir(path)


def exist(path):
    return os.path.exists(path)


def exist_and_file(path):
    return os.path.exists(path) and os.path.isfile(path)


def exist_and_link(path):
    return os.path.exists(path) and os.path.islink(path)


def exist_and_readable(path):
    return os.path.exists(path) and os.access(path, os.R_OK)


def exist_and_nonzero(path):
    return os.path.exists(path) and os.path.getsize(path) > 0


def exist_and_writable(path):
    return os.path.exists(path) and os.access(path, os.W_OK)


def exist_and_executable(path):
    return os.path.exists(path) and os.access(path, os.X_OK)


def int_eq(a, b):
    return int(a, 10) == int(b, 10)


def int_ge(a, b):
    return int(a, 10) >= int(b, 10)


def int_gt(a, b):
    return int(a, 10) > int(b, 10)


def int_le(a, b):
    return int(a, 10) <= int(b, 10)


def int_lt(a, b):
    return int(a, 10) < int(b, 10)


def int_ne(a, b):
    return int(a, 10) != int(b, 10)


mapping_single_table = {
    "-b": exist_and_bloc,
    "-c": exist_and_character,
    "-d": exist_and_dir,
    "-e": exist,
    "-f": exist_and_file,
    "-h": exist_and_link,
    "-L": exist_and_link,
    "-r": exist_and_readable,
    "-s": exist_and_nonzero,
    "-w": exist_and_writable,
    "-x": exist_and_executable,
}

mapping_double_table = {
    "-eq": int_eq,
    "-ge": int_ge,
    "-gt": int_gt,
    "-le": int_le,
    "-lt": int_lt,
    "-ne": int_ne,
}


def interpolate_next(it):
    tmp = next(it)
    if "$" not in tmp:
        return tmp
    start = tmp.find("$")
    end = tmp.find(" ", start)
    interp = os.getenv(tmp[start:end] if end > 0 else tmp[start:])
    return "%s%s%s" % (tmp[:start], interp, tmp[end:])


def parse():
    ans = False
    it = iter(sys.argv)
    _ = next(it)
    args = [interpolate_next(it), interpolate_next(it)]
    if args[0] in mapping_single_table.keys():
        ans = mapping_single_table[args[-1]](args[-1])
    elif args[1] in mapping_double_table.keys():
        args.append(interpolate_next(it))
        ans = mapping_double_table[args[1]](args[0], args[-1])
    if not ans:
        print("False")
        exit(2)
    print("True")
    exit(0)


if __name__ == "__main__":
    try:
        parse()
    except ValueError:
        print("ERROR: expect an INTEGER and received a STRING", file=sys.stderr)
    except StopIteration:
        print("ERROR: missing arguments", file=sys.stderr)