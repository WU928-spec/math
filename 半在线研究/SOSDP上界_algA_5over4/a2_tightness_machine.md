# a2_tightness_machine.md —— 机器角落版紧性：Qcount 松弛（agent-2）

> 目标（main 指令）：证明「机器角落 + sliver + rest 可装箱 ⟹ 装箱全紧（σ=0）」。
> 实际达成：**更强结果**——机器角落（mon2/fs/LZ-HZ/pair/帽K）+ rest 可装箱 是**空集**，
> 且**不需要 sliver**。因此紧性引理平凡成立（前件为空）。证明载体是一族精确有理
> Farkas 证书，核心新约束是本文导出的 **Qcount**。

---

## 1. Qcount 引理（(A) 类合法：mon2 + pair 导出）

**记号**（值语言 1-indexed）：$s_1\le\cdots\le s_{nS}$ 为 senior 值序，$j_1\le\cdots\le j_{nS}$ 为 junior
值序；$nS=m-1$；$k=jj+1$ 为低端区机器数（$k=\#\{i: s_i\le K-q_1\}$，由值唯一确定，引理 1.6）；
$s_0=a_m=s_1$ 为最小 senior；$q_1=j_{nS}$ 为最大 junior；$p$ 为 $M_0$ 负载。

**引理 Qcount**：口袋 2 角落 + 机器结构（mon2/fs/pair/LZ-HZ）⟹
$$\boxed{\;j_{\,nS-k+1}\ \ge\ p - s_0 + MG.\;} \tag{Q}$$
即「值序第 $nS-k+1$ 小的 junior ≥ $p-s_0+MG$」，等价于 **至少 $k$ 个 junior 都 ≥ $p-s_0+MG$**。

**证明（4 行）**：
1. **机 0 pair**：机 0 的 senior 是 $s_0$（最小），其 junior $x_0$ 满足 $s_0+x_0\ge p+MG$（pair，负载 $>p$）⟹ $x_0\ge p-s_0+MG$。
2. **mon2 升链**（引理 1.5a）：低端区 junior 不减 $x_0\le x_1\le\cdots\le x_{jj}=q_1$。
3. **低端区 $k$ 台 junior 全 ≥ $p-s_0+MG$**：由 1、2，$x_i\ge x_0\ge p-s_0+MG$ 对 $i=0..jj$（共 $k$ 台）。
4. **值序翻译**：存在 $k$ 个 junior 都 ≥ $p-s_0+MG$ ⟹ 第 $nS-k+1$ 小的 junior ≥ $p-s_0+MG$。∎

> 合法性标注：Qcount 是 **(A) 类（机器角落必要）**，只用了 pair（引理框架甲 #9）与 mon2
> （引理 1.5a），不依赖任何装箱假设，也不依赖 sliver、窄带上界 $j\le2t$。

---

## 2. LP 松弛（Qcount + LZ/HZ + 装箱必要行 + value 角落）

对每个 $(m,\mathrm{cnt},k)$（$m\ge4$，razor cnt，$k=1..nS$），建以下线性行系统（变量
$x=[p,a_m,q_1,s_1..s_{nS},j_1..j_{nS}]$，$t$ 为参数，行形 $r\cdot x\le b_c+b_t\,t$）：

**value 角落（(A) 类）**：danger $-p\le-\tfrac54+t$；$p\le1$；$j_1\ge t$；$s_1\ge1-2t$；$s_{nS}\le1$；
$j_{nS}\le q_1$；$q_1\le a_m$；$a_m\le s_1$；$a_m+q_1\le1$；$t\le q_1$；$t\ge t_{\rm lo}$；$t\le\tfrac13$；
srt / jrt（值序定义）；**A1**（反序 maximin，B.2）$p-s_{nS+1-r}-j_r\le0$，$r=1..nS$。
（注：**不含** 窄带上界 $j\le2t$、A2 反序帽、B4、SJrev——见 §4 消融，这些均非必需。）

**装箱必要（(B) 类）**：B1（$s_1+s_2\le1$）；B2（$t+j_1+j_2\le1$，即 $j_1+j_2\le1-t$）；
B3（$s_{nS}\le1-t$）；squeeze（$\sum s+\sum j\le nS-t$）。

**机器（(A) 类）**：LZ $s_k\le K-q_1$（即 $s_k-\tfrac54 a_m-\tfrac14 q_1\le0$）；
HZ（$k<nS$ 时）$s_{k+1}\ge K-q_1+MG$（即 $-s_{k+1}+\tfrac54 a_m+\tfrac14 q_1\le-MG$）；
**Qcount** $p-a_m-j_{\,nS-k+1}\le-MG$。

## 3. 不可行证据（精确有理 Farkas 证书）

对上述松弛，**全部 $(m,\mathrm{cnt},k)$ 有精确 Farkas 证书**（$A^Ty=0,\ b_t^Ty=0,\ b_c^Ty=-1,\ y\ge0$，
`rationalize_verify` 精确 Fraction 核验）：

