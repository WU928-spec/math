# a4_region_cert.py —— 区域证书管线（fallback 预备）

**用途**（JEL.md §③ 子问题2 fallback）：若 region-portability 猜想失败（模板权重不可搬运），
逐区域重解证书。输入胞腔极小形的箱内容（变量索引），构造"角落 LP + 该区域装箱容量行"，
求解并出精确常数证书。

## 接口

```python
from a4_region_cert import region_cert, canonical_bins, build_region_rows, validate_bins
st, cert = region_cert(m, cnt, k, bins)   # st ∈ 'cert' | 'feasible' | 'ratfail'
```

- `bins` 格式：`{"SS":[(u,v)], "SJ":[(i,p)], "JJJ":[(p,q,r)], "JJ":[(p,q)]}`
  - senior 索引 `u,v,i ∈ 0..nS-1`（nS=m−1）；junior 槽位 `p,q,r ∈ 0..nS`，**nS = t 槽**；
  - 组数必须等于 cnt=(a,b,c,d,e,f) 的 (a,b,d,e)；c（独箱 senior）、f（独箱 junior）不产生行；
  - senior 索引在 SS∪SJ 互不相交；junior 槽位全局至多出现一次（非法输入抛 ValueError）。
- `canonical_bins(m,cnt)`：rows_fixed 默认规范形转本格式（对照/冒烟用）。
- 构造 = `fast_lp.rows_fixed(m,cnt,k,use_order=True)` 去默认装箱行 + 输入箱形容量行
  （行名唯一编号 `SS#0/SJ#3/...`，规避 opt_db P02 重名陷阱）；求解复用
  `float_cert_rows` + `exact_verify_support`（浮点定位 + 支撑行 Fraction 精确验证）。
- CLI：`python a4_region_cert.py cert '<bins_json>' m '[a,b,c,d,e,f]' k`；
  冒烟：`python a4_region_cert.py smoke`。

## 冒烟结果（m=12 cnt=(2,7,0,1,1,0) k=11）

- 规范形 → cert（13 项）✓（与主管线闭合一致）；
- 合法非规范变体A（SS 交叉配对+SJ 槽对调）→ cert（15 项）；变体B（JJJ 含 t 槽）→ cert（13 项）
  ——该案例闭合对箱形扰动稳健（保序约束承重）；
- 阴性对照：use_order=False 规范形 → feasible（与"旧一步洞"一致 ✓，编码非空洞）；
- 非法输入（组数不足/senior 重复/junior 槽位重复）全部拒绝 ✓。

**状态：备胎管线，试点若证可搬运则不进主证明。** 依赖 fast_lp.py（VALID）。
