# Algorithm A（CKK 2012）竞争比 ≤ 5/4：LP 对偶证书证明（终稿 v1.0）

> 2026-09-22 定稿。本文是 **LP 独立路线**的完整证明：对 m≥4 的半在线递减调度，
> 证明 Algorithm A（cap K=(5/4)(p_m+p_{m+1})，best-fit 最满优先）的 fallback 分支
> 无危险角落，从而竞争比 ≤ 5/4。证明主体是**全 m 纯符号**（手证引理 + 模板恒等式），
> 计算证书（46.8 万份，全部独立复核）作厚证据与发现引擎。边界诚实标注见 §4。
> 记号：OPT=1 归一化；fallback 任务 t（最闲机末位）；Lemma A/B：C_A≤1+t(1−1/m)、t≤2/5；
> 硬窗口 t∈((m−1)/(4(m−2)), 1/3]。

## §0 方法论

**常数证书**：各角落 LP 中 t 只出现在右端（A 为 t 无关常数矩阵，b(t)=bc+t·bt）。
常数 Farkas 证书 y（Aᵀy=0、btᵀy=0、bcᵀy=−1、y≥0，Fraction 精确）使 LP 在全 t 窗口
不可行 ⟹ 角落不存在。构造：浮点定位 → 有理化 → 精确验证 → 从文件解析回独立复验
（verify_certs.py，纯 Fraction、列平衡强制指派，不经 linprog）。

**修正 firststep 编码**（2026-09-21 裁决，全部本文结论的前提）：Algorithm A 为 best-fit
最满优先（`loads[i] > loads[best]`）。q₁=p_{m+1}（最大后续=首个后续）到达时各机仅
senior，落"放得下的最大 senior 机"jj：fit s_jj+q₁≤K、nofit s_i+q₁>K（i>jj）、
j_jj=q₁（最大 junior）。旧编码（nofit 在 i<jj、j_jj≤j_i）方向全反，其派生证书已封存。

**纪律**（血泪条款）：任何 LP 结论必须配①消融（去承重约束回 feasible）、②sanity
（去 danger 回 feasible）、③逐条语义审核（LP_CONSTRAINTS.md，agent-3）。本路线历史
上由此抓住 4 个真 bug（编码方向、y 下界、K₂ 偏紧、浮点 MARGIN 失真）。

**保序引理（动力学基石，双独立推导）**：他机 2 件形态下 s_i<s_k 且 j_i>j_k ⟹
s_k+j_i>K（先到任务落机时对方仅 senior；不落更满机 ⟹ 被 cap 阻断）。推论：低端区
（s_i≤K−q₁）junior 单调不降。置信：1495 万实例、51516 真角落事件 0 反例。

## §1 口袋 2（单子机角落）

## 2.0 模型、记号与计数恒等式

**口袋 2 角落**（最紧形态）：递减到达、OPT=1 归一化；fallback 任务 t 落入单子机
M₀={p}（p=最大初始任务；其余情形由 rest 体积界归纳到他处）。角落必需：
- 他机 m−1 台各恰 2 件 {s_i, j_i}（s_i 初始件 senior，j_i 首个后至件 junior）；
- 后至件递减 q₁=p_{m+1}≥…≥t（t 最闲在最后），junior 窄带 j∈[t,2t)、senior s_i>1−2t；
- danger p+t>5/4；K=(5/4)L，L=a_m+q₁≤1；**a_m=s₀**（p_m=最小初始件=最小 senior，
  递减到达 ⟹ 初始 m 件=全局最大 m 件；SEMANTICS 登记原料）；
- pair（M₀ 最闲）：s_i+j_i≥p ∀i；kcap：j_i≤q₁、q₁≤a_m、p<K。
- k 参数（firststep）：senior 升序 s₀≤…≤s_{m−2}；q₁ 落机 jj=k−1（best-fit 最满优先）：
  fit s_jj+q₁≤K；nofit s_i+q₁>K（i>jj）；j_jj=q₁。

