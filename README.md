### Fleet Assignment Model: 
Reassigns aircraft types to JFK routes to minimize operating cost under a CO2 cap,
then sweeps the required CO2 reduction (alpha) from 0% to 3%.

### Setup

Need Python 3.9 or newer.

**Mac / Linux**
```
cd fleet_assignment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**
```
cd fleet_assignment
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Run

```
python src/main.py
```

### Expected output

Current: cost = $4,024,633, CO2 = 5,619,090 kg, then one block per alpha.
alpha = 2.5% and 3.0% are infeasible with the current fleet.

Writes the full assignment for every alpha to results/assignments.csv.

### Project Structure

- `src/variables.py` loads all parameters from `data/`
- `src/model.py` builds and solves the integer program
- `src/main.py` runs the baseline and the alpha sweep
- `src/run_scenario.py` re-solves the model with changed parameters (sensitivity analysis)
- `data/` holds the input CSVs

### Sensitivity Analysis

Use `run_scenario()` instead of editing the data or model. Pass only the
parameter you want to change; everything else stays at its base value.

Example:

    from run_scenario import run_scenario

    for value in [...]:                        # your range of values
        res = run_scenario(parameter=value)    # replace with your argument
        if res["status"] == "optimal":
            print(value, res["cost"], res["co2_kg"])
        else:
            print(value, "infeasible")

### Adding an analysis

- Name the script after what it analyzes
- Save its CSVs and charts to `results/<what_is_analyzed>/`

