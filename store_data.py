"""Local TSV storage and reporting for the single-user desktop demo."""

from datetime import date
from pathlib import Path
import os
import re
import shutil
import tempfile

import pandas as pd


TABLE_COLUMNS = {
    "customers": ["customer_id", "name", "email", "phone", "city", "customer_type"],
    "products": ["product_id", "name", "category", "unit_price"],
    "orders": ["order_id", "customer_id", "product_id", "quantity", "order_date"],
    "categories": ["category_id", "category_name"],
}


def prepare_demo_directory(destination: Path) -> Path:
    """Copy synthetic fixtures on first use; never replace an existing directory."""
    destination = Path(destination).expanduser().resolve()
    if not destination.exists():
        shutil.copytree(Path(__file__).resolve().parent / "sample_data", destination)
    return destination


def _integer(value, label, minimum=0, optional=False):
    text = str(value).strip()
    if optional and not text:
        return None
    if not re.fullmatch(r"[0-9]+", text) or int(text) < minimum:
        raise ValueError(f"{label} must be a whole number of at least {minimum}.")
    return int(text)


def _date(value, label):
    text = str(value).strip()
    if not text:
        return None
    try:
        result = date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"{label} must be a valid date in YYYY-MM-DD format.") from exc
    if result.isoformat() != text:
        raise ValueError(f"{label} must use YYYY-MM-DD format.")
    return result


def _write_table(frame, path):
    """Replace each table only after a complete temporary file has been written."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            frame.to_csv(stream, sep="\t", index=False)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


class StoreData:
    def __init__(self, directory):
        self.directory = Path(directory)
        for table, columns in TABLE_COLUMNS.items():
            path = self.directory / f"{table}.txt"
            frame = pd.read_csv(path, sep="\t", keep_default_na=False)
            missing = set(columns) - set(frame.columns)
            if missing:
                raise ValueError(f"{path.name} is missing columns: {', '.join(sorted(missing))}")
            setattr(self, "raw_orders" if table == "orders" else table, frame)

    @property
    def orders(self):
        frame = self.raw_orders.merge(self.customers, on="customer_id", how="left", validate="many_to_one")
        frame = frame.merge(self.products, on="product_id", how="left", validate="many_to_one")
        frame["total"] = (frame["quantity"] * frame["unit_price"]).round(2)
        return frame

    def filter_orders(self, customer="", product="", min_quantity="", max_quantity="", date_from="", date_to=""):
        minimum = _integer(min_quantity, "Minimum quantity", optional=True)
        maximum = _integer(max_quantity, "Maximum quantity", optional=True)
        start = _date(date_from, "From date")
        end = _date(date_to, "To date")
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("Minimum quantity cannot exceed maximum quantity.")
        if start and end and start > end:
            raise ValueError("From date cannot be later than to date.")
        frame = self.orders
        for column, value in [("name_x", customer), ("name_y", product)]:
            if str(value).strip():
                frame = frame[frame[column].str.contains(str(value).strip(), case=False, regex=False, na=False)]
        if minimum is not None:
            frame = frame[frame["quantity"] >= minimum]
        if maximum is not None:
            frame = frame[frame["quantity"] <= maximum]
        if start:
            frame = frame[frame["order_date"] >= start.isoformat()]
        if end:
            frame = frame[frame["order_date"] <= end.isoformat()]
        return frame

    def generate_report(self, report_type, sort_option="Revenue Descending", limit=10):
        limit = _integer(limit, "Maximum rows")
        frame = self.orders
        if report_type == "Revenue by Product":
            result = frame.groupby("name_y")["total"].sum().reset_index().rename(columns={"name_y": "Product", "total": "Revenue"})
        elif report_type == "Revenue by Category":
            frame = frame.merge(self.categories, left_on="category", right_on="category_id", validate="many_to_one")
            result = frame.groupby("category_name")["total"].sum().reset_index().rename(columns={"category_name": "Category", "total": "Revenue"})
        elif report_type == "Top Customers":
            result = frame.groupby("name_x")["total"].sum().reset_index().rename(columns={"name_x": "Customer", "total": "Revenue"})
        else:
            raise ValueError("Choose a supported report type.")
        if sort_option in ("Revenue Ascending", "Revenue Descending"):
            result = result.sort_values("Revenue", ascending=sort_option == "Revenue Ascending", kind="stable")
        elif sort_option == "Alphabetical":
            result = result.sort_values(result.columns[0], kind="stable")
        else:
            raise ValueError("Choose a supported sort order.")
        result["Revenue"] = result["Revenue"].round(2)
        return result.head(limit) if limit else result

    def add_order(self, customer_name, product_name, quantity, email="", phone="", city="", customer_type="", order_date=None):
        customer_name = str(customer_name).strip()
        if not customer_name:
            raise ValueError("Enter a customer name.")
        quantity = _integer(quantity, "Quantity", minimum=1)
        product_rows = self.products[self.products["name"] == str(product_name).strip()]
        if product_rows.empty:
            raise ValueError("Select a product from the list.")
        email = str(email).strip()
        if email and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise ValueError("Enter a valid email address or leave email empty.")
        when = _date(order_date or date.today().isoformat(), "Order date")
        customers = self.customers.copy()
        matches = customers[customers["name"].str.casefold() == customer_name.casefold()]
        is_new_customer = matches.empty
        if is_new_customer:
            customer_id = int(customers["customer_id"].max()) + 1 if not customers.empty else 1
            new_customer = dict(zip(TABLE_COLUMNS["customers"], [customer_id, customer_name, email, str(phone).strip(), str(city).strip(), str(customer_type).strip()]))
            customers = pd.concat([customers, pd.DataFrame([new_customer])], ignore_index=True)
        else:
            customer_id = int(matches.iloc[0]["customer_id"])
        order_id = int(self.raw_orders["order_id"].max()) + 1 if not self.raw_orders.empty else 1
        new_order = {"order_id": order_id, "customer_id": customer_id, "product_id": int(product_rows.iloc[0]["product_id"]), "quantity": quantity, "order_date": when.isoformat()}
        orders = pd.concat([self.raw_orders, pd.DataFrame([new_order])], ignore_index=True)
        # Flat files are intended for one local user, not concurrent transactions.
        if is_new_customer:
            _write_table(customers, self.directory / "customers.txt")
            self.customers = customers
        _write_table(orders, self.directory / "orders.txt")
        self.raw_orders = orders
        return order_id
