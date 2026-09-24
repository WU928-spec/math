# 口袋 1 全节（LP_ROUTE 终稿）— a1_pocket1_chapter

> 作者：agent-1（口袋1 全史）。素材：a1_pocket1_lemmas.md（P1K1 五链 + P1K-top 四支，
> agent-3 终审签字）、a1_pocket1_templates.md（中段模板移植收官）、pocket1_bins.py 系
> （装箱 LP：m=4..32 计算闭合、q₁→M₀ 分支、约 7900 精确常数证书）。
> 角落定义归一化 OPT=1，t 窗口 t∈((m−1)/(4(m−2)), 1/3]。

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
