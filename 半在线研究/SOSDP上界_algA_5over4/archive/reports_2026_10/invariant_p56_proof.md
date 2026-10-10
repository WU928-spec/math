# A4c: the "(p5,p6)-invariant", fill-rotation generalization, and ≤2-item machine bounds

**Status:** honest report — the *global* claim in the task is **FALSE**; the invariant holds **only in the Λ = p4+p5 branch** (and there it is true, with a clean proof). Fill-rotation **does not** generalize to later pairs (explicit counterexamples + trace counts). The ≤2-item machine has a clean C*-level bound **only in the fill subcase**; the overflow subcase is exactly the known 4% gap and has no per-machine C*-level bound.

All numerics below were re-derived/checked by me from the committed files in
`SOSDP上界_algA_5over4/code/m3_a3_verify/jl/` (single core, as requested).

---

## 0. Notation and the algorithm (as stated in the task)

- 4 machines M1..M4. Items arrive nonincreasingly `p1 >= p2 >= ... >= pn`, each `> alpha' = 4/15`.
- Initial step: `p_i` goes to `M_i`, `i = 1..4`.
- Safety line `tau = rho * Lambda`, `Lambda = max(p1, p4+p5)`, `rho = c = (1+sqrt(37))/6 ≈ 1.18046`.
- For `j >= 5`: `E_j = { m : ℓ_m + p_j <= tau }`.
  - if `E_j != ∅`, put `p_j` on the **fullest** machine of `E_j` (ties → smallest index);
  - else put `p_j` on the **lightest** machine (ties → smallest index).
- `C*` = optimal makespan; normalize `C* = 1`.

Two branches: **B** = `p4+p5 >= p1` (`Lambda = p4+p5`), **A** = `p1 >= p4+p5` (`Lambda = p1`).
(Ties `p1 = p4+p5` belong to both; the argument for branch B below only needs `>=`.)

Useful constants: `rho - 1 = (sqrt(37)-5)/6 ≈ 0.18046 < 4/15 ≈ 0.26667 < ...`, and `rho < 6/5`.
In particular **`rho - 1 < 4/15`**, so every item `p_j >= 4/15 > rho - 1`.

---

## 1. Task 1 — does p5 and p6 ever share a machine?

### 1.1 The global claim is FALSE (counterexample in branch A, Λ = p1)

Take `n = 6`, `p = (1, 1/2, 2/5, 2/5, 7/20, 3/10)`.

- All items `> 4/15`. A feasible packing with makespan 1 is
  `M1={1}, M2={1/2, 7/20}=17/20, M3={2/5, 2/5}=4/5, M4={3/10}`;
  since `p1 = 1`, we have `C* = 1`.
- `Lambda = max(p1, p4+p5) = max(1, 2/5+7/20=3/4) = 1`, so branch A, `tau = rho`.
- Step 5: `E_5 = {m : p_m + 7/20 <= rho}`.
  `1+7/20 = 27/20 = 1.35 > rho` (M1 out); `1/2+7/20 = 17/20 < rho`; `2/5+7/20 = 3/4 < rho`.
  So `E_5 = {2,3,4}`, argmax = M2 (load `1/2`). **p5 → M2.** Loads `(1, 17/20, 2/5, 2/5)`.
- Step 6: `E_6 = {m : ℓ_m + 3/10 <= rho}`.
  `1+3/10 = 13/10 > rho` (M1 out); `17/20 + 3/10 = 23/20 = 1.15 <= rho ≈ 1.18046`; `2/5+3/10 = 7/10`.
  So `E_6 = {2,3,4}`, argmax = M2 (load `17/20`). **p6 → M2.**

So **p5 and p6 are both placed on M2**. The algorithm's makespan is `1/2 + 7/20 + 3/10 = 23/20 = 1.15`,
ratio `1.15 <= 6/5`, so this is *not* a competitive-ratio violation — it only disproves the structural
invariant "p5 and p6 never share a machine" as a universal statement.

This was also confirmed by direct simulation with `a4_sim` (coords `[:p1,:p45]`, no slot, no branch):

