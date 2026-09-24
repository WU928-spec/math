# Algorithms Better than LPT for Semi-Online Scheduling with Decreasing Processing Times

> **期刊**: Operations Research Letters 40 (2012) 349–352
> **作者**: T.C.E. Cheng（The Hong Kong Polytechnic University）、Hans Kellerer（Universität Graz）、Vladimir Kotov（Belarusian State University）
> **收稿**: 2012-01-20 | **修回**: 2012-05-08 | **录用**: 2012-05-16 | **在线**: 2012-06-04
> **DOI**: 10.1016/j.orl.2012.05.009
> **关键词**: Online algorithms; Semi-online algorithms; Competitive ratio; Multiprocessor scheduling

---

## 摘要

研究带**递减加工时间**的半在线多机调度问题（SOSDP）：$m$ 台同型并行机，最小化 makespan，工件按加工时间非增序到达。经典离线 LPT 算法（Graham, 1966）的 worst-case 界为 $\frac{4}{3} - \frac{1}{3m}$，此前一直没有人给出比 LPT 竞争比更优的半在线算法。本文给出：

- 对 $m \geq 3$，一个竞争比为 $\boxed{\frac{5}{4}}$ 的算法（Algorithm A）；
- 对 $m = 3$，一个**最优**算法（Algorithm A3），竞争比恰为 $\frac{1+\sqrt{37}}{6} \approx 1.18046$。

两个算法都是初等的，运行时间为线性（原文未展开；推导见下文 §2.1 与 `CKK2012_m3最优上界_A3_完整证明.md` §2.1）。

---

## 1. 引言

### 问题定义

- $n$ 个独立工件，加工时间 $p_1, \dots, p_n$，非抢占地分配到 $m$ 台同型机 $M_1, \dots, M_m$，目标最小化 makespan。
- **在线**版本中，每个工件必须立即且不可撤销地指派，不知道未来工件。算法性能用**竞争比**衡量：算法解与离线最优解 $C^*$ 的最坏比值。
- 机器 $M$ 的**负载**记为 $\ell(M)$。文中"大于 $x$ 的工件"即加工时间大于 $x$。

### 已知结果

| 结果 | 内容 |
|---|---|
| Graham [5, 4] | 列表调度（LS）竞争比恰为 $2 - \frac{1}{m}$，$m \leq 3$ 时最优 |
| Fleischer & Wahl [3] | 最好启发式，竞争比 $< 1.9201$（$m \to \infty$） |
| LPT [4] | 离线经典启发式：递减排序后依次放入当前最小负载机，界为 $\frac{4}{3} - \frac{1}{3m}$ |
| Hochbaum & Shmoys [6] | PTAS（对偶近似算法族） |

### 半在线模型（SOSDP）

实际问题常介于在线与离线之间。本文研究 **decreasing processing times** 半在线问题（SOSDP）：已知 $p_j \geq p_{j+1}$。

- **Seiden–Sgall–Woeginger [7]**（SSW, 2000）：首次研究 SOSDP。证明 $m=2$ 时 LPT（竞争比 $\frac{7}{6}$）最优；给出 $m \geq 3$ 的下界 $\frac{1+\sqrt{37}}{6} \approx 1.18046$。
- **Epstein & Favrholdt [1]**：两台均匀机上的 SOSDP。

**此前，没有人给出竞争比优于 LPT 的 SOSDP 算法。** 本文填补这一空白。

---

## 2. 任意机数下的 $\frac{5}{4}$-竞争算法（Algorithm A）

LPT 的界为 $\frac{4}{3} - \frac{1}{3m}$，仅在 $m \leq 3$ 时优于 $\frac{5}{4}$，故 Algorithm A 对 $m \geq 4$ 是改进。

### 算法描述

1. 将 $p_1, \dots, p_m$ 分别放入 $M_1, \dots, M_m$（每台机器一个）。
2. 设 $L := p_m + p_{m+1}$。
3. 对当前工件 $p_j$（$j \geq m+1$）：若存在机器 $M$ 使 $\ell(M) + p_j \leq \frac{5}{4}L$，则放入**负载最大**的这样一台机器；否则放入**负载最小**的机器。

