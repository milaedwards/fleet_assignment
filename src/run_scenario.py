# re-solves the model with changed parameters for the sensitivity analysis

from variables import load_params
from model import solve

BASE = load_params()
CO2_PER_GAL = 9.75


def run_scenario(co2_cut=0.0, fuel_price=None, nonfuel_mult=1.0, fuel_burn_mult=1.0,
                 demand_mult=1.0, util_buffer=1.1, fleet=None):
    p = dict(BASE)
    R, K = p["R"], p["K"]
    price = BASE["P_f"] if fuel_price is None else fuel_price
    if not isinstance(fuel_burn_mult, dict):
        fuel_burn_mult = {k: fuel_burn_mult for k in K}

    # Split each cost c_rk = P_f * F_rk + C_k * T_r into fuel and non-fuel parts, then rebuild
    E, c = {}, {}
    for r in R:
        for k in K:
            gallons = BASE["E"][r, k] / CO2_PER_GAL
            nonfuel = BASE["c"][r, k] - BASE["P_f"] * gallons
            gallons = gallons * fuel_burn_mult.get(k, 1.0)
            E[r, k] = CO2_PER_GAL * gallons
            c[r, k] = price * gallons + nonfuel_mult * nonfuel

    p["E"], p["c"] = E, c
    p["D"] = {r: demand_mult * BASE["D"][r] for r in R}
    p["N"] = {**BASE["N"], **(fleet or {})}

    # Baselines: the real Nov 26 schedule
    p["E_base"] = sum(BASE["x0"][r, k] * E[r, k] for r in R for k in K)
    p["cost_base"] = sum(BASE["x0"][r, k] * c[r, k] for r in R for k in K)

    m, x = solve(p, co2_cut, util_buffer)

    result = {"status": "infeasible", "cost": None, "co2_kg": None,
              "baseline_cost": p["cost_base"], "baseline_co2_kg": p["E_base"],
              "hours_used": None, "assignment": None}
    if m.SolCount == 0:
        return result

    co2 = sum(E[r, k] * x[r, k].X for r in R for k in K)
    result.update({
        "status": "optimal",
        "cost": m.ObjVal,
        "co2_kg": co2,
        "cost_vs_current": m.ObjVal / p["cost_base"] - 1,
        "co2_cut_achieved": 1 - co2 / p["E_base"],
        "hours_used": {k: sum(p["T"][r, k] * x[r, k].X for r in R) for k in K},
        "assignment": {(r, k): round(x[r, k].X) for r in R for k in K},
    })
    return result