| 扫描 | 结果 |
|---|---|
| $m=6..14$ × 两 razor cnt × $k=1..m-1$ | **零洞**（每点一张精确有理证书）|
| 同上 + sliver 行 | 零洞（sliver 非必需，验证冗余）|

即：**机器角落 ⟹ rest 不可装箱**（对全 $k$，无需 sliver）。这正是命题 (P) 本身，且把
§2.1/§2.2/§2.3/§3/§4 五段统一成同一证书族。

## 4. 消融（哪些行真正必需）

| 去掉的行 | 结果 |
|---|---|
| $j\le2t$（窄带上界） | 仍全部不可行（**非必需**）|
| 全部窄带（$j\le2t$ + $j_1\ge t$） | 仍全部不可行（**非必需**）|
| B3（$s_{nS}\le1-t$） | 出现洞：恰为薄层/端点 $k$（$m=8:k=5$；$m=9:k=5,6$；…即 $k\in[m-4,m-2]$）|
| 全部装箱行（B1/B2/B3/squeeze） | **全部可行**（机器角落本身存在，松弛非平凡假死）|

结论：不可行的来源是「**机器结构（Qcount+LZ/HZ）+ 装箱必要（B1/B2/B3/squeeze）**」；
B3 在薄层/端点必需，窄带与 A2/B4/SJrev 均不需要。

## 5. 分区证书样例（m=9，cnt=(1,6,0,1,0,0)，全 k 整数化支撑）

> 每行「行名:权重」，权重为 $w_i\cdot(\text{公共分母})$ 的分子；公共分母见行尾。
> 未列行权重 0。证 $A^Ty=0,\ b_t^Ty=0,\ b_c^Ty=-1$。

```
k=1: jrt1:50000 danger:150000 j1>=t:100000 jmax<=q1:150000 q1<=am:120000 am<=s1:120000 B1:120000 B2:50000 HZ:120000 Qcount:150000
k=2: srt1:50000 jrt1:250000 jrt2:200000 srt3:250000 jrt3:150000 srt4:200000 jrt4:100000 srt5:150000 jrt5:50000 srt6:100000 srt7:50000 jrt7:270000 danger:330000 j1>=t:300000 j7<=2t:10000 jmax<=q1:220000 q1<=am:145000 am<=s1:100000 squeeze:50000 HZ:300000 Qcount:330000
k=3: srt1:80000 jrt1:170000 srt2:40000 jrt2:120000 jrt3:80000 srt4:160000 jrt4:40000 srt5:120000 srt6:80000 jrt6:230000 srt7:40000 jrt7:190000 danger:270000 j1>=t:220000 jmax<=q1:150000 q1<=am:100000 am<=s1:120000 squeeze:40000 B2:10000 HZ:200000 Qcount:270000
k=4: srt1:90000 jrt1:110000 srt2:60000 jrt2:60000 srt3:30000 jrt3:30000 srt5:90000 jrt5:180000 srt6:60000 jrt6:150000 srt7:30000 jrt7:120000 danger:210000 j1>=t:160000 jmax<=q1:90000 q1<=am:60000 am<=s1:120000 squeeze:30000 B2:20000 HZ:120000 Qcount:210000
k=5: srt1:40000 jrt1:20000 srt2:30000 jrt2:10000 srt3:20000 srt4:10000 jrt4:160000 jrt5:150000 srt6:150000 jrt6:140000 srt7:140000 jrt7:130000 danger:170000 j1>=t:30000 jmax<=q1:120000 q1<=am:80000 am<=s1:50000 squeeze:10000 B3:130000 HZ:160000 Qcount:170000
k=6: srt1:10000 jrt1:2000 srt2:8000 srt3:6000 jrt3:28000 srt4:4000 jrt4:26000 srt5:2000 jrt5:24000 jrt6:22000 srt7:38000 jrt7:20000 danger:42000 j1>=t:4000 jmax<=q1:30000 q1<=am:20000 A1_8:12000 squeeze:2000 B3:36000 HZ:40000 Qcount:30000
k=7: srt1:10000 srt2:5000 jrt2:10000 jrt3:5000 srt4:15000 srt5:10000 jrt5:15000 srt6:5000 jrt6:10000 jrt7:5000 danger:145000 jmax<=q1:15000 q1<=am:2500 A1_1:50000 A1_5:20000 A1_8:15000 squeeze:5000 B2:45000 B3:95000 HZ:50000 Qcount:60000
k=8: jrt1:15000 jrt7:15000 danger:45000 jmax<=q1:15000 am<=s1:15000 L<=1:15000 t<=1/3:30000 A1_7:15000 B1:15000 B2:15000 Qcount:30000
```

（注：$k=1$ 用 B1 墙、$k=8=nS$ 用 B1+B2 双墙、$k=7=nS-1$ 用 B2+B3 墙、薄层 $k=6$ 用 B3+HZ+Qcount、
中段 $k=2..5$ 用 squeeze+HZ+Qcount——分区结构清晰。）

---

## 6. 薄层闭式 Farkas 证书（Step 2，已闭合：∀nS 显式权重）