> **直觉**：尽量把工件塞进"阈值 $\frac{5}{4}L$ 内负载最大"的机器（不贪心，主动避开隐患配对）；塞不下才退回 LPT 规则。

### 运行时间（原文一句话 "both algorithms are elementary and have linear running time"，此处补出推导）

**计算模型**：单位成本 RAM，只计基本算术与比较；$L:=p_m+p_{m+1}$ 在实例内固定，故阈值 $T:=\frac54L$ 也固定。工件按非增序到达，只需当前工件。

- **步骤 1–2**：$m$ 次放置 + 1 次加法 + 1 次常量乘法 ⟹ 一次性 $O(m)$。
- **步骤 3（每个工件一次）**：需要回答两个查询
  1. $\max\{\ell(M):\ell(M)\le T-p_j\}$（存在则选该机）——**带阈值的前驱查询**，上界 $T-p_j$ 随工件变化；
  2. 若 1 无解，取 $\min_M \ell(M)$（负载最小机）。
  随后更新该机负载（$+p_j$）。

| 实现 | 每工件 | 总计 | 空间 |
|---|---|---|---|
| 朴素扫描 $m$ 台机器 | $O(m)$ | $O(nm)$ | $O(m)$ |
| 平衡搜索树 / 跳表（键＝负载，允许并键：同一负载的多台机器各存一个条目） | $O(\log m)$（前驱 + 更新各 $O(\log m)$，最小值＝最左叶） | $O(n\log m)$ | $O(m)$ |
| $m$ 视为常数（该文语境） | $O(1)$ | $O(n)$ | $O(1)$ |

**结论**：原文的 "linear running time" 对 $m=3$ 的 Algorithm A3（见 `CKK2012_m3最优上界_A3_完整证明.md` §2.1）逐字成立；对一般 $m$ 的 Algorithm A，它只在把 $m$ 视为常数时逐字成立，否则按字面实现得到 $O(n\log m)$。在比较模型下"阈值前驱查询"本身有 $\Omega(\log m)$ 的下界，故 $O(n\log m)$ 已是该查询模型下的最优量级；原文未讨论数据结构，故**本条为原文声明，未展开**。

**精确算术注记**：阈值比较 $\ell(M)+p_j\le\frac54L$ 可用整数运算精确判定：$4\big(\ell(M)+p_j\big)\le5L$，无需浮点。

**工程备注**（原文未讨论）：SOSDP 中 $p_j$ 非增 ⟹ 查询上界 $T-p_j$ **非减**，且负载单调增；据此可用"按负载分桶 + 单调指针"降低常数因子。

### 定理 1

> **Theorem 1.** Algorithm A 是 SOSDP 的确定性算法，竞争比为 $\frac{5}{4}$。

### 证明（反证法 + 极小反例）

不妨设 $C^* = 1$。假设存在反例，取**极小**反例，其**失败工件** $z$ 是首个使某机器负载 $> \frac{5}{4}$ 的工件；由极小性 $z = p_n$ 是最后一个工件，且它被放到了**最小负载机**。

**事实 1**：$z > \frac{1}{4}$ 且不存在 $\leq \frac{1}{4}$ 的工件（$x_4 = 0$）。

> 证明：$z$ 到来前总负载 $\leq m$（$C^* = 1$），故最小负载机负载 $\leq 1$；又 $z$ 放最小负载机使负载 $> \frac{5}{4}$，故 $z > \frac{5}{4} - 1 = \frac{1}{4}$。∎

**事实 2**：最优解中每台机器至多 3 个工件。

> 证明：所有工件 $> \frac{1}{4}$，每台机器负载 $\leq 1$，4 个工件之和 $> 1$。∎

按加工时间分类：