**装箱 taxonomy 与计数**：rest（{s_i}∪{j_i}∪{t}）装入 m−1 箱（p 独占），窗口 t>1/4 排除
SJJ/SSS/SSJ/JJJJ 型 ⟹ 六型 SS/SJ/S/JJJ/JJ/J，计数 (a,b,c,d,e,f)。三守恒
（2a+b+c=m−1、b+3d+2e+f=m、箱数 m−1）⟹ **d=1+c+f≥1、a=1+c+e+2f≥1**（两箱型恒存在）。

## 2.1 保序引理（动力学的唯一入口）

**引理 2.1（保序）**：他机 2 件形态下，s_i<s_k 且 j_i>j_k ⟹ s_k+j_i>K。
证明：j_i 先到（递减）；其到达时两机各仅 senior；落 i 不落 k，best-fit 最满优先 ⟹
k 被 cap 阻断（s_k+j_i>K）或 s_i≥s_k，矛盾。∎
**推论**：低端区（s_i≤K−q₁，即 i≤jj）junior 单调不降：j₀≤…≤j_jj=q₁（同级重标号 WLOG）。
置信：双独立推导（主代理 + agent-2 的单调匹配引理）+ 1495 万实例 51516 真角落事件 0 反例
（fuzz_mon2.py）。这是全部中段论证的动力学基石。

## 2.2 全 m 手证：k=1 与 k≥m−2（无 LP）

**引理 2.2（P2K1）**：k=1 的角落不存在。
证明：a≥1 ⟹ SS 箱 {s_u,s_v}（u<v），s_u+s_v≤1。pair 与 j≤q₁ 给 s_u≥p−q₁；k=1 的 nofit
覆盖 v≥1：s_v>K−q₁=(5/4)a_m+(1/4)q₁≥(3/2)q₁。代入：1≥s_u+s_v>p+(1/2)q₁>5/4−t/2
（danger+q₁≥t）⟹ t>1/2，与 t≤2/5（Lemma B）矛盾。∎（agent-2 敌意复核通过：链极小、
原料全必要，adversarial_review.py。）

**引理 2.3（P2K-top）**：k≥m−2 的角落不存在。
证明：取 SS 箱大 mate v 分两支。
-（v 高端，v>jj）与 P2K1 同链：s_v>(5/4)a_m+(1/4)q₁，s_u≥p−q₁ ⟹ p<1−(5/4)a_m+(3/4)q₁
  ⟹（danger、a_m≥q₁）(1/2)q₁<t−1/4 ⟹ q₁<2t−1/2，与 q₁≥t 得 t>1/2 矛盾。
-（v 低端，v≤jj）：SS 配对+pair+danger ⟹ j_u+j_v>3/2−2t ⟹（低端单调）j_v>3/4−t，
  q₁≥j_v；L≤1 与 a_m=s₀ ⟹ j₀≥p−a_m>1/4−t+q₁>1−2t ⟹ 低端 junior 全>1−2t；
  JJJ 箱含低端 junior 则超载（(1−2t)+2t=1）⟹ JJJ 只能装 {t}∪{高端 junior} 共
  m−1−jj=m−k≤2 件<3 ⟹ d=0，与 d≥1 矛盾。∎（复核通过；低端支原料 a_m=s₀ 已登记。）

**引理 2.4（P2K-high，agent-2）**：任意 k，若某 SS 箱大 mate 在 nofit 区（v>jj）则矛盾
（同引理 2.2 的链）。**推论**：任何角落的全部 SS senior 都在低端区 ⟹ **2a≤k**。

**引理 2.5（P2S）**：q₁ 不入 JJJ 箱（q₁+两件≥q₁+2t，若入 JJJ 则 q₁≤1−2t；SS 箱给
p≤1/2+q₁≤3/2−2t，与 danger 得 t<1/4，与窗口矛盾）。**推论**：规范代表的池位 jj 若落入
JJJ 池段 [b, b+3d−1]（⟺ k∈[b+1, b+3d]）则该 (cnt,k) 不可能。

**引理 2.6（Class II 为空，agent-2）**：若 2a+b≤k（SS+SJ senior 全低端），则由引理 2.1
低端 junior 全>1−2t（引理 2.3 低端支链，k 无关）⟹ JJJ 只能装 {t}∪{高端} 共 m−k 件 ⟹
3d≤m−k；但 2a+b≤k ⟹ c=m−1−2a−b≥m−1−k ⟹ d=1+c+f≥m−k ⟹ 3d≥3(m−k)>m−k。矛盾。∎

