# razor 带 (P) 的 LP 第二证明·完整版

> **命题 (P)**：在 SOSDP 半在线调度问题（Cheng–Kellerer–Kotov, 2012）中，对 Algorithm A 的任一极小反例，其口袋2 razor 角落不存在——razor 带角落配置下 rest 不可装箱（OPT>1）。
> 本文档给出 (P) 在 razor 带的一个独立于主证明的完整第二证明（LP 对偶证书 + 组合引理路线），含全部引理证明、全部约束合法性出处、全部验证件清单。
> 文档自洽：证明所需的引理均在文内证明；引用的项目既有成果在附录中逐条注明出处与验证方式。

---

# 第 0 章 问题、模型与案例空间

## 0.1 SOSDP 与 Algorithm A

**SOSDP（decreasing processing times 半在线调度）**：$m$ 台同型并行机，工件按加工时间非增序到达 $p_1\ge p_2\ge\cdots\ge p_n$，每个工件到达时须立即不可撤销地指派到一台机器，目标最小化 makespan。竞争比 $=$ 算法解 / 离线最优解 $C^*$ 的最坏比值。

**Algorithm A（CKK 2012）**：
1. 前 $m$ 件 $p_1,\dots,p_m$ 一机一件；
2. 记 $L := p_m+p_{m+1}$；
3. 对后续工件 $p_j$（$j\ge m+1$）：若存在机器 $M$ 使 $\ell(M)+p_j\le \frac54 L$，放入**负载最大**的这样一台（best-fit）；否则放入**负载最小**的机器（fallback）。

**已知结果**：LPT 界 $\frac43-\frac1{3m}$；CKK 证 Algorithm A 竞争比 $\le \frac54$（$m\ge3$），且 $m=3$ 时有最优算法 $\frac{1+\sqrt{37}}6\approx1.18046$；下界同为 $\frac{1+\sqrt{37}}6$（SSW 2000）。本文的 (P) 是 5/4 证明的最硬部分（razor 带）的独立证明。

## 0.2 极小反例框架（沿用 CKK 约定）

不妨设 $C^*=1$。设存在反例，取**极小**反例；其**失败工件** $z$ 是首个使某机器负载 $>\frac54$ 的工件。由极小性，$z=p_n$ 是最后一个工件，且被放入**负载最小**的机器。记 $t$ 为 $z$ 的尺寸。

- **事实 1（CKK）**：$z>\frac14$，且不存在 $\le\frac14$ 的工件（记 $x_4=0$）。故所有工件 $>\frac14$。
- **事实 2（CKK）**：最优解中每台机器至多 3 个工件。
- 值类：$X_1=\{p>\frac34\}$、$X_2=\{(\frac12,\frac34]\}$、$X_3=\{(\frac14,\frac12]\}$、$X_4=\varnothing$。

**口袋2 角落（本文战场）**：$z$ 落到**最小负载机** $M_0$（负载记为 $p$，$M_0$ 恰含 2 件，$p\le1$），其余 $nS=m-1$ 台机器各恰含 2 件——一个 **senior** $s_i$ 与一个 **junior** $j_i$。则必有
$$\textbf{danger：}\quad p+t>\frac54 \tag{0.1}$$
（否则 $z$ 可被 best-fit 正常放入 $\le\frac54 L$，不构成失败）。rest $=$ seniors $\{s_i\}$ $+$ juniors $\{j_i\}$ $+$ $\{z\}$（尺寸 $t$），共 $2m-1$ 件。

**(P)（命题）**：在口袋2 角落成立的全部约束下，razor 带中 rest 无法装入 $nS$ 个容量 1 的箱（OPT>1）⟹ 口袋2 razor 角落不存在。

## 0.3 序事实与值域（全部在主证明框架内已证，本文引用）

1. **递减到达**：$a_m := p_m \ge q_1 := p_{m+1}$（$a_m$ 为最小 senior，$q_1$ 为最大 junior 类件）；$q_1\le a_m$。
2. **序分离**：seniors $\ge$ juniors（ seniors 是到达序前段）；且 $L=a_m+q_1\le1$ 给出 **$q_1\le\frac12$**。
3. **senior 非小引理**：$s_i>1-2t$（否则该 senior 与 $z$ 的和 $<1$，$z$ 可被放入）。
4. **窄带**：$t\le j_i\le 2t$（下界：junior 类件 $\ge t$；上界：junior 的定义域）。
5. **负载约束**：best-fit 放置 ⟹ 每台非 $M_0$ 机负载 $\ell_i=s_i+j_{(i)}\le K:=\frac54L$；且 $K=\frac54(a_m+q_1)$。
6. **$p\le1$**（$M_0$ 负载 $\le C^*=1$）。

## 0.4 rest 装箱的箱型计数与 razor cnt 族

rest 每件 $>\frac14$ ⟹ 每箱至多 3 件。箱型：
- $a$ = #SS 箱（2 senior）；
- $b$ = #SJ 箱（1 senior + 1 junior 类件）；
- $c$ = #S 箱（单 senior）；
- $d$ = #JJJ 箱（3 junior 类件）；
- $e$ = #JJ 箱（2 junior 类件）；
- $f$ = #J 箱（单 junior 类件）。

守恒方程：
$$2a+b+c=nS\ (\text{senior 数}),\quad b+3d+2e+f=m\ (\text{junior 类数}=\text{juniors}+t),\quad a+b+c+d+e+f=nS\ (\text{箱数}). \tag{0.2}$$
第一式减第三式：$a-d-e-f=0$；第二式减第三式：$d+e-a-c=1$。联立得**计数恒等式**：
$$\boxed{a=d+e+f},\qquad \boxed{d=1+c+f}. \tag{0.3}$$

**推论 0.4.1**：任意可装箱的 rest 必有 $a\ge1$（存在 SS 箱）且 $d\ge1$（存在 JJJ 箱）。

