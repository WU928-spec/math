# a4_one.jl <KIND> —— 单条规则的固定预算攻击（供并行对比）
# 用法：julia --project=. a4_one.jl A4c   （KIND ∈ A4c | M1 | M4 | S1 | H2）
include("common.jl")
include("a4_lib.jl")

const KIND     = Symbol(ARGS[1])
const SEEDS    = (1, 7, 2026)
const RESTARTS = 50
const ROUNDS   = 300

function rule(p::Vector{Float64}, kind::Symbol)
    n = length(p); load = zeros(4); cnt = zeros(Int, 4)
    put(j, m) = (load[m] += p[j]; cnt[m] += 1)
    for j in 1:min(4, n); put(j, j); end
    n <= 4 && return maximum(load)
    Λ0 = max(p[1], p[4] + p[5]); seen = sum(p[1:4]); lpt = false
    for j in 5:n
        seen += p[j]
        τ = kind == :H2 ? min(C_TARGET * Λ0, C_TARGET * (seen / 4)) : C_TARGET * Λ0
        if kind == :M4 && lpt
            put(j, argmin(load)); continue
        end
        E = [m for m in 1:4 if load[m] + p[j] <= τ]
        if isempty(E)
            kind == :M4 && (lpt = true)
            put(j, argmin(load))
        elseif kind == :S1
            (cnt[1] == 1 && p[1] + p[j] <= τ) ? put(j, 1) : put(j, argmin(load))
        elseif kind == :M1
            lite = argmin(load); E2 = setdiff(E, [lite])
            put(j, isempty(E2) ? lite : E2[argmax(load[E2])])
        else
            put(j, E[argmax(load[E])])
        end
    end
    return maximum(load)
end

rr(p::Vector{Float64}) = rule(p, KIND) / opt_makespan(p, 4)

function attack()
    best = 0.0; bp = Float64[]; bn = 0
    for seed in SEEDS
        rng = MersenneTwister(seed)
        for _ in 1:RESTARTS
            n = rand(rng, 8:12)
            p = gen_instance(n, rng; family = rand(rng, (:pow, :blocks, :two, :tight, :general)),
                             lower = rand(rng) < 0.7 ? ALPHA + 1e-9 : 0.0)
            cur = rr(p)
            for _ in 1:ROUNDS
                imp = false
                for i in eachindex(p)
                    for ε in (-0.25, -0.12, -0.05, -0.02, 0.02, 0.05, 0.12, 0.25, 0.6)
                        q = copy(p); q[i] = max(q[i] * (1 + ε), 0.0); sort!(q; rev = true)
                        r = rr(q)
                        r > cur + 1e-10 && (cur = r; p = q; imp = true)
                    end
                end
                for i in 1:length(p)
                    for ε in (-0.2, -0.08, 0.08, 0.2)
                        q = copy(p); q[i:end] .*= (1 + ε); sort!(q; rev = true)
                        r = rr(q)
                        r > cur + 1e-10 && (cur = r; p = q; imp = true)
                    end
                end
                imp || break
            end
            cur > best && (best = cur; bp = copy(p); bn = length(p))
        end
    end
    return best, bp, bn
end

best, bp, bn = attack()

# 固定的诊断实例
den = [0.8694, 0.7341, 0.7203, 0.5947, 0.5883, 0.5871, 0.4412, 0.4288, 0.4273, 0.4267]
dpy = [1.0862, 0.9842, 0.9527, 0.7885, 0.7548, 0.6149, 0.6068, 0.5735, 0.5598]
dpz = [0.3664, 0.3481, 0.3157, 0.2923, 0.2611, 0.2385, 0.2047, 0.2022, 0.2022]
r_ = (2 + sqrt(37)) / 11; s_ = (13 + sqrt(37)) / 33
lowfam = vcat(fill(1.0, 3), fill(r_, 3), fill(s_, 3))

println("KIND\t最坏\t n\t×c\t×5/4\tpx\tpy\tpz\t下界家族\t见证")
println(string(KIND), "\t", round(best, digits = 6), "\t", bn, "\t",
        round(best / C_TARGET, digits = 3), "\t", round(best / 1.25, digits = 3), "\t",
        round(rr(den), digits = 5), "\t", round(rr(dpy), digits = 5), "\t", round(rr(dpz), digits = 5), "\t",
        round(rr(lowfam), digits = 5), "\t", join(round.(bp, digits = 4), ","))
