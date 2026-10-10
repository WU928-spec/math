using JuMP, HiGHS
m = Model(HiGHS.Optimizer); set_silent(m)
@variable(m, 0 <= x <= 5); @variable(m, z, Bin)
try
    @constraint(m, z => {x <= 2})
    @objective(m, Max, x); optimize!(m)
    println("支持 indicator：状态=", termination_status(m), " x=", value(x), " z=", value(z))
catch e
    println("不支持 indicator：", sprint(showerror, e)[1:min(200,end)])
end