```
p = [1.0, 0.5, 0.4, 0.4, 0.35, 0.3]
asg = [[1], [2,5,6], [3], [4]]      # p5,p6 both on machine 2
makespan = 1.15,  opt = 1.0
```

**Conclusion for Task 1:** the invariant as literally stated ("for any instance") is **false**. It is true in the Λ = p4+p5 branch, proved next.

### 1.2 The invariant IS true in branch B (Λ = p4+p5) — proof

**Theorem (branch-B (5,6)-invariant).** Assume `p4+p5 >= p1` (so `tau = rho(p4+p5)`) and `C* = 1`,
`n >= 6`, all items `>= 4/15`. Let `X` be the machine that receives `p5`. Then `X ∉ E_6`, hence
`p6` is placed on a machine different from `X`.

**Proof.**

1. `X ∈ {1,2,3,4}`, so its initial item satisfies `p_X >= p4`.
2. **Claim `p4+p5 <= C* = 1`.** Among the first five items `p1..p5`, pigeonhole forces two of them
   onto the same machine in an optimal packing. That machine's load is at least the sum of those two
   items, which is at least the smallest pair-sum `p4+p5`. Hence `C* >= p4+p5`.
3. `p6 >= 4/15 > rho-1`, and `p4+p5 <= 1` implies `(rho-1)(p4+p5) <= rho-1 < 4/15`. Therefore
   `p6 > (rho-1)(p4+p5)`, i.e.
   `p4 + p5 + p6 > rho(p4+p5) = tau`.
4. Since `p_X >= p4`, `p_X + p5 + p6 >= p4 + p5 + p6 > tau`.
   But `p_X + p5` is exactly `ℓ_X` after step 5, so `ℓ_X + p6 > tau`, i.e. **`X ∉ E_6`**.
5. Therefore step 6 cannot place `p6` on `X`. ∎

Remarks:

- The proof never uses the *argmax/tie* part of the E-rule: it shows the receiving machine is simply
  **ineligible** at step 6. Hence it holds for **every** tie-breaking, which is consistent with the
  trace enumeration (see §4) counting *all* argmax-tie variants and finding 0 co-occurrences.
- The two facts that make the argument work are specific to step 5: (i) before step 5 the four loads
  are exactly the four initial items (so `p_X >= p4`), and (ii) `p4+p5` is a genuine `C*`-lower bound.
  Both disappear at later steps — this is precisely why the principle does not generalize (§2).

### 1.3 What the trace fact actually is

The committed fact was verified on the enumerated family
`{n = 10, items >= 4/15, C* <= 1, Lambda = p4+p5}` (the "卡点家族", which additionally carries
`p2 <= p3+p4, p3 <= p4+p5, p5 <= p3`). On that family the count of traces with `a5 = a6` is **0**.
This is *consistent with*, and strictly weaker than, Theorem 1.2 (which covers the whole Λ = p4+p5
branch with no extra predicates). The trace enumeration never inspected the Λ = p1 branch, where the
invariant fails (§1.1).

---

## 2. Task 2 — does "fill rotation" generalize to consecutive pairs `(p_j, p_{j+1})`, `j >= 6`?

**No.** It already fails for `j = 6`, and it keeps failing. Both pieces of evidence:

### 2.1 Trace counts on the 6533-trace family (Λ = p4+p5, "卡点家族")

| consecutive pair | traces with `a_j == a_{j+1}` (of 6533) |
|---|---|
| (p5, p6) | **0** |
| (p6, p7) | **348** |
| (p7, p8) | **760** |
| (p8, p9) | **1154** |
| (p9, p10) | **424** |

(Counted by parsing `fam10_leaves2_all.txt`: fields 1..6 are `a5..a10`.)

### 2.2 Explicit actual-algorithm counterexamples (strict branch `p4+p5 > p1`, `C* = 1`)

The following instances were found by running the *actual* A4c simulator (`a4_sim`, smallest-index ties);
each is normalized to `C* = 1` (up to `1e-12`) and all items `>= 4/15`. The column `a5..a10` is the
machine assignment the algorithm produces.

