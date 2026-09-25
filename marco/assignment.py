"""Hungarian algorithm (Kuhn–Munkres) for optimal one-to-one assignment.

Needed because brute-force permutation is O(n!) and becomes intractable past
n=8. BL1 used n=6 (720 permutations, fine); BL2 uses n=16 (20.9 trillion, never
finishes). This is the O(n^3) replacement.
"""

import numpy as np


def linear_sum_assignment(cost: np.ndarray):
    """Return (row_ind, col_ind) minimising total cost. Minimal JV-style
    implementation of the Hungarian algorithm for square matrices."""
    cost = np.asarray(cost, dtype=float)
    n, m = cost.shape
    assert n == m, "square matrices only"
    INF = float("inf")
    u = [0.0] * (n + 1)
    v = [0.0] * (m + 1)
    p = [0] * (m + 1)
    way = [0] * (m + 1)

    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (m + 1)
        used = [False] * (m + 1)
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = INF
            j1 = -1
            for j in range(1, m + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j
            for j in range(m + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break

    row_ind = [0] * n
    col_ind = [0] * n
    for j in range(1, m + 1):
        if p[j] > 0:
            row_ind[p[j] - 1] = p[j] - 1
            col_ind[p[j] - 1] = j - 1
    return np.array(row_ind), np.array(col_ind)


def assignment_accuracy(A: dict, B: dict, keys: list) -> tuple:
    """Optimal one-to-one matching accuracy between two labelled signature
    dicts. Returns (correct, total)."""
    n = len(keys)
    C = np.zeros((n, n))
    for i, ka in enumerate(keys):
        for j, kb in enumerate(keys):
            C[i, j] = float(np.sum(A[ka] != B[kb]))
    r, c = linear_sum_assignment(C)
    return int(np.sum(r == c)), n


if __name__ == "__main__":
    import itertools, time
    rng = np.random.RandomState(0)
    # correctness vs brute force on small n
    for n in (4, 5, 6, 7):
        for _ in range(20):
            C = rng.rand(n, n)
            r, c = linear_sum_assignment(C)
            hung = C[r, c].sum()
            best = min(sum(C[i, perm[i]] for i in range(n))
                       for perm in itertools.permutations(range(n)))
            assert abs(hung - best) < 1e-9, (n, hung, best)
    print("correct vs brute force for n=4..7")
    # speed on n=16
    C = rng.rand(16, 16)
    t0 = time.time()
    r, c = linear_sum_assignment(C)
    print(f"n=16 solved in {time.time()-t0:.4f}s")