- $X_1 = \{p_j \mid p_j > \frac{3}{4}\}$
- $X_2 = \{p_j \mid \frac{3}{4} \geq p_j > \frac{1}{2}\}$
- $X_3 = \{p_j \mid \frac{1}{2} \geq p_j > \frac{1}{4}\}$
- $X_4 = \{p_j \mid p_j \leq \frac{1}{4}\}$（已证为空）

记 $x_i = |X_i|$。记最优解中恰含 1、2、3 个工件的机器集合为 $\mathcal{M}_1^*, \mathcal{M}_2^*, \mathcal{M}_3^*$，数量为 $m_1^*, m_2^*, m_3^*$。

**式 (1)**：$n_{1/2} \le m_1^* + m_2^*$

> 证明：$> \frac{1}{2}$ 的工件不能两两共箱（和 $> 1$），故每个 $> \frac{1}{2}$ 的工件独占一台、至多再配一个 $\leq \frac{1}{2}$ 的工件；含 $> \frac{1}{2}$ 工件的机器只能是 1 件机或 2 件机。∎

**式 (2)**：$n_{3/8} \le m_1^* + 2m_2^* + m_3^* = m + m_2^*$

> 证明：3 件机的第二个工件 $< \frac{3}{8}$（否则前两个 $\geq \frac{3}{8}$、第三个 $> \frac{1}{4}$，和 $> 1$），故 3 件机至多贡献 1 个 $> \frac{3}{8}$ 的工件；1 件机至多 1 个，2 件机至多 2 个。∎

若最优解中每台机器至多 2 个工件（$m_3^* = 0$），则 $C^* \geq \max_{j=1,\dots,m}(p_j + p_{2m-j+1})$，此时 Algorithm A 平凡地是 $5/4$-competitive。故 $m_3^* > 0$，且由此 $z \leq \frac{1}{3}$。

分两大情形：

**Case 1: $p_1 + p_{m+1} \leq \frac{5}{4}L$**

令 $\mathcal{M}_1 = \{M_1, \dots, M_{m_1^*+m_2^*}\}$，$\mathcal{M}_2 = \{M_{m_1^*+m_2^*+1}, \dots, M_m\}$。由 $p_1 + p_{m+1} \leq \frac{5}{4}L$，Algorithm A 把 $p_{m+1}, \dots, p_{m+m_1^*+m_2^*}$（共 $m_1^* + m_2^*$ 个工件）放进 $\mathcal{M}_1$。

由式 (1) 知 $\mathcal{M}_2$ 上所有工件 $\leq \frac{1}{2}$；由式 (2) 知 $\mathcal{M}_2$ 上所有次工件 $\leq \frac{3}{8}$。除 $z$ 外至少 $2(m_1^* + m_2^*)$ 个工件落在 $\mathcal{M}_1$，故 $\mathcal{M}_2$ 中某台机器在 $z$ 到来前至多 2 个工件，$z$ 可作为第三个工件放入，负载 $\leq \frac{1}{2} + \frac{3}{8} + \frac{1}{3} = \frac{29}{24} < \frac{5}{4}$，与 $z$ 是失败工件矛盾。

**Case 2: $p_1 + p_{m+1} > \frac{5}{4}L$**

若最优解有单工件机器 $x$，可与 $p_1$ 交换使 $p_1$ 独占一机且不增大最优 makespan；删去该机及 A 解中与 $p_1$ 同机的其余工件（除 $z$），得一新实例：$L$ 不变、其余指派不变、$z$ 至多移到更差位置，由极小性得矛盾。故 $m_1^* = 0$。

又由 $z > \frac{1}{4}$ 得 $x_1 = 0$（$X_1$ 工件 $> \frac{3}{4}$，配任何 $> \frac{1}{4}$ 的工件和 $> 1$，必独占一机；$m_1^* = 0$ 故 $X_1 = \emptyset$）。

**Subcase 2a: $\frac{5}{4}L \geq 1$**

