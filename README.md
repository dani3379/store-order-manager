# Store Order Manager

Enter an order, find records with filters, and export product, category or customer summaries from a local desktop app.

This **Python/Tkinter personal demo** shows a focused business-data workflow: validated forms, related tables, saved orders and **pandas** reports. It includes fictional sample records and runs without external accounts or services. The code demonstrates skills used in custom desktop tools and reporting automation.

## What the app does

- Browse customers, products and orders in separate tabs.
- Filter orders by literal customer/product text, quantity bounds and date range; **Clear** restores the full order view.
- Add an order for an existing customer, or create a customer with their first order.
- Refresh the customer/order views after saving and regenerate an existing report using the current valid report options.
- Group calculated order totals by product/category or customer, sort the results and limit the number of rows.
- Export the current report to a CSV destination selected in a save dialog.

The report labels use “revenue”; the calculation is quantity × the unit price currently in the product table. This demo does not record a historical price on each order.

## See the workflow

After [setup](#setup), start with a fresh sample directory:

```powershell
.\.venv\Scripts\python.exe app.py --data-dir demo-data
```

Choose a directory that does not already exist. The app copies the four synthetic tables from `sample_data/` into it; an existing working directory is reused rather than reset.

1. **Orders** starts with five sample orders. Filter by `Demo Customer One`, then choose **Clear** to see all rows again.
2. In **Reports**, generate **Revenue by Product**. The sample Notebook total is `16.50`.
3. In **New Order**, enter `Demo Customer One`, choose `Notebook` and enter quantity `2`. Other fields may remain empty for this existing customer.
4. Save the order. The order list now has six rows and the generated Notebook total becomes `27.50` without restarting.
5. Return to **Reports**, choose **Export**, and select a CSV destination.

New orders use the computer's current date. Date filters use `YYYY-MM-DD`. Order quantity must be a positive whole number; email is optional and a supplied value receives a basic format check. A report row limit of `0` shows all results.

## Setup

Use Python 3.10 or newer with Tkinter available. Verification used Python 3.12.4; other Python/OS combinations have not been checked. Run from the repository root.

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

macOS/Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

Some Linux installations provide Tkinter as a separate operating-system package. The app needs a graphical desktop; the model tests can run without a display.

Without `--data-dir`, the app uses `data/` beside the source and initializes it from `sample_data/` only when that directory is absent. Dependency installation needs internet access; the app itself works locally.

## Tests and verification

Windows:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

macOS/Linux:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

**10 model tests passed on Windows on 20 October 2026**, using Python 3.12.4 and pandas 3.0.6. This audit reran the existing suite with network access blocked. Tests use disposable synthetic data and check saved/reloaded orders, immediate report updates, new customers, rejected input, filters, grouping/sorting, sample initialization, required columns and a simulated failed write.

The checked-in suite covers the data model and persistence. An earlier local Tkinter callback smoke check exercised filtering/reset, adding an order, report refresh and CSV export; visual layout and behavior on other operating systems remain manual checks.

## Data and code

```text
app.py             Tkinter tabs, dialogs and view refresh
store_data.py      TSV storage, validation, filters and reports
sample_data/       Four synthetic tables
tests/            Offline model and persistence tests
```

All shipped names, contact details and orders are fictional. Emails use `example.com` and phone fields are empty. No recovered customer records or packaged binaries are included.

Working data consists of `customers.txt`, `products.txt`, `orders.txt` and `categories.txt`, all tab-separated. Git ignores the default `data/` and example `demo-data/` directories; keep other working data outside version control too.

## Scope

- One local user, with no authentication or concurrent editing.
- Customers are matched by case-insensitive name. Products/categories are edited in the data files; the GUI focuses on order entry and reporting.
- Table writes use temporary-file replacement. Creating a customer and order spans two files, so a failure between writes can leave a customer without an order.
- Custom data must follow the sample schema. Required columns are checked; full import repair is not provided.
- Totals use pandas numeric values, rounded to two decimal places. Historical pricing, payments, tax, discounts, refunds and stock accounting are outside this example.

## Provenance

Adapted from a recovered snapshot originally stored as `kursova/mian.py`. This public version retains the Tkinter/pandas workflow, separates the data logic, repairs stale order/report state, and adds validation, synthetic fixtures and offline tests. The original folder name is recorded as source history; an educational or client context has not been independently established.

No explicit license or authorship notice was present in the recovered first-party source, and no project-code license has been selected. The repository is a personal/demo example; it does not claim a client deployment or measured business results.