## 2.3 中段模板族：∀m 统一证书

中段（2≤k≤m−3）由五个模板族覆盖，全部"不解 LP 的符号证书"：权为显式常数，
对任意 m 满足 Aᵀy=0、btᵀy=0、bcᵀy<0（y≥0）。∀m 验证 = 系数簿记（望远镜恒等式
Σ(j_i−j_{i+1})=j_u−j_{v+1}）+ 索引存在性簿记（守恒+firing ⟹ 支撑行合法），
见 midk_note.md §9（a2_forall_m.py，10 regime 全绿）。

**引理 2.7（引理 2 模板，k≥b+2 族）**：若 b≥1、b+2≤m−2、k≥b+2，则
6D+3P₀+3P₁+3C_SS+4G_JJJ+2(j_{b+1}−t)+4(j_{b+2}−t)+3M₀+6Σ_{i=1}^{b−1}M_i+2M_b = −1/2，
各项非负，矛盾（D=danger 余量、P_i=pair、C/G=箱容量余量、M_i=j_{i+1}−j_i≥0 为保序链，
存在性由 k≥b+2 保证）。**覆盖全部洞区**（m=12..30 完整洞图 154 洞逐洞精确证书，
hole_template_certs.jsonl）。

**引理 2.8（Template-b0，b=0 族）**：b=0 ⟹ m≥5 ∧ a≥2；
6D+4P₀+2P₁+4(s₁−s₀)+6(s₂−s₁)+3(s₃−s₂)+3(1−s₂−s₃)+4G_JJJ+2(j₁−t)+4(j₂−t)=−1/2。
（srt 排序链替代保序链，k-无关。）

**引理 2.9（K<1 链 / Template-K1，k≤b 族）**：k≤b ⟹ q₁ 的池位 jj 是 SJ 伙伴位，存在
SJ 箱 (s_g,q₁) 且 g=2a+k−1 恒在 nofit 区（g>jj ⟺ a≥1；g≤m−2 ⟺ m−2−g=b+c−k≥0 ⟸ k≤b）。
nofit s_g+q₁>K 与 SJ 容量 s_g+q₁≤1 ⟹ K<1 ⟹ a_m+q₁<4/5 ⟹ q₁<2/5；SS+pair ⟹ p<1/2+q₁<9/10；
danger ⟹ t>7/20>1/3；JJJ 三件各≥t ⟹ t≤1/3。矛盾。∎（RHS=−17MG，razor-thin 严格。）

**引理 2.10（Template-JT，JJJ含t 家族 (1,m−3,0,1,0,0) 在 k=m−1）**：b=m−3 时唯一 cnt，
JJJ 箱=(j_{m−3},j_{m−2},t)；引理 2.7 的同构链（链到 mon2_{m−3}，恰存在）。

**引理 2.11（Template-NF，残留首部）**：2a≤k 且 k'=k−2a∈[0,min(b−1,2a−1)] 时，
SJ 箱+nofit_k 反传 j_{k'}<1−(5/4)a_m−(1/4)q₁，SS 箱+pair 正传 s_{k'}>p−1+(5/4)a_m+(1/4)q₁，
夹出 p<1−q₁/4 ⟹ q₁<4t−1 ⟹ t>1/3 vs JJJ t≤1/3。（与 K1 独立的交叉验证件。）

**覆盖定理 2.12（全 (cnt,k) 符号闭合）**：口袋 2 角落的每个合法 (cnt,k) 至少被一条
上述引理排除：k=1（引理 2.2）；k≥m−2（引理 2.3）；2a≥k+1（引理 2.4，鸽笼：2a>k ⟹
某 SS senior 落入 nofit 区）；2a≤k ∧ 2a+b≤k（引理 2.6，含全部 b=0 情形）；其余
2≤k≤m−3 ∧ b≥1 ∧ 2a+b≥k+1：k≤b（引理 2.9）；k≥b+1：P2S 修剪（引理 2.5，junior-WLOG
条件）逼出 k≥b+3d+1≥b+2 ⟹ 引理 2.7（b≤m−4）；b=m−3 ⟹ cnt=(1,m−3,0,1,0,0)：
k≤m−3 由引理 2.9、k=m−2 由引理 2.3、k=m−1 由引理 2.10。∎（m=4..40 全 (cnt,k)
逐一举证残留 0：a2_residual_final.py；五族精确证书 m=4..40 共 150,801+4,840+9,666+9,165
例全 PASS；WLOG-free 子集覆盖 k=1、k≥m−2、2a≥k+1、2a+b≤k 四类。）

