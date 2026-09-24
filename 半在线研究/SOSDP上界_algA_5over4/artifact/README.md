# Artifact：口袋2 计算闭合证据链（m=4..50）

半在线调度证明项目（Algorithm A 竞争比 5/4）的计算证据包：**口袋2（最闲机为单子机）角落
在修正版 LP + 保序约束下 m=4..50 全闭（零洞）**，证书经独立纯 Fraction 复核。

- 打包时间：2026-09-22（agent-4）。
- 来源目录：`半在线研究/SOSDP上界_algA_5over4/`（打包时名为 `research/2026-09-19_algA_5over4/`）。
- **2026-09-24 整理说明**：三个大证文明文（15M / 97M / 80M）已从本包移出，改为只保留
  `../archive/data/` 下的 gzip 规范副本（**内容无损，gunzip 即恢复**；sha256 见 `../archive/data/SHA256SUMS`）。
  本包内不再存明文大件；下列复核步骤与全部结论不变。

## 1. 结论与规模

| 范围 | 情形数 (m,cnt,k) | 洞 | 证书 | 独立复核 |
|---|---|---|---|---|
| m=4..30 | 43981 | 0 | 43981 份 | PASS 43981 / FAIL 0 |
| m=31..45 | 263575 | 0 | 263575 份 | PASS 263575 / FAIL 0 |
| m=46..50 | 204312 | 0 | 204312 份（+97 重复行） | 部分（123425 行 PASS，其余 80984 行未验，见 §5） |
| **合计 m=4..50** | **511868** | **0** | | |

另含遗留编码（build_fixed 无保序 / build_fixed2 二步）证书：419 + 3021 份，均全量复核 PASS
（m=4..11 一步全闭；二步闭合 3021 个 (m,cnt,k,jj2)，m=12..30 残留 304 个由保序引理杀死——
见 `../archive/collab/BOARD.md`、`../archive/collab/SEMANTICS.md`）。

## 2. 证书存放位置

| 范围 | 规范副本（压缩，在 `../archive/data/`） | 行数 | 原明文（已删） |
|---|---|---|---|
| m=4..30 | `pocket2_onestep_order_certs.txt.gz`（756K） | 43981 | 15M |
| m=31..50 | `pocket2_onestep_order_certs_31_45.txt.gz`（8.6M） | 467984 | 97M + 80M |
| 遗留一步 / 二步 | 本包 `certs/pocket2_legacy_build_fixed.jsonl` / `..._fixed2_2step.jsonl` | 419 / 3021 | —（原样保留） |

> **m=31..50 的 gz 是合并整文件**：前 263575 行 = m=31..45（原 97M），其后 204409 行 = m=46..50（原 80M）。
> “未验尾巴”是整文件的后 80984 行；`certs/unverified/*.vprog.note` 记录了断点对应关系。

## 3. 目录结构

```
artifact/
├── README.md                       ← 本文件
├── manifest.sha256                 ← 本包内全部文件的 sha256（自洽快照）
├── certs/
│   ├── pocket2_legacy_build_fixed.jsonl           419 份（旧编码一步，全验）
│   ├── pocket2_legacy_build_fixed2_2step.jsonl    3021 份（旧编码二步，全验）
│   └── unverified/
│       └── pocket2_onestep_order_certs_46_50.partial.txt.vprog.note
│           （原 partial.txt 明文已删；正文在 ../archive/data/pocket2_onestep_order_certs_31_45.txt.gz 的后 204409 行）
└── code/                           ← 自足复核器 + 扫描驱动
    ├── README.md                   ← 逐文件说明
    ├── fast_lp.py / fast_scan.py / fast_scan_31_45.py
    └── verify_certs.py / pairing_feasible.py / farkas_fixed.py / second_step.py
```

`code/` 内 7 个 .py 与项目 `code/` 顶层的同名文件**逐字节相同**（整理时已核对）；此处保留一份，
是为了让本证据包**自足**——从 `artifact/code/` 内运行即可，不依赖项目其他文件。

## 4. 复现步骤

环境：macOS + Python 3.12 venv（`/Users/a123456/math/.venv`，依赖 numpy/scipy/sympy）。
python 一律用 `/Users/a123456/math/.venv/bin/python`。以下命令在项目根（`半在线研究/SOSDP上界_algA_5over4/`）执行。

### 4.1 复核已验证书（最核心）——先从 gz 还原

