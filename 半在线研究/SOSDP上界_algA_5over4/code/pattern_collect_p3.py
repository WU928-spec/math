"""口袋3证书模式分析：从 p3_big_scan.jsonl 读精确证书，按 (m,k) 列非零约束+权重，
寻找与 m 无关的统一结构。输出：k=1 / k=2 / k=m-1 三个切片的证书全文，及跨 m 对比统计。
"""
import sys, os, json
from fractions import Fraction as F
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))


def load():
    recs = {}
    with open(os.path.join(HERE, 'p3_big_scan.jsonl')) as f:
        for line in f:
            r = json.loads(line)
            recs[(r['m'], r['k'])] = r
    return recs


def show(recs, m, k):
    r = recs.get((m, k))
    if not r or r['status'] != 'OK':
        print(f'  m={m} k={k}: {r["status"] if r else "缺失"}')
        return
    parts = ' '.join(f'{nm}:{w}' for nm, w in r['cert'])
    print(f'  m={m} k={k} ({len(r["cert"])}项): {parts}')


if __name__ == '__main__':
    recs = load()
    print('==== k=1 切片（m=4..16）====')
    for m in range(4, 17):
        show(recs, m, 1)
    print('==== k=m-1 切片（m=4..16）====')
    for m in range(4, 17):
        show(recs, m, m - 1)
    print('==== k=2 切片（m=5..12）====')
    for m in range(5, 13):
        show(recs, m, 2)
    # 统计：约束名出现频率（跨全部 m,k）
    cnt = Counter()
    for (m, k), r in recs.items():
        if r['status'] == 'OK':
            for nm, w in r['cert']:
                base = nm.rstrip('0123456789').replace('>M0', '')
                cnt[base] += 1
    print('==== 约束基名出现频次（全样本）====')
    for nm, c in cnt.most_common():
        print(f'  {nm:12s}: {c}')
