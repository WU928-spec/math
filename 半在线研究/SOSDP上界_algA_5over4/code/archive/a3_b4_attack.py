"""a3_b4_attack.py —— B4（threshold-Hall，uncond 115 的 109/115 承重行）敌意构造性复核。

B4_q: s_{nS+1-q} + j_{q+2} <= 1, q = 2a+1..nS-2（值语言坐标）。
agent-1 一行论证的逃逸口（agent-3 发现）：
  (iii) j_{q+2} > 1 - s_{nS+1-q}（B4_q 破）⟹ 大 q 个 senior (L_q) 的兼容 junior 集
        C = {t, j_1..j_{q+1}}（q+2 件；t 与一切 senior 兼容因 B3: s<=1-t）。
  Hall 亏缺只在 ss_L=0（L_q 无 SS 配对）∧ jjj_C=3（JJJ 三件全取自 C）时成立。
  逃逸(a)：JJJ 用池外 junior ⟺ 某 j_u(u>=q+2) <= 1-2t ⟸ s_{nS+1-q} > 2t 且 j_{q+2}<=1-2t
  逃逸(b)：L_q 某 senior 进 SS ⟺ s_1 + s_{nS+1-q} <= 1（须 s_{nS+1-q} <= 2t）
本脚本：角落域（noSJrev 行集 − B4）+ (iii) + 逃逸(a/b) 分别 LP 搜见证点（密 t 网格），
命中则抽多点做 DFS 精确装箱（nS 箱 cap 1，池 = seniors+juniors+t）。
可装箱 ⟹ B4 INVALID（BREAKING：uncond 115 的 109 发证书塌）；全不可装 ⟹ SUSPECT 维持。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
from itertools import combinations
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a1_value_lp2 as V
from main_cegar3 import MG

MGF = 1e-4
# 密 t 网格
TMESH = [round(0.255 + 0.002 * i, 3) for i in range(40)] + [1 / 3]
BASE_KW = dict(use_sjrev=False, use_s1v=False, use_jjrev=False, use_b4=False)


def build_corner(m, cnt, k):
    """uncond 证明行集 − B4（含 A5/LZ/HZ）。"""
    nS = m - 1
    A, bc, bt, names, leg, nv = V.build(m, cnt, **BASE_KW)
    A, bc, bt, names = list(A), list(bc), list(bt), list(names)
    IP, IAM, IQ1 = 0, 1, 2
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)
    for i in range(1, k + 1):
        row = [F(0)] * nv; row[IP] = 1; row[vs(i)] = -1; row[vj(nS - k + i)] = -1
        A.append(row); bc.append(-MG); bt.append(F(0)); names.append(f'A5_{i}')
    row = [F(0)] * nv; row[vs(k)] = 4; row[IAM] = -5; row[IQ1] = -1
    A.append(row); bc.append(F(0)); bt.append(F(0)); names.append('LZ')
    if k < nS:
        row = [F(0)] * nv; row[vs(k + 1)] = -4; row[IAM] = 5; row[IQ1] = 1
        A.append(row); bc.append(-MG); bt.append(F(0)); names.append('HZ')
    return A, bc, bt, names, nv


def add_rows(A, bc, bt, names, nv, m, q, mode):
    """(iii) + 逃逸行。mode='a'/'b'。"""
    nS = m - 1
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)
    # (iii): j_{q+2} + s_{nS+1-q} >= 1 + MG  →  -j - s <= -1 - MG
    row = [F(0)] * nv; row[vj(q + 2)] = -1; row[vs(nS + 1 - q)] = -1
    A.append(row); bc.append(F(-1) - MG); bt.append(F(0)); names.append('iii')
    if mode == 'a':
        # j_{q+2} <= 1 - 2t
        row = [F(0)] * nv; row[vj(q + 2)] = 1
        A.append(row); bc.append(F(1)); bt.append(F(-2)); names.append('escA')
    else:
        # s_1 + s_{nS+1-q} <= 1
        row = [F(0)] * nv; row[vs(1)] = 1; row[vs(nS + 1 - q)] = 1
        A.append(row); bc.append(F(1)); bt.append(F(0)); names.append('escB')


def dfs_pack(items, nbins, cap=1.0, eps=1e-9):
    """精确 DFS 装箱判定（浮点带 eps；物品降序，首适分支+对称剪枝）。"""
    items = sorted(items, reverse=True)
    loads = [0.0] * nbins

    def rec(i):
        if i == len(items):
            return True
        seen = set()
        for b in range(nbins):
            if loads[b] in seen:
                continue
            if loads[b] + items[i] <= cap + eps:
                seen.add(loads[b])
                loads[b] += items[i]
                if rec(i + 1):
                    return True
                loads[b] -= items[i]
            if loads[b] == 0.0:
                break
        return False
    return rec(0)


def attack(m, cnt, k, q, mode):
    """返回 (n_witness, n_packable, sample)。"""
    nS = m - 1
    A, bc, bt, names, nv = build_corner(m, cnt, k)
    add_rows(A, bc, bt, names, nv, m, q, mode)
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc])
    btf = np.array([float(x) for x in bt])
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)
    rng = np.random.default_rng(hash((m, cnt[0], k, q, mode)) % 2**32)
    nw = 0; npack = 0; samp = None
    for t0 in TMESH:
        if t0 < (m - 1) / (4 * (m - 2)) - 1e-9:
            continue
        res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bcf + btf * t0,
                      bounds=(None, None), method='highs')
        if res.status != 0:
            continue
        nw += 1
        # 每个命中 t 抽 3 个目标方向的点做装箱
        for trial in range(3):
            c = rng.uniform(-1, 1, nv)
            r2 = linprog(c=c, A_ub=Af, b_ub=bcf + btf * t0, bounds=(None, None), method='highs')
            if r2.status != 0:
                continue
            x = r2.x
            items = [x[vs(r)] for r in range(1, nS + 1)] + \
                    [x[vj(r)] for r in range(1, nS + 1)] + [t0]
            if dfs_pack(items, nS):
                npack += 1
                samp = dict(m=m, cnt=cnt, k=k, q=q, mode=mode, t=t0,
                            s=[round(float(x[vs(r)]), 4) for r in range(1, nS + 1)],
                            j=[round(float(x[vj(r)]), 4) for r in range(1, nS + 1)])
                return nw, npack, samp
    return nw, npack, samp


def main():
    t_start = time.time()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a3_b4_attack.jsonl')
    done = set()
    if os.path.exists(path):
        for l in open(path):
            try:
                r = json.loads(l)
                done.add((r['m'], tuple(r['cnt']), r['k'], r['q'], r['mode']))
            except Exception:
                pass
        print(f'断点：已完成 {len(done)} 组合，续跑', flush=True)
    out = open(path, 'a')
    total_w = total_p = 0
    for m in range(6, 17):
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            a = cnt[0]; nS = m - 1
            for k in range(2, m - 2):
                for q in range(2 * a + 1, nS - 1):
                    for mode in ['a', 'b']:
                        if (m, tuple(cnt), k, q, mode) in done:
                            continue
                        nw, npack, samp = attack(m, cnt, k, q, mode)
                        total_w += nw; total_p += npack
                        rec = dict(m=m, cnt=cnt, k=k, q=q, mode=mode,
                                   witnesses=nw, packable=npack)
                        out.write(json.dumps(rec) + '\n'); out.flush()
                        if npack:
                            print(f'  ★ 可装箱反例! {json.dumps(samp)}', flush=True)
        print(f'm={m} 完成（{time.time()-t_start:.0f}s，累计见证 {total_w} 可装箱 {total_p}）',
              flush=True)
    out.close()
    print(f'\nB4 攻击收官：见证点 {total_w}，可装箱 {total_p}')
    print('判读：可装箱>0 ⟹ B4 INVALID；=0 且见证>0 ⟹ 逃逸点全幻影（SUSPECT 维持）；见证=0 ⟹ 角落域无逃逸（B4 被角落行蕴涵）')


if __name__ == '__main__':
    main()
