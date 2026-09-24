# 口袋 2 角落中段（2≤k≤m−3）攻坚笔记 + P2K1/P2K-top 敌意复核报告

> 2026-09-22，agent-2（刻意验证者角色）。配套代码：code/adversarial_review.py、
> code/template_b0.py、code/template_jt.py、code/topk_check.py、code/midk_struct*.py。

## 1. 敌意复核判决（任务 1）

### 引理 P2K1（k=1，LP_ROUTE.md §1.1）——**成立**

逐行复核 + mini-LP 数值证伪（code/adversarial_review.py）：
- 核心链 {SS容量, s_u≥p−q₁(pair+j≤q₁), s_v>(5/4)a_m+(1/4)q₁(nofit, v≥1), danger, q₁≥t,
  a_m≥q₁, t≤2/5} 在 m=4..100 全 INFEASIBLE；
- 七个原料**逐一消融全部回 FEASIBLE**（无幻影约束、无冗余）；
- 计数恒等式 d=1+c+f≥1、a=1+c+e+2f≥1：枚举 m=4..30 全部 cnt 成立 + 独立消元推导一致
  （2d+e=a+c+1 与 a=d+e+f ⟹ d=c+f+1）；
- 严格性审查：pair 非严格即够用（链的严格性来自 nofit 与 danger 的严格）✓；
- 复核过程自纠一处：测试初版我把 s_u≥p−q₁ 误写为 s_u≥p+q₁（本家族宿疾），修正后全绿。
- 结论检查（base LP，k=1 全 cnt）：m=31..38 零反例（m=39,40 补跑中，topk_check.py）。

### 引理 P2K-top（k≥m−2，LP_ROUTE.md §1.1'）——**成立**，但有一处未登记原料

- 高端支：与 P2K1 同一条链（nofit(v) 因 v≥jj+1 适用），数值复核通过。
- 低端支 step1（j_u+j_v>3/2−2t）、step2（j_v>3/4−t，用低端升序）、step3（j_0>1−2t）
  全部 mini-LP INFEASIBLE 且原料逐一消融必要。
- **FLAG（已上板）**：低端支 step3 的 "pair 机 0 ⟹ j_0≥p−a_m" 用了 **a_m=s_0**（p_m=最小
  senior），而非 LP 登记的 a_m≤s_i。a_m=s_0 为真：初始 m 件=全局最大 m 件={p}∪{senior}，
  p_m=min 初始=最小 senior=s_0（senior≥junior 由递减到达）。建议 LP_ROUTE.md 显式引用。
- JJJ 计数步：低端 junior 全 >1−2t ⟹ JJJ 只能装 {t}∪{高端 junior} 共 m−1−jj≤2 件 <3
  ⟹ d=0，与 d=1+c+f≥1 矛盾 ✓；senior 并列不跨越 jj 边界（nofit 严格 ⟹ s_jj<s_{jj+1}
  严格）✓。
- 结论检查（build_close mon2+ammin，k=m−2,m−1 全 cnt）：m=31..38 零反例（39,40 补跑中）。

## 2. 新全 m 引理（任务 2 副产物）

### 引理 P2K-high（任意 k）：SS 箱大 mate 落入 nofit 区 ⟹ 矛盾

P2K-top 高端支的链其实**不需要 k≥m−2**：任何角落中，若某 SS 箱 {s_u,s_v}（a≥1 恒有）
的大 mate v 满足 v≥jj+1（nofit 区），则 P2K1 同链给出 t>1/2，与 t≤2/5 矛盾。
数值复核（m=4..100）全 INFEASIBLE ✓。
**推论**：任何口袋 2 角落（任意 k）的所有 SS 箱 senior 都在低端区 [0,jj] ⟹ **2a≤k**。

### 中段结构定理

