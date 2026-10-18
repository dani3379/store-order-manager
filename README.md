# Store Order Manager

A small Python desktop application for browsing customer orders and producing sales reports. It demonstrates local business-data processing with **Tkinter** and **pandas**.

This is a personal/coursework portfolio example prepared from a recovered project named `kursova`. The original desktop workflow has been retained, with publication cleanup for validation, portable data paths, current order/report state, and offline tests. It is not presented as paid client work or a deployed production system.

## Features

- Browse customers, products and orders in separate tabs.
- Filter orders by customer/product text, quantity range and ISO date range.
- Add an order for an existing customer or create a customer with their first order.
- Immediately refresh the orders, customers and any generated report after saving.
- Summarize revenue by product/category or show top customers, with sorting and row limits.
- Export the current report to a CSV file selected through a save dialog.
- Start with a small, entirely synthetic dataset; no external accounts or services are needed.

## Setup

Use Python 3.10 or newer with Tkinter available. Run these commands from this repository's root.

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

Some Linux Python installations provide Tkinter as a separate operating-system package. A graphical desktop is needed to open the application; the model tests below can run without a display.

## Try the sample workflow

The first launch copies the four tables in `sample_data/` into a new `data/` working directory. Later launches reuse the working files. Existing directories are never replaced automatically.

1. Open **Orders**. The sample contains five orders.
2. Filter by customer `Demo Customer One`, then select **Clear** to restore all orders.
3. In **Reports**, generate **Revenue by Product**. Sample Notebook revenue starts at `16.50`.
4. In **New Order**, enter customer `Demo Customer One`, select product `Notebook`, and enter quantity `2`. Other fields may remain empty for this existing customer.
5. Add the order. The orders view now contains six rows; the generated Notebook revenue becomes `27.50` without restarting the application.
6. Export the report from **Reports** and choose a CSV destination.

For a separate fresh demo, choose a directory that does not yet exist:

```powershell
.\.venv\Scripts\python.exe app.py --data-dir demo-data
```

Dates in filters use `YYYY-MM-DD`. Quantity must be a positive whole number when adding an order. Email is optional; a supplied email must have a basic email format. A maximum report row count of `0` means all rows.

## Data and structure

```text
app.py             Tkinter tabs, dialogs and view refresh
store_data.py      Local TSV storage, validation, filtering and reporting
sample_data/       Four small synthetic tables
tests/             Offline model and persistence tests
```

The shipped customer names, addresses and transactions are fictional examples created for this publication version. Email addresses use `example.com`; phone fields are empty. Recovered customer files and packaged binaries are excluded.

The working directory is configurable through `--data-dir`. Its tables are tab-separated text files named `customers.txt`, `products.txt`, `orders.txt` and `categories.txt`. The default `data/` directory and alternate `demo-data/` directory are ignored by Git. Other working directories should also be kept outside version control.

## Tests

Windows:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

macOS/Linux:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Tests use disposable copies of the synthetic tables. They check order persistence and immediate report updates, new customers, rejected input without data changes, filter bounds/reset behavior, report totals/sorting, sample initialization, required columns and failed writes. They do not require a graphical desktop or a live service.

Publication verification on Windows used Python 3.12.4 and pandas 3.0.6: all 10 model tests passed. A separate withdrawn-window Tkinter smoke check also exercised startup, filtering/reset, adding an order, report refresh and CSV export using disposable synthetic data. This checks the workflow callbacks; it does not establish visual quality on every desktop platform.

## Current scope and limitations

- Designed for one local user. There is no authentication, concurrent editing or database transaction manager.
- Customer matching uses case-insensitive names; a real system should use a stronger identity workflow.
- Product/category editing is performed in the data files. The GUI focuses on order entry and reporting.
- Each table is replaced only after its temporary file is fully written. Adding a new customer and order still spans two files; a disk failure between those writes can leave a saved customer without an order.
- Existing custom data must follow the sample schema. The app checks required columns, but does not provide a general data-import repair tool.
- Monetary totals use pandas numeric values and are displayed to two decimal places. Tax, discounts, refunds, stock and accounting rules are outside this demo's scope.
- The automated checks cover the data model. Manual GUI verification should include adding an order, clearing filters and exporting a report on the target desktop.

## Provenance

The starting material was the recovered `kursova/mian.py` coursework/personal snapshot. This repository keeps its Tkinter/pandas functionality and develops that focused example rather than publishing the archived virtual environment or build output. The publication changes separate data logic, fix stale order/report state, add validation and synthetic fixtures, and document reproducible setup and checks.

No explicit license or authorship notice was present in the recovered first-party source. No client names, commercial outcomes or performance claims are asserted here, and no new license has been selected in this preparation.
