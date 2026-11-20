# Mila: CO2 tradeoff curve and fuel price sensitivity

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from run_scenario import run_scenario

out = Path(__file__).resolve().parent.parent / "results" / "co2_and_fuel_price"
out.mkdir(parents=True, exist_ok=True)

cuts = [i * 0.0025 for i in range(11)]          # 0% to 2.5% in 0.25% steps
prices = [2.00, 2.25, 2.456, 2.75, 3.00]        # $/gal, base is 2.456

pd.options.display.float_format = "{:,.4f}".format

# Cost vs CO2 cut, at low, base, and high fuel price
rows = []
for price in [2.00, 2.456, 3.00]:
    for cut in cuts:
        res = run_scenario(co2_cut=cut, fuel_price=price)
        rows.append({"fuel_price": price, "co2_cut": cut,
                     "status": res["status"], "cost": res["cost"]})
curve = pd.DataFrame(rows)
curve.to_csv(out / "co2_tradeoff.csv", index=False)

for price, grp in curve.dropna().groupby("fuel_price"):
    plt.plot(grp.co2_cut * 100, grp.cost, marker="o", label=f"${price:.2f}/gal")
plt.xlabel("CO2 reduction vs current schedule (%)")
plt.ylabel("Daily operating cost ($)")
plt.legend(title="Fuel price")
plt.savefig(out / "co2_tradeoff.png", dpi=200)
plt.close()

# Fuel price sensitivity with no CO2 cap
rows = []
for price in prices:
    res = run_scenario(fuel_price=price, co2_cut=-1)
    rows.append({"fuel_price": price, "cost": res["cost"],
                 "co2_kg": res["co2_kg"], "co2_cut_achieved": res["co2_cut_achieved"]})
fuel = pd.DataFrame(rows)
fuel.to_csv(out / "fuel_price.csv", index=False)

plt.plot(fuel.fuel_price, fuel.cost, marker="o")
plt.xlabel("Fuel price ($/gal)")
plt.ylabel("Daily operating cost ($)")
plt.savefig(out / "fuel_price.png", dpi=200)
plt.close()

print(curve.dropna())
print(fuel)