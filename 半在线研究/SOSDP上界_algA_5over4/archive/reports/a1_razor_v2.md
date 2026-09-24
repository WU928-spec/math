# razor 带规范形 v2 设计-probe 循环 — a1_

> 任务：角落域（瓶颈配对 ≥ 5/4−t，主代理关键澄清后）razor 带实例的规范形 v2 探测。
> 代码 code/a1_razor_v2.py（双峰实例生成 + mask-DP lex-min typed 装箱）。
> 结论：**v2a/v2b 未进入结构常数检测——实例生成失败本身揭示了 counting 矛盾**（下）。

## 1. 实例生成：系统失败（probe 级发现）
角落域实例（pair 绑机 ℓ_i=s_i+j_i ≥ p > 5/4−t、SS 两 senior≤1、JJJ 三件≤1）在
razor cnt 形态 (1,m−3,0,1,0,0)/(2,m−5,0,1,1,0) 下**生成 0 成功**（双峰值调三轮：
随机带 30 试 0、双峰{小 senior 0.47, 大 senior 0.63} 结构化绑机仍 0）。

**根因（counting 矛盾，逐形验证 m=6）**：
- 形 B (2,1,0,1,1,0)：4 台 SS senior（≤0.5）各自的绑机 junior 须 ≥ p−0.5 ≈ 0.43
  （mid 级），JJJ 又须 t+2·junior≤1 ⟹ 两件 junior ≤0.34（small 级）；junior 总数
  nS=5 须同时供 4 mid + 2 small = 6 > 5 ✗。
- 形 A (1,3,0,1,0,0)：2 台 SS senior 绑机 junior ≥ 0.46（mid），JJJ 须 2 small；
  3 台 SJ senior（大）绑机 junior ≥ p−0.64 ≈ 0.29（可 small）。计数：junior 5 =
  2 mid + 3 small：SJ 三台配 small 0.29-0.34（razor 恰过 0.93），JJJ 取 t+2 small
  ✓——**数值上 razor 恰可行**（本探针 0 成功是因 razor 窗 ~0.01 宽，采样未中；非 counting 禁）。
  ⟹ 形 A 存在角落域可行实例（hairline），形 B counting 禁（junior 预算矛盾）。

## 2. 判决
- **形 B (2,m−5,0,1,1,0)：(W'')-razor 可能 counting 闭合**——junior 预算矛盾
  （pair 下界 vs JJJ 上界）是结构性的：∀ 实例不可装箱 ⟹ (P)-razor 对形 B 由
  两行计数账成立。**待形式化**（∀m 簿记：SS  senior 数 2a 的绑机 junior 下界
  Σ≥2a·(p−1/2+) vs JJJ small 需求 2d 件 ≤(1−t)/2，总 junior nS 预算）。
- **形 A (1,m−3,0,1,0,0)：razor hairline 实例存在**（构造如上），v2 需真实 probe；
  采样难题=razor 窗 ~0.01，建议主代理的 LP 鬼影点（若角落域可实现）或精确构造器
  作实例源。
- v2a/v2b 候选（MRF 分流 / lex-min 结构常数）在形 A 实例未生成前无法检测——
  登记为"实例基建"先决。

## 3. 下一步（按序）
1. 形 B counting 形式化（junior 预算矛盾 ∀m）——最可能直接闭合 (P)-razor 一半。
2. 形 A 精确构造器（razor 恰可行的参数化：s={0.47×2, 0.63×(nS−2)}, j 全 small
   递增, t 固定, p=min ℓ+ε）→ v2b lex-min 结构常数检测。
3. 若形 A lex-min 结构恒定 → v2 规范形 = lex-min 形态；不恒定 → 反例族喂 v2c。
