# L0/L1/L2 层，n=10,11,12 × full45/full1（纯 LP，快）
include("dc_dff.jl")
for n in (10, 11, 12), preds in (:full45, :full1)
    n == 12 && preds == :full1 && continue
    for layer in (0, 1, 2)
        run_config(n, preds, layer, 60.0)
    end
end