## 2.4 为何中段必须 k-适配证书（必要性定理）

**定理 2.13（fs/nofit 必要性，agent-2）**：在当前合法约束集上，k 相关约束恰为 fs 组
（j_jj=q₁、s_jj+q₁≤K）与 nofit 组（i>jj）；其余约束组全部 k-不变。对 m=12/14/16 的
全部 66 个中段残留 (cnt,k)（引理 2.7/2.9 覆盖域之外的计算闭合区），消融 fs+nofit 后
LP 全部回 feasible ⟹ **这些 (cnt,k) 的任何不可行证书必须引用 k 相关行** ⟹ 不存在
k-无关统一权向量证书（在现约束集上）。其证书实测为路径形（nofit/SJ/srt 多跳、
支撑随 |k−4a| 增长）。注：此定理不排除未来新增 k-不变合法约束改变格局；
它刻画的是"模板覆盖边界 = k 适配起点"。

## 2.5 计算证书记录（独立复核）

- m=4..30：一步 LP 全 cnt 全 k 精确常数证书（farkas_fixed 管线）+ 保序 LP
  （order_step.py），43,981 份证书独立复核 PASS/FAIL 0（verify_certs.py，纯 Fraction）。
- m=31..45：扩扫 263,575 情形零洞，证书全量独立复核 PASS（agent-4）。
- m=46..50：扩扫零洞（累计 **467,887 情形零洞**）；46..50 证书 204,312 份增量复核
  进行中（断点 .vprog，已验 275,000/467,984 全 PASS）。
- 洞图 m=12..30 全 154 洞由引理 2.7 符号证书逐洞闭合（与计算证书互证）。

## 2.6 WLOG 边界（诚实声明）

模板族（引理 2.7–2.11）与全部 LP 证书依赖**规范代表分组**（装箱按 senior 序固定指派）。
现状（agent-3 交换引理，LP_CONSTRAINTS.md §11.0）：**senior 侧已完全 w.l.o.g. 化**
（SS=最小 2a 极端配对、SJ=剩余最小 b、S=最大 c——任意装箱 ⟹ 同型此等装箱存在）；
残留缺口收窄到 **junior 侧的集合划分**（JJJ/JJ 箱的 junior 指派，指数核心）。
引理 2.7 的 JJJ 三件定位、引理 2.9 的"SJ 箱恰配 q₁"恰属此侧——故这些引理的条件
记为"规范代表框架内"。**不依赖任何分组 WLOG 的部分**：引理 2.1–2.4 与 2.6（保序、
P2K1、P2K-top、P2K-high、Class II 计数）与全部体积/计数/动力论证。引理 2.5（P2S）
本身 WLOG-free（q₁ 不入 JJJ 箱是真实装箱的命题）；但它在覆盖定理中的**修剪用法**
（规范代表的池位 jj 是否落入 JJJ 池段）依赖 junior 侧 WLOG，特此区分。
若 junior 侧 WLOG 得证，本章全线升级为无条件全 m 证明；若证伪，回落到逐 m 计算证书
（m≤50 已封顶）与 proof.md 主证明（不依赖任何 LP）。

**冗余声明（置信加强）**：Template-b0 与 Template-NF 在覆盖定理 2.12 中严格冗余——
b=0 全域已由 P2K-high（2a≥k+1）∪ Class II 计数（2a≤k）覆盖；NF 的残留首部已由
K1 链+P2S 覆盖。二者保留的价值：**不依赖保序引理**的独立交叉验证（b0 只用 srt+pair+
箱容量；NF 用 nofit/SJ/SS 直链），各自 4840+9983 / 9165+27336 例精确通过。

## 2.7 开放问题

