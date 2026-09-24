"""a3_beta_probe.py —— β 引理（razor 带 (P) 第二证明最后命题）探针+符号攻关。

β 陈述：razor 角落（值语言行）+ sliver（J=j₁+j₂、jᵢ>1−J ∀i≥3、t+J≤1）+ s_{nS}<J
  ⟹ ∀SS 合法对 {u,v}（s_u+s_v≤1）：残差反序配对（seniors\{u,v} 降序 × juniors j₃..j_{nS} 升序）
     存在失配 rank（σ_r + j_{2+r} > 1）——即不可装箱。
sliver 行（线性化）：jᵢ+j₁+j₂ >= 1+MG ∀i>=3；t+j₁+j₂ <= 1；s_{nS}+MG <= j₁+j₂。
探针：角落 LP（noSJrev 系值行 ±A5/LZ/HZ）+ sliver 行采样，统计：
  (a) 是否存在某 SS 合法对使残差匹配可行（β 反例候选）；
  (b) 全 SS 对的最大可行边际 min_{u,v} max_r(σ_r+j_{2+r}) 的分布（失败缝有多薄）。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a1_value_lp2 as V
from itertools import combinations

MG = F(1, 10000)
TMESH = [0.28, 0.30, 0.31, 0.32, 1 / 3]


def build_beta(m, cnt, k=None):
    """值角落行（noSJrev/S1v/JJrev、含 B1/B2/B3）+ 可选 A5/LZ/HZ(k) + sliver + s_nS<J。"""
    nS = m - 1
    A, bc, bt, names, leg, nv = V.build(m, cnt, use_sjrev=False, use_s1v=False,
                                        use_jjrev=False, use_a2=False, use_b4=False)
    A, bc, bt, names = list(A), list(bc), list(bt), list(names)
    IP, IAM, IQ1 = 0, 1, 2
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)

    def con(row, c0, c1, nm):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)

    if k is not None:
        for i in range(1, k + 1):
            row = [F(0)] * nv; row[IP] = 1; row[vs(i)] = -1; row[vj(nS - k + i)] = -1
            con(row, -MG, 0, f'A5_{i}')
        row = [F(0)] * nv; row[vs(k)] = 4; row[IAM] = -5; row[IQ1] = -1
        con(row, 0, 0, 'LZ')
        row = [F(0)] * nv; row[vs(k + 1)] = -4; row[IAM] = 5; row[IQ1] = 1
        con(row, -MG, 0, 'HZ')
    # sliver: j_i + j_1 + j_2 >= 1+MG (i>=3); t+j_1+j_2 <= 1; s_nS + MG <= j_1+j_2
    for i in range(3, nS + 1):
        row = [F(0)] * nv; row[vj(i)] = -1; row[vj(1)] = -1; row[vj(2)] = -1
        con(row, -F(1) - MG, 0, f'slv{i}')
    row = [F(0)] * nv; row[vj(1)] = 1; row[vj(2)] = 1
    A.append(row); bc.append(F(1)); bt.append(F(-1)); names.append('tJ<=1')
    row = [F(0)] * nv; row[vs(nS)] = 1; row[vj(1)] = -1; row[vj(2)] = -1
    con(row, -MG, 0, 'smax<J')
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc])
    btf = np.array([float(x) for x in bt])
    return Af, bcf, btf, nv


def residual_bottleneck(s, j, u, v):
    """残差（去 SS 对 {u,v}，juniors j₃..）反序配对 bottleneck=max_r σ_r+j_{2+r}。"""
    nS = len(s)
    sig = sorted([s[i] for i in range(nS) if i not in (u, v)], reverse=True)
    jj = sorted(j)[2:]
    return max(sig[r] + jj[r] for r in range(len(sig)))


def probe(m, cnt, k=None, ntry=40):
    nS = m - 1
    Af, bcf, btf, nv = build_beta(m, cnt, k)
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)
    rng = np.random.default_rng(m * 100 + cnt[0] * 10 + (k or 0))
    out = dict(m=m, cnt=cnt, k=k, feas=0, counter=0, min_margin=None, samples=0)
    for t0 in TMESH:
        r0 = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bcf + btf * t0, bounds=(None, None), method='highs')
        if r0.status != 0:
            continue
        out['feas'] += 1
        for _ in range(ntry):
            c = rng.uniform(-1, 1, nv)
            res = linprog(c=c, A_ub=Af, b_ub=bcf + btf * t0, bounds=(None, None), method='highs')
            if res.status != 0:
                continue
            x = res.x
            s = [x[vs(r)] for r in range(1, nS + 1)]
            j = [x[vj(r)] for r in range(1, nS + 1)]
            out['samples'] += 1
            # 全 SS 合法对：best bottleneck
            best = None
            for u, v in combinations(range(nS), 2):
                if s[u] + s[v] <= 1 + 1e-9:
                    bn = residual_bottleneck(s, j, u, v)
                    if best is None or bn < best[0]:
                        best = (bn, u, v)
            if best is None:
                continue  # 无合法 SS 对（装箱不可能，平凡）
            margin = 1 - best[0]  # >0 表示有 SS 对使残差可行（β 反例）
            if out['min_margin'] is None or margin < out['min_margin'][0]:
                out['min_margin'] = (margin, t0, [round(v_, 4) for v_ in s],
                                     [round(v_, 4) for v_ in j], best[1], best[2])
            if margin > 1e-9:
                out['counter'] += 1
    return out


def main():
    t0 = time.time()
    for ktag, k in [('kfree', None)]:
        for m in range(6, 17):
            for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
                o = probe(m, cnt, k)
                print(f'{ktag} m={m} cnt={cnt}: LP可行t {o["feas"]}/5 采样 {o["samples"]} '
                      f'β反例候选 {o["counter"]} 最薄边际 {o["min_margin"]}', flush=True)
    print(f'({time.time()-t0:.0f}s)')


if __name__ == '__main__':
    main()
