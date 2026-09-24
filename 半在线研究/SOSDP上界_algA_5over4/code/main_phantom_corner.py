"""main_phantom_corner.py —— 值语言幻影的"真角落"判定（CEGAR 种子）。
流程：值语言 LP（全行含 SJrev）采样幻影 → 验证按构造可装箱（B1/B2/SJrev 显式装箱）
→ 真角落判定：senior 定机（srt），jj 由 s_jj<=K-q1<s_{jj+1} 唯一确定，
junior 回机器的可行指派（窗口 [max(t,p-s), min(2t,K-s)] + 低端区单调(mon2)+fs j_jj=q1）存在？
  存在 ⟹ 真角落+可装箱 = (P) 反例（警报，与 T'' 冲突须复核）
  不存在 ⟹ 幻影非真角落，报告阻断约束（=候选新 A 行，值语言可线性化者入 CEGAR）
"""
import numpy as np
from scipy.optimize import linprog
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a1_value_lp2 as V


def sample_phantom(m, cnt, t0, seed=7):
    A, bc, bt, names, leg, nv = V.build(m, cnt)
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc])
    btf = np.array([float(x) for x in bt])
    rng = np.random.default_rng(seed)
    for _ in range(50):
        c = rng.standard_normal(nv)
        res = linprog(c=c, A_ub=Af, b_ub=bcf + btf * t0, bounds=(None, None), method='highs')
        if res.status == 0:
            return res.x
    return None


def check_packing(s, j, t):
    """按构造：SS={s1,s2}、JJJ={t,j1,j2}、残差反序 SJ。"""
    nS = len(s)
    ok_ss = s[0] + s[1] <= 1 + 1e-9
    ok_jjj = t + j[0] + j[1] <= 1 + 1e-9
    ok_sj = all(s[nS - 1 - r] + j[2 + r] <= 1 + 1e-9 for r in range(nS - 2))
    return ok_ss and ok_jjj and ok_sj


def assign_juniors(s, j, p, t, am, q1, eps=1e-4):
    """真角落判定：返回 (ok, k, pi, reason)。senior 定机 0..nS-1（升序）。"""
    nS = len(s)
    K = 5 * (am + q1) / 4
    # jj 由 seniors 与 q1=j[-1] 唯一确定
    jj = max((i for i in range(nS) if s[i] <= K - q1 + 1e-12), default=-1)
    if jj < 0:
        return False, None, None, '无机器容得下 q1（s_i<=K-q1 为空）'
    if any(s[i] <= K - q1 + 1e-12 for i in range(jj + 1, nS)):
        return False, None, None, 'hizone 冲突'
    # 窗口
    lo = [max(t, p - s[i] + eps) for i in range(nS)]
    hi = [min(2 * t, K - s[i]) for i in range(nS)]
    if any(lo[i] > hi[i] + 1e-12 for i in range(nS)):
        bad = [i for i in range(nS) if lo[i] > hi[i] + 1e-12]
        return False, jj, None, f'窗口空: 机器{bad}（[lo,hi] 不相交——pair 与 cap 在值上冲突）'
    # fs: 机器 jj <- q1（最大 junior）
    jvals = list(j)
    q1v = jvals[-1]
    if not (lo[jj] - 1e-12 <= q1v <= hi[jj] + 1e-12):
        return False, jj, None, f'fs 冲突: q1={q1v:.4f} 不在机器{jj}窗口[{lo[jj]:.4f},{hi[jj]:.4f}]'
    pool = jvals[:-1]
    assign = {jj: q1v}
    # 低端区 [0, jj-1]：单调非降指派（贪心最小可行）
    rest = list(pool)
    prev = -1
    for i in range(jj):
        cand = [v for v in rest if v >= prev - 1e-12 and lo[i] - 1e-12 <= v <= hi[i] + 1e-12]
        if not cand:
            return False, jj, None, f'mon2 死: 低端机器{i} 无可指派 junior（窗口[{lo[i]:.4f},{hi[i]:.4f}]，prev={prev:.4f}，余{[round(v,3) for v in rest]}）'
        v = min(cand)
        assign[i] = v
        rest.remove(v)
        prev = v
    # hi 区 [jj+1, nS-1]：任意匹配（DFS）
    hims = list(range(jj + 1, nS))
    def dfs(idx, rest):
        if idx == len(hims):
            return True
        i = hims[idx]
        for v in list(rest):
            if lo[i] - 1e-12 <= v <= hi[i] + 1e-12:
                assign[i] = v
                rest.remove(v)
                if dfs(idx + 1, rest):
                    return True
                rest.append(v)
                del assign[i]
        return False
    if not dfs(0, rest):
        return False, jj, None, f'hi 区匹配死（机器{hims} 窗口与余量 junior 无完美匹配）'
    return True, jj + 1, assign, '真角落成立'


def main(m=10, cnt=(1, 7, 0, 1, 0, 0), t0=0.30, ntry=5):
    nS = m - 1
    nreal = 0
    for seed in range(ntry):
        x = sample_phantom(m, cnt, t0, seed=seed)
        if x is None:
            print(f'seed={seed}: 无幻影（INF）')
            continue
        p, am, q1 = x[0], x[1], x[2]
        s = list(x[3:3 + nS])
        j = list(x[3 + nS:3 + 2 * nS])
        pack = check_packing(s, j, t0)
        ok, k, assign, reason = assign_juniors(s, j, p, t0, am, q1)
        print(f'seed={seed}: 构造装箱={"✓" if pack else "✗"} 真角落={"✓ k=%d" % k if ok else "✗"}')
        print(f'   p={p:.3f} am={am:.3f} q1={q1:.3f} t={t0}')
        print(f'   s={np.round(s,3)}')
        print(f'   j={np.round(j,3)}')
        if not ok:
            print(f'   阻断: {reason}')
        else:
            nreal += 1
            print('   **警报：真角落+可装箱——(P) 反例候选！**')
    print(f'\n真角落幻影 {nreal}/{ntry}')


if __name__ == '__main__':
    main()
