"""a3_ 枚举路线可行性评估：不等价装箱分组数的精确计数。
前提（交换论证已证 w.l.o.g.）：senior 侧指派固定——SS=最小 2a 个极端配对、
SJ=接下来 b 个、S=最大 c 个。剩余枚举 = junior 池（口袋2 m 件=m-1 juniors+t；
口袋1 多 x 共 m+1 件）到 b 个 SJ 位（可区分，配 s_{2a+k}）+ d 个 JJJ 箱（无序）
+ e 个 JJ 箱（无序）+ f 个 J 位（无序）的集合指派：
    G = M! / [ (3!)^d (2!)^e · d! · e! · f! ]    （M = 池大小）
（SJ 位可区分故不除 b!；箱内无序除 (3!)^d/(2!)^e；同型箱间无序除 d!/e!/f!。）
"""
from math import factorial
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pairing_feasible import bin_count_solutions
from pocket1_bins import bin_counts


def G(cnt, M):
    a, b, c, d, e, f = cnt
    return factorial(M) // (6 ** d * 2 ** e * factorial(d) * factorial(e) * factorial(f))


def stats(m, enum, M, tag):
    cnts = enum(m)
    gs = sorted(G(cnt, M) for cnt in cnts)
    tot = sum(gs)
    print(f'{tag} m={m}: 合法 cnt {len(cnts)} 个；分组数 min={gs[0]:.3g} 中位={gs[len(gs)//2]:.3g} '
          f'max={gs[-1]:.3g}  逐情形合计Σ={tot:.3g}')
    return tot


def main():
    print('== 口袋2（池 M=m：m-1 juniors + t；合法 cnt 由 bin_count_solutions）==')
    for m in [6, 8, 12, 16, 20, 26, 30]:
        stats(m, bin_count_solutions, m, 'P2')
    print('== 口袋1（池 M=m+1：m-1 juniors + x + t；bin_counts）==')
    for m in [6, 8, 12, 16, 20, 26]:
        stats(m, bin_counts, m + 1, 'P1')
    # 增长形态：固定 cnt 族 (1,m-3,0,1,0,0) 的 G 随 m
    print('== 单族形态（JJJ 含 t 族 (1,m-3,0,1,0,0)，d=1,e=f=0）==')
    for m in [6, 8, 12, 16, 20, 26, 30, 40]:
        g = factorial(m) // 6
        print(f'  m={m}: G=m!/6 = {g:.3g}')


if __name__ == '__main__':
    main()