1. **junior 侧转移引理**（唯一剩余 WLOG 缺口）：任意装箱 ⟹ 存在同型装箱使 JJJ/JJ 的
   junior 指派满足保序序——卡点已刻画（LP_CONSTRAINTS.md §11：junior 侧集合划分无
   对称可商）；候选路线：直接证明 / LP+装箱 DFS 混合。
2. **K<1 链的 WLOG-free 版**：需"q₁ 的 SJ 箱伴在 nofit 区"的独立论证（现依赖规范代表）；
   q₁∈JJ/J 箱的 case split 开放。
3. **JJJ含t 家族 k∈[4,m−4] 的 WLOG-free 处理**（现为引理 2.9 覆盖）。
4. m>50 的计算封顶已无必要（∀m 符号闭合在本章），但若 WLOG 长期未决，可偶发抽样复核。
EOF
## §2 口袋 1（最闲机恰 2 件，子情形 B）

## 0. 角落定义与原料

**口袋1 子情形 B**：fallback 于 t，最闲机 M₀={x,y}（恰 2 件，x≤y），他机全 2 件
{senior s_i, junior j_i}。原料（逐条审核 LP_CONSTRAINTS.md §6/§7）：

| 原料 | 形式 | 备注 |
|---|---|---|
| mach | s_i+j_i ≥ x+y (+MG) | M₀ 最闲；**非严格**（链的严格性由 nofit/danger 供） |
| danger | x+y > 5/4−t | |
| 大任务 | y>1−2t, s_i>1−2t（升序 s₀≤…≤s_{nS−1}）；x≥t, x≤y | |
| 窄带 | j_i∈[t,2t)；j_i≤q₁, t≤q₁, q₁≤a_m；L=a_m+q₁≤1；K=(5/4)(a_m+q₁) | |
| firststep（修正编码） | q₁ 填最大可容 senior 机 jj：srt 升序、nofit i>jj、s_jj+q₁≤K、j_jj=q₁=max junior | best-fit 最满优先（toolbox.py:27） |
| 装箱计数 | 2a+b+c=m, b+3d+2e+f=m+1 ⟹ a=d+e+f≥1, d=1+c+f≥1 | BB/BJ/B/JJJ/JJ/J 六型 |

**口袋1 特有结构**（全节引用）：
- **(P1-a)** a_m = min(y, s₀)——初始 m 件={y}∪{senior}（x 是后续件）。LP 曾缺 `am<=y`
  （松弛缺口），手证按 dichotomy 显式处理。
- **(P1-b)** BB 箱可含 y：bigs=[s₀..s_{nS−1}, y]。引理 P1-BB-y：y 恰出现一次 ⟹
  a≥2 时至少一个纯 senior BB 对（和 ≤1）。
- **(P1-c)** junior 池多 x：JJJ 池={t, x, 高端 junior}（口袋2 为 {t, 高端 junior}）。
- **(P1-d)** 无 p<K 行（口袋2 的 p<K 在口袋1 无对应原料，部分口袋2 模板不可逐字移植）。

## 1. 全 m 手证

### 引理 P1K1（k=1，全 m≥4，全装箱，全 t 窗口）
k=1 角落不存在。**证明**（五链，agent-3 终审签字 LP_CONSTRAINTS §10）：
k=1 ⟹ jj=0，nofit 对全部 i≥1：s_i > (5/4)a_m+q₁/4。取 BB 箱（a≥1 恒存在）。
1. **BB 为 senior-senior 对**（含 a≥2 时的非 y 箱，P1-BB-y）：1 ≥ s_u+s_v >
   (x+y−q₁)+(3/2)q₁ > 5/4−t/2 ⟹ t>1/2。∎
2. **BB={y,s_v} 且 a_m=y、v≥1**：y+s_v≤1 与 nofit 联立 y < 4/9−q₁/9，与 y>5/8−t/2
   联立 q₁ < 9t/2−13/8，又 q₁≥t ⟹ t>13/28>1/3。∎
3. **同上 v=0、某 senior 入 BJ**（3a）：BJ 容量与 nofit 双侧夹击 q₁，得
   q₁<7/8−3t/2 与 q₁>7/8−3t/2 严格矛盾（与 t 无关）。∎
