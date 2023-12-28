from typing import List


def _add(v1: List[int], v2: List[int]) -> List[int]:
    assert len(v1) == len(v2)
    res = [a + b for a, b in zip(v1, v2)]
    return res


def find_match_number(R: str, P: List[int]) -> int:
    """Find the number of arrangements that match both the corrupted sequence `R` and
    the run-length encoding `P`.
    """
    # Let us define
    #   M(n, C1, C2, k, V)
    #       = number of arrangements where the corrupted sequence is join(R[0:n], C1, C2),
    #         while the run-length encoding is P[0:k] + [V] .
    # We assume V > 0 in general, but k = V = 0 is allowed to represent an empty
    # encoding. The characters C1, C2 will sometimes be written as part of a single
    # string, for convenience; e.g., ".#".

    # The number of arrangements that we're looking for is given by
    #   Count = M(N-2, R[N-2], R[N-1], K-1, P[K-1]) ,
    # where N = len(R), K = len(P). This assumes K >= 1, which is always true in our
    # examples, and N >= 2. To handle N == 1, we can simply pad the sequence R with a
    # dot, since adding a dot never changes the RLE.

    # max size of M: N * K * 9 * N = O(N^2 * K)

    assert len(R) >= 1
    assert len(P) >= 1

    if len(R) < 2:
        R = "." + R

    N = len(R)
    K = len(P)
    M = {}

    # base cases
    # * M(0, "..", 0, V) = 1 if V == 0 else 0
    M[0, "..", 0] = [1] + (N - 1) * [0]

    # * M(0, ".#", 0, V) = 1 if V == 1 else 0
    # * M(0, "#.", 0, V) = 1 if V == 1 else 0
    for cc in [".#", "#."]:
        M[0, cc, 0] = N * [0]
        M[0, cc, 0][1] = 1

    # * M(0, "##", 0, V) = 1 if V == 2 else 0
    M[0, "##", 0] = N * [0]
    M[0, "##", 0][2] = 1

    # * M(0, "?.", 0, V) = 1 if V in [0, 1] else 0
    M[0, "?.", 0] = [1, 1] + (N - 2) * [0]

    for k in range(1, K):
        for c1 in ".#?":
            for c2 in ".#?":
                M[0, c1 + c2, k] = N * [0]

    # * M(0, "?#", k, V) =  M(0, ".#", k, V) + M(0, "##", k, V)
    for k in range(K):
        M[0, "?#", k] = _add(M[0, ".#", k], M[0, "##", k])

    # * M(0, C, "?", k, V) = M(0, C, ".", k, V) + M(0, C, "#", k, V)
    for c in ".#?":
        for k in range(K):
            M[0, c + "?", k] = _add(M[0, c + ".", k], M[0, c + "#", k])

    for n in range(1, N):
        # * M(n, C, ".", k, V) = M(n-1, R[n-1], C, k, V)
        for c in ".#?":
            for k in range(K):
                M[n, c + ".", k] = M[n - 1, R[n - 1] + c, k]

        # * M(n, ".#", k, V)
        #       =  0                                        if V != 1
        #       =  M(n-1, R[n-1], ".", 0, 0)                if V == 1 and k == 0
        #       =  M(n-1, R[n-1], ".", k-1, P[k-1])         if V == 1 and k > 0
        for k in range(K):
            M[n, ".#", k] = N * [0]
            if k == 0:
                M[n, ".#", k][1] = M[n - 1, R[n - 1] + ".", 0][0]
            else:
                M[n, ".#", k][1] = M[n - 1, R[n - 1] + ".", k - 1][P[k - 1]]

        # * M(n, "##", k, V)
        #       =  0                                        if V < 2
        #       =  M(n-1, R[n-1], "#", k, V-1)              if V >= 2
        for k in range(K):
            M[n, "##", k] = N * [0]
            for V in range(2, N):
                M[n, "##", k][V] = M[n - 1, R[n - 1] + "#", k][V - 1]

        # * M(n, "?#", k, V) =  M(n, ".#", k, V) + M(n, "##", k, V)
        for k in range(K):
            M[n, "?#", k] = _add(M[n, ".#", k], M[n, "##", k])

        # * M(n, C, "?", k, V) = M(n, C, ".", k, V) + M(n, C, "#", k, V)
        for k in range(K):
            for c in ".#?":
                M[n, c + "?", k] = _add(M[n, c + ".", k], M[n, c + "#", k])

    count = M[N - 2, R[-2:], K - 1][P[K - 1]]
    return count