```bash
cd 半在线研究/SOSDP上界_algA_5over4

# m=4..30（43981 份，约 5-8 min @2 workers）
# ⚠️ 还原时务必保留原文件名（内含 "onestep_order"）——复核器靠这个子串判定证书格式，见下方注②
gunzip -c archive/data/pocket2_onestep_order_certs.txt.gz > /tmp/pocket2_onestep_order_certs.txt
nice -n 15 .venv/bin/python artifact/code/verify_certs.py /tmp/pocket2_onestep_order_certs.txt

# m=31..50 全量（467984 份；分片自退 + 断点续跑，每片 ≤8min，重复执行至 EOF）
gunzip -c archive/data/pocket2_onestep_order_certs_31_45.txt.gz > /tmp/pocket2_onestep_order_certs_31_50.txt
A4_VERIFY_SLICE=24000 nice -n 15 .venv/bin/python artifact/code/verify_certs.py /tmp/pocket2_onestep_order_certs_31_50.txt

# 遗留编码（秒级）
.venv/bin/python artifact/code/verify_certs.py artifact/certs/pocket2_legacy_build_fixed.jsonl
.venv/bin/python artifact/code/verify_certs.py artifact/certs/pocket2_legacy_build_fixed2_2step.jsonl
```

预期输出：`PASS <份数>, FAIL 0`。复核器不调用 linprog：用 `rows_fixed`/`build_fixed`/`build_fixed2`
重建约束矩阵（Fraction 精确），纯 Fraction 核对 Aᵀy=0、btᵀy=0、bcᵀy=−1、y≥0。
重名装箱行（SS/SJ/JJJ/JJ）由“列平衡强制指派”完备对齐。

> ⚠️ **两个已知遗留缺陷（整理时未改动脚本逻辑，实测复现）**：
> ① **无参数运行等于空跑**：`verify_certs.py` 不带参数时，缺省文件表 `DEFAULTS` 按脚本自身目录
> （`artifact/code/`）解析路径，而证书并不在该目录，结果全部“不存在，跳过”，末尾打印
> `总计: PASS 0, FAIL 0`——**这是空跑，不是通过**。请一律显式传入证书路径。
> ② **格式按文件名子串判定**：传参时，basename 含 `onestep_order` → 口袋2 fast 格式（`p2fast`）；
> 否则若以 `.txt` 结尾 → 口袋1 txt 格式（`p1txt`，需 `pocket1_bins.py`，**不在本包**）；其余 →
> jsonl。所以从 gz 还原时**必须保留原文件名**：若把 m=4..30 的证书改名成 `certs_4_30.txt`，
> 会被误判为口袋1 格式而报 `ModuleNotFoundError: No module named 'pocket1_bins'`。

### 4.2 重跑扫描（重新生成证书）

```bash
# m=4..30（8 workers 基线 102s；CPU 条款下请先改 workers≤2 或设 nice）
.venv/bin/python artifact/code/fast_scan.py            # 自带断点 fast_scan_progress.jsonl
# m≥31（workers=2、nice15、440s 时间盒自退，被杀/超时后直接重跑同一命令续）
nice -n 15 .venv/bin/python artifact/code/fast_scan_31_45.py 31 50
```

预期：每个 m 打印 `洞 0 个`；全部情形输出精确常数证书（float 定位 + 支撑行 Fraction 验证）。
实测耗时基线（M 系 Mac，负载中等）：m=46..50 单 m 各 3.5/4.7/5.8/≈8/≈11.5 min（2 workers）；
复核 ~60-90 份/s（2 workers, nice 15）。

### 4.3 m=46..50 未验部分续验

未验部分是还原后整文件的**后 80984 行**。续验：对该文件按 §4.1 分片式执行，先跳过已验前缀
（断点/sidecar 对应关系见 `certs/unverified/pocket2_onestep_order_certs_46_50.partial.txt.vprog.note`）。

## 5. 诚实声明（已知边界）

- 复核是**快照语义**：`manifest.sha256` 锁定本包内文件与其复核时内容逐字节一致。
  移出的大证文明文由 `../archive/data/SHA256SUMS` 锁定其 gz 规范副本（gunzip 后与复核时内容一致）。
- m=46..50 证书**未全验**：已验部分全 PASS，未验部分不当作已验证据引用。
- 本证据链仅覆盖口袋2；口袋1（agent-1）/ 口袋3 的证据链不在本包。
  口袋3 曾有一版“统一体积证书”（agent-4 会话22）建于已判 INVALID 的约束 `y>=1-2t`，
  **已作废，不在本包**（见 `../archive/collab/SEMANTICS.md`）。
- LP 语义合法性依赖：修正 firststep 编码、保序引理、装箱固定分组 w.l.o.g.（最后一项
  SEMANTICS 标注“字面为假/角落语境可接受”，严格化未完成——为本证据链的唯一 SUSPECT 依赖）。
