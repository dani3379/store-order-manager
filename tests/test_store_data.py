"""Offline behavior checks against disposable synthetic tables."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from store_data import StoreData, prepare_demo_directory


class StoreDataTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = prepare_demo_directory(Path(self.temporary.name) / "working")
        self.store = StoreData(self.directory)

    def test_existing_customer_order_immediately_updates_reports_and_survives_reload(self):
        order_id = self.store.add_order("demo customer one", "Notebook", "2", order_date="2026-04-01")
        self.assertEqual(order_id, 1006)
        self.assertEqual(len(self.store.customers), 3)
        self.assertEqual(len(self.store.orders), 6)
        report = self.store.generate_report("Revenue by Product", limit=0).set_index("Product")
        self.assertAlmostEqual(report.loc["Notebook", "Revenue"], 27.50)
        self.assertAlmostEqual(self.store.orders["total"].sum(), 129.00)
        reloaded = StoreData(self.directory)
        self.assertEqual(reloaded.raw_orders.iloc[-1]["order_id"], order_id)
        self.assertEqual(reloaded.raw_orders.iloc[-1]["quantity"], 2)
        self.assertAlmostEqual(reloaded.orders["total"].sum(), 129.00)

    def test_new_customer_and_order_are_joined_in_current_and_reloaded_views(self):
        self.store.add_order("New Demo Buyer", "Desk Lamp", 3, email="new.buyer@example.com", order_date="2026-04-02")
        for store in (self.store, StoreData(self.directory)):
            self.assertEqual(len(store.customers), 4)
            added = store.orders.iloc[-1]
            self.assertEqual(added["name_x"], "New Demo Buyer")
            self.assertEqual(added["name_y"], "Desk Lamp")
            self.assertAlmostEqual(added["total"], 72.00)

    def test_invalid_orders_do_not_change_disk_or_memory(self):
        before = {p.name: p.read_bytes() for p in self.directory.glob("*.txt")}
        cases = [
            {"customer_name": "", "product_name": "Notebook", "quantity": "1"},
            {"customer_name": "Demo Buyer", "product_name": "", "quantity": "1"},
            {"customer_name": "Demo Buyer", "product_name": "Notebook", "quantity": "1", "email": "invalid"},
            {"customer_name": "Demo Buyer", "product_name": "Notebook", "quantity": "1", "order_date": "2026-02-30"},
        ]
        cases.extend({"customer_name": "Demo Buyer", "product_name": "Notebook", "quantity": q} for q in ("", "0", "-2", "1.5", "many", True))
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                self.store.add_order(**case)
        self.assertEqual(len(self.store.raw_orders), 5)
        self.assertEqual(len(self.store.customers), 3)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.directory.glob("*.txt")})

    def test_filters_combine_bounds_and_empty_filters_restore_all_rows(self):
        result = self.store.filter_orders(customer="DEMO", product="notebook", min_quantity="3", max_quantity="3", date_from="2026-01-01", date_to="2026-01-31")
        self.assertEqual(result["order_id"].tolist(), [1001])
        self.assertEqual(len(self.store.filter_orders(date_from="2026-02-01", date_to="2026-03-31")), 3)
        self.assertEqual(len(self.store.filter_orders()), 5)
        self.assertEqual(len(self.store.filter_orders(customer="[")), 0)

    def test_invalid_filter_ranges_and_dates_are_reported(self):
        for arguments in ({"min_quantity": "4", "max_quantity": "2"}, {"min_quantity": "abc"}, {"date_from": "2026-02-30"}, {"date_from": "2026-03-01", "date_to": "2026-02-01"}, {"date_to": "2026-2-01"}):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                self.store.filter_orders(**arguments)

    def test_report_grouping_sorting_and_limit(self):
        categories = self.store.generate_report("Revenue by Category", limit=0).set_index("Category")["Revenue"].to_dict()
        self.assertEqual(categories, {"Accessories": 56.25, "Office": 37.75, "Workspace": 24.00})
        customers = self.store.generate_report("Top Customers", limit=1)
        self.assertEqual(customers.iloc[0]["Customer"], "Sample Studio")
        self.assertAlmostEqual(customers.iloc[0]["Revenue"], 58.75)
        products = self.store.generate_report("Revenue by Product", "Revenue Ascending", 2)
        self.assertEqual(products["Product"].tolist(), ["Notebook", "Pen Set"])

    def test_invalid_report_options_are_rejected(self):
        for arguments in (("unknown", "Revenue Descending", 10), ("Top Customers", "unknown", 10), ("Top Customers", "Alphabetical", -1), ("Top Customers", "Alphabetical", "invalid")):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                self.store.generate_report(*arguments)

    def test_demo_preparation_does_not_replace_existing_data(self):
        marker = self.directory / "customer-note.txt"
        marker.write_text("local user data", encoding="utf-8")
        before = (self.directory / "orders.txt").read_bytes()
        self.assertEqual(prepare_demo_directory(self.directory), self.directory)
        self.assertEqual(marker.read_text(encoding="utf-8"), "local user data")
        self.assertEqual((self.directory / "orders.txt").read_bytes(), before)

    def test_failed_table_write_keeps_existing_order_file(self):
        before = (self.directory / "orders.txt").read_bytes()
        with patch.object(pd.DataFrame, "to_csv", side_effect=OSError("simulated write failure")):
            with self.assertRaises(OSError):
                self.store.add_order("Demo Customer One", "Notebook", 1)
        self.assertEqual((self.directory / "orders.txt").read_bytes(), before)
        self.assertEqual(len(self.store.raw_orders), 5)
        self.assertEqual(set(p.name for p in self.directory.iterdir()), {"categories.txt", "customers.txt", "products.txt", "orders.txt"})

    def test_missing_required_columns_are_explained(self):
        (self.directory / "customers.txt").write_text("customer_id\tname\n1\tDemo\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "customers.txt is missing columns"):
            StoreData(self.directory)


if __name__ == "__main__":
    unittest.main()
