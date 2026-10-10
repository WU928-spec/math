import glob, sys
rows, seen = [], set()
for f in sorted(glob.glob("fam10_leaves2_*.txt")):
    if "_all" in f: continue
    for ln in open(f):
        ln = ln.strip()
        if ln and ln not in seen:
            seen.add(ln); rows.append(ln)
out = "fam10_leaves2_all.txt"
open(out, "w").write("\n".join(rows) + ("\n" if rows else ""))
print(f"{len(rows)} 条去重片 → {out}")
