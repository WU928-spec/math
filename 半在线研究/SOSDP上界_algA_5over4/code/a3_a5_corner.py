"""a3_a5_corner.py —— A5 角落域敌意复核（main 催办，2026-09-23）。

A5（main_cegar3.build_k，值语言）: j_{nS-k+i} >= p - s_i + MG, i=1..k
  值语言语义：全体 junior 按值升序第 (nS-k+i) 名 >= p - s_i（s_i = 第 i 小 senior）。

判定框架：机 LP（fast_lp.rows_fixed use_order=True，绑机 pair{i}: s_i+j_i>=p+MG
  + ord 低端区 junior 升序 + lowzone/hizone + 全角落行）。机 LP 可行域 ⊇ 真角落域 ⟹
  A5 在机 LP 全域成立 ⟹ A5 合法（对真角落更成立）。

先验证明（4 步，待数值确认）：
  1. chosen = 低端机 0..k-1（0-based）的 junior；ord 行使 chosen 升序 = j_0..j_{k-1}
  2. pair{i}: chosen_i(第i小)=j_{i-1} >= p - s_{i-1} + MG
  3. top-k 支配：全体第 (nS-k+i) 小 >= 任意 k 件第 i 小 = chosen_i
  4. ⟹ j_{nS-k+i} >= p - s_i + MG（A5）——纯 pair+ord 推论，机 LP 中冗余；
     值语言 LP 中 A1 弱于 pair ⟹ A5 有切割力（main 154/154 INF 的力量来源）。

测试（main 指令）：
  ①合法性：机 LP 采样角落点 N 个（随机+结构化目标），统计 max (p - s_i) - j_{(nS-k+i)}
  ②m<=8 子集精确化：违例 ⟺ ∃(nS-k+i) 子集 S 使 max_{u∈S} j_u < p - s_i；
    全子集 LP 最大化违例量 < 0 ⟹ A5 被 pair+ord 蕴涵（精确蕴涵证明）。
"""
import numpy as np
from scipy.optimize import linprog
from itertools import combinations
from fractions import Fraction as F
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fast_lp

TMESH = [0.27, 0.29, 0.30, 0.31, 0.32, 0.33, 1 / 3]
NSAMP = 40
rng = np.random.default_rng(20260923)
CAPNAMES = {'SS', 'SJ', 'JJJ', 'JJ'}   # 装箱帽（cnt 规范分组 w.l.o.g.），非角落约束，须剔除


def corner_rows(m, cnt, k):
    """fast_lp.rows_fixed(use_order=True) 去掉装箱帽行 = 纯角落域（非装箱约束+保序）。"""
    R, nv = fast_lp.rows_fixed(m, cnt, k, use_order=True)
    return [r for r in R if r[3] not in CAPNAMES], nv


def lp_feasible_point(Af, bcf, btf, t0, nv, c):
    res = linprog(c=c, A_ub=Af, b_ub=bcf + btf * t0, bounds=(None, None), method='highs')
    if res.status == 0:
        return res.x
    return None


def check_config(m, cnt, k):
    """返回 (status, maxviol, detail)。status: INF / 数值结论。"""
    nS = m - 1
    R, nv = corner_rows(m, cnt, k)
    Af = np.array([row for row, _, _, _ in R])
    bcf = np.array([float(c0) for _, c0, _, _ in R])
    btf = np.array([float(c1) for _, _, c1, _ in R])
    ip, it = 0, 1
    vs = lambda i: 2 + i            # 0-based 机 i
    vj = lambda i: 2 + nS + i

    # 找可行 t0
    x0 = None; t_used = None
    for t0 in TMESH:
        x0 = lp_feasible_point(Af, bcf, btf, t0, nv, np.zeros(nv))
        if x0 is not None:
            t_used = t0
            break
    if x0 is None:
        return ('INF', None, None)

    # 目标库：随机 + 结构化（压低全体 junior、抬高 p-s_i）
    objs = []
    for _ in range(NSAMP):
        objs.append(rng.uniform(-1, 1, nv))
    cmean = np.zeros(nv)
    for u in range(nS):
        cmean[vj(u)] = 1.0 / nS
    for i in range(1, k + 1):
        c1 = cmean.copy(); c1[ip] -= 1.0; c1[vs(i - 1)] += 1.0   # min mean_j - (p - s_i)
        objs.append(c1)
        c2 = np.zeros(nv); c2[ip] = -1.0; c2[vs(i - 1)] = 1.0   # max p - s_i
        objs.append(c2)

    maxviol = -1e9; arg = None
    for c in objs:
        x = lp_feasible_point(Af, bcf, btf, t_used, nv, c)
        if x is None:
            continue
        p = x[ip]
        sj = sorted(x[vj(u)] for u in range(nS))   # 全体 junior 值升序
        for i in range(1, k + 1):
            s_i = x[vs(i - 1)]
            j_rank = sj[nS - k + i - 1]            # 第 (nS-k+i) 小（1-based → 0-based）
            viol = (p - s_i) - j_rank
            if viol > maxviol:
                maxviol = viol
                arg = dict(i=i, p=float(p), s_i=float(s_i), j_rank=float(j_rank),
                           juniors=[float(v) for v in sj], t=t_used)
    return ('SAMPLED', maxviol, arg)


