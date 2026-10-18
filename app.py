"""Tkinter order-management demo, adapted from a recovered coursework snapshot."""

import argparse
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, StringVar, IntVar

from store_data import StoreData, prepare_demo_directory


def run_app(store):
    root = tk.Tk()
    root.title("Store Order Manager")
    root.geometry("1200x600")

    tab_control = ttk.Notebook(root)

    tab_products = ttk.Frame(tab_control)
    tab_clients = ttk.Frame(tab_control)
    tab_orders = ttk.Frame(tab_control)
    tab_reports = ttk.Frame(tab_control)
    tab_new_order = ttk.Frame(tab_control)

    tab_control.add(tab_clients, text='Customers')
    tab_control.add(tab_products, text='Products')
    tab_control.add(tab_orders, text='Orders')
    tab_control.add(tab_reports, text='Reports')
    tab_control.add(tab_new_order, text='New Order')

    tab_control.pack(expand=1, fill='both')


    customer_frame = ttk.LabelFrame(tab_clients, text="Customers")
    customer_frame.pack(side="left", expand=True, fill="both", padx=10, pady=10)

    customer_tree = ttk.Treeview(customer_frame, columns=("ID", "Name", "Email","Phone","City","Customer_type"), show="headings")
    customer_tree.heading("ID", text="ID")
    customer_tree.heading("Name", text="Name")
    customer_tree.heading("Email", text="Email")
    customer_tree.heading("Phone", text="Phone")
    customer_tree.heading("City", text="City")
    customer_tree.heading("Customer_type", text="Customer_type")
    customer_tree.pack(expand=True, fill="both")

    for _, row in store.customers.iterrows():
        customer_tree.insert("", "end", values=(row["customer_id"], row["name"], row["email"],row["phone"],row["city"],row["customer_type"]))

    product_frame = ttk.LabelFrame(tab_products, text="Products")
    product_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

    product_tree = ttk.Treeview(product_frame, columns=("ID", "Name", "Category", "Price"), show="headings")
    product_tree.heading("ID", text="ID")
    product_tree.heading("Name", text="Name")
    product_tree.heading("Category", text="Category ID")
    product_tree.heading("Price", text="Unit Price")
    product_tree.pack(expand=True, fill="both")

    for _, row in store.products.iterrows():
        product_tree.insert("", "end", values=(row["product_id"], row["name"], row["category"], row["unit_price"]))


    orders_frame = ttk.LabelFrame(tab_orders, text="Orders")
    orders_frame.pack(expand=True, fill="both", padx=10, pady=10)

    orders_tree = ttk.Treeview(
        orders_frame,
        columns=("Order ID", "Customer", "Product", "Quantity", "Date", "Total"),
        show="headings"
    )
    for col in orders_tree["columns"]:
        orders_tree.heading(col, text=col)
    orders_tree.pack(expand=True, fill="both")

    for _, row in store.orders.iterrows():
        orders_tree.insert("", "end", values=(
            row["order_id"], row["name_x"], row["name_y"],
            row["quantity"], row["order_date"], f"{row['total']:.2f}"
        ))


    filter_frame = ttk.LabelFrame(orders_frame, text="Filters")
    filter_frame.pack(fill="x", padx=10, pady=5)

    filter_customer_var = tk.StringVar()
    filter_product_var = tk.StringVar()
    min_qty_var = tk.StringVar()
    max_qty_var = tk.StringVar()
    date_from_var = tk.StringVar()
    date_to_var = tk.StringVar()

    ttk.Label(filter_frame, text="Customer:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
    ttk.Entry(filter_frame, textvariable=filter_customer_var, width=15).grid(row=0, column=1)

    ttk.Label(filter_frame, text="Product:").grid(row=0, column=2, padx=5, pady=2, sticky="e")
    ttk.Entry(filter_frame, textvariable=filter_product_var, width=15).grid(row=0, column=3)

    ttk.Label(filter_frame, text="Min Qty:").grid(row=0, column=4, padx=5, pady=2, sticky="e")
    ttk.Entry(filter_frame, textvariable=min_qty_var, width=7).grid(row=0, column=5)

    ttk.Label(filter_frame, text="Max Qty:").grid(row=0, column=6, padx=5, pady=2, sticky="e")
    ttk.Entry(filter_frame, textvariable=max_qty_var, width=7).grid(row=0, column=7)

    ttk.Label(filter_frame, text="Date From (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=2, sticky="e")
    ttk.Entry(filter_frame, textvariable=date_from_var, width=15).grid(row=1, column=1)

    ttk.Label(filter_frame, text="Date To (YYYY-MM-DD):").grid(row=1, column=2, padx=5, pady=2, sticky="e")
    ttk.Entry(filter_frame, textvariable=date_to_var, width=15).grid(row=1, column=3)

    def display_orders(frame):
        orders_tree.delete(*orders_tree.get_children())
        for _, row in frame.iterrows():
            orders_tree.insert("", "end", values=(
                row["order_id"], row["name_x"], row["name_y"],
                row["quantity"], row["order_date"], f"{row['total']:.2f}"
            ))


    def apply_filter():
        try:
            filtered = store.filter_orders(
                customer=filter_customer_var.get(), product=filter_product_var.get(),
                min_quantity=min_qty_var.get(), max_quantity=max_qty_var.get(),
                date_from=date_from_var.get(), date_to=date_to_var.get(),
            )
            display_orders(filtered)
        except ValueError as exc:
            messagebox.showerror("Invalid filter", str(exc))


    def clear_filter():
        for variable in (filter_customer_var, filter_product_var, min_qty_var,
                         max_qty_var, date_from_var, date_to_var):
            variable.set("")
        display_orders(store.orders)

    ttk.Button(filter_frame, text="Filter", command=apply_filter).grid(row=1, column=4, padx=5, pady=5)
    ttk.Button(filter_frame, text="Clear", command=clear_filter).grid(row=1, column=5, padx=5, pady=5)



    report_frame = ttk.LabelFrame(tab_reports, text="Generate Custom Reports")
    report_frame.pack(fill="x", padx=10, pady=10)


    report_type_var = StringVar()
    sort_option_var = StringVar()
    limit_var = IntVar()


    ttk.Label(report_frame, text="Report Type:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    report_type_combo = ttk.Combobox(report_frame, textvariable=report_type_var, state="readonly", width=30)
    report_type_combo["values"] = [
        "Revenue by Product",
        "Revenue by Category",
        "Top Customers"
    ]
    report_type_combo.grid(row=0, column=1, padx=5, pady=5)
    report_type_combo.current(0)


    ttk.Label(report_frame, text="Sort By:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    sort_option_combo = ttk.Combobox(report_frame, textvariable=sort_option_var, state="readonly", width=30)
    sort_option_combo["values"] = [
        "Revenue Descending",
        "Revenue Ascending",
        "Alphabetical"
    ]
    sort_option_combo.grid(row=0, column=3, padx=5, pady=5)
    sort_option_combo.current(0)


    ttk.Label(report_frame, text="Max Rows:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
    limit_entry = ttk.Entry(report_frame, textvariable=limit_var, width=10)
    limit_var.set(10)
    limit_entry.grid(row=0, column=5, padx=5, pady=5)


    report_result = ttk.Treeview(tab_reports, columns=("Col1", "Col2"), show="headings")
    report_result.pack(expand=True, fill="both", padx=10, pady=10)
    def generate_report():
        try:
            frame = store.generate_report(report_type_var.get(), sort_option_var.get(), limit_var.get())
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Invalid report options", str(exc))
            return
        report_result.delete(*report_result.get_children())
        report_result["columns"] = list(frame.columns)
        for column in frame.columns:
            report_result.heading(column, text=column)
        for _, row in frame.iterrows():
            report_result.insert("", "end", values=tuple(row))
        report_result.df = frame
        export_btn.config(state="normal")


    def export_current_report():
        if not hasattr(report_result, "df"):
            return
        path = filedialog.asksaveasfilename(
            title="Export report", initialfile="report.csv", defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if path:
            try:
                report_result.df.to_csv(path, index=False)
            except OSError as exc:
                messagebox.showerror("Export failed", str(exc))
                return
            messagebox.showinfo("Export", f"Report exported to {path}")

    ttk.Button(report_frame, text="Generate Report", command=generate_report).grid(row=0, column=6, padx=10)
    export_btn = ttk.Button(report_frame, text="Export", command=export_current_report, state="disabled")
    export_btn.grid(row=0, column=7, padx=10)



    def add_order():
        try:
            order_id = store.add_order(
                customer_name=customer_var.get(), product_name=product_var.get(),
                quantity=quantity_var.get(), email=email_var.get(), phone=phone_var.get(),
                city=city_var.get(), customer_type=type_var.get(),
            )
        except (ValueError, OSError) as exc:
            messagebox.showerror("Order not saved", str(exc))
            return
        customer_tree.delete(*customer_tree.get_children())
        for _, row in store.customers.iterrows():
            customer_tree.insert("", "end", values=(row["customer_id"], row["name"], row["email"], row["phone"], row["city"], row["customer_type"]))
        clear_filter()
        if hasattr(report_result, "df"):
            generate_report()
        quantity_var.set("")
        messagebox.showinfo("Success", f"Order {order_id} saved. Orders and generated reports are up to date.")

    form_frame = ttk.LabelFrame(tab_new_order, text="Add New Order")
    form_frame.pack(padx=20, pady=20, fill="x")

    ttk.Label(form_frame, text="Customer Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    customer_var = tk.StringVar()
    email_var = tk.StringVar()
    phone_var = tk.StringVar()
    city_var = tk.StringVar()
    type_var = tk.StringVar()

    customer_entry = ttk.Entry(form_frame, textvariable=customer_var)
    customer_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    email_entry = ttk.Entry(form_frame, textvariable=email_var)
    email_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Phone:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    phone_entry = ttk.Entry(form_frame, textvariable=phone_var)
    phone_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="City:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
    city_entry = ttk.Entry(form_frame, textvariable=city_var)
    city_entry.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Customer Type:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
    type_entry = ttk.Entry(form_frame, textvariable=type_var)
    type_entry.grid(row=4, column=1, padx=5, pady=5)
    ttk.Label(form_frame, text="Product:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
    product_var = tk.StringVar()
    product_combo = ttk.Combobox(form_frame, textvariable=product_var, values=store.products["name"].tolist(), state="readonly")
    product_combo.grid(row=5, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Quantity:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
    quantity_var = tk.StringVar()
    quantity_entry = ttk.Entry(form_frame, textvariable=quantity_var)
    quantity_entry.grid(row=6, column=1, padx=5, pady=5)

    ttk.Button(form_frame, text="Add Order", command=add_order).grid(row=7, column=0, columnspan=2, pady=10)


    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Local order management with synthetic sample data.")
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent / "data",
                        help="Working TSV directory; initialized from sample_data only when absent.")
    args = parser.parse_args()
    try:
        store = StoreData(prepare_demo_directory(args.data_dir))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Cannot load store data: {exc}\n")
    run_app(store)


if __name__ == "__main__":
    main()
