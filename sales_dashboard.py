import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Main application class for the sales dashboard
class SalesDashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sales Data Analysis Dashboard")
        self.root.geometry("1200x750")
        self.root.configure(bg="#f5f6fa")
        self.data = None
        self.sample_data_path = os.path.join(os.path.dirname(__file__), "sample_sales_data.csv")

        # Apply a clean visual style for cards and inputs
        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.configure("Card.TFrame", background="white", borderwidth=1, relief="solid")
        self.style.configure("CardTitle.TLabel", background="white", foreground="#2f3542", font=("Helvetica", 12))
        self.style.configure("CardValue.TLabel", background="white", foreground="#1e90ff", font=("Helvetica", 24, "bold"))
        self.style.configure("InfoValue.TLabel", background="white", foreground="#3742fa", font=("Helvetica", 20, "bold"))

        # Build the user interface
        self.build_header()
        self.build_controls()
        self.build_kpi_section()
        self.build_data_health_section()
        self.build_chart_buttons()
        self.build_data_preview()

    def build_header(self):
        # Header section with title
        header_frame = tk.Frame(self.root, bg="#2f3542", pady=20)
        header_frame.pack(fill="x")

        title_label = tk.Label(
            header_frame,
            text="Sales Data Analysis Dashboard",
            fg="white",
            bg="#2f3542",
            font=("Helvetica", 24, "bold"),
        )
        title_label.pack()

    def build_controls(self):
        # Controls section for file upload and status message
        controls_frame = tk.Frame(self.root, bg="#f5f6fa", pady=10)
        controls_frame.pack(fill="x")

        upload_button = tk.Button(
            controls_frame,
            text="Upload CSV File",
            command=self.upload_csv,
            bg="#3742fa",
            fg="white",
            font=("Helvetica", 12, "bold"),
            padx=15,
            pady=8,
        )
        upload_button.pack(side="left", padx=20)

        sample_button = tk.Button(
            controls_frame,
            text="Load Sample Data",
            command=self.load_sample_data,
            bg="#ff7f50",
            fg="white",
            font=("Helvetica", 12, "bold"),
            padx=15,
            pady=8,
        )
        sample_button.pack(side="left", padx=10)

        self.status_label = tk.Label(
            controls_frame,
            text="Please upload a sales CSV file to begin.",
            bg="#f5f6fa",
            fg="#57606f",
            font=("Helvetica", 11),
        )
        self.status_label.pack(side="left", padx=20)

    def build_kpi_section(self):
        # KPI section showing summary metrics
        kpi_frame = tk.Frame(self.root, bg="#f5f6fa", pady=10)
        kpi_frame.pack(fill="x")

        self.kpi_cards = {}
        kpi_titles = [
            "Total Sales Revenue",
            "Total Orders",
            "Total Quantity Sold",
            "Average Sales per Order",
        ]

        for title in kpi_titles:
            card = ttk.Frame(kpi_frame, style="Card.TFrame", padding=(15, 15))
            card.pack(side="left", expand=True, fill="both", padx=10)
            label_title = ttk.Label(card, text=title, style="CardTitle.TLabel")
            label_title.pack(anchor="w")
            label_value = ttk.Label(card, text="N/A", style="CardValue.TLabel")
            label_value.pack(anchor="w", pady=(10, 0))
            self.kpi_cards[title] = label_value

    def build_data_health_section(self):
        # Data quality section showing completeness and duplicate checks
        health_frame = tk.Frame(self.root, bg="#f5f6fa", pady=10)
        health_frame.pack(fill="x")

        self.health_cards = {}
        health_titles = [
            "Data Completeness",
            "Duplicate Orders",
            "Unique Products",
        ]

        for title in health_titles:
            card = ttk.Frame(health_frame, style="Card.TFrame", padding=(15, 15))
            card.pack(side="left", expand=True, fill="both", padx=10)
            label_title = ttk.Label(card, text=title, style="CardTitle.TLabel")
            label_title.pack(anchor="w")
            label_value = ttk.Label(card, text="N/A", style="InfoValue.TLabel")
            label_value.pack(anchor="w", pady=(10, 0))
            self.health_cards[title] = label_value

    def build_chart_buttons(self):
        # Buttons to trigger chart generation
        charts_frame = tk.Frame(self.root, bg="#f5f6fa", pady=10)
        charts_frame.pack(fill="x")

        chart_info = [
            ("Year-wise Sales", self.show_yearly_sales_chart),
            ("Monthly Trend", self.show_monthly_trend_chart),
            ("Online vs Offline", self.show_order_type_pie_chart),
            ("Quantity vs Sales", self.show_quantity_sales_scatter),
            ("Top Products", self.show_top_products_chart),
            ("Sales by Category", self.show_category_sales_chart),
            ("Sales by Region", self.show_region_sales_chart),
            ("Sales Forecast", self.show_sales_forecast_chart),
        ]

        for text, command in chart_info:
            button = tk.Button(
                charts_frame,
                text=text,
                command=command,
                bg="#2ed573",
                fg="white",
                font=("Helvetica", 11, "bold"),
                padx=15,
                pady=10,
            )
            button.pack(side="left", padx=10, pady=5)

    def build_data_preview(self):
        # Data preview table with scrollbars
        preview_frame = tk.Frame(self.root, bg="#f5f6fa", pady=10)
        preview_frame.pack(fill="both", expand=True)

        preview_label = tk.Label(
            preview_frame,
            text="Data Preview (First 10 rows)",
            bg="#f5f6fa",
            fg="#2f3542",
            font=("Helvetica", 14, "bold"),
        )
        preview_label.pack(anchor="w", padx=20)

        table_frame = tk.Frame(preview_frame)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.data_table = ttk.Treeview(table_frame, show="headings")
        self.data_table.pack(side="left", fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.data_table.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.data_table.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(preview_frame, orient="horizontal", command=self.data_table.xview)
        scrollbar_x.pack(fill="x", padx=20)
        self.data_table.configure(xscrollcommand=scrollbar_x.set)

    def upload_csv(self):
        # Open a file dialog for CSV selection
        file_path = filedialog.askopenfilename(
            title="Open Sales CSV",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*")],
        )

        if not file_path:
            self.status_label.config(text="No file selected. Please choose a CSV file.")
            return

        self.load_data_from_file(file_path)

    def load_sample_data(self):
        # Load the included sample CSV data file
        if not os.path.exists(self.sample_data_path):
            messagebox.showerror(
                "Sample Data Not Found",
                f"Sample data file not found at: {self.sample_data_path}",
            )
            return

        self.load_data_from_file(self.sample_data_path)

    def load_data_from_file(self, file_path):
        try:
            self.data = pd.read_csv(file_path)
            self.status_label.config(text=f"Loaded file: {file_path}")
            self.prepare_data()
            self.update_kpis()
            self.show_data_preview()
            messagebox.showinfo("Success", "Sales data loaded successfully.")
        except Exception as error:
            self.status_label.config(text="Failed to load file. Please select a valid CSV file.")
            messagebox.showerror("Error", f"Could not load CSV file. {error}")

    def prepare_data(self):
        # Ensure correct columns and parse dates
        expected_columns = [
            "Order_ID",
            "Order_Date",
            "Year",
            "Month",
            "Product",
            "Category",
            "Region",
            "Sales",
            "Quantity",
            "Order_Type",
        ]

        # Rename columns if they are concatenated without separators
        if len(self.data.columns) == 1:
            combined = self.data.columns[0]
            if combined.replace(" ", "") == "Order_IDOrder_DateYearMonthProductCategoryRegionSalesQuantityOrder_Type":
                self.data.columns = expected_columns

        # Reindex or add missing expected columns to keep the dataset consistent
        for col in expected_columns:
            if col not in self.data.columns:
                self.data[col] = np.nan

        # Convert sales and quantity to numeric values
        self.data["Sales"] = pd.to_numeric(self.data["Sales"], errors="coerce")
        self.data["Quantity"] = pd.to_numeric(self.data["Quantity"], errors="coerce")

        # Convert order date to datetime if possible
        self.data["Order_Date"] = pd.to_datetime(self.data["Order_Date"], errors="coerce")

        # Fill missing year and month information if possible
        self.data["Year"] = pd.to_numeric(self.data["Year"], errors="coerce")
        self.data["Month"] = pd.to_numeric(self.data["Month"], errors="coerce")
        self.data.loc[self.data["Year"].isnull() & self.data["Order_Date"].notnull(), "Year"] = self.data["Order_Date"].dt.year
        self.data.loc[self.data["Month"].isnull() & self.data["Order_Date"].notnull(), "Month"] = self.data["Order_Date"].dt.month

        # Convert Order_ID to string to preserve leading zeros and ensure consistent counts
        self.data["Order_ID"] = self.data["Order_ID"].astype(str).str.strip()
        self.data["Order_Type"] = self.data["Order_Type"].fillna("Unknown")

        # Calculate data health metrics before dropping invalid rows
        self.missing_pct = round(self.data.isna().mean().mean() * 100, 1)
        self.duplicate_orders = int(self.data.duplicated(subset=["Order_ID"]).sum())
        self.unique_products = int(self.data["Product"].nunique(dropna=True))

        # Remove rows with no sales, no quantity, or no order ID
        self.data = self.data.dropna(subset=["Order_ID", "Sales", "Quantity"])

        # Remove exact duplicate rows to keep analysis accurate
        self.data = self.data.drop_duplicates()

    def update_kpis(self):
        # Calculate the main KPIs from the data
        if self.data is None or self.data.empty:
            return

        total_revenue = self.data["Sales"].sum()
        total_orders = self.data["Order_ID"].nunique()
        total_quantity = self.data["Quantity"].sum()
        average_sales = total_revenue / total_orders if total_orders > 0 else 0

        self.kpi_cards["Total Sales Revenue"].config(text=f"₹{total_revenue:,.2f}")
        self.kpi_cards["Total Orders"].config(text=f"{int(total_orders):,}")
        self.kpi_cards["Total Quantity Sold"].config(text=f"{int(total_quantity):,}")
        self.kpi_cards["Average Sales per Order"].config(text=f"₹{average_sales:,.2f}")
        self.update_data_health()

    def update_data_health(self):
        # Update the data quality cards for a professional dashboard
        if not hasattr(self, "missing_pct"):
            self.missing_pct = 0
            self.duplicate_orders = 0
            self.unique_products = 0

        self.health_cards["Data Completeness"].config(text=f"{100 - self.missing_pct:.1f}%")
        self.health_cards["Duplicate Orders"].config(text=f"{self.duplicate_orders}")
        self.health_cards["Unique Products"].config(text=f"{self.unique_products}")

    def show_data_preview(self):
        # Show first 10 rows of the data in the table
        for column in self.data_table.get_children():
            self.data_table.delete(column)

        columns = list(self.data.columns)
        self.data_table.config(columns=columns)

        for col in columns:
            self.data_table.heading(col, text=col)
            self.data_table.column(col, width=120, minwidth=100)

        preview_rows = self.data.head(10)
        for _, row in preview_rows.iterrows():
            row_values = [str(row.get(col, "")) for col in columns]
            self.data_table.insert("", "end", values=row_values)

    def show_yearly_sales_chart(self):
        # Plot year-wise sales bar chart
        if self.data is None or self.data.empty:
            messagebox.showwarning("No Data", "Upload sales data first.")
            return

        sales_by_year = self.data.groupby("Year")["Sales"].sum().sort_index()
        if sales_by_year.empty:
            messagebox.showwarning("Data Missing", "Year-wise sales data is not available.")
            return

        plt.figure(figsize=(10, 6))
        plt.bar(sales_by_year.index.astype(str), sales_by_year.values, color="#3742fa")
        plt.title("Year-wise Sales")
        plt.xlabel("Year")
        plt.ylabel("Sales Revenue")
        plt.tight_layout()
        plt.show()

    def show_monthly_trend_chart(self):
        # Plot month-wise sales trend line chart
        if self.data is None or self.data.empty:
            messagebox.showwarning("No Data", "Upload sales data first.")
            return

        sales_by_month = self.data.groupby("Month")["Sales"].sum().reindex(range(1, 13), fill_value=0)
        if sales_by_month.empty:
            messagebox.showwarning("Data Missing", "Monthly sales data is not available.")
            return

        plt.figure(figsize=(10, 6))
        plt.plot(sales_by_month.index, sales_by_month.values, marker="o", color="#ff4757")
        plt.title("Monthly Sales Trend")
        plt.xlabel("Month")
        plt.ylabel("Sales Revenue")
        plt.xticks(range(1, 13))
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    def show_order_type_pie_chart(self):
        # Plot online vs offline orders pie chart
        if self.data is None or self.data.empty:
            messagebox.showwarning("No Data", "Upload sales data first.")
            return

        order_type_counts = self.data["Order_Type"].fillna("Unknown").value_counts()
        if order_type_counts.empty:
            messagebox.showwarning("Data Missing", "Order type data is not available.")
            return

        plt.figure(figsize=(8, 8))
        plt.pie(order_type_counts.values, labels=order_type_counts.index, autopct="%1.1f%%", startangle=140)
        plt.title("Online vs Offline Orders")
        plt.tight_layout()
        plt.show()

    def show_quantity_sales_scatter(self):
        # Plot quantity vs sales scatter plot
        if self.data is None or self.data.empty:
            messagebox.showwarning("No Data", "Upload sales data first.")
            return

        plt.figure(figsize=(10, 6))
        plt.scatter(self.data["Quantity"], self.data["Sales"], alpha=0.6, color="#1e90ff")
        plt.title("Quantity vs Sales")
        plt.xlabel("Quantity Sold")
        plt.ylabel("Sales Revenue")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    def show_top_products_chart(self):
        # Plot the top 10 selling products by revenue
        if self.data is None or self.data.empty:
            messagebox.showwarning("No Data", "Upload sales data first.")
            return

        if "Product" not in self.data.columns:
            messagebox.showwarning("Data Missing", "Product data is not available.")
            return

        top_products = self.data.groupby("Product")["Sales"].sum().nlargest(10)
        if top_products.empty:
            messagebox.showwarning("Data Missing", "Top product sales data is not available.")
            return

        plt.figure(figsize=(12, 6))
        plt.barh(top_products.index[::-1], top_products.values[::-1], color="#2ed573")
        plt.title("Top 10 Selling Products")
        plt.xlabel("Sales Revenue")
        plt.tight_layout()
        plt.show()

    def show_category_sales_chart(self):
        # Plot sales by category bar chart
        if self.data is None or self.data.empty:
            messagebox.showwarning("No Data", "Upload sales data first.")
            return

        if "Category" not in self.data.columns:
            messagebox.showwarning("Data Missing", "Category data is not available.")
            return

        category_sales = self.data.groupby("Category")["Sales"].sum().sort_values(ascending=False)
        if category_sales.empty:
            messagebox.showwarning("Data Missing", "Sales by category data is not available.")
            return

        plt.figure(figsize=(10, 6))
        plt.bar(category_sales.index, category_sales.values, color="#ffa502")
        plt.title("Sales by Category")
        plt.xlabel("Category")
        plt.ylabel("Sales Revenue")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

    def show_region_sales_chart(self):
        # Plot sales by region bar chart
        if self.data is None or self.data.empty:
            messagebox.showwarning("No Data", "Upload sales data first.")
            return

        if "Region" not in self.data.columns:
            messagebox.showwarning("Data Missing", "Region data is not available.")
            return

        region_sales = self.data.groupby("Region")["Sales"].sum().sort_values(ascending=False)
        if region_sales.empty:
            messagebox.showwarning("Data Missing", "Sales by region data is not available.")
            return

        plt.figure(figsize=(10, 6))
        plt.bar(region_sales.index, region_sales.values, color="#ff6b81")
        plt.title("Sales by Region")
        plt.xlabel("Region")
        plt.ylabel("Sales Revenue")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()

    def show_sales_forecast_chart(self):
        # Plot a simple linear forecast for future sales
        if self.data is None or self.data.empty:
            messagebox.showwarning("No Data", "Upload sales data first.")
            return

        if not all(col in self.data.columns for col in ["Year", "Month", "Sales"]):
            messagebox.showwarning("Data Missing", "Forecast requires Year, Month, and Sales data.")
            return

        self.data["InvoiceDate"] = pd.to_datetime(
            self.data["Year"].astype(int).astype(str) + "-" + self.data["Month"].astype(int).astype(str) + "-01",
            errors="coerce",
        )
        monthly_sales = self.data.dropna(subset=["InvoiceDate"]).groupby("InvoiceDate")["Sales"].sum().sort_index()
        if len(monthly_sales) < 3:
            messagebox.showwarning("Insufficient Data", "Need at least 3 months of sales data for forecasting.")
            return

        x = np.arange(len(monthly_sales))
        y = monthly_sales.values
        coefficients = np.polyfit(x, y, 1)
        trend = np.poly1d(coefficients)

        forecast_steps = 3
        forecast_x = np.arange(len(monthly_sales), len(monthly_sales) + forecast_steps)
        forecast_y = trend(forecast_x)

        plt.figure(figsize=(12, 6))
        plt.plot(monthly_sales.index, y, marker="o", label="Historical Sales", color="#3742fa")
        future_dates = pd.date_range(monthly_sales.index.max() + pd.offsets.MonthBegin(1), periods=forecast_steps, freq="MS")
        plt.plot(future_dates, forecast_y, marker="o", linestyle="--", label="Forecast", color="#ffa502")
        plt.title("Monthly Sales Forecast")
        plt.xlabel("Month")
        plt.ylabel("Sales Revenue")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

        forecast_text = "\n".join([f"{future_dates[i].strftime('%Y-%m')}: ₹{forecast_y[i]:,.2f}" for i in range(forecast_steps)])
        messagebox.showinfo("Forecast Summary", f"Forecast for next {forecast_steps} months:\n{forecast_text}")


def main():
    # Create the main window and start the application
    root = tk.Tk()
    app = SalesDashboardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