薄层 $k\in[nS-2a,\ nS-2]$，记 $h:=nS-k$ 为 hi 区机器数，则薄层 $h\in[2,2a]$
（$a=1$：$h=2$；$a=2$：$h\in\{2,3,4\}$）。以下闭式对每个 $h$ 成立，与 $a$ 无关
（松弛的行集不含 S1v/JJrev，故 a=1/a=2 同一张证书）。

**证书权重（小整数；真实权重 = 下表 × 正标量）**：

| 行 | 权重 $w$ |
|---|---|
| danger（$p+t>\tfrac54$） | $4nS-4h-3$ |
| **Qcount**（$j_{h+1}\ge p-s_1+MG$） | $4nS-4h-3$ |
| **HZ**（$s_{k+1}>K-q_1$） | $4nS-4h-4$ |
| B3（$s_{nS}\le1-t$） | $4nS-5h-4$ |
| jmax≤q1（$j_{nS}\le q_1$） | $3(nS-h-1)$ |
| q1≤am | $2(nS-h-1)$ |
| am≤s1 | $nS-h$ |
| j1≥t | $h$ |
| squeeze（$\sum s+\sum j\le nS-t$） | $1$ |
| srt$_i$，$i=1..nS-h$ | $nS-h-i$ |
| srt$_i$，$i=nS-h+1..nS-1$ | $5nS-5h-4-i$ |
| jrt$_i$，$i=1..h$ | $h-i$ |
| jrt$_i$，$i=h+1..nS-1$ | $4nS-3h-3-i$ |

其余全部行（LZ、B1、B2、A1、窄带、$p\le1$、$s\ge1-2t$、$L\le1$、$t$ 窗口等）**权重 0**。

**逐变量配平结果**（已手算 + 精确 Fraction 核验 $nS=5..20$ 全过）：
$$\boxed{A^Tw=0,\qquad b_t^Tw=0,\qquad b_c^Tw=-\big(\tfrac14+(8nS-8h-7)\,MG\big)<0.} \tag{6.1}$$

**非负性**：$w\ge0$ 当 $h=2$（$nS\ge4$）、$h=3$（$nS\ge5$）、$h=4$（$nS\ge6$）。
$h=4,nS=5$ 的边点 $k=1$ 即 SS 墙（§2.1，已另证），无需本证书。

**逐变量配平核对（手算要点，供复核）**：令 $E:=h$（j1≥t 权）、$H:=nS-h$（am≤s1 权）、
$M:=4nS-4h-4$（HZ 权）、$D=N:=4nS-4h-3$（danger=Qcount 权）、$S:=1$（squeeze 权）。
- 变量 $p$：$-D+N=0$（danger 与 Qcount 权相等即为此）。
- 变量 $am$：$-G+H+\tfrac54 M-N=0$；变量 $q_1$：$-F+G+\tfrac14 M=0$（$F,G$ 为 jmax≤q1、q1≤am 权）。
- 变量 $s_1$：$\alpha_1-H+S=0$；$s_i$（$2..nS-1$）：$-\alpha_{i-1}+\alpha_i+S=0$，其中 $i=k+1$ 处再减 $M$（HZ）、$i=nS$ 处再减 $S$ 加 $L$（B3）——$\alpha_i$ 取上表 srt 权即全消。
- 变量 $j_1$：$\gamma_1-E+S=0$；$j_i$：$-\gamma_{i-1}+\gamma_i+S=0$，$i=h+1$ 处再减 $N$（Qcount）、$i=nS$ 处再 $+F$（jmax）——$\gamma_i$ 取上表 jrt 权即全消。
- $b_t^Tw=D-E-1-L=0$；$b_c^Tw=-\tfrac54 D+nS+L-MG(M+N)=-\tfrac14-MG(8nS-8h-7)$。

**含义**：薄层（razor 临界值域，§4）的机器角落 + rest 可装箱 **直接矛盾**，无需 sliver、
无需紧性结构、无需 α′/β′ 五步。这取代 §1.6 引理 1.8 与 §4.1/§4.2。

## 7. 结论与待办

- [x] Qcount 引理（(A) 类，mon2+pair 四行）已证。
- [x] 薄层闭式 Farkas 权重（∀nS，$h=2,3,4$）已证 + 精确核验。
- [ ] Qcount 需在 `完整证明_5over4.md` 附录 B 补一行 (A) 类登记；§4 可整体替换为本证书。
- [ ] 中段/端点（$k\le nS-2a-1$ 与 $k=m-2,m-1$）非本任务，仍由 §2.1/§2.2/§2.3/§3 符号化承担
      （本松弛对全 $k$ 也有数字证书，见 §3，闭式未反解）。

## 附录：复现

- 松弛构建 + 证书核验：`code/a1_value_lp2.py`（value 角落行）+ 本文件 §2 的三类附加行；
  精确有理核验走 `code/farkas_fixed.py` 的 `float_cert` + `rationalize_verify`。
- 实证背板：`realizable`/`assign_juniors` 判定下 sliver+可装箱点 **全部 ghost**
  （15469 / 58293 例，0 个机器可实现），与 main_tight_construct「4373/4373 全紧实例无效」互印。
