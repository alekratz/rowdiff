#!/usr/bin/env python3
import abc
import csv
from collections import defaultdict
import argparse
from typing import Sequence, Union, Optional, Mapping
import itertools as it


ANSI_RED = "\u001b[31m"
ANSI_GREEN = "\u001b[32m"
ANSI_RESET = "\u001b[0m"


class Diff:
    def __init__(self, line: Union[str, Sequence[str]], added: bool):
        self.line = line
        self.added = added

    def __str__(self):
        if self.added:
            s = ANSI_GREEN + "+ "
        else:
            s = ANSI_RED + "- "
        return s + str(self.line) + ANSI_RESET


class DiffCol:
    def __init__(self, col: str, diffs: Sequence[Diff]):
        self.col = col
        self.diffs = diffs

    def __str__(self) -> str:
        s = "= {} =".format(self.col).ljust(80, "=") + "\n"
        return s + "\n".join(map(str, self.diffs))

    def __bool__(self) -> bool:
        return bool(self.diffs)


class DiffColGroup:
    def __init__(self, col: str, group_name: str, groups: Mapping[str, Sequence[Diff]]):
        self.col = col
        self.group_name = group_name
        self.groups = groups

    def __str__(self) -> str:
        INDENT = 2
        lines = ["= {} =".format(self.col).ljust(80, "=")]
        for group, diffs in self.groups.items():
            if not diffs:
                continue
            lines += ["{} group {}".format(self.group_name, group)]
            lines += [" {}".format(diff) for diff in diffs]
        return "\n".join(lines)

    def __bool__(self) -> bool:
        return any(v for v in self.groups.values())


def column_diff(col1, col2):
    col1 = set(col1)
    col2 = set(col2)
    col2_missing = col1 - col2
    col1_missing = col2 - col1
    return [Diff(v, True) for v in col1_missing] + [
        Diff(v, False) for v in col2_missing
    ]


def flat_diff(cols, rows1, rows2):
    rows1 = aos_to_soa(rows1, cols)
    rows2 = aos_to_soa(rows2, cols)
    diff_cols = []
    for col in cols:
        diffs = column_diff(rows1[col], rows2[col])
        diff_cols += [DiffCol(col, diffs)]
    return diff_cols


def group_by_diff(cols, group_by, rows1, rows2):
    def getter(c):
        return c[group_by]

    rows1 = sorted(rows1, key=getter)
    rows2 = sorted(rows2, key=getter)

    groups1 = {k: aos_to_soa(v, cols) for k, v in it.groupby(rows1, key=getter)}
    groups2 = {k: aos_to_soa(v, cols) for k, v in it.groupby(rows2, key=getter)}
    groups1_keys = set(groups1.keys())
    groups2_keys = set(groups2.keys())

    common_groups = groups1_keys & groups2_keys
    diff_col_groups = []
    for col in cols:
        group_diffs = defaultdict(list)
        for group in common_groups:
            group_diffs[group] += column_diff(groups1[group][col], groups2[group][col])
        diff_col_groups += [DiffColGroup(col, group_by, dict(group_diffs))]

    return diff_col_groups


def aos_to_soa(array, keys=None):
    "Converts a list of structures to a structure of lists."
    if not array:
        return {}

    struct = defaultdict(list)
    array = list(array)
    if keys is None:
        keys = array[0].keys()
    keys = list(keys)
    for row in array:
        for key in keys:
            # grouped keys are broken up by a comma
            if "," in key:
                grouped_keys = key.split(",")
                struct[key] += [tuple(map(row.get, grouped_keys))]
            else:
                struct[key] += [row.get(key, None)]
    return dict(struct)


def main():
    parser = argparse.ArgumentParser("rowdiff")
    parser.add_argument(
        "DIFF_FILE",
        nargs=2,
        type=argparse.FileType("r"),
        help="a pair of CSV files to compare",
    )
    parser.add_argument(
        "-c",
        "--col",
        metavar="COL",
        default=[],
        action="append",
        dest="cols",
        help="a set of columns to find the difference of",
    )
    parser.add_argument(
        "-i",
        "--ignore",
        metavar="COL",
        default=[],
        action="append",
        dest="ignore",
        help="a set of columns to ignore when doing a diff",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        default=False,
        help="compares all columns, overriding any explicitly added columns",
    )
    parser.add_argument(
        "-g",
        "--group-by",
        metavar="column",
        dest="group_by",
        type=str,
        default=None,
        help="a column to group diff values by",
    )
    args = parser.parse_args()
    file1, file2 = args.DIFF_FILE
    rows1, rows2 = tuple(map(lambda fp: list(csv.DictReader(fp)), args.DIFF_FILE))
    if len(rows1) + len(rows2) == 0:
        print("Both sets are empty")
        return

    cols = set(args.cols)
    if args.all:
        cols |= set((rows1 or rows2)[0].keys())
    cols -= set(args.ignore)

    if args.group_by:
        col_diffs = group_by_diff(cols, args.group_by, rows1, rows2)
    else:
        col_diffs = flat_diff(cols, rows1, rows2)

    for col_diff in col_diffs:
        if col_diff:
            print(col_diff)


if __name__ == "__main__":
    main()
