import glob, itertools
rows=[]
for f in sorted(glob.glob("/tmp/feat_*.out")):
    for ln in open(f):
        parts=ln.strip().split("\t")
        if len(parts)!=14 or not parts[3].replace(".","").isdigit(): continue
        seed,idx,n,c,lam,nE,nFB,prof,p2,p3,p5,p45,m1,mn = parts
        rows.append(dict(seed=seed,n=int(n),c=float(c),lam=lam,nE=int(nE),nFB=int(nFB),
                         prof=prof,p2=int(p2),p3=int(p3),p5=int(p5),p45=int(p45),m1=int(m1),mn=float(mn)))
print("合并片数 =", len(rows))
hi=[r for r in rows if r['c']>1.19]
print("天花板 > 1.19 的片数 =", len(hi), "  最大天花板 =", max(r['c'] for r in rows))
# 候选特征组合（§2j）
def prof_ok(r): return r['n']==10 and r['lam']=='p45' and r['p2']==0 and r['p3']==0 and r['p5']==0
viol=[r for r in hi if not prof_ok(r)]
print("\n高天花板片中**违反**候选特征组合（n=10, Λ=p45, p2<p3+p4, p3<p45, p5<p3）的：", len(viol))
for r in viol[:12]: print("   ", r)
# 反向：满足候选组合但天花板低/高
ok=[r for r in rows if prof_ok(r)]
print("\n满足候选组合的片数 =", len(ok), " 其中天花板分布:",
      sorted(round(r['c'],4) for r in ok)[-8:])
# 按 n 看天花板上确界
import collections
d=collections.defaultdict(float)
for r in rows: d[r['n']]=max(d[r['n']], r['c'])
print("\n各 n 的最大天花板:", dict(sorted(d.items())))
# 按 nE/nFB 看
d2=collections.defaultdict(float)
for r in rows: d2[(r['nE'],r['nFB'])]=max(d2[(r['nE'],r['nFB'])], r['c'])
print("各 (E步, 兜底步) 的最大天花板:", dict(sorted(d2.items(), key=lambda kv:-kv[1])[:6]))