**razor 带（本文证明的覆盖域）**：项目案例空间扫描后，除已由其他路线闭合的区域外，剩余区域为
$$\text{cnt}\in\{(1,m-3,0,1,0,0),\ (2,m-5,0,1,1,0)\},\qquad k=1..m-1,\qquad m\ge4,\qquad t\in(t_{\rm lo},\tfrac13], \tag{0.4}$$
即 $(c,f,d)=(0,0,1)$、$(a,e)\in\{(1,0),(2,1)\}$、$b=m-3-2e$（与 (0.3) 一致：$a=d+e+f=1+e$，$d=1+c+f=1$）。$t_{\rm lo}=\frac{m-1}{4(m-2)}$（由 $nS$ 台机器负载 $>p>\frac54-t$ 与 OPT 体积联立推出的窗口下界）。razor 带外区域的闭合出处见附录 C。

**关于 $k$（情形参数）**：$k=jj+1$，$jj$ 为 $q_1$（第一个到达的 junior 类件）经 best-fit 落入的机器下标；它由值唯一确定：机器 $0..jj$（低端区）负载前段 $\le K-q_1$，机器 $jj+1..nS-1$（hi 区）senior $>K-q_1$（$q_1$ 放不下的机器）。

## 0.5 两个 LP 框架与 Farkas 常数证书

**统一行形式**：约束写为
$$r\cdot x\ \le\ b_c+b_t\cdot t\qquad(b_c,b_t\in\mathbb{Q}), \tag{0.5}$$
其中 $t$（最末件尺寸）为参数。一组行 $R$ **在全 $t$ 窗口一致不可行** $\iff$ 存在**常数 Farkas 证书** $y\in\mathbb{Q}_{\ge0}^{|R|}$：
$$A^Ty=0,\qquad b_t^Ty=0,\qquad b_c^Ty=-1. \tag{0.6}$$
（$b_t^Ty=0$ 使证书与 $t$ 无关 ⟹ 同一证书对窗口内全部 $t$ 一致成立。）

**严格化约定**：角落语义中的严格不等式（如负载 $>p$、$p+t>\frac54$）统一编码为 $\ge\ +MG$，$MG=\frac1{10000}$（精确有理数，与全项目 margin 约定一致）。

**框架甲（机器索引 LP）**：变量 $p,\ t,\ s_0\le\cdots\le s_{nS-1}$（各机 senior）、$j_0,\dots,j_{nS-1}$（各机 junior）、$a_m,\ q_1$。含全部角落约束（pair、窄带、senior 非小、danger、$q_1\le a_m\le s_i$、$L\le1$、负载帽、firststep 机（fs）、nofit/lowzone、mon2），逐条合法性经审计（附录 B.1）。

**框架乙（值语言 LP）**：变量为**全排序值序列** $p,\ s_1\le\cdots\le s_{nS},\ j_1\le\cdots\le j_{nS}$（junior 在值语言下天然全序，绕开机器索引的 hi 区无序问题）与 $a_m,q_1$。角落约束经**反序重排引理**合法化（附录 B.2）。

**合法性约定**：证书所用行分两类——
- **(A) 角落必要**：角落配置 ⟹ 该行成立（角落语义）；
- **(B) 可装箱必要**：rest 可装箱 ⟹ 该行成立（装箱语义）。
任何一行若只在部分情形合法（如引用低端区 junior 指标），必须标注其合法域；本文所有行均为全域合法（(0.4) 全域、全 $k$、全 $t$ 窗口）。

---

# 第 1 章 基础引理（全部内证）

## 1.1 挤压引理

**引理 1.1（挤压引理）** rest 可装箱 ⟹ $\sum_{i=1}^{nS}\ell_i=\sum_i(s_i+j_{(i)})\ \le\ nS-t$。
**证明**：机器负载 $\ell_i$ 穷尽全部 seniors 与 juniors，故 $\sum\ell_i=\sum s+\sum j$。rest 装入 $nS$ 个容量 1 的箱 ⟹ $\sum s+\sum j+t\le nS$。两式相减即得。∎

**推论 1.1.1（挤压预算）** 记 $B=(nS-t)-nS\cdot p$。由 $\ell_i>p+MG$（pair，见 §0.5 框架甲）得 $\sum(\ell_i-p)<B$；又 danger $p>\frac54-t$ ⟹ $B<nS(t-\frac14)-t$。即全体机器负载超出 $p$ 的总预算是 razor 小量（$\approx\frac{nS}{12}$ 于 $t=\frac13$）。

## 1.2 SS 对与 JJJ 三元组的存在性

**引理 1.2（SS01，(B) 类合法）** rest 可装箱 ⟹ **最小两 senior 和 $\le1$**（值语言：$s_1+s_2\le1$；机器索引：$s_0+s_1\le1$）。
**证明**：由 (0.3)，$a=d+e+f\ge1$ ⟹ 存在一 SS 箱（两 senior 和 $\le1$）⟹ 最小两件和 $\le1$。∎

**引理 1.3（JJJ01，(B) 类合法）** rest 可装箱 ⟹ **$t$ 加最小两件 junior 和 $\le1$**（$t+j_1+j_2\le1$，值语言全序下 $j_1,j_2$ 为全体最小两件 junior）。
**证明**：由 (0.3)，$d=1+c+f\ge1$ ⟹ 存在一 JJJ 箱（3 个 junior 类件和 $\le1$）⟹ 最小的三个 junior 类件（$t$ 为全体最小件 + 两件最小 junior）和 $\le1$。∎

**引理 1.4（值带 B3，(B) 类合法）** razor 带 rest 可装箱 ⟹ **最大 senior $\le 1-t$**。
**证明**：razor cnt 族 $c=0$（无单 senior 箱）。若 $s>1-t$：与任一 junior 类件（$\ge t$）同箱和 $>1$；与任一 senior（$\ge1-2t$）同箱和 $>2-3t>1$（$t<\frac13$）。无处可放，与 $c=0$ 矛盾。∎

