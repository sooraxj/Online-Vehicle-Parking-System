import tkinter as tk
from tkinter import ttk, Canvas, Frame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from db_connection import connect_to_db

class RevenueSalesGraph:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="white")

        self.create_ui()
        self.show_graph("all")

    def create_ui(self):
        """Creates the UI layout with buttons and scrollable graph area."""
        # **Header Frame for Buttons**
        button_frame = tk.Frame(self.root, bg="white")
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Buttons for selecting different graphs
        graph_buttons = [
            ("Revenue Graph", "revenue", "#3498db"),
            ("Sales Graph", "sales", "#27ae60"),
            ("Pie Chart", "pie", "#e67e22"),
            ("Scatter Plot", "scatter", "#8e44ad"),
            ("Revenue Growth", "growth", "#f1c40f"),
            ("Show All Graphs", "all", "#2c3e50")
        ]

        # Center the buttons by using grid with equal space distribution
        for i, (text, graph_type, color) in enumerate(graph_buttons):
            btn = tk.Button(
                button_frame, text=text, command=lambda g=graph_type: self.show_graph(g),
                bg=color, fg="white", font=("Arial", 10, "bold"),
                padx=12, pady=8, width=15, relief="raised"
            )
            btn.grid(row=0, column=i, padx=5, pady=5)

        # Make the grid layout fill the horizontal space equally
        button_frame.grid_columnconfigure(0, weight=1, uniform="equal")
        button_frame.grid_columnconfigure(1, weight=1, uniform="equal")
        button_frame.grid_columnconfigure(2, weight=1, uniform="equal")
        button_frame.grid_columnconfigure(3, weight=1, uniform="equal")
        button_frame.grid_columnconfigure(4, weight=1, uniform="equal")
        button_frame.grid_columnconfigure(5, weight=1, uniform="equal")

        # **Scrollable Frame for Graphs**
        canvas = Canvas(self.root, bg="white")
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        self.graph_frame = Frame(canvas, bg="white")

        self.graph_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.graph_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = canvas
        self.current_canvas = None




    def fetch_data(self):
        """Fetches revenue and sales data from the database."""
        conn = connect_to_db()
        cursor = conn.cursor()

        # Fetch Revenue Data (Total Payments Per Date)
        cursor.execute("""
            SELECT p.date, SUM(pay.amount) 
            FROM tbl_payment pay
            JOIN tbl_parking p ON pay.park_id = p.park_id
            GROUP BY p.date 
            ORDER BY p.date
        """)
        revenue_data = cursor.fetchall()

        # Fetch Sales Data (Total Parked Vehicles Per Date)
        cursor.execute("SELECT date, COUNT(*) FROM tbl_parking GROUP BY date ORDER BY date")
        sales_data = cursor.fetchall()

        conn.close()
        return revenue_data, sales_data

    def show_graph(self, graph_type):
        """Generates and displays the selected graph type."""
        # Remove old graph
        if self.current_canvas:
            self.current_canvas.get_tk_widget().destroy()

        revenue_data, sales_data = self.fetch_data()

        # Extract Data
        dates = [str(row[0]) for row in revenue_data]  # X-axis (Dates)
        revenue_values = [float(row[1]) for row in revenue_data]  # Y-axis (Revenue ₹)
        sales_values = [int(row[1]) for row in sales_data]  # Y-axis (Sales Count)
        date_indices = range(len(dates))  # Use indices for setting xticks properly

        # Create Figure for Graphs
        if graph_type == "all":
            fig, axes = plt.subplots(3, 2, figsize=(12, 10))  # 3 rows, 2 columns layout
            axes = axes.flatten()  # Flatten 2D array to loop easily

            # Graph 1: Revenue Trend
            axes[0].plot(dates, revenue_values, marker='o', linestyle='-', color='green', linewidth=2)
            axes[0].set_title("Revenue Trend Over Time")
            axes[0].set_xticks(date_indices)  # Explicitly set tick positions
            axes[0].set_xticklabels(dates, rotation=45, fontsize=8)
            axes[0].set_ylabel("Revenue (₹)")
            axes[0].grid(True)

            # Graph 2: Sales Trend
            axes[1].plot(dates, sales_values, marker='o', linestyle='-', color='blue', linewidth=2)
            axes[1].set_title("Sales Trend Over Time")
            axes[1].set_xticks(date_indices)
            axes[1].set_xticklabels(dates, rotation=45, fontsize=8)
            axes[1].set_ylabel("Total Parkings")
            axes[1].grid(True)

            # Graph 3: Pie Chart (Revenue Distribution)
            axes[2].pie(revenue_values, labels=dates, autopct='%1.1f%%', startangle=140,
                        colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
            axes[2].set_title("Revenue Distribution")

            # Graph 4: Scatter Plot (Revenue vs. Sales)
            axes[3].scatter(revenue_values, sales_values, color='red')
            axes[3].set_xlabel("Revenue (₹)")
            axes[3].set_ylabel("Total Parkings")
            axes[3].set_title("Revenue vs. Sales Correlation")
            axes[3].grid(True)

            # Graph 5: Revenue Growth
            growth_values = [revenue_values[i] - revenue_values[i-1] if i > 0 else 0 for i in range(len(revenue_values))]
            axes[4].bar(dates, growth_values, color='purple')
            axes[4].set_title("Revenue Growth Per Day")
            axes[4].set_xticks(date_indices)
            axes[4].set_xticklabels(dates, rotation=45, fontsize=8)
            axes[4].set_ylabel("Growth in ₹")
            axes[4].grid(True)

            # Hide extra subplot if there are empty slots in grid
            axes[5].axis("off")

            fig.tight_layout()  # Adjust layout to prevent overlapping

        else:
            fig, ax = plt.subplots(figsize=(10, 6))

            if graph_type == "revenue":
                ax.plot(dates, revenue_values, marker='o', linestyle='-', color='green', linewidth=2)
                ax.set_title("Revenue Trend Over Time")
                ax.set_xticks(date_indices)
                ax.set_xticklabels(dates, rotation=45, fontsize=8)
                ax.set_ylabel("Revenue (₹)")
                ax.grid(True)

            elif graph_type == "sales":
                ax.plot(dates, sales_values, marker='o', linestyle='-', color='blue', linewidth=2)
                ax.set_title("Sales Trend Over Time")
                ax.set_xticks(date_indices)
                ax.set_xticklabels(dates, rotation=45, fontsize=8)
                ax.set_ylabel("Total Parkings")
                ax.grid(True)

            elif graph_type == "pie":
                ax.pie(revenue_values, labels=dates, autopct='%1.1f%%', startangle=140,
                       colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99'])
                ax.set_title("Revenue Distribution")

            elif graph_type == "scatter":
                ax.scatter(revenue_values, sales_values, color='red')
                ax.set_xlabel("Revenue (₹)")
                ax.set_ylabel("Total Parkings")
                ax.set_title("Revenue vs. Sales Correlation")
                ax.grid(True)

            elif graph_type == "growth":
                growth_values = [revenue_values[i] - revenue_values[i-1] if i > 0 else 0 for i in range(len(revenue_values))]
                ax.bar(dates, growth_values, color='purple')
                ax.set_title("Revenue Growth Per Day")
                ax.set_xticks(date_indices)
                ax.set_xticklabels(dates, rotation=45, fontsize=8)
                ax.set_ylabel("Growth in ₹")
                ax.grid(True)

        # Embed Matplotlib Figure into Tkinter
        self.current_canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        self.current_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.current_canvas.draw()

# Example Usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Revenue & Sales Analysis")
    root.geometry("1000x700")
    RevenueSalesGraph(root)
    root.mainloop()