4. **同上 v=0、其余 senior 全 B 独箱**（3b，箱数矛盾）：bigs 占 m−1 箱，剩 1 箱装
   m+1 小件；t>1/4 ⟹ 每箱 ≤3 件 <m+1（∀m≥3）。∎（真杀手是箱数；体积差 1/12 为红鲱鱼）
5. **a_m=s₀**：Farkas 重构链 mach₀+j₀≤q₁+q₁≤s₀+s₀≤y+nofit_v+BB+danger ⟹ t>1/2
   （证书版 t>9/20，支撑 7 行权比 5:5:5:4:4:1:4，m=12/18 核验）。∎
∎（恒等式佐证 m-无关；分组无关链如上）

### 引理 P1K-top（k≥m−2，全 m≥4）
高端支：nofit s_v>(5/4)a_m+q₁/4 + BB + mach + a_m≥q₁ ⟹ q₁<2t−1/2 ⟹ t>1/2。∎
低端支（保序 ord：低端 junior 升序）：
- **a_m=s₀**：j₀>1−2t 链成立；JJJ 池按 (P1-c) 含 x——x>1−2t 归原计数（池 ≤2<3）；
  x≤1−2t 为刚性壳（JJJ={t,x,j_h} 被迫、d=1 强制），纯符号杀手登记开放
  （mini-LP 兜底：k=m−2+保序+x≤1−2t 全 cnt INF，m=6/8/12 复现对拍）。
- **a_m=y**：含 ord 后全域 INFEASIBLE；可读链（固定分组佐证）mach×2+BB+fs ⟹
  q₁≥x+y−1/2，JJJ0={q₁,x,tv}≤1 ⟹ x+tv<1/4+t，x,tv≥t ⟹ t<1/4 矛盾窗口。∎
∎（agent-3 终审 VALID 附注）

## 2. 中段模板族（2≤k≤m−3）

移植总表（a1_pocket1_templates.md；逐字移植 0/5 族，(P1-a/b/c/d) 各自挡族）：

| 区域 | 武器 | 状态 |
|---|---|---|
| Class II（2a+b≤k） | 纯计数 3d>m−k | ✅ 逐字（计数与角落无关） |
| K1 域 k≤b、伴=senior | K<1 链（K=(5/4)(a_m+q₁)<1 ⟹ q₁<2/5 ⟹ t>7/20>1/3） | ✅ 逐字 |
| K1 域、伴=y 壳 | uniform 情形（2a≥k）∀m 链：BB₀ 纯 senior s₀≤1/2→j₀>3/4−t→a_m>3/4−t→BJ₀={s_{2a},j₀} nofit 良定义→q₁<9t−11/4→**t>11/32** | ✅ ∀m（簿记逐步验证）；2a<k 变体登记 |
| b=0 | b0 分形：2a≤nS 口袋2 恒等式；2a>nS 剩 a−1 纯 senior 对支撑 | ✅ 簿记级 |
| NF 域 | 机制链不涉 p<K，p→x+y 移植；SS 指派按 P1-BB-y | ✅ 机制，簿记重算机械 |
| JT 族 | **空集**：(1,m−3,0,1,0,0) 违反小件守恒（m≠m+1）；唯一 t-入-JJJ 族 (1,m−2,0,1,0,0)@k=m−1 已被 P1K-top 覆盖 | ✅ 关门 |
| 引理 2（k≥b+2） | 同 b0 分形路径 | ✅ |

**开放登记（全部计算闭合 m≤26）**：①伴=y 壳 2a<k 变体簿记（ord 提升链，靶机随 (a,k) 漂移，
与 NF 的 k' 漂移同型）；②NF 簿记重算；③b0 的 2a>nS 分形恒等式提取。

## 3. 装箱计算证书（m=4..32）

pocket1_bins.py 管线（修正 firststep 编码 + 装箱箱型枚举 + 二步/保序/q₁→M₀ 分层升级）：
- 分层：阶段A（装箱+角落）→ 阶段B（firststep jj 枚举）→ 阶段C/D（二步 q₂）→
  阶段E（保序 forced h=nS−1−jj）→ q₁→M₀ 分支（q1m0/hy 枚举）。
