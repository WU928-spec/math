"""restricted.py - restricted min-max evaluation:
given profile c and witness set W, compute min over structural partitions P
of max over v in W of C_P(v)/OPT(v).  This is a LOWER bound on minmax(c)
(restricting the adversary). Great for fast candidate search.
"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compute import gen_partitions, partitions_array, partition_str


def restricted_minmax(c, n, W):
    c = tuple(c)
    k = len(c)
    parts = gen_partitions(c, n)
    P_arr = partitions_array(parts, n, k).astype(float)   # (np_, n, k)
    best = np.inf
    best_i = -1
    V = np.array([np.asarray(v, float) for v in W])       # (nw, k)
    loads = np.einsum("pnk,wk->pnw", P_arr, V)            # (np_, n, nw)
    cmax = loads.max(axis=1)                              # (np_, nw)
    opt = cmax.min(axis=0)                                # (nw,)
    ratio = cmax / opt[None, :]                           # (np_, nw)
    rmax = ratio.max(axis=1)                              # (np_,)
    best_i = int(rmax.argmin())
    return float(rmax[best_i]), parts[best_i], rmax