若角落落在 2≤k≤m−3 且未被 P2K-high 杀死（即全部 SS senior 在低端），则
P2K-top 低端支链（保序+a_m=s_0+L≤1，与 k 无关）给出低端 junior 全 >1−2t，于是
JJJ 箱只能从 {t}∪{高端 junior} 装 ⟹ **3d≤m−k**。联立计数恒等式：
**2a+3d≤m ⟺ 5+5c+2e+7f≤m**（用 a=1+c+e+2f, d=1+c+f）。
这把中段残留压到很小一类 cnt（小 a、小 d）。

## 3. Template-b0：b=0 区全灭（全 m≥4、全 k、不解 LP）

b=0（无 SJ 箱）时 JJJ#0=（j₀,j₁,j₂)，且 m≥4 ⟹ a≥2 自动（a=1 ⟹ m=3）。统一证书
（RHS=−1/2−12MG）：

| 约束 | 权 | | 约束 | 权 |
|---|---|---|---|---|
| danger | 6 | | srt2 (s₂≤s₃) | 3 |
| pair₀ | 4 | | SS#1 (s₂+s₃≤1) | 3 |
| pair₁ | 2 | | JJJ#0 (j₀+j₁+j₂≤1) | 4 |
| srt0 (s₀≤s₁) | 4 | | j₁≥t | 2 |
| srt1 (s₁≤s₂) | 6 | | j₂≥t | 4 |

恒等式（各括号非负）：6D+4P₀+2P₁+4(s₁−s₀)+6(s₂−s₁)+3(s₃−s₂)+3(1−s₂−s₃)
+4(1−j₀−j₁−j₂)+2(j₁−t)+4(j₂−t) = −1/2。
**只用排序+pair+箱+danger+窄带，无 k 依赖、无单调匹配**（srt 链把 pair 下界从机 0,1
传递到 SS#1 的两件 senior）。m=4..30 全部 **4840** 个 b=0 (cnt,k) 精确验证通过
（code/template_b0.py）。

## 4. Template-JT：JJJ含t 家族（1,m−3,0,1,0,0) 在 k=m−1 全灭

JJJ 箱含 t：(j_{m−3}, j_{m−2}, t)。证书：danger:6, pair₀:3, pair₁:3, SS#0:3, JJJ:4,
j_{m−2}≥t:2, mon2₀:3, mon2_{1..m−4}:6, mon2_{m−3}:2（RHS=−1/2−12MG）。
（k=m−1 ⟹ mon2_{m−3} 存在。）code/template_jt.py 精确验证 **m=5..30 全通过**（2026-09-22 续跑完成）。

**该家族是中段的硬核**：仅用体积/装箱它饱和窗口下界 t>(m−1)/(4(m−2))（等式链恰为窗口），
杀它必须用 K 结构（fs/nofit/kcap）——其 k≤m−2 的证书呈 k 依赖形态（code/midk_struct2.py
提取，含 fs_j/nofit/SJ/j≤q₁ 混合支撑），统一符号证书未出。

### 残留域证书机制画像（2026-09-22 提取，家族 A (2,m−5,0,1,1,0) 在 k∈[4,m−4]）

支撑骨架：danger + pair（SS 箱两台）+ SS + nofit（某台 nofit 区的 SJ senior）+ SJ 箱
（该 senior 配某低端 junior）+ fs/kcap 关系（j_jj=q₁、j_i≤q₁、q₁≤a_m）+ JJJ + j≥t×3。
机制：nofit 给 s>K−q₁，SJ 容量反传 j≤1−(5/4)a_m−(1/4)q₁，pair+SS 正传 j≥2p−1−q₁，
夹出 q₁<4t−1，与 JJJ 的 t≤1/3 及 q₁≥t 矛盾。**nofit 靶机随 k 与箱分配而变**，
跨 k 的统一符号族未在本会话出现——这是残留域的实质障碍。

## 5. 残留地图（口袋 2 角落，全 m 视角）——2026-09-22 更新（Template-NF 后）