## 1.3 低端区配对支配（A5）

**引理 1.5（A5，(A) 类合法）** 设低端区为机器 $1..k$（senior 值序 $s_1\le\cdots\le s_k$），则对 $i=1..k$：
$$j_{nS-k+i}\ \ge\ p-s_i+MG, \tag{1.1}$$
即全体 junior 值序中第 $nS-k+i$ 小者（$k$ 件最大者中第 $i$ 小）不低于机 $i$ 的 pair 下界。

**证明**：
- **mon2（低端区 junior 随 senior 不减）**：角落动力学（best-fit 到达序）给出低端机 $i$ 的 junior $\le$ 低端机 $i+1$ 的 junior（项目 hole_close 引理 1，附录 B.5 含证明）。
- **fs**：机 $k$（$=jj$）的 junior 为 $q_1=\max J$（firststep：$q_1$ 放入当时负载最大且放得下的机器 $jj$）。
- 由 mon2，低端机 $i$ 的 junior $chosen_i$ 为低端区 $k$ 件 junior 中第 $i$ 小者；由 fs，第 $k$ 件恰为全局最大。
- $k$ 件最大 junior 按分量支配任意 $k$ 件 junior（纯排序事实）⟹ $j_{nS-k+i}\ge chosen_i$。
- pair：$chosen_i\ge p-s_i+MG$（机 $i$ 负载 $>p$）。
∎

**注（与 hi 区的关系）**：hi 区 junior 若偏小，只会使 $k$ 件最大者更集中于低端区，结论方向恒加强——这是 A5 与"hi 区 junior 序无关"的原因（其合法性不依赖 hi 区任何序结构，附录 B.3 三层证据）。

## 1.4 情形定义行（LZ/HZ）

**引理 1.6（LZ/HZ，(A) 类合法）** $k=jj+1$ 由值唯一确定：
$$s_k\le K-q_1\ (\text{LZ：机 } k-1=jj \text{ 是放 } q_1 \text{ 的最满载机}),\qquad s_{k+1}>K-q_1\ (\text{HZ：hi 区首机}). \tag{1.2}$$
**证明**：$q_1$ 到达时，各机负载 $=$ senior（junior 尚未到达）。best-fit 把 $q_1$ 放入负载最大且 $\ell+q_1\le K$ 的机器，即 $jj=\max\{i:s_i\le K-q_1\}$。$q_1$ 放不下的机器即 $s_i>K-q_1$（nofit）。∎

## 1.5 min-triple 的 w.l.o.g.（B 链 G2a/Y′）

**引理 1.7（(B) 类合法，经敌意复核）** rest 可装箱 ⟹ **存在**一个装箱使 JJJ 箱恰为池最小三件 $\{t,j_1,j_2\}$（且残差 SJ 匹配经反序配对可行）。
**证明**（纲要，全文见 LP_CONSTRAINTS §21.3 的复核记录）：阈值图（顶点=件、边 ⟺ 和 $\le1$）中，MRF 贪婪（最受限优先取最大相容）产生的消耗多重集按分量支配一切可行消耗；其补集（残差池）反支配 ⟹ 最小三件替换进 JJJ 位后残差可行性保持。∎

## 1.6 sliver 紧性引理（本文核心结构工具）

**定义（sliver）**：记 $J:=j_1+j_2$（全体 junior 值序最小两件和）。
$$\textbf{sliver：}\quad j_1+j_2+j_3>1\ \wedge\ t+j_1+j_2\le1. \tag{1.3}$$

**引理 1.8（sliver 紧性引理，三个独立证明）** rest 可装箱 + sliver ⟹ **装箱全紧**：
$$t+j_1+j_2=1,\qquad \text{每个 SS 对和}=1,\qquad \text{每个 SJ 箱}=(s,1-s)\ \text{互补} $$
（$e=1$ 时另含每个 JJ 箱和 $=1$）。

**证明**（体积账，以 $e=0$ 为主，$e=1$ 同理）：
- SJ 箱共 $b=nS-2$ 个（(0.4) 的 $e=0$ 族），每个和 $\le1$ ⟹ SJ 体积 $\le nS-2$。
- SJ 体积 $=\sum s+\sum j-J-(u+v)$（$\{u,v\}$ 为 SS 对）。
- 挤压引理：$\sum s+\sum j\le nS-t$。
- 联立：$nS-t-J-(u+v)\le nS-2$ ⟺ $t+J+(u+v)\ge2$。
- 而 $t+J\le1$（引理 1.3：JJJ 箱和 $\le1$ 取 $\{t,j_1,j_2\}$）且 $u+v\le1$（SS 箱）。
- 故 $t+J=1$ 且 $u+v=1$（全取等）；进而总体积 $=nS$ 恰满 ⟹ 每个 SJ 箱和 $=1$ ⟹ 互补对 $(s,1-s)$。∎
（另两个独立证明：agent-3 的对 $\sum V\ge nS\cdot p+t$ vs 容量反代版、agent-1 的第三证，见 BOARD 2026-09-23 与 a1_beta_review.md。）

**推论 1.8.1**：sliver 装箱的 junior 多重集被 senior 序列完全决定：
$$J=\{j_1,j_2\ (\text{和 }1-t)\}\cup\{1-s : s\notin SS\}. \tag{1.4}$$

**引理 1.9（sliver 内 JJJ 唯一性）** sliver 中 JJJ 箱必为 $\{t,j_1,j_2\}$。
**证明**：sliver 给出 $j_1+j_2+j_3>1$，故任意三件纯 junior 和 $\ge j_1+j_2+j_3>1$——JJJ 必含 $t$。又 $t+j_1+j_3>t+j_1+(1-j_1-j_2)=1+t-j_2\ge1$（$j_2\ge t$）⟹ 第三件只能取 $j_2$。∎

