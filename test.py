from lang import *


def is_palindrome(s: str) -> bool:
    a = FeatureAllocator()
    S = a.alloc()
    POS = a.alloc(len(P))
    ID = a.alloc(len(E))
    CMP = a.alloc()
    RESULT = a.alloc()
    code = [
        [
            [
                [
                    ["QUERY", [a.ANY]],  # Q = [1]
                    ["KEY", [who("$")]],  # K = [1] if end-of-str token
                    ["VALUE", slice(a.POS, len(P))],  # if match, then copy pos
                    ["PROJ", slice(POS, len(P))],  # project into POS subspace
                ],
            ],
            [
                ["NOR", [who("^"), who("$")], [S]],  # mark non-special tokens
                *sub_one_hot(POS, a.POS, len(P)),  # subtract actual pos from mirrored
            ],
        ],
        [
            [
                [
                    ["QUERY", slice(POS, len(P))],  # looking for mirrored pos
                    ["KEY", slice(a.POS, len(P))],  # ... in each tokens actual pos
                    ["VALUE", slice(a.EMB, len(E))],  # copy matching token's identity
                    ["PROJ", slice(ID, len(E))],  # into ID
                ]
            ],
            [
                *neq_one_hot(a.EMB, ID, len(E), CMP),  # compare one-hot into CMP
            ],
        ],
        [
            [
                [
                    ["QUERY", [who("^")]],  # Q = 1 for ^, 0 else
                    ["KEY", [S]],  # K = non-special tokens, ie broadcast
                    ["VALUE", [CMP]],  # aggregate 1 if non-match, else 0
                    ["PROJ", [RESULT]],  #  OR them into 42nd, 0 of palindrome, 1 if not
                ],
            ],
            [
                ["NOT", [RESULT], [RESULT]],
            ],
        ],
        [
            lambda m: m[0][RESULT],
        ],
    ]
    return run(code, f"^{s}$") == 1.0


