# Measurement Uncertainty Tool

An interactive web tool for computing measurement uncertainty using the **GUM (Guide to the Expression of Uncertainty in Measurement)** analytical method and **Monte Carlo simulation**.

🔗 **[https://your-app-url.streamlit.app](https://uncertaintycalculator.streamlit.app/)** ← replace with your Streamlit URL

---

## What it does

Enter any explicit measurement model as an equation (e.g. `rho = m / (L * W * H)`) and the tool automatically:

- Parses the model symbolically using SymPy
- Accepts **Type A** inputs (repeated measurements) and **Type B** inputs (stated uncertainty + distribution)
- Computes sensitivity coefficients via symbolic partial differentiation
- Propagates uncertainty using the **GUM analytical method** (weighted L2 norm)
- Runs an **n-sample Monte Carlo simulation** for comparison
- Outputs combined uncertainty, expanded uncertainty (k=2, 95% confidence), a full uncertainty budget table, and a histogram comparing GUM vs. Monte Carlo output distributions

---

## Demo

Try this example out of the box:

**Model:** `rho = m / (L * W * H)`

| Variable | Type | Value | Uncertainty | Distribution |
|---|---|---|---|---|
| m | B | 30.00 g | 0.50 g | Normal, k=2 |
| L | A | paste repeated measurements | — | — |
| W | B | 13.50 mm | 0.05 mm | Uniform |
| H | B | 5.00 mm | 0.05 mm | Uniform |

---

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## File structure

| File | Purpose |
|---|---|
| `app.py` | Streamlit UI |
| `gum.py` | Symbolic differentiation and GUM uncertainty propagation |
| `monte_carlo.py` | Monte Carlo sampling and evaluation |
| `utilities.py` | Type A/B uncertainty calculations, budget table |

---

## References

- JCGM 100:2008 — *Evaluation of measurement data: Guide to the Expression of Uncertainty in Measurement*
- JCGM 101:2008 — *Supplement 1: Propagation of distributions using a Monte Carlo method*