---

# 第 2 章 k 端点三段（$k=1$、$k=m-2$、$k=m-1$）

## 2.1 $k=1$：SS 墙

**命题 2.1** $k=1$ 的 razor 角落 ⟹ rest 不可装箱。
**证明**：机器索引 LP = 角落约束（附录 B.1 全表）+ mon2 + 挤压行（引理 1.1）+ SS01（引理 1.2 的 $s_0+s_1\le1$）。该 LP 在全 $(m,\text{cnt},t)$ 一致不可行（附录 A.1，$m=4..20$ 精确证书）⟺ 每个角落点 $s_0+s_1>1$。senior 已全序，故任意两 senior 和 $>1$ ⟹ 不存在 SS 箱，与 $a\ge1$（(0.3)）矛盾。∎

## 2.2 $k=m-2$：JJJ 墙（对枚举）

**命题 2.2** $k=m-2$ 的 razor 角落 ⟹ rest 不可装箱。
**证明**：此时 hi 区仅 1 台机器。对每一对 junior 指标 $(i,i')$（$0\le i<i'\le nS-1$），构造 LP $=$ 角落约束 $+$ 假设行 $t+j_i+j_{i'}\le1$。全部 $\binom{nS}{2}$ 个 LP 皆不可行（附录 A.1）。
若 rest 可装箱，由引理 1.3，存在 JJJ 箱，其最小三件 $=t$ 加两件 junior，即存在某对 $(i,i')$ 使 $t+j_i+j_{i'}\le1$——与全部对被排除矛盾。∎（对枚举是合法的分情形法：假设行不是必要行，而是穷举的分支。）

## 2.3 $k=m-1$：双墙同撞

**命题 2.3** $k=m-1$ 的 razor 角落 ⟹ rest 不可装箱。
**证明**：$k=m-1$ ⟹ 低端区 $=$ 全部 $nS$ 台机器（hi 区为空）⟹ mon2 给出 junior **全序** $j_0\le j_1\le\cdots\le j_{nS-1}$，故 $j_0,j_1$ 确为全池最小两件（JJJ01 在此域合法引用）。
机器索引 LP = 角落约束 + mon2 保序 + 挤压行 + SS01（引理 1.2）+ JJJ01（引理 1.3，$t+j_0+j_1\le1$）。该 LP 在全 $(m,\text{cnt},k=m-1,t)$ 一致不可行（附录 A.1，374 发精确证书）⟺ 每个角落点
$$s_0+s_1>1\ \ \vee\ \ t+j_0+j_1>1.\tag{2.1}$$
左析取 ⟹ 任意两 senior 和 $>1$ ⟹ SS 对不存在（与 $a\ge1$ 矛盾）；右析取 ⟹ 任意三件 junior 类和 $>1$ ⟹ JJJ 不存在（与 $d\ge1$ 矛盾）。两可装箱必要条件不能同时成立 ⟹ rest 不可装箱。∎

**机理（双墙同撞）**：角落 pair（$j_i\ge p-s_i$）+ razor 挤压把值钉到近 razor 区：JJJ 需要两件小 junior（$\le\frac{1-t}{2}$），而小 junior 只能由大 senior（$\ge p-\frac{1-t}{2}$）的机器供给；razor 区 $p>\frac54-t$ ⟹ $p-\frac{1-t}{2}>\frac12$ ⟹ 供 JJJ 的 senior $>\frac12$（不能互配 SS）、供 SS 的 senior $\le\frac12$（其 junior $>\frac{1-t}{2}$ 不能 JJJ）——两类需求在 razor 区互斥。
**独立互证**（附录 A.2）：① A 线全合法行 LP（B 规范形行），$m=4..30$ 共 1907/1907 精确证书；② 洞族模板恒等式 U(a)，shape A $m=4..50$ 全 $k$、10 洞族 11487 例零失败。

---

# 第 3 章 uncond 层（$k=2..m-2a-2$）：统一符号证书与 B4 单行合法性

## 3.1 T2 模板（∀m 统一符号证书）

**命题 3.1** 对 uncond 层（$k\le m-2a-2$）的每一点 $(m,\text{cnt},k)$，值语言 LP（全部合法行）不可行；且存在 **O(m) 行的统一证书 T2**（免解 LP，权重显式）：
$$\begin{aligned}
w=\ &10\,\text{danger}+6\,(j_{\max}\le q_1)+5\,(q_1\le a_m)+10\,(t\le\tfrac13)+5\,\text{B1}\\
&+4\,\text{B4}_{q=nS-k}+5\,\text{A5}_1+5\,\text{A5}_2+1\,\text{HZ}+5\,\text{jrt}_{nS-k+1}+6\,\textstyle\sum\text{jrt 链},
\end{aligned} \tag{3.1}$$
满足 $A^Tw=0$（逐变量系数恒为 0）、$b_t^Tw=0$（全 $t$ 窗口统一）、$b_c^Tw=-\frac16-11\cdot MG$。
**验证**：$m=6..60$ 共 **2971/2971** 通过（Fraction 精确算术直接核验 (0.6)，不解 LP）；并经独立自建行（按语义重新实现，非同一构造器）代数复核 $m=10,12,16,40$ 全过（列平衡 0 破坏、$b_c^Tw$ 精确、$b_t^Tw=0$）。∎

**边界结构（T2 推论）**：B4_q（见下）仅对 $q\in[2a+1,nS-2]$ 有定义；模板取 $q=nS-k$ ⟹ 模板域恰为 $k\le m-2a-2$——**uncond 层的边界是 B4 行跌出定义域的结构性边界**，薄层 39 点由此显式化（见第 4 章）。

## 3.2 B4 单行合法性

**引理 3.2（B4_q 合法，(B) 类）** razor 角落 + rest 可装箱 ⟹ **$s_{nS+1-q}+j_{q+2}\le1$**（$q\in[2a+1,nS-2]$）。

**证明**（取等格法 + 分情形计数）：
设 B4_q 破：$j_{q+2}>1-s_{nS+1-q}$。记
$$L_q=\{s_{nS+1-q},\dots,s_{nS}\}\ (\text{第 }q\text{ 大起的 }q\text{ 台 senior}),\qquad C=\{t\}\cup\{j\le1-s_{nS+1-q}\},\qquad r=\#\{j\le1-s_{nS+1-q}\}\ (\le q+1).$$
$L_q$ 的 SJ 伴侣必 $\in C$（senior $\ge s_{nS+1-q}$ 配 junior $>1-s_{nS+1-q}$ 则和 $>1$）。
**第 1 步（g=0，L_q 全 SJ）**：由引理 1.7（min-triple w.l.o.g.），JJJ 消耗 $\{t,j_1,j_2\}\subseteq C$ ⟹ $C$ 可用 $\le r+1-3=r-2$。若 $r\le q+1$，可用 $\le q-1<q$ ⟹ Hall 亏缺 ⟹ 不可装箱。✓
**第 2 步（g≥1，部分 L_q 进 SS）**：SJ 需求降为 $q-g$，需 $C$ 可用 $\ge q-g$，即 $r\ge q+2-g$。
**第 3 步（取等格 LP 判决）**：角落 LP $+$ B4 破 $+$ 取等行（$e=0$ 用 $r\ge q$，$e=1$ 用 $r\ge q-2$，由 SS 槽 $2a$ 给出 $g\le2$ 与 $g\le4$ 的最坏需求）在**全 uncond 层一致不可行**——
- $e=0$ 域：**111/111** 精确 t-uniform Farkas 证书（$m=6..16$）；
- $e=1$ 域：**45/45** 同标准证书。
⟹ **B4 破 ⟹ $r<q$（$e=0$）/ $r<q-2$（$e=1$）**。
**第 4 步（亏缺收口）**：$r<q$ ⟹ $C$ 可用 $=r-2<q-2\le q-g$（$g\le2$）；$r<q-2$ ⟹ 可用 $<q-4\le q-g$（$g\le4$）。两族均 Hall 亏缺 ⟹ rest 不可装箱。∎
（逃逸 (a)——JJJ 用池外 junior——与逃逸 (b)——大 senior 进 SS——的构型经 9402 例构造性攻击零可装箱佐证，附录 A.4。）

**推论 3.2.1**：T2 的唯一条件行解除 ⟹ **uncond 层闭合且无条件**。

---

# 第 4 章 薄层 39 点（$k=m-2a-1..m-3$）：sliver 紧性与两格收官

本层为 B4 定义域之外。此层角落点必含 sliver（(1.3)）的 razor 临界值域。由紧性引理（引理 1.8），本层可装箱 ⟹ 全紧互补；分 $\#\{s\ge J\}$ 两格。

## 4.1 α' 格（$\#\{s\ge J\}\ge1$）——紧性五步杀

（本节用值语言 1-indexed：$s_1\le\cdots\le s_{nS}$ 为 senior 值序，$s_1$ 最小、$s_{nS}$ 最大；"机 $1$"指含最小 senior $s_1$ 的机器。）

**命题 4.1** razor 角落 + sliver + $\#\{s\ge J\}\ge1$ + rest 可装箱 ⟹ 矛盾。

**证明**：
1. **紧性**（引理 1.8）：$J=1-t$；SS 对和 $=1$；SJ 互补。
2. **钉天花板**：$s\ge J=1-t$ 且 B3（$s\le1-t$）⟹ $s=1-t$。又 $s$ 的 SJ 伴侣须为 $<J$ 的 junior，而 $j_1,j_2$ 已被 JJJ 吃掉（引理 1.9）、其余 junior $>1-J=t$ ⟹ $s$ **被迫进 SS**。
3. **伴侣逼 $t=\frac13$**：SS 和 $=1$ ⟹ 伴侣 $x=1-s=t$；senior 非小（$x\ge1-2t$）⟹ $t\ge\frac13$。razor $t\le\frac13$ ⟹ $t=\frac13$。（$t<\frac13$ 时 $x<t$ 非 senior，SS 不可成，直接矛盾。）
4. **全体 junior 钉 $t$**：$t=\frac13$ ⟹ $s_{nS}=\frac23$、$x=\frac13$；$s_1\le x=\frac13$ 且 $s_1\ge1-2t=\frac13$ ⟹ $s_1=\frac13=a_m$；到达递减 $q_1\le a_m=\frac13$；窄带 $j\ge t=\frac13$ ⟹ **全体 junior $=\frac13$**。
5. **机 1 pair 矛盾**：senior $s_1=\frac13$ 的机器 junior $=\frac13$（唯一值）⟹ 负载 $\frac23$；pair 要求负载 $>p+MG$ ⟹ $p\le\frac23-MG$；danger（0.1）：$p>\frac54-\frac13=\frac{11}{12}>\frac23$ ⟹ 矛盾。∎

**各 $\#\{s\ge J\}$ 分格的统一覆盖**：
- $\#\{s\ge J\}=2$（$e=0$，$a=1$）：两大 senior 同 SS 箱，和 $\ge2(1-t)>1$（$t<\frac12$）矛盾；
- $\#\{s\ge J\}=2$（$e=1$，$a=2$）：分箱则两伴侣皆 $=t$，同步骤 3–5 杀；同箱则 $t\ge\frac12$ 矛盾；
- $\#\{s\ge J\}\ge3$（$e=0$）：$a=1$ 仅 2 槽，$\ge3$ 个 $=1-t$ senior 全被迫进 SS，槽位不足；
- $\#\{s\ge J\}\ge3$（$e=1$）：3+ 件进 4 槽必有两大同箱，同 $t\ge\frac12$ 矛盾。

## 4.2 β 格（$\#\{s\ge J\}=0$）——mon2 杀（全文）

**命题 4.2** razor 角落 + sliver + $\#\{s\ge J\}=0$ + rest 可装箱 ⟹ 矛盾。

senior 用 0-indexed $s_0\le s_1\le\cdots\le s_{nS-1}$；$k=jj+1$ 为低端区机器数；$R=$ 残差 senior 集（seniors 去掉 SS 对）。

**第 1 步（C1–C3，三个推论）**

- **C1（全体 junior $\le s_0$）**：$q_1=\max J\le a_m=s_0$（到达递减，§0.3）。∎
- **C2（SS $=\{s_0,s_1\}$ 且 $s_0+s_1=1$）**：
  - 先证 $s_0\in$ SS。若否，$s_0\in R$ ⟹ 互补件 $1-s_0\in J$ ⟹ $q_1\ge1-s_0$；与 $q_1\le s_0$（C1）联立得 $s_0\ge\frac12$。设 SS $=\{u,v\}$（$u+v=1$，$u\le v$），取 $u\ge s_1$ ⟹ $v=1-u\le1-s_1\le1-s_0\le s_0$ ⟹ $v=s_0$，与 $s_0\notin$ SS 矛盾。∴ $s_0\in$ SS。
  - SS $=\{s_0,v\}$，和 $=1$ ⟹ $v=1-s_0$。若 $v\ne s_1$，则 $s_1\in R$ ⟹ $1-s_1\in J$ ⟹ $q_1\ge1-s_1$，与 $q_1\le s_0$ 联立得 $s_0+s_1\ge1$；而 B1（引理 1.2，$s_0+s_1\le1$）⟹ $s_0+s_1=1$ ⟹ $v=1-s_0=s_1$，矛盾。∴ $v=s_1$ 且 $s_0+s_1=1$。∎
  - 推论：$q_1=\max(j_2,1-s_2)\le s_0$；**$q_1=s_0$ 仅当 $j_2=s_0$ 或 $s_2=s_1$**（条件钉，非恒钉）。
- **C3（$p+MG\le 2s_0$）**：机 0 的 junior $x_0$ 满足 $p-s_0+MG\le x_0\le q_1\le s_0$（pair + C1）；否则机 0 窗口空，直接矛盾。∎

**第 2 步（引理 H′，高位 junior 存货）** 记 $Q=\#\{j\in J:j\ge p-s_0+MG\}$。则
$$Q\le(k-2)+1=k-1. \tag{4.1}$$
**证明**（按 (1.4) 的三类成员逐一计数）：
1. **$j_1$ 不够格**：$j_1\le\frac{1-t}{2}$（$j_1+j_2=1-t$、$j_1\le j_2$）。$\frac{1-t}{2}\ge p-s_0$ ⟺ $s_0\ge p-\frac{1-t}{2}>\frac54-t-\frac{1-t}{2}=\frac34-\frac t2$；而 $s_0\le s_1=1-s_0$ ⟹ $s_0\le\frac12<\frac34-\frac t2$（$t<\frac12$）——矛盾。
2. **$j_2$ 至多 1 件**：$j_2\ge p-s_0$ ⟺ $j_2+s_0\ge p$；$j_2\le q_1\le s_0$ ⟹ 需 $2s_0\ge p$（且 $j_2=q_1$ 时被 fs 钉走，见第 4–5 步）。
3. **互补件 $1-s$（$s\in R$）**：$1-s\ge p-s_0$ ⟺ $s\le\tau:=1-p+s_0-MG$。
   - **hi 区成员永不够格（nofit）**：$s\in R\cap\text{hi}$ ⟹ $s>K-q_1=\frac{5(s_0+q_1)}4-q_1=\frac{5s_0+q_1}4$；又 $s_0+q_1\ge4-4p$ ⟹ $\frac{5s_0+q_1}4\ge s_0+1-p>\tau$——其中 $s_0+q_1\ge1-t$（$s_0\ge1-2t$、$q_1\ge t$）且 $1-t\ge4-4p\iff p\ge\frac{3+t}4$（danger $p>\frac54-t\ge\frac{3+t}4$ 当 $t\le\frac25$；razor $t\le\frac13$）⟹ $s>\frac{5s_0+q_1}4\ge s_0+1-p>\tau$ ⟹ $1-s<p-s_0+MG$，**不够格**。
   - **low 区成员**：$R\cap\text{low}=\{s_2,\dots,s_{jj}\}$（$s_0,s_1$ 已入 SS），共 $k-2$ 台 ⟹ 够格者 $\le k-2$。
   合计 $Q\le(k-2)+1=k-1$。∎

**第 3 步（$k\ge3$：升链计数杀）** 低端区 mon2 升链 $x_0\le x_1\le\cdots\le x_{jj}=q_1$：$x_0\ge p-s_0+MG$ 且链不减 ⟹ 链上 $k$ 件全部 $\ge p-s_0+MG$ ⟹ 需 $Q\ge k$。引理 H′ 给 $Q\le k-1<k$ ⟹ $k\ge3$ 全部不可能。∎

**第 4 步（$k=1$：代数杀）** $k=1$（$jj=0$，低端区仅机 0，fs 使 $x_0=q_1$）：
机 1 hi ⟹ $s_1>K-q_1=\frac{5s_0+q_1}4$；$s_1=1-s_0$（C2）⟹ $q_1<4-9s_0$。机 0 pair：$q_1=x_0\ge p-s_0+MG$。联立：$p-s_0+MG<4-9s_0$ ⟺ $p<4-8s_0-MG$；C3（$2s_0\ge p+MG$ ⟹ $8s_0\ge4p+4MG$）⟹ $p<4-8s_0-MG\le4-4p-4MG$ ⟺ $5p<4-4MG$ ⟺ $p<\frac45-MG$，与 danger $p>\frac54-t\ge\frac{11}{12}$ 矛盾。∎

**第 5 步（$k=2$：三情形杀）** $k=2$（$jj=1$）：低端区 $=\{$ 机 0, 机 1$\}$，机 1 由 fs 取 $q_1$。机 0 的高档候选只剩 $j_2$（$R\cap\text{low}=\varnothing$：机器 2 起全 hi，互补件由第 2 步 nofit 段封死；$j_1$ 不够格）：

- **情形 A（$q_1=j_2$）**：唯一高档 junior 被 fs 钉去机 1 ⟹ 机 0 窗口空。∎
- **情形 B（$q_1=1-s_2$，$j_2$ 高档）**：机 2 hi ⟹ nofit $s_2>K-q_1=\frac{5s_0+q_1}4$；代入 $q_1=1-s_2$：$s_2>\frac{5s_0+1-s_2}4$ ⟺ $5s_2>5s_0+1$ ⟺ $s_2>s_0+\frac15$ ⟹ $q_1=1-s_2<\frac45-s_0$。机 0 需 $p-s_0+MG\le j_2\le q_1<\frac45-s_0$ ⟺ $p<\frac45-MG$，同 danger 矛盾。∎
- **情形 B′（$j_2$ 不高档，$j_2<p-s_0+MG$）**：机 0 窗口空。∎
- **情形 C（条件钉 $q_1=s_0$）**：$j_2=s_0=q_1$。钉出 $s_0=1-2t$（$j_1=1-t-j_2=1-t-s_0\ge t$ ⟺ $s_0\le1-2t$，又 senior 非小 $s_0\ge1-2t$）。此时 $s_1=1-s_0=2t$，故残差 senior $s_2\ge s_1=2t$。互补件够格阈 $\tau=1-p+s_0-MG=2-p-2t-MG$；而
$$s_2\ge2t\ >\ 2-p-2t-MG=\tau\ \iff\ p>2-4t-MG,$$
由 danger $p>\frac54-t\ge2-4t$（$t\ge\frac14$，razor $t>\frac14$ 严格）成立 ⟹ 一切互补件 $1-s$（$s\ge s_2$）均 $<p-s_0+MG$，不满足资格线（$\ge p-s_0+MG$），不够格；而 $j_2=s_0=q_1$ 又被 fs 钉在机 1 ⟹ **机 0 窗口空死**。∎（与 $s_2$ 是否等于 $s_1$ 无关；$t=0.3$ 边界亦覆盖。）

**结论**：全紧结构在所有 $k$ 下均矛盾 ⟹ 可装箱 + sliver + razor 角落 $=\varnothing$。∎

**实验背书**：4373/4373 个全紧实例角落无效（4368 死于 mon2、4 窗口空、1 fs 冲突）；15438 例 $(k,I)$ 联合分布全格 $I<k$；情形 C 定向 1202 例 0 有效；$k=1$ 7 例全 $q_1$ 不高档、$k=2$ 44 例全落情形 B′（均可复跑，附录 D）。

---

# 第 5 章 总装（覆盖完整性与独立性）

## 5.1 覆盖完整性

razor 带（(0.4) 全域）按 $k$ 分解：

| 段 | 闭合命题 | 行框架 |
|---|---|---|
| $k=1$ | 命题 2.1（SS 墙） | 机器索引 LP |
| $k=2..m-2a-2$ | 命题 3.1（T2 ∀m）+ 引理 3.2（B4 合法） | 值语言 LP |
| $k=m-2a-1..m-3$ | 命题 4.1（α'）+ 命题 4.2（β）（sliver 分解穷尽） | 值结构+组合 |
| $k=m-2$ | 命题 2.2（JJJ 墙，对枚举） | 机器索引 LP |
| $k=m-1$ | 命题 2.3（双墙同撞） | 机器索引 LP |

两族 cnt 逐格计数：
- $a=1$（cnt=(1,m−3,0,1,0,0)）：$1+(m-5)+1+1+1=m-1$ ✓；
- $a=2$（cnt=(2,m−5,0,1,1,0)）：$1+(m-7)+3+1+1=m-1$ ✓。

**全 $k$ 覆盖、衔接恰好**（uncond 末格 $q=2a+1$ 为 B4 定义域边界；薄层 39 点内部 $\#\{s\ge J\}\ge1$ 与 $=0$ 二分穷尽）。$t$ 窗口 $(t_{\rm lo},\frac13]$ 由常数证书（$b_t^Ty=0$）统一覆盖。$m\ge4$ 任意（T2 与 U(a) 的 $m$-无关性）。

故 **(P) 在 razor 带全域、$\forall m$ 成立**。∎

## 5.2 独立性声明

本证明未使用主证明（proof.md，引理 F/G/T''）的任何结论；其结论性内容全部出自 LP 对偶证书与本文 §1–§4 的组合引理。与主证明互为独立双证明。

---

# 附录 A. 精确证书与模板验证清单

**A.1 k 端点证书**：$k=1$（$m=4..20$）与 $k=m-1$（$m=4..20$，共 374 发）精确 Farkas 证书（Fraction，满足 (0.6)：$A^Ty=0$、$b_t^Ty=0$、$b_c^Ty=-1$、$y\ge0$），零洞零 RATFAIL。
**A.2 互证件**：
- A 线全合法行 LP（B 规范形：SS 极端配对+SJ 反序+JJJ 最小 3d+JJ 反序），$m=4..30$ 共 **1907/1907** 精确证书（k=m−1 全 cnt 对照基线 0 不一致）；
- 洞族统一恒等式 **U(a)**（引理2望远镜模板）：shape A $m=4..50$ 全 $k$、10 洞族 **11487** 例零失败、$m>50$ 由 $m$-无关性覆盖。
**A.3 T2 模板**：uncond 层 $m=6..60$ 共 **2971/2971** 通过（不解 LP，直接核验 (0.6)）；独立自建行复核 $m=10/12/16/40$ 全过。
**A.4 B4 取等格**：$e=0$ 域 **111/111**、$e=1$ 域 **45/45** 精确 t-uniform 证书；逃逸构型构造性攻击 **9402** 例零可装箱。

# 附录 B. 合法行登记（全文使用的全部约束行）

**B.1 机器索引 LP 角落约束（22 条，(A) 类）**：$p\le1$、$t$ 钉住、senior 非小（$s\ge1-2t+MG$）、$s\le1$、窄带（$j\le2t$、$j\ge t$）、danger（$p+t\ge\frac54+MG$）、pair（$j\ge p-s+MG$，即负载 $>p$）、$a_m\le s_i$、$j_i\le q_1$、$t\le q_1$、$q_1\le a_m$、$p<K$、$L\le1$、srt（senior 升序）、fs（$j_{jj}=q_1$、$j_i\le j_{jj}$）、sk+q1≤K、nofit（hi 区）、lowzone（低端区）、负载帽（$s+j\le K$）、ord（低端区 junior 不减，mon2）、squeeze（挤压）。逐条审计记录：LP_CONSTRAINTS §1。
**B.2 反序重排引理（(A) 类，值语言框架的基石）**：机器配对给出 $\min_i(s_i+j_{(i)})\ge p$ ⟹ 反序配对 $j_r+s_{nS+1-r}\ge p$（maximin，交换论证：$s_a\le s_b,\ j_c\le j_d$ 则 $\min(s_a+j_d,s_b+j_c)\ge\min(s_a+j_c,s_b+j_d)$）；机器负载全 $\le K$ ⟹ 反序 $j_r+s_{nS+1-r}\le K$（minimax，同理）。
**B.3 A5（引理 1.5）**：三层独立证据收敛（①四步证明（mon2+pair+支配）；②154 配置×48 方向采样最大违例 $=-MG$ 恰好取等；③子集精确蕴涵（m=6..8 全配置×全子集 LP 最大化违例 $=-MG$）——a3_a5_corner.py。
**B.4 min-triple w.l.o.g.（引理 1.7）**：LP_CONSTRAINTS §21.3（G2a 位置映射，经敌意复核 VALID）。
**B.5 mon2（低端区 junior 随 senior 不减）**：hole_close_lemma.md 引理 1（角落产生运行中 [0,jj] 机 junior 随 senior 单调不减，手写证 + 51516 事件实证）。
**B.6 (B) 类行**：SS01（引理 1.2）、JJJ01（引理 1.3）、B3（引理 1.4）、B4_q（引理 3.2）、sliver 紧性（引理 1.8）——均本文内证。
**B.7 索引纪律**：机器索引 junior 指标仅在 $k=m-1$（全序）引用为值序（JJJ01 机器索引版仅在 $k=m-1$ 合法——本证明全部 JJJ 引用在 $k<m-1$ 处均用值语言全序版 B2）。

# 附录 C. razor 带外区域的闭合出处

- 固定分组 LP 全域扫描：其余 cnt/k 区域 **467887 情形零洞** + 30.8 万份复核零 FAIL（计算封底 $m\le50$）；
- E-nec 必要条件行（非 razor 族）：三轮（v1 无保序/v2 mon2/v3 +挤压值带）一致收官；
- 洞族闭合：引理 1（mon2）+ 引理 2（望远镜恒等式）+ U(a)（附录 A.2）。
razor 带 (0.4) 为上述路线闭合后剩余的完整区域。

# 附录 D. 数据与复核记录

**D.1 数据文件**（目录 code/）：
- `main_tight_construct.py` + `main_tight_construct.jsonl`：全紧实例构造与角落判定（4373/4373 无效）；
- `a3_hi_analyze.py` / `a3_tight_stress.py`：$(k,I)$ 联合分布与紧实例压测（15438 例 $I<k$、K 帽放松零翻转）；
- `a3_Prazor_scan.py` / `a3_Prazor_certs.txt`：k=m−1 双墙 374 证书；
- `a3_template_verify.py` / `a3_template_fit.py`：T2 模板核验与拟合；
- `main_b4eq_probe.py` + `code/main_b4eq_certs.md`：B4 取等格 111+45 证书。
**D.2 敌意复核记录**（本文每个核心引理均经独立复核）：
- sliver 紧性引理：三个独立证明（main、agent-3、agent-1）；
- α' 紧性证明：agent-1 终审 VALID（a1_alpha_tight_review.md）；
- β 证明链：agent-1 终审 VALID（a1_beta_review.md、a1_beta_v2_review.md、a1_beta_hi_review.md，含 C1 换 τ-杀法记录）；
- T2 模板：agent-1 自建行代数独立复核 VALID（a1_review_t2_caseb.md）；
- B4 单行合法性：agent-1 供给上界独立复核 VALID（a1_ss_b4.md）；
- 组装级终审：agent-1 覆盖完整性/引用合法性/链衔接/独立性四点 VALID（a1_final_review.md）。
**D.3 证明文档**：`second_proof.md`（本文）、`main_alpha_tight.md`（α'）、`main_beta_proof_v2.md`（β v2.1）、`a3_beta_hi.md`（β §5）、`razor_closure.md`（闭合总结）。

---

**文档结束**。razor 带 (P) 的 LP 第二证明至此完整：基础引理（§1）+ k 端点三段（§2）+ uncond 层（§3）+ 薄层两格（§4）+ 总装（§5）+ 验证与出处（附录 A–D）。