# def count_letter(s: str, c: str) -> int:
#     a = FeatureAllocator()
#     POS = a.alloc(len(P))
#     code = [
#         [
#             [
#                 [
#                     ["QUERY", [who("^")]],
#                     ["KEY", [who(c)]],
#                     ["VALUE", slice(a.POS, len(P))],
#                     ["PROJ", slice(POS, len(P))],
#                 ],
#             ],
#             [],
#         ],
#         [lambda m: int(sum(m[0][POS : POS + len(P)]))],
#     ]
#     return run(code, f"^{s}$")
#
#
# def strcmp(s1: str, s2: str) -> bool:
#     a = FeatureAllocator()
#     A = a.alloc()
#     POS = a.alloc(len(P))
#     BRO = a.alloc(len(E))
#     EQ = a.alloc()
#     LT = a.alloc()
#     RESULT = a.alloc()
#     C = a.alloc()
#     code = [
#         [
#             [],
#             [["NOT", [A], [A]]],
#         ],
#         [
#             [
#                 [
#                     # copy pos of | into each token
#                     ["QUERY", [A]],
#                     ["KEY", [who("|")]],
#                     ["VALUE", slice(a.POS, len(P))],
#                     ["PROJ", slice(POS, len(P))],
#                 ],
#             ],
#             [
#                 *add_one_hot(POS, a.POS, len(P)),  # add curr pos to |'s pos to obtain opposite
#                 *lt_one_hot(a.POS, POS, len(P), LT),  # flag if to the left of |
#             ],
#         ],
#         [
#             [
#                 [
#                     # copy the twin token embedding
#                     ["QUERY", slice(POS, len(P))],
#                     ["KEY", slice(a.POS, len(P))],
#                     ["VALUE", slice(a.EMB, len(E))],
#                     ["PROJ", slice(BRO, len(E))],
#                 ],
#             ],
#             [
#                 *eq_one_hot(a.EMB, BRO, len(E), EQ),  # EQ = 1 if twin matches
#             ],
#         ],
#         [
#             [],
#             [
#                 ["NOT", [EQ], [EQ]],  # negate EQ for aggregation
#                 ["NOT", [who("^")], [C]],  # only want to hear from letters
#             ],
#         ],
#         [
#             [
#                 [
#                     # aggregate all !EQs, if >0 then return false else true
#                     ["QUERY", [who("^"), who("^")]],
#                     ["KEY", [LT, C]],
#                     ["VALUE", [EQ]],
#                     ["PROJ", [RESULT]],
#                 ],
#             ],
#             [],
#         ],
#         [lambda m: m[0][RESULT]],
#     ]
#     return run(code, f"^{s1}|{s2}$") + run(code, f"^{s2}|{s1}$") == 0.0  # meh
#
#
# def reverse(s: str) -> str:
#     a = FeatureAllocator()
#     A = a.alloc()
#     MID = a.alloc(len(P))
#     POS = a.alloc(len(P))
#     BRO = a.alloc(len(E))
#     EQ = a.alloc()
#     GT = a.alloc()
#     RESULT = a.alloc()
#     C = a.alloc()
#     code = [
#         [
#             [],
#             [["NOT", [A], [A]]],
#         ],
#         [
#             [
#                 [
#                     # copy pos of $ into each token
#                     ["QUERY", [A]],
#                     ["KEY", [who("$")]],
#                     ["VALUE", slice(a.POS, len(P))],
#                     ["PROJ", slice(POS, len(P))],
#                 ],
#                 [
#                     # copy pos of | into each token
#                     ["QUERY", [A]],
#                     ["KEY", [who("|")]],
#                     ["VALUE", slice(a.POS, len(P))],
#                     ["PROJ", slice(MID, len(P))],
#                 ],
#             ],
#             [
#                 *sub_one_hot(POS, a.POS, len(P)),  # sub |'s pos from curr pos to obtain opposite
#                 *gt_one_hot(a.POS, MID, len(P), GT),  # flag if to the right of |
#             ],
#         ],
#         [
#             [
#                 [
#                     # copy the twin token embedding
#                     ["QUERY", slice(POS, len(P))],
#                     ["KEY", slice(a.POS, len(P))],
#                     ["VALUE", slice(a.EMB, len(E))],
#                     ["PROJ", slice(BRO, len(E))],
#                 ],
#             ],
#             [
#                 ["AND", [who("?"), GT], [RESULT]],
#             ],
#         ],
#         [
#             lambda m: "".join(un_E(u[BRO : BRO + len(E)]) for u in m if u[RESULT] == 1.0),
#         ],
#     ]
#     return run(code, f"^{s}|{str('?' * len(s))}$")
#
#
# def kv(s: str) -> str:
#     a = FeatureAllocator()
#     A = a.alloc()
#     COMMA = a.alloc(len(P))
#     PIPE = a.alloc(len(P))
#     GT = a.alloc()
#     LT = a.alloc()
#     BETWEEN = a.alloc()
#     OUTSIDE = a.alloc()
#     POS = a.alloc(len(P))
#     VALUE = a.alloc(len(E))
#     code = [
#         [
#             [],
#             [
#                 ["NOT", [A], [A]],
#             ],
#         ],
#         [
#             [
#                 [
#                     # copy pos of , into each token
#                     ["QUERY", [A]],
#                     ["KEY", [who(",")]],
#                     ["VALUE", slice(a.POS, len(P))],
#                     ["PROJ", slice(COMMA, len(P))],
#                 ],
#                 [
#                     # copy pos of | into each token
#                     ["QUERY", [A]],
#                     ["KEY", [who("|")]],
#                     ["VALUE", slice(a.POS, len(P))],
#                     ["PROJ", slice(PIPE, len(P))],
#                 ],
#             ],
#             [
#                 *gt_one_hot(a.POS, COMMA, len(P), GT),  # flag if to the right of ,
#                 *lt_one_hot(a.POS, PIPE, len(P), LT),  # flag if to the left of |
#             ],
#         ],
#         [
#             [],
#             [
#                 ["AND", [GT, LT], [BETWEEN]],
#             ],
#         ],
#         [
#             [],
#             [
#                 ["NOT", [BETWEEN], [OUTSIDE]],
#             ],
#         ],
#         [
#             [
#                 [
#                     # copy twin token's position
#                     ["QUERY", [BETWEEN, *slice(a.EMB, len(E))]],
#                     ["KEY", [OUTSIDE, *slice(a.EMB, len(E))]],
#                     ["VALUE", slice(a.POS, len(P))],
#                     ["PROJ", slice(POS, len(P))],
#                 ],
#             ],
#             [
#                 *inc_one_hot(POS, len(P)),
#             ],
#         ],
#         [
#             [
#                 [
#                     # copy target token's position
#                     ["QUERY", slice(POS, len(P))],
#                     ["KEY", slice(a.POS, len(P))],
#                     ["VALUE", slice(a.EMB, len(E))],
#                     ["PROJ", slice(VALUE, len(E))],
#                 ],
#             ],
#             [],
#         ],
#         [
#             lambda m: "".join([un_E(u[VALUE : VALUE + len(E)]) for u in m if u[BETWEEN] == 1.0]),
#         ],
#     ]
#     return run(code, f"^{s}|{str('?' * len(s.split(',')[1]))}$")  # ?'s are currently redundant


def run_tests():
    print(
        "palindrome",
        all(
            [
                is_palindrome("a"),
                is_palindrome("aa"),
                is_palindrome("ababa"),
                is_palindrome("abba"),
                is_palindrome("abbba"),
                is_palindrome("nolemonnomelon"),
                not is_palindrome("hfaksdfhs"),
                not is_palindrome("ababababab"),
            ]
        ),
    )
    # print("strawberry", count_letter("strawberry", "r") == 3.0)
    # print(
    #     "strcmp    ",
    #     all(
    #         [
    #             strcmp("a", "a"),
    #             strcmp("strcmp", "strcmp"),
    #             not strcmp("hello", "world"),
    #             not strcmp("a", "b"),
    #             not strcmp("a", "aa"),
    #             not strcmp("aa", "a"),
    #         ]
    #     ),
    # )
    # print(
    #     "reverse   ",
    #     all(
    #         [
    #             reverse("abc") == "cba",
    #             reverse("a") == "a",
    #             reverse("hello") == "olleh",
    #             reverse("xyzab") == "bazyx",
    #         ]
    #     ),
    # )
    # print(
    #     "kv        ",
    #     all(
    #         [
    #             kv("a1b2c3,cba") == "321",
    #             kv("a1b2z8y1,yzb") == "182",
    #             kv("d7x3w3,xwxw") == "3333",
    #             kv("d7x3w3,xwdw") == "3373",
    #         ]
    #     ),
    # )


if __name__ == "__main__":
    run_tests()
