# T-lang
WIP

Sample program below constructs 3-block 2-attention head transformer for reversing strings.

Features are 1-hot vectors superimposed in 192-dimensional space.


```python
def reverse(s: str) -> str:
    a = FeatureAllocator()
    A = a.alloc()
    MID = a.alloc(len(P))
    POS = a.alloc(len(P))
    BRO = a.alloc(len(E))
    EQ = a.alloc()
    GT = a.alloc()
    RESULT = a.alloc()
    C = a.alloc()
    code = [
        [
            [],
            [["NOT", [A], [A]]],
        ],
        [
            [
                [
                    # copy pos of $ into each token
                    ["QUERY", [A]],
                    ["KEY", [who("$")]],
                    ["VALUE", slice(a.POS, len(P))],
                    ["PROJ", slice(POS, len(P))],
                ],
                [
                    # copy pos of | into each token
                    ["QUERY", [A]],
                    ["KEY", [who("|")]],
                    ["VALUE", slice(a.POS, len(P))],
                    ["PROJ", slice(MID, len(P))],
                ],
            ],
            [
                *sub_one_hot(POS, a.POS, len(P)),  # sub |'s pos from curr pos to obtain opposite
                *gt_one_hot(a.POS, MID, len(P), GT),  # flag if to the right of |
            ],
        ],
        [
            [
                [
                    # copy the twin token embedding
                    ["QUERY", slice(POS, len(P))],
                    ["KEY", slice(a.POS, len(P))],
                    ["VALUE", slice(a.EMB, len(E))],
                    ["PROJ", slice(BRO, len(E))],
                ],
            ],
            [
                ["AND", [who("?"), GT], [RESULT]],
            ],
        ],
        [
            lambda m: "".join(un_E(u[BRO : BRO + len(E)]) for u in m if u[RESULT] == 1.0),
        ],
    ]
    return run(code, f"^{s}|{str('?' * len(s))}$")
```