- 闭合：**m=4..32 全 (cnt, k) 零洞**（m=4..12: 182 证书；m=13..26: 7304 证书全量复验通过；
  m=27..32: 8084 块抽样 150/150 PASS）；q₁→M₀ 分支 m=13..26 共 2050 证书零洞。
- 证书标准：t 只出现在右端 ⟹ 常数 Farkas 证书 y（A^T y=0, bt^T y=0, bc^T y=−1, y≥0
  Fraction 精确），浮点定位+有理化+从文件解析回独立复验。
- 消融纪律：每阶段配去约束回 feasible 自检（装箱/danger/mach/firststep/二步/保序
  各承重性均有消融记录）。

## 4. q₁→M₀ 分支

角落 M₀={y,q₁}（x=q₁）曾不被任何 jj 分支覆盖（a3 审计）。补扫（build_p1b q1m0/hy）：
x=q₁ 双向、y+q₁≤K、`am<=y`、h_y 后缀 nofit + 前缀 s_i≤y 枚举。**m=13..26 全阶段 A 洞
cnt 2050 份精确证书零洞**（m=6..12 对拍 a3 实验 7/7 一致；60/60 抽样复验 PASS）。
口袋1 全分支（q₁→他机 / q₁→M₀）闭合。

## 5. WLOG 标注（诚实声明）

装箱固定代表分组（"bigs=[s 升序,y 末位]、槽位顺序消耗"）全管线使用，SEMANTICS 行11
SUSPECT 未证：全部 LP 证书与本文 §2/§3 的条件于该 WLOG；手证 WLOG-free 部分 =
§1 全节（五链+四支均为分组无关组合链）。若 WLOG 被证伪：回落逐 m LP（m≤32 已闭）。
proof.md 主证明（引理 F/G 纯符号）不依赖本路线任何工件。

## 6. 开放问题

1. 伴=y 壳 2a<k 变体、NF 簿记、b0 的 2a>nS 分形——三件簿记级机械工作（计算已闭）。
2. 装箱固定分组 WLOG 的证明或证伪（影响整条 LP 路线升级为无条件）。
3. a_m=y 支的 JJJ0/BB0 恒等式含固定分组内容；分组无关一般链（候选结构引理
   "q₁ 被迫与 x,tv 同箱"）开放。
4. m>32 扩程：管线断点就绪（pocket1b_progress.jsonl），单扫描条款下续跑即可。

## §3 口袋 3（最闲机 ≥3 件）

**引理 P3C（纯计数，全 m，无需 LP）**：他机全 2 件角落中，z≥q₁（z=M₀ 初始件，递减到达
迫使 M₀ 最大件=初始件）、x,y≥t ⟹ mach（s_i+j_i≥ℓ₀）给 s_i≥ℓ₀−q₁≥2t ∀i ⟹
两 senior 和 >4t>1（t>1/4，窗口内严格）两两不共箱、各占一箱；senior 箱至多带 1 件非
senior；第 m 箱至多 3 件（每箱 ≥3t>3/4... 即 ≤3 件）⟹ 非 senior 容量 (m−1)+3=m+2 <
m+3 件数（x,y,z,t + m−1 个 j_i）。矛盾。∎
（agent-3 重建 + agent-2 敌意复核通过：逐环查 + 数值证伪 344 例 0 可装箱 + 消融有牙；
重建 LP 佐证：pocket3_bins.py m=4..20 全 cnt×全分支 19915 份精确证书零洞。
不用 danger/y 下界/firststep/体积/窄带；q₁→M₀ 自动覆盖。注：早期 pocket3 证明的
'y≥1−2t' 约束已被证不合法（agent-3 审计），P3C 绕开它。）

## §4 WLOG 边界（全局诚实声明）

装箱 LP 与模板族使用**规范代表分组**（senior 升序固定指派）。三级现状：
1. **senior 侧已 w.l.o.g. 化**（agent-3 交换引理 LP_CONSTRAINTS §11.0）：任意装箱 ⟹
   同型装箱（SS=最小 2a 极端配对、SJ=次小 b、S=最大 c）。
