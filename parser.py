import sys
import traceback

from lang import FeatureAllocator
from model import P, E

LINE_NUM = 0


def parse(code: str) -> list[list]:
    try:
        lines = [s.strip(" \t") for s in code.split("\n")]
        parsed = []
        fa = FeatureAllocator()
        fs = {}
        while lines:
            match first(lines):
                case "Features:":
                    parse_features(lines, fa, fs)
                case "Block:":
                    parse_block(lines, parsed, fs)
                case "Unembed:":
                    parse_unembed(lines, parsed, fs)
                case _:
                    continue
        return parsed
    except Exception as e:
        traceback.print_exc()
        return fail(e)


def parse_features(lines: list[str], fa: FeatureAllocator, fs: dict):
    line = first(lines)
    while line:
        key, size = line.split(": ")
        r = len(P) if size == "number" else len(E) if size == "char" else 1
        fs[key] = fa.alloc(r)
        line = first(lines)


def parse_block(lines: list[str], parsed: list[list], fs: dict):
    line = first(lines)
    if line == "Attention:":
        print("parse attention heads")
    else:
        fail(f"unexpected '{line}'")
    line = first(lines)
    if line == "FeedForward:":
        print("parse ffn")
    else:
        fail(f"unexpected '{line}'")


def fail(e):
    print(f"{e} at line {LINE_NUM}", file=sys.stderr, flush=True)
    sys.exit(1)


def first(lines: list):
    global LINE_NUM
    LINE_NUM += 1
    return lines.pop(0)