| 区域 | 状态 | 武器 |
|---|---|---|
| k=1 | ✅ 全 m 手证 | P2K1 |
| k≥m−2 | ✅ 全 m 手证 | P2K-top（+登记 a_m=s_0） |
| SS mate 在 nofit 区（2a≥k+1，任意 k） | ✅ 全 m 手证 | P2K-high |
| k≥b+2（b≥1，b+2≤m−2） | ✅ 全 m 符号证书 | 引理 2 模板 |
| b=0（全 k） | ✅ 全 m 符号证书 | Template-b0 |
| (1,m−3,0,1,0,0) @ k=m−1 | ✅ 全 m 符号证书 | Template-JT（m=5..30 精确） |
| **残留域内 k≤4a−1 且 2a+b≥k+1**（2≤k≤m−3, 2a≤k, b≥1） | ✅ 全 m 符号证书 | **Template-NF（新，9165 (cnt,k) 精确通过）** |
| m=4..11 全 (cnt,k) | ✅ 精确 LP 证书 | farkas_fixed 基线 |
| m=12..30 全 (cnt,k)；m=31..45 一步+保序 | ✅ LP/洞图 | 基线扫描/agent-4 |
| **最终残留：2≤k≤m−3 ∧ 2a≤k ∧ (k≥4a 或 2a+b≤k)** | 🔶 m≤45 计算闭合；m>45 开放 | 见 §6 |

### 6. Template-NF（残留域首部统一证书）