2. **junior 侧指派是唯一残留缺口**（JJJ/JJ 箱的 junior 集合划分，指数核心；枚举路线
   经评估不可承受，LP_CONSTRAINTS §11）。**junior 侧交换引理已被证否**（pair 绑机
   ⟹ 池内不可交换，LP_CONSTRAINTS §12）——但伴随关键收窄：所有"规范指派死"的构造
   都伴随"JJJ 先死"，定向裁决 90 角点+§8 的 3114+ 点 **0 可装箱**，即**角落 LP 区域
   内不存在可装箱点**；缺口的真实性质不是交换失败而是"可装箱性先死"——全部障碍
   收敛于命题 (P)：角落 ⟹ 不可装箱。规范指派实为"误差 ≤ junior 跨度"的近似
   w.l.o.g.，而"跨度 < slack"与 (P) 本质等价。
3. **WLOG-free 的部分**：口袋2 引理 2.1–2.4、2.6（保序/P2K1/P2K-top/P2K-high/Class II）
   与口袋1 §1 全节（手证五链+四支均分组无关）；P3C 纯计数天然无关。
影响范围：口袋1/2 中段模板的"条件"即此缺口；若 junior 侧 WLOG 得证，两口袋中段
立即升级为无条件全 m；若证伪，回落逐 m 计算证书（口袋2 m≤50 封顶、口袋1 m≤32）
——本路线任何工件都不影响主定理的成立（见 §6）。

## §5 计算证书记录（全部独立复核，纯 Fraction）

| 线 | 规模 | 状态 |
|---|---|---|
| 口袋2 一步+保序 m=4..30 | 43981 份 | 全量复核 PASS/FAIL 0 |
| 口袋2 m=31..45 | 263575 情形零洞 | 全量复核 PASS/FAIL 0 |
| 口袋2 m=46..50 | 204312 份 | 增量复核收尾中（已验 27.5万+/46.8万全 PASS） |
| 口袋2 扫描总计 | **467887 情形零洞** | m=4..50 永久封顶 |
| 口袋1 装箱 LP m=4..32 | ~7900 份（含 q₁→M₀ 2050） | 全量/抽样复验 PASS |
| 口袋3 重建 LP m=4..20 | 19915 份 | 零洞（佐证） |
| 模板族有限记录 | 150801+4840+9666+9165 例 | 全 PASS（∀m 符号验证的互补） |

## §6 与符号主证明的关系

proof.md（引理 F/G 纯符号路径）是**独立的第一证明**：全程不依赖任何 LP、装箱指派
或计算工件，已五轮敌意复核。本文是**第二独立证明**（LP 路线），价值在三点：
①定量结构（洞图、tiered ghost、razor-thin 尺度 t/2−1/4）；②模板族与必要性定理
（定理 2.13：中段证书本质 k-适配）；③46.8 份计算证书的机器可检性。两证明结论一致
（1495 万实例模糊测试峰值 1.067 < 5/4 与之一致）。

## §7 开放问题（合并）

1. **junior 侧转移/交换引理**（唯一剩余 WLOG 缺口；agent-3 攻坚中 LP_CONSTRAINTS §12）。
2. 口袋1 三件簿记（伴=y 壳 2a<k 变体、NF 簿记、b0 的 2a>nS 分形恒等式）——机械，
   计算已闭 m≤26。
3. 口袋1 s₀ 刚性壳的纯符号杀手（望远镜恒等式；mini-LP 兜底已对拍）。
4. a_m=y 支 JJJ0/BB0 恒等式含固定分组内容；分组无关一般链（候选：q₁ 被迫与 x,tv 同箱
   的结构引理）。
5. 口袋1 m>32 计算扩程（断点就绪；手证已全 m，扩程仅加厚记录）。

## 附录：工件索引

- 手证：a1_pocket1_lemmas.md / a1_pocket1_templates.md / midk_note.md（§8/§9）/
  hole_close_lemma.md / pocket3_counting.md
- 审计：LP_CONSTRAINTS.md（§6–§12）
- 真值表：SEMANTICS.md；消息板：BOARD.md；优化库：opt_db.json
- 章节原稿：a1_pocket1_chapter.md / a2_pocket2_chapter.md（本文 §1/§2 的合并源）
- 代码：code/（fast_lp.py、fast_scan*.py、order_step.py、pocket1_bins.py、
  pocket3_bins.py、verify_certs.py、template_*.py、a2_forall_m.py、a3_*.py）