由 $p_1 + p_{m+1} > \frac{5}{4}L \geq 1$ 得 $p_1 > \frac{1}{2}$，$p_1$ 所在最优机 $M_1^* \in \mathcal{M}_2^*$。取最大 $\ell$ 使 $p_1 + p_\ell \leq 1$（由 $p_1 + p_{m+1} > 1$ 得 $\ell > m+1$）。由 $\frac{5}{4}L \geq 1$ 知存在 $\ell' > \ell$ 被 A 放入 $M_1$ 且 $p_1 + p_{\ell'} \leq \frac{5}{4}L$。删除 $M_1$ 上的 $p_1, p_\ell$（及可能的第三工件）并删一机；最优解中用 $p_{\ell'}$ 替换 $p_\ell$（$\ell' > \ell \Rightarrow p_{\ell'} \geq p_\ell$）不增大最优值，与极小性矛盾。

**Subcase 2b: $\frac{5}{4}L < 1$**

记 $z$ 到来前的指派为 $\mathcal{A}$，其中恰含 1、2、$\geq 3$ 个工件的机器数为 $m_1, m_2, m_3$。

- 单工件机器 $M$：$\ell(M) + z \leq \frac{3}{4} + \frac{1}{3} < \frac{5}{4}$（因 $x_1 = 0$，$\ell(M) \leq \frac{3}{4}$），故 $m_1 = 0$。
- 双工件机 $y_1 \geq y_2$ 且 $y_1 \in X_3$：$y_1 + y_2 + z \leq \frac{1}{2} + \frac{L}{2} + \frac{1}{3} \leq \frac{5}{4}$（$y_1 \leq \frac{1}{2}$，$y_2 \leq p_{m+1} \leq \frac{L}{2}$，$z \leq \frac{1}{3}$），故 $y_1 \in X_2$ 且 $m_2 \leq x_2$。

于是（$m = m_2 + m_3$）

$$n \;\geq\; 2m_2 + 3m_3 + 1 \;=\; 3m - m_2 + 1 \;\geq\; 3m - x_2 + 1$$

另一方面，$X_2$ 中每个工件在最优解中独占一台、至多再配一个（$X_1 = X_4 = \emptyset$，故工件只有 $X_2, X_3$ 两类），故

$$n \;\leq\; 2x_2 + 3(m - x_2) \;=\; 3m - x_2$$

两式矛盾。$\blacksquare$

---

## 3. 结论

- 给出 SOSDP 上**优于 LPT** 的简单算法（$\frac{5}{4}$，任意 $m$），以及 $m = 3$ 时的**最优**算法（$c = \frac{1+\sqrt{37}}{6}$）。
- **开放问题**：一般 $m$ 下，$\frac{5}{4}$ 与下界 $\frac{1+\sqrt{37}}{6}$ 之间仍有显著差距。

**致谢**: 部分受 The Hong Kong Polytechnic University 基金 G-T397 资助。

---

## 参考文献

1. L. Epstein, L.M. Favrholdt, *Optimal non-preemptive semi-online scheduling on two related machines*, Journal of Algorithms 57 (2005) 49–73.
2. U. Faigle, W. Kern, G. Turán, *On the performance of on-line algorithms for partition problems*, Acta Cybernetica 9 (1989) 107–119.
3. R. Fleischer, M. Wahl, *On-line scheduling revisited*, Journal of Scheduling 3 (2000) 343–353.
4. R.L. Graham, *Bounds on multiprocessing timing anomalies*, SIAM Journal on Applied Mathematics 17 (1969) 263–269.
5. R.L. Graham, *Bounds for certain multiprocessor anomalies*, Bell System Technical Journal 45 (1966) 1563–1581.
6. D.S. Hochbaum, D. Shmoys, *Using dual approximation algorithms for scheduling problems: theoretical and practical results*, JACM 34 (1987) 144–162.
7. S. Seiden, J. Sgall, G. Woeginger, *Semi-online scheduling with decreasing job sizes*, Operations Research Letters 27 (2000) 215–222.