机制：SJ 箱+nofit 反传 j_{k'}<1−(5/4)a_m−(1/4)q₁；pair 正传 s_{k'}>p−1+(5/4)a_m+(1/4)q₁；
SS 箱+pair+j≤q₁ 给出 2p<2−(1/2)q₁ ⟹ p<1−q₁/4；danger ⟹ q₁<4t−1；t≤q₁ ⟹ t>1/3；
JJJ 三件各≥t ⟹ t≤1/3。矛盾。
证书权（RHS=−17MG<0，razor-thin 严格）：danger:8, pair_{k'}:4, pair_{mate}:4,
j_{mate}≤q₁:4, nofit_g:1, SJ#k':4, SS#(k'//2):4, q₁≤a_m:5, t≤q₁:2, JJJ#0:2, j≥t:2×3。
前台：k'=k−2a∈[0,min(b−1,2a−1)]，g=k（nofit 区首台）；mate=k'⊕1（SS 箱内伙伴）。
验证：code/a2_template_nf.py，m=4..30 全部 9165 个满足前台的 (cnt,k) 精确通过。

### 7. fs/nofit 必要性定理（为何残留域没有 k-无关统一证书）

**论断**：当前合法约束集上，k 相关行 = fs 组（j_jj=q₁、s_jj+q₁≤K）与 nofit 组（i>jj）；
其余约束组（senior 界、junior 窄带、pair、kcap、装箱、srt、danger）全部 k-不变。
对 m=12/14/16 的全部 66 个残留 (cnt,k)（NF 后仍未覆盖者），消融 fs+nofit 后 LP 全部
回 feasible ⟹ **残留域每个 (cnt,k) 的任何不可行证书必须引用 k 相关行** ⟹ 不存在
k-无关的统一权向量证书（在现约束集上）。残留证书实测为**路径形**（nofit/SJ/srt 多跳、
权沿机器序递减，支撑随 |k−4a| 增长）——统一化只能走"算法式路径模板"（构造路径+
望远镜不变量证明）或逐 (m,k) 计算。注：此论断不排除未来新增 k-不变合法约束改变格局。

**被取代的旧 §5 表述**（2026-09-22 前）：中段残留曾记为 "2≤k≤m−3 ∧ k<b+2 ∧ b≥1"，
现由 Template-NF 覆盖其 k≤4a−1 且 2a+b≥k+1 部分；最终残留收紧为
"2≤k≤m−3 ∧ 2a≤k ∧ (k≥4a 或 2a+b≤k)"（满足 2a≤k、3d≤m−k 结构约束）。

## 8. 收口：K<1 链 + 全 (cnt,k) 符号覆盖图（2026-09-22 12 时，agent-2）

### 8.0 两个先行击杀

- **Class II（2a+b≤k）纯计数为空**：2a+b≤k ⟹ c=m−1−2a−b≥m−1−k ⟹ d=1+c+f≥m−k
  ⟹ 3d≥3(m−k)>m−k（m−k≥3），与中段结构定理 3d≤m−k 矛盾。∎
  验证：a2_residual_final.py 扫描 m=4..40 全部 7832 个 class II (cnt,k) 逐一确认 3d>m−k。
- **P2S 修剪**（引理 P2S：q₁ 不入 JJJ 箱，SEMANTICS VALID，本次复核其证明无误）：
  规范代表中 jj=k−1 的池位落入 JJJ 池段 [b, b+3d−1] ⟺ k∈[b+1, b+3d] 的 (cnt,k) 直接不可能。

### 8.1 引理 K<1（Template-K1）：k≤b ⟹ 角落不可能

k≤b ⟹ jj=k−1≤b−1 ⟹ q₁ 的池位 jj 是 SJ 伙伴位：存在 SJ 箱 (s_g, q₁)，g=2a+jj=2a+k−1。
g>jj（a≥1 恒真）且 g≤m−2（k≤b ⟹ 2a+k≤2a+b≤m−1）⟹ g 在 nofit 区：s_g+q₁>K。
联立 SJ 容量 s_g+q₁≤1 ⟹ **K<1** ⟹ a_m+q₁<4/5 ⟹ q₁<2/5。
SS 箱（a≥1）+pair+j≤q₁ ⟹ 2(p−q₁)≤1 ⟹ p<1/2+q₁<9/10；danger ⟹ t>5/4−9/10=7/20>1/3；
JJJ 箱（d≥1）三件各≥t ⟹ t≤1/3。矛盾。∎
证书（支撑子矩阵+求解器产权，精确复核）：danger:8, pair0:4, pair1:4, j0≤q₁:4, j1≤q₁:4,
nofit_g:2, SJ#jj:8, SS#0:4, q₁≤a_m:1, q₁≤j_jj:4, t≤q₁:2, JJJ#0:2, j≥t×3:2；RHS=−17MG
（常数项恰消，razor-thin 靠 danger/nofit/pair 严格性）。验证：a2_template_k1.py，
**m=4..30 全部 9666 个 k≤b (cnt,k) 精确通过**。

### 8.2 全 (cnt,k) 符号覆盖图（口袋 2 角落，全 m≥4）

| 区域 | 武器 | WLOG 依赖 |
|---|---|---|
| k=1 | P2K1（手证，复核通过） | 无 |
| k≥m−2 | P2K-top（手证，复核通过；登记 a_m=s₀） | 无 |
| SS mate 在 nofit 区（2a≥k+1） | P2K-high（手证） | 无 |
| Class II（2a+b≤k，2a≤k） | 纯计数为空（§8.0） | 无 |
| k∈[b+1,b+3d] | P2S 修剪（§8.0） | 见下注 |
| b=0 | Template-b0 | 规范代表 |
| 2≤k≤m−3 ∧ b≥1 ∧ k≤b | **Template-K1（引理 K<1）** | 规范代表 |
| 2≤k≤m−3 ∧ b≥1 ∧ k≥b+3d+1（≥b+2） | 引理 2 模板（b≤m−4 时） | 规范代表 |
| (1,m−3,0,1,0,0)（b=m−3）@ k=m−1 | Template-JT | 规范代表 |

覆盖证明：b=0 → b0；b≥1 ∧ 2≤k≤m−3：k≤b → K1；k≥b+1 → P2S 逼出 k≥b+3d+1≥b+2
→ 引理 2（b≤m−4）；b=m−3 ⟹ cnt=(1,m−3,0,1,0,0) ⟹ k≤m−3 由 K1、k=m−2 由 P2K-top、
k=m−1 由 JT。**故 LP 框架内全 (cnt,k) 符号闭合，无需逐 m 计算**。

### 8.3 诚实声明（WLOG 边界）

- 规范代表 WLOG（"装箱固定分组"，SEMANTICS 行11 SUSPECT）：Lemma 2/b0/K1/JT/NF 的箱内容
  指派（如 K1 的"SJ 箱 #jj 恰配 q₁"）依赖它。WLOG-free 的手证只覆盖 k=1、k≥m−2、
  P2K-high、Class II、P2S；**其余区域的全 m 闭合条件于该 WLOG**（与整条 LP 证书路线同一
  基础；proof.md 主证明不依赖它）。K1 的 WLOG-free 版需 q₁ 的 SJ 箱伴在 nofit 区——不恒真，
  留有 case split 的开放细化空间。
- 若 WLOG 被证：本表全线升级为无条件全 m 符号证明。若被证伪：回落到逐 m LP（m≤45 已闭）。
- K1 的 t≤1/3 只用"存在 3 件池物品共箱 ≤1"（d≥1 恒真，物品身份无关）✓ WLOG-free 部分。

## 9. 五模板族的 ∀m 符号验证（2026-09-22 13 时，agent-2）

**结论：五族（Lemma2 / b0 / JT / K1 / NF）的望远镜恒等式与索引存在性对任意 m≥4 成立**
——系数簿记与 regime 分解由 `code/a2_forall_m.py` 符号核验（10/10 全绿：列平衡 Aᵀy=0、
btᵀy=0、bcᵀy<0）；索引簿记逐条如下（一行一式）。由此口袋 2 中段的符号闭合从有限 m
升级为 ∀m（在 §8.3 的规范代表 WLOG 边界内）。

### 9.1 望远镜恒等式（m-无关部分）

每族的证书都是固定权的线性组合；列平衡只涉及**局部索引**的变量。链状部分一律用
**望远镜恒等式**：Σ_{i=u}^{v}(j_i − j_{i+1}) = j_u − j_{v+1}（一行归纳：部分和
S_N = j_u − j_{u+N}）。各族的变量系数表（sympy 精确核验，a2_forall_m.py）：

- **Lemma2**（3 regimes）：RHS=−1/2−12MG。j_0: −3+3=0；j_1: −3−3+6=0；
  j_r (2≤r≤b−1): −6+6=0（链中段的内部均匀性）；j_b: 4−6+2=0；j_{b+1}: 4−2−2=0；
  j_{b+2}: 4−4=0。p: −6+6=0；t: −6+2+4=0；s_0,s_1: ∓3±3=0。regime b=1/b=2 单独核验（链退化）。
- **b0**（b=0 唯一 regime）：RHS=−1/2−12MG。s_0: −4+4；s_1: −2−4+6；s_2: −6+3+3；
  s_3: −3+3；j_0: −4+4；j_1: −2−2+4；j_2: −4+4；p,t 同 Lemma2。
- **JT**（cnt=(1,m−3,0,1,0,0)，JJJ=(j_{m−3},j_{m−2},t) 含 t）：regimes m=5 / m≥6。
  t: −6+2+4=0（JJJ 的 t 系数 4）；j_{m−3}: 4−6+2=0；j_{m−2}: 4−2−2=0；链 6(j_1−j_{m−3})。
- **K1**（k≤b；两 regime：JJJ 含/不含 t）：RHS=−17MG（razor-thin）。p: −8+8=0；
  q₁: −4−4+1+4+5−2=0；a_m: 5−5=0；s_g: −4+4=0；j_jj: 4−4=0；t: −8+2+6=0（含 t regime 换 2+4+2）。
- **NF**（残留域首部；两 regime 同上）：RHS=−17MG。q₁: −4+1+5−2=0；s_k: −4+4=0；
  s_kp: −4+4=0；s_mate: −4+4=0；j_kp: −4+4=0；j_mate: −4+4=0。

### 9.2 索引存在性簿记（firing 条件 + cnt 守恒 ⟹ 支撑行 ∀m 合法）

守恒：2a+b+c=m−1、b+3d+2e+f=m；恒真事实 a≥1、d≥1（§3 结构事实）。nS=m−1；mon2_i
存在 ⟺ i≤jj−1=k−2（build_close）；nofit_i 存在 ⟺ jj+1≤i≤m−2；SJ#i 存在 ⟺ 0≤i≤b−1；
SS#i 存在 ⟺ 0≤i≤a−1；JJJ#0 存在 ⟺ d≥1✓；j_i 相关行存在 ⟺ 0≤i≤m−2。

- **Lemma2**（fires: b≥1, b+2≤m−2, k≥b+2）：SS#0（a≥1✓）；JJJ#0（d≥1✓）且其内容
  j_b,j_{b+1},j_{b+2} 为机器 junior ⟺ b+2≤m−2（firing ✓）；mon2_0..mon2_b 存在 ⟺
  b≤k−2 ⟺ k≥b+2（firing ✓）；pair0/pair1 与 j_{b+1},j_{b+2}≥t 行 ⟺ 1、b+2≤m−2✓（m≥4）。
- **b0**（fires: b=0）：b=0 合法 cnt 仅在 m≥5（b=0∧a=1 ⟹ m=3；m=4 无 b=0 cnt，数值确认
  m=4..30）⟹ s_3 存在（nS≥4）✓；SS#1 存在 ⟺ a≥2 ✓（b=0∧m≥5 ⟹ a≥2）；JJJ#0=(j_0,j_1,j_2)
  机器 junior ⟺ 2≤m−2 ⟺ m≥4 ✓。
- **JT**（cnt=(1,m−3,0,1,0,0)，k=m−1）：cnt 合法 ⟺ m≥5；mon2_{m−3} 存在 ⟺ m−3≤jj−1=m−3
  恰取等 ✓；j_{m−2} 存在（m−2=nS−1 ✓）。
- **K1**（fires: 2≤k≤m−3, k≤b）：g=2a+k−1；g>jj ⟺ 2a≥1 ✓；g≤m−2 ⟺ m−2−g=b+c−k≥0
  ⟸ k≤b（sympy 恒等式确认）✓；SJ#jj 存在 ⟺ jj≤b−1 ⟺ k≤b ✓，其池伙伴即 j_jj=q₁（fs）✓。
- **NF**（fires: 2a≤k, kp=k−2a∈[0,min(b−1,2a−1)], 2≤k≤m−2）：nofit_k 存在 ⟺ k≤m−2 ✓
  且 k=jj+1 在 nofit 区 ✓；SJ#kp 存在 ⟺ kp≤b−1 ✓；SS#(kp//2) 含 kp 与 mate=kp⊕1：
  kp 偶 ⟹ (kp,kp+1)，kp 奇 ⟹ (kp−1,kp)，均 ⊆ [0,2a−1]（kp≤2a−1；kp=2a−1 为奇，落
  bin #(a−1) ✓）。

### 9.3 边界 m=4,5 与小 regime

m=4：无 b=0 cnt；Lemma2 需 b+2≤2 即 b≤0 且 b≥1——无 firing cnt（全部情形由 k=1/k≥m−2
手证与 b0/NF 覆盖，m=4..30 全覆盖扫描残留 0 可证）。m=5：JT 的链退化为单节 mon2_1
（权 6）+ mon2_2（权 2），已单独核验 ✓。K1/NF 在 m=4,5 的 firing 情形均由数值验证覆盖
（m=4..30 全量精确通过记录）。

**总计**：∀m 符号部分（恒等式+索引）成立；有限 m 记录 m=4..40 精确通过（150,801 例精益
+此前真行验证），两者互补：∀m 证明覆盖任意 m，有限记录兜底簿记实现细节。
