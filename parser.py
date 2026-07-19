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
            line = first(lines)
            print(f"'{line}'")
            match line:
                case "Features:":
                    parse_features(lines, fa, fs)
                case "Block:":
                    parsed.append(parse_block(lines, fs))
                case "Unembed:":
                    parsed.append(parse_unembed(lines, fs))
                case _:
                    continue
            print(parsed)
            print("---")
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
        if lines[0] == "":
            break
        line = first(lines)


def parse_block(lines: list[str], fs: dict) -> list:
    parsed = []
    line = first(lines)
    if line == "Attention:":
        parsed.append(parse_attention(lines, fs))
    else:
        fail(f"unexpected '{line}'")
    line = first(lines)
    if line == "FeedForward:":
        parsed.append(parse_feedforward(lines, fs))
    else:
        fail(f"unexpected '{line}'")
    return parsed


def parse_attention(lines: list[str], fs: dict):
    line = first(lines)
    if line == "- Head:":
        q = first(lines).split()
        k = first(lines).split()
        v = first(lines).split()
        p = first(lines).split()
        match [q, k, v, p]:
            case [["Query:", q], ["Key:", k], ["Value:", v], ["Proj:", p]]:
                return [
                    ["QUERY", [q]],
                    ["KEY", [k]],
                    ["VALUE", [v]],
                    ["PROJ", [p]],
                ]


def parse_feedforward(lines: list[str], fs: dict):
    parsed = []
    line = first(lines)
    while line.startswith("-"):
        parsed.append(["AND", [], []])
        line = first(lines)
    return parsed


def parse_unembed(lines: list[str], fs: dict):
    parsed = []
    line = first(lines)
    while line:
        [k, v] = line.split(": ")
        match k:
            case "Char":
                parsed.append(["CHAR", fs[k]]) use fa
            case "Tokens":
                parsed.append(v)
        line = first(lines)
    return parsed


def resolve(fa: FeatureAllocator, f: str, fs: dict):
    match f:
        case "token.ANY":
            return fa.ANY
        case "token.pos":
            return fa.POS
        case "token.emb":
            return fa.EMB
        case k if fs.get(k):
            return fs[k]
        case _:
            fail(f"unknown feature '{f}")


def fail(e):
    print(f"{e} at line {LINE_NUM}", file=sys.stderr, flush=True)
    sys.exit(1)


def first(lines: list) -> str:
    global LINE_NUM
    LINE_NUM += 1
    return lines.pop(0)
