# a4_l5_midwit.jl —— 层 (5) z<3/10 段的终端 sup witness 提取（引导手证）
using JuMP, HiGHS

function layer5_mid(zcap)
    n = 11
    best = -Inf; bp = Float64[]; bx = Float64[]
    for a in 1:4, b in (a+1):4
        cnt = fill(2, 4); cnt[a] = 3; cnt[b] = 3
        m = Model(HiGHS.Optimizer); set_silent(m)
        @variable(m, 4 / 15 <= P[1:n] <= 1.0)
        for i in 1:(n-1); @constraint(m, P[i] >= P[i+1]); end
        @constraint(m, sum(P) <= 4.0)
        @constraint(m, P[n] <= zcap)
        @variable(m, u[1:(n-1), 1:4], Bin)
        @variable(m, v[1:(n-1), 1:4] >= 0)
        for i in 1:(n-1)
            @constraint(m, sum(u[i, :]) == 1)
            for mm in 1:4
                @constraint(m, v[i, mm] <= u[i, mm])
                @constraint(m, v[i, mm] <= P[i])
                @constraint(m, v[i, mm] >= P[i] - (1 - u[i, mm]))
            end
        end
        for mm in 1:4
            @constraint(m, u[mm, mm] == 1)
            @constraint(m, sum(u[:, mm]) == cnt[mm])
        end
        ℓ = [sum(v[:, mm]) for mm in 1:4]
        @variable(m, x[1:n, 1:4], Bin)
        @variable(m, y[1:n, 1:4] >= 0)
        for i in 1:n
            @constraint(m, sum(x[i, :]) == 1)
            for bb in 1:4
                @constraint(m, y[i, bb] <= x[i, bb])
                @constraint(m, y[i, bb] <= P[i])
                @constraint(m, y[i, bb] >= P[i] - (1 - x[i, bb]))
            end
        end
        for bb in 1:4
            @constraint(m, sum(y[:, bb]) <= 1.0)
            @constraint(m, sum(x[:, bb]) <= 3)
        end
        @constraint(m, x[1, 1] == 1)
        @variable(m, t)
        for mm in 1:4; @constraint(m, t <= ℓ[mm] + P[n]); end
        @objective(m, Max, t)
        optimize!(m)
        if termination_status(m) == OPTIMAL && objective_value(m) > best
            best = objective_value(m); bp = value.(P); bx = value.(x)
        end
    end
    println("zcap=$zcap  sup=", round(best, digits = 6), "  p=", round.(bp, digits = 4))
    # 打印装箱模式
    for bb in 1:4
        blk = findall(i -> bx[i, bb] > 0.5, 1:length(bp))
        isempty(blk) || println("   箱 $bb: ", blk, " → ", round.(bp[blk], digits = 3))
    end
end

layer5_mid(0.2999)
