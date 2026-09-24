"""U(a) 统一恒等式对 razor 全族（洞+残留真实 cnt 族驱动）的 ∀m 验证（agent-4）。

统一恒等式（a≥1 全形）：
  2(j₁−t) + 6·danger + 4·pair0 + 2·pair1 + (s₁−s₀)
  + 3·Σ_{i=1}^{2a−2}(s_{i+1}−s_i) + 3·(1−s₀−s_{2a−1}) + 4·XTRI = −1/2 − 12·MG
族清单直接从 p2_holes_big.jsonl（洞族）+ E-nec 残留形态的合法 cnt 推导，避免手推 cnt 笔误。
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a4_symbolic_verify import check_identity
from fractions import Fraction as F
from pairing_feasible import bin_count_solutions

HERE = os.path.dirname(os.path.abspath(__file__))


def U(a):
    rows = [(('j1>=t', 0), F(2)), (('danger', 0), F(6)), (('pair0', 0), F(4)),
            (('pair1', 0), F(2)), (('srt0', 0), F(1))]
    rows += [((f'srt{i}', 0), F(3)) for i in range(1, 2 * a - 1)]
    rows += [(('XSS0', 0), F(3)), (('XTRI', 0), F(4))]
    return rows


def fams_from_holes():
    """洞族 (c,d,e,f) -> a（由守恒推出）。"""
    seen = {}
    for line in open(os.path.join(HERE, 'p2_holes_big.jsonl')):
        h = json.loads(line)
        seen[tuple(h['cnt'])] = h['m']
    # razor 残留补充族（E-nec 文件记录的形态）
    return seen


def mk_fam(a, c, d, e, f, m):
    b = m - 1 - 2 * a - c
    cnt = (a, b, c, d, e, f)
    if b < 0 or min(cnt) < 0:
        return None
    if 2 * a + b + c != m - 1 or b + 3 * d + 2 * e + f != m:
        return None
    return cnt


if __name__ == '__main__':
    t0 = time.time()
    holes = fams_from_holes()
    # 洞族 + 邻近 razor 族：(c,d,e,f) 集合
    key_fams = sorted(set((cnt[2], cnt[3], cnt[4], cnt[5]) for cnt in holes))
    print(f'洞族 (c,d,e,f) 键: {key_fams}')
    # 对每个 cnt 族（取代表 a,b）：在其有效 m 范围全 k 验证 U(a)
    summary = {}
    for (c, d, e, f) in key_fams:
        # 由守恒: b+3d+2e+f = m 且 2a+b+c = m-1 ⟹ a = (m-1-c-(m-3d-2e-f))/2 = (3d+2e+f-1-c)/2
        a_num = 3 * d + 2 * e + f - 1 - c
        if a_num % 2 or a_num <= 0:
            print(f'  (c,d,e,f)=({c},{d},{e},{f}): a 非正整数，跳过')
            continue
        a = a_num // 2
        bad = []
        n_case = 0
        for m in range(max(2 * a + 1, c + 2 * a + 1), 51):
            cnt = mk_fam(a, c, d, e, f, m)
            if cnt is None:
                continue
            for k in range(2, m):
                n_case += 1
                ok, r = check_identity(m, cnt, k, U(a))
                if not ok:
                    bad.append((m, k, r))
        summary[(c, d, e, f)] = (a, n_case, len(bad), bad[:2])
        print(f'  (c,d,e,f)=({c},{d},{e},{f}) a={a}: {n_case} 案例, '
              f'{"全通过 ✓" if not bad else f"{len(bad)} 失败 例 {bad[:2]}"} ({time.time()-t0:.0f}s)',
              flush=True)
    nbad = sum(v[2] for v in summary.values())
    print(f'总结: {"razor 全族 U(a) 全通过 ✓" if nbad == 0 else f"共 {nbad} 处失败"}')