def exact_subset_check(m, cnt, k):
    """m<=8 精确蕴涵检验：对每个 i 与每个 (nS-k+i) 子集 S，最大化 (p-s_i) - max_{u∈S} j_u。
    全部 < 0 ⟹ A5_i 被 pair+ord+角落行精确蕴涵。"""
    nS = m - 1
    R, nv = corner_rows(m, cnt, k)
    Af = np.array([row for row, _, _, _ in R])
    bcf = np.array([float(c0) for _, c0, _, _ in R])
    btf = np.array([float(c1) for _, _, c1, _ in R])
    ip = 0
    vs = lambda i: 2 + i
    vj = lambda i: 2 + nS + i
    worst = -1e9; worst_desc = None
    for t0 in TMESH:
        # 该 t0 下全子集全 i
        for i in range(1, k + 1):
            r_size = nS - k + i
            for S in combinations(range(nS), r_size):
                # 增广变量 w >= j_u ∀u∈S；目标 max (p - s_i) - w
                A2 = [list(row) + [0.0] for row in Af]
                b2 = list(bcf + btf * t0)
                for u in S:
                    row = [0.0] * (nv + 1); row[vj(u)] = 1.0; row[nv] = -1.0
                    A2.append(row); b2.append(0.0)
                c = np.zeros(nv + 1); c[ip] = -1.0; c[vs(i - 1)] = 1.0; c[nv] = 1.0
                res = linprog(c=c, A_ub=np.array(A2), b_ub=np.array(b2),
                              bounds=(None, None), method='highs')
                if res.status == 0:
                    viol = -res.fun
                    if viol > worst:
                        worst = viol
                        worst_desc = dict(t=t0, i=i, S=S, viol=float(viol))
    return worst, worst_desc


def main():
    t_start = time.time()
    out = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'a3_a5_corner.jsonl'), 'w')
    print('=== ① 采样合法性扫描 m=6..16 × 2cnt × k=2..m-3 ===', flush=True)
    gmax = -1e9; garg = None; ninf = 0; nsampled = 0
    for m in range(6, 17):
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            for k in range(2, m - 2):
                st, mv, arg = check_config(m, cnt, k)
                rec = dict(m=m, cnt=cnt, k=k, status=st, maxviol=mv)
                out.write(json.dumps(rec) + '\n'); out.flush()
                if st == 'INF':
                    ninf += 1
                    print(f'  m={m} cnt={cnt} k={k}: 机LP全网格 INF', flush=True)
                else:
                    nsampled += 1
                    tag = '' if mv <= 1e-7 else '  <<< 违例!!'
                    if mv > gmax:
                        gmax = mv; garg = dict(m=m, cnt=cnt, k=k, **arg)
                    if mv > 1e-7:
                        print(f'  m={m} cnt={cnt} k={k}: maxviol={mv:.6f}{tag}', flush=True)
        print(f'm={m} 扫完（{time.time()-t_start:.0f}s）', flush=True)
    print(f'\n采样判决：INF {ninf} / 采样 {nsampled}；全局 maxviol={gmax:.8f}')
    if garg:
        print('  argmax:', json.dumps(garg))
    print('  判读：maxviol<=0 ⟹ 角落域恒满足 A5（合法）')

    print('\n=== ② m<=8 子集精确蕴涵检验 ===', flush=True)
    for m in range(6, 9):
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            for k in range(2, m - 2):
                w, desc = exact_subset_check(m, cnt, k)
                tag = '蕴涵 ✓（A5 合法，机 LP 冗余）' if w is not None and w <= 1e-7 else '<<< 违例'
                print(f'  m={m} cnt={cnt} k={k}: 全子集最大违例={w:.8f} {tag}', flush=True)
                if desc and w > 1e-7:
                    print('    ', json.dumps(desc), flush=True)
    out.close()
    print(f'\n总耗时 {time.time()-t_start:.0f}s')


if __name__ == '__main__':
    main()
