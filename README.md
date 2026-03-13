
Final degree dissertation (TFG) — Universidad de Zaragoza, 2023.

This project analyses the **Active Share** of 154 Spanish equity investment funds over a 20-year period (December 1999 – June 2020), using the IBEX-35 as the benchmark. The full calculation was first developed in Excel, then rewritten in Python to handle a dataset of approximately one million rows.

The findings show a clear upward trend in Active Share over time, suggesting that Spanish fund managers have increasingly distanced their portfolios from the benchmark in pursuit of higher returns.

📄 Full report available in `OSPINA_EMANUELE_TFG.pdf`

---

## Methodology

Active Share measures how much a fund's holdings differ from its benchmark index. It is calculated as:

```
Active Share = (1/2) * Σ |w_fund,i - w_index,i|
```

Where `w_fund,i` is the weight of asset `i` in the fund, and `w_index,i` is its weight in the IBEX-35.

A value of 0% means the fund perfectly replicates the index. A value of 100% means there is no overlap at all.

---

## Project Structure

```
active-share-tfg/
├── README.md
├── OSPINA_EMANUELE_TFG.pdf     # Full dissertation report
├── TFG.py                      # Main script (English comments)
├── Ibex.csv                    # IBEX-35 historical composition (public data)
└── data/                       # Input data (not included — see below)
    ├── fondos_hasta1500.csv
    ├── LISTA ISINs NO RV.csv
    └── LISTA FI-ETF.csv
```

---

## Input Data

Three input files are required to run the script. They are not included in this repository as they contain proprietary data from CNMV and Morningstar Direct.

### `fondos_hasta1500.csv`
Portfolio composition data for each fund, per date.

| Column | Type | Description |
|--------|------|-------------|
| `Número fondo` | int | Fund identifier |
| `Fecha` | date (dd/mm/yy) | Reporting date |
| `ISIN` | string | Security ISIN code |
| `Valor de realización (VR)` | float | Market value of the holding |

### `LISTA ISINs NO RV.csv`
List of ISINs that are **not** equity (renta variable) — e.g. bonds, repos, money market instruments.

| Column | Type | Description |
|--------|------|-------------|
| `ISIN` | string | Security ISIN code |
| `Titulos No Rvble` | string | Mark (`*` or `1`) if non-equity |

### `LISTA FI-ETF.csv`
List of ISINs corresponding to investment funds or ETFs within the portfolios.

| Column | Type | Description |
|--------|------|-------------|
| `ISIN` | string | Security ISIN code |
| `Todos ETF o FI Rvble` | int | `2` = non-IBEX FI/ETF, `1000` = FI/ETF, `0` = otherwise |

---

## Requirements

```
pandas
numpy
```

Install with:

```bash
pip install pandas numpy
```

---

## Usage

Place all input CSV files in the same directory as the script, then run:

```bash
python TFG.py
```

The script will generate two output files:

- `fondos_hasta.csv` — full security-level data with computed weights and Active Share components
- `AS.csv` — final Active Share value per fund and date

---

## Results

Active Share was computed for 154 Spanish equity funds from December 1999 to June 2020. Key findings:

- The **average Active Share increased steadily** from ~49% in 2000 to ~68% in 2020
- Some funds maintained an Active Share close to 100%, indicating fully active management
- A small subset of funds showed Active Share below 10%, suggesting closet indexing

---

## Data Sources

- Fund portfolio data: [CNMV](https://www.cnmv.es) & [Morningstar Direct](https://www.morningstar.com)
- IBEX-35 historical composition: [BME](https://www.bolsasymercados.es)

---

## Reference

Cremers, M. & Petajisto, A. (2009). *How Active Is Your Fund Manager? A New Measure that Predicts Performance*. Review of Financial Studies, 22(9).