| pair | witness `p` (rounded, 8 decimals) | `a5..a10` (machines) | failure mode |
|---|---|---|---|
| (p6,p7) | `(0.68756214, 0.68503128, 0.40575376, 0.36996341, 0.31911987, 0.31496872, 0.29645928, 0.29347524, 0.27980848, 0.27949423)` | `3 4 4 2 1 3` | p6 fill on M4, then p7 **overflow** on M4 (lightest) |
| (p7,p8) | `(0.72377760, 0.44776386, 0.41319048, 0.37469795, 0.35953052, 0.34941754, 0.31509682, 0.29674635, 0.27770894, 0.27622240)` | `2 3 4 4 1 3` | p7 fill on M4, then p8 **overflow** on M4 |
| (p8,p9) | `(0.50938434, 0.50722893, 0.49277107, 0.41132824, 0.33023384, 0.32930571, 0.32722890, 0.32665266, 0.32615986, 0.31856737)` | `1 2 3 4 4 3` | p8 fill on M4, then p9 **overflow** on M4 |
| (p9,p10) | `(0.54555616, 0.47569549, 0.47493965, 0.46171028, 0.44650288, 0.39450237, 0.31651483, 0.27254533, 0.27062103, 0.26766870)` | `1 2 3 3 4 4` | p9 fill on M4, then p10 **fill** on M4 (M4 still eligible) |

In every row `p4+p5 > p1` (strict branch B) and the machine of the two consecutive items is the same.
All makespans are `< 6/5` (≈ 1.004, 1.039, 1.139, 1.064), so these are structural failures, not ratio
violations.

**Why the principle breaks.** The step-5 argument used `p_X >= p4` and the C*-bound `p4+p5 <= C*`,
which only hold because before step 5 the machines carry exactly the initial items. Later, the machine
receiving `p_j` can be a *tail-light* machine (e.g. M4 holding `p4 + p_j'`), and the two failure modes
are:

1. `p_j` is a fill on machine `X`, `X` becomes ineligible for `p_{j+1}` (`ℓ_X + p_{j+1} > tau`) —
   but `E_{j+1} = ∅` and `X` happens to be the **lightest**, so `p_{j+1}` is overflowed onto `X`.
2. `p_j` is a fill on `X` and `X` **stays eligible** for `p_{j+1}` (`ℓ_X + p_j + p_{j+1} <= tau`),
   and it is still the fullest eligible machine.

Both modes occur in the table above, so "consecutive fill items rotate to distinct machines" is false.

---

## 3. Task 3 — a bound for "≤2-item machines"

**Definition.** A machine is a *≤2-item machine* if its final content is its initial item `p_m`
(`m = 1..4`) plus **at most one** later item. The later item (if present) is either a *fill* item
(placed by the E-rule) or an *overflow* item (placed by the lightest rule).

### 3.1 Fill subcase — clean C*-level bound (proved)

**Lemma (fill receiver).** If a machine's last (and only extra) item was placed by the E-rule at step `j`,
then its final load is `<= tau <= rho*C* < (6/5)*C*`.

*Proof.* E-rule placement means `ℓ_m^{j-1} + p_j <= tau`; the machine receives nothing after `j`, so its
final load equals `ℓ_m^{j-1} + p_j <= tau`. Now `tau = rho * max(p1, p4+p5)`:
`p1 <= C*` is immediate, and `p4+p5 <= C*` by the pigeonhole argument in §1.2. Hence
`tau <= rho*C* ≈ 1.1805*C* < 1.2*C*`. ∎

So the answer to the literal question ("initial item + at most one **fill** item") is: **yes**, the load
is `<= rho*C* < (6/5)*C*`, and this is a clean, C*-level bound.

### 3.2 Overflow subcase — no clean per-machine C*-level bound (this is the 4% gap)

If the single extra item was placed by the **lightest** rule at step `j` (`E_j = ∅`), then:

- The machine was the lightest just before step `j`, so
  `ℓ_m^{j-1} <= (1/4) * Σ_{i<j} p_i`, and its final load is
  `<= (1/4) Σ_{i<j} p_i + p_j`.
  (This is the "min ≤ average" bound; it is valid for **any** overflow placement, and summing over all
  final steps gives the uniform bound `ℓ_max <= max(tau, max_j [ (1/4)Σ_{i<j}p_i + p_j ])` — the §2o
  bound in the exploration record.)
- This bound is **not** a C*-level bound: it can reach `5/4 * C*`, which is exactly the documented 4%
  gap between the uniform bound (1.25) and the true ceiling (1.2). The exploration record's LP/MILP
  evidence shows the per-machine constraints alone cannot close it: no-boxing LP gives 1.29, +counting
  1.25, +boxing 1.2444 — all `> 1.2`.

**Honest statement.** I can prove the fill subcase cleanly (`ℓ <= rho*C*`). I can **not** prove a
per-machine C*-level bound (`ℓ <= (6/5 - z)*C*` style) for the overflow subcase, and no such bound follows
from per-machine reasoning; closing 6/5 there requires the trajectory-level "spread" lemma already
identified in the exploration record (the TL lemma / 引理 O), not a load cap on a single ≤2-item machine.
A trivial bound that *does* hold for the overflow subcase is `load = p_m + p_j <= p_m + p5 <= p1 + p5 <= 2C*`,
which is useless for 6/5.

---

## 4. Verification log

Run from `SOSDP上界_algA_5over4/code/m3_a3_verify/jl/` with `nice -n 12 julia --project=. ...` (single core).

1. **Branch-A counterexample** (`/tmp/test_p56.jl`, `a4_sim` with coords `[:p1,:p45]`):
   `p = [1, .5, .4, .4, .35, .3]` → `asg = [[1],[2,5,6],[3],[4]]`, makespan `1.15`, opt `1.0`.
2. **Trace counts** (Python parse of `fam10_leaves2_all.txt`): 6533 lines;
   `a5==a6`: **0**; `a6==a7`: 348; `a7==a8`: 760; `a8==a9`: 1154; `a9==a10`: 424.
3. **Branch-B random sanity check** (`/tmp/check_branchB.jl`, 20000 random n=10 instances,
   filtered to `p4+p5 >= p1`, `C*` normalized, items `>= 4/15`): 563 in-branch instances,
   **0 violations** of `a5 != a6` (independent of, but consistent with, the proof).
4. **Explicit generalization counterexamples** (`/tmp/search_direct.jl`, 93k direct branch-B samples):
   actual-algorithm witnesses for `(p6,p7)`, `(p7,p8)`, `(p8,p9)`, `(p9,p10)` as in §2.2.
5. **E-set failure-mode printout** (`/tmp/print_E.jl`): confirms the two failure modes in §2.2.

---

## 5. Proven vs numerically supported

| Statement | Status |
|---|---|
| (p5,p6) never share a machine **in branch Λ = p4+p5** | **Proven** (§1.2), tie-independent |
| (p5,p6) never share a machine **in branch Λ = p1** | **FALSE** — explicit counterexample `(1, 1/2, 2/5, 2/5, 7/20, 3/10)` (§1.1) |
| (p5,p6) never share a machine **for any instance** | **FALSE** (fails in branch A) |
| fill rotation generalizes to `(p_j,p_{j+1})`, `j >= 6` | **FALSE** — trace counts + explicit instances (§2) |
| ≤2-item machine with a fill item has load `<= rho*C* < (6/5)C*` | **Proven** (§3.1) |
| ≤2-item machine with an overflow item has a per-machine C*-level bound | **Not proven / not true from per-machine reasoning** (§3.2) |

**Net message for the 6/5 proof.** The structural invariant can be used *only in the Λ = p4+p5 branch*;
the Λ = p1 branch must be handled by a separate argument. The exploration record already indicates the
Λ = p1 branch is not the bottleneck: it is **empty** at `n = 12` (proved there, "n=12 且 Λ=p1 家族为空"),
while the tight `1.2` ceiling is a `n = 10`, Λ = p4+p5 case. The ≤2-item-machine route closes the fill case
cleanly but does **not** close the overflow case; that remains the TL / 引理 O problem.
