# payment_view.py
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from db_connection import connect_to_db
import tempfile
import webbrowser
import os
import platform

class PaymentViewPage:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="#f0f0f0")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header = tk.Frame(self.frame, bg="#010f26", height=60)
        header.pack(fill=tk.X)

        tk.Label(header, text="💰 Payment View Details", font=("Arial", 18, "bold"), 
                 fg="white", bg="#010f26", pady=15).pack()

        # Table Frame
        table_frame = tk.Frame(self.frame, bg="white", padx=20, pady=10)
        table_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Table Styling
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 11), rowheight=30, background="white", fieldbackground="white")
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#1F618D", foreground="black")
        style.map("Treeview.Heading", background=[("active", "#154360")])

        # Add Aadhar Number in columns
        self.tree = ttk.Treeview(table_frame, columns=("Ticket Number", "Customer Name", "Vehicle Number", "Contact No", 
                                                       "Aadhar Number", "Parking Date", "Entry Time", "Exit Time", 
                                                       "Slot Name", "Hours Parked", "Amount", "Payment Status"), show="headings")

        headers = ["Ticket Number", "Customer Name", "Vehicle Number", "Contact No", 
                   "Aadhar Number", "Parking Date", "Entry Time", "Exit Time", 
                   "Slot Name", "Hours Parked", "Amount", "Payment Status"]

        col_widths = [120, 120, 100, 120, 140, 110, 100, 100, 100, 100, 100, 120]

        for col, width in zip(headers, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')

        # Add scrollbar
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Alternating row colors
        self.tree.tag_configure('oddrow', background="#f9f9f9")
        self.tree.tag_configure('evenrow', background="white")

        self.load_payment_data()

        # Print Ticket Button
        btn_frame = tk.Frame(self.frame, bg="#f0f0f0")
        btn_frame.pack(pady=10)
        
        self.print_btn = tk.Button(btn_frame, text="🖨 Display Ticket", font=("Arial", 12, "bold"), bg="#27AE60", fg="white", 
                                   padx=10, pady=5, command=self.display_ticket)
        self.print_btn.pack()

    def load_payment_data(self):
        try:
            conn = connect_to_db()
            cursor = conn.cursor()

            query = """
                SELECT 
                  p.ticket_number, 
                  pr.custname, 
                  pr.veh_no, 
                  pr.contact_no, 
                  pr.aadhar_no,
                  pr.date, 
                  pr.entry_time, 
                  pr.exit_time, 
                  s.slotname, 
                  TIMESTAMPDIFF(HOUR, pr.entry_time, pr.exit_time) AS hours_parked, 
                  p.amount, 
                  p.status
                FROM 
                  tbl_payment p
                JOIN 
                  tbl_parking pr ON p.park_id = pr.park_id
                LEFT JOIN 
                  tbl_slots s ON pr.slot_id = s.slot_id;
            """
            cursor.execute(query)
            rows = cursor.fetchall()

            for index, row in enumerate(rows):
                tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                row = list(row)
                row[10] = f"₹{row[10]}"  # Add Rupee Symbol
                self.tree.insert("", tk.END, values=row, tags=(tag,))
            
            cursor.close()
            conn.close()
        except Exception as err:
            tk.Label(self.frame, text=f"Error: {err}", fg="red", bg="#f0f0f0").pack()

    def display_ticket(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a payment record to display.")
            return
        
        item = self.tree.item(selected_item)
        values = item['values']
        
        details = [
            f"Ticket Number: {values[0]}",
            f"Customer Name: {values[1]}",
            f"Vehicle Number: {values[2]}",
            f"Contact No: {values[3]}",
            f"Aadhar Number: {values[4]}",
            f"Parking Date: {values[5]}",
            f"Entry Time: {values[6]}",
            f"Exit Time: {values[7]}",
            f"Slot Name: {values[8]}",
            f"Hours Parked: {values[9]}",
            f"Amount Paid: {values[10]}",  # Already formatted with ₹
            f"Payment Status: {values[11]}",
        ]

        self.show_ticket_popup(details)

    def show_ticket_popup(self, details):
        ticket_window = Toplevel()
        ticket_window.title("Parking Ticket")
        ticket_window.geometry("450x600")
        ticket_window.configure(bg="white")

        tk.Label(ticket_window, text="🚗 Parking Ticket", font=("Arial", 18, "bold"), fg="darkblue", bg="white").pack(pady=15)

        ticket_frame = tk.Frame(ticket_window, bg="white", padx=15, pady=15, relief=tk.RIDGE, borderwidth=2)
        ticket_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for detail in details:
            key, value = detail.split(":", 1)
            row_frame = tk.Frame(ticket_frame, bg="white")
            row_frame.pack(fill=tk.X, pady=4)
            
            tk.Label(row_frame, text=key.strip() + ":", font=("Arial", 12, "bold"), bg="white", anchor="w", width=16).pack(side=tk.LEFT)
            tk.Label(row_frame, text=value.strip(), font=("Arial", 12), bg="white", anchor="w").pack(side=tk.LEFT, expand=True, padx=10)

        tk.Label(ticket_frame, text="Thank You for Choosing Us!", font=("Arial", 12, "bold"), fg="green", bg="white", pady=10).pack()

        button_frame = tk.Frame(ticket_window, bg="white", pady=10)
        button_frame.pack()

        print_button = tk.Button(button_frame, text="🖨 Print", font=("Arial", 12, "bold"), bg="#27AE60", fg="white",
                                padx=12, pady=6, command=lambda: self.print_ticket(details, ticket_window))
        print_button.pack(side=tk.LEFT, padx=10)

        close_button = tk.Button(button_frame, text="❌ Close", font=("Arial", 12, "bold"), bg="#E74C3C", fg="white",
                                padx=12, pady=6, command=ticket_window.destroy)
        close_button.pack(side=tk.RIGHT, padx=10)

    def print_ticket(self, details, ticket_window):
        ticket_window.destroy()

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")

        with open(temp_file.name, "w", encoding="utf-8") as file:
            file.write("""
            <html>
            <head>
                <title>Parking Ticket</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; }
                    .container { width: 400px; margin: auto; border: 2px solid #000; padding: 20px; border-radius: 10px; }
                    h1 { color: darkblue; }
                    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                    td { padding: 8px; border-bottom: 1px solid #ddd; text-align: left; }
                    .footer { font-weight: bold; color: green; margin-top: 10px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚗 Parking Ticket</h1>
                    <hr>
                    <table>
            """)
            for detail in details:
                key, value = detail.split(":", 1)
                file.write(f"<tr><td style='font-weight:bold;'>{key.strip()}:</td><td>{value.strip()}</td></tr>")

            file.write("""
                    </table>
                    <hr>
                    <p class="footer">Thank You for Choosing Us!</p>
                </div>
            <script>
                window.onload = function() {
                    window.print();
                    setTimeout(function() {
                        window.close();
                    }, 500);
                };
            </script>
            </body>
            </html>
            """)

        if platform.system() == "Windows":
            os.startfile(temp_file.name)
        else:
            webbrowser.open_new("file://" + temp_file.name)
