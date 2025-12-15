import datetime
import re
import tkinter as tk
from tkinter import messagebox, ttk
from db_connection import connect_to_db
from payment import PaymentPage

class ParkingPage:
    def __init__(self, root, slot_id=None, slot_number=None):
        self.root = root
        self.slot_id = slot_id
        self.slot_number = slot_number
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#EAF2F8")
        self.build_page()

        exit_btn = tk.Button(
            self.root, text="❌ Exit Full Screen",
            font=("Arial", 12, "bold"), bg="#E74C3C", fg="white",
            activebackground="#C0392B", activeforeground="white",
            relief="raised", bd=3, padx=15, pady=8,
            command=lambda: self.root.attributes('-fullscreen', False)
        )
        exit_btn.pack(pady=15)

    def build_page(self):
        tk.Label(self.root, text="Parking Management", font=("Arial", 18, "bold"),
                 bg="#010f26", fg="white", pady=10).pack(fill=tk.X)

        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"),
                        background="#010f26", foreground="white")

        self.parking_table = ttk.Treeview(
            self.root, columns=("Customer Name", "Vehicle Number", "Contact", "Aadhar Number", "Entry Time",
                                "Exit Time", "Status", "Slot Number"), show='headings')
        for col in self.parking_table["columns"]:
            self.parking_table.heading(col, text=col)
            self.parking_table.column(col, anchor="center")

        self.parking_table.tag_configure("oddrow", background="#f9f9f9")
        self.parking_table.tag_configure("evenrow", background="white")
        self.parking_table.pack(pady=10, padx=10)

        self.load_parking_entries()

        tk.Button(self.root, text="➕ Add Parking", font=("Arial", 14, "bold"),
                  bg="#27AE60", fg="white", padx=15, pady=10, activebackground="#229954",
                  command=self.show_add_parking_form).pack(pady=20)

    def show_add_parking_form(self):
        form_window = tk.Toplevel(self.root)
        form_window.title("Add Parking Entry")
        form_window.configure(bg="#EAF2F8")

        tk.Label(form_window, text="Add Parking Entry", font=("Arial", 16, "bold"),
                 bg="#010f26", fg="white", pady=10).pack(fill=tk.X)

        form_frame = tk.Frame(form_window, bg="#EAF2F8", padx=20, pady=10)
        form_frame.pack(fill=tk.BOTH, expand=True)

        labels = ["Customer Name", "Vehicle Number", "Contact Number", "Aadhar Number",
                  "Slot Number", "Parking Duration (in hours)"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(form_frame, text=label, font=("Arial", 12, "bold"),
                     bg="#EAF2F8", fg="#010f26").grid(row=i, column=0, padx=10, pady=8, sticky="w")
            entry = tk.Entry(form_frame, font=("Arial", 12), bd=2, relief="solid")
            entry.grid(row=i, column=1, padx=10, pady=8, ipadx=5, sticky="ew")
            self.entries[label] = entry

        if self.slot_id and self.slot_number:
            self.entries["Slot Number"].insert(0, str(self.slot_number))
            self.entries["Slot Number"].config(state="disabled")

        tk.Button(form_frame, text="✅ Add and Proceed to Payment", font=("Arial", 14, "bold"),
                  bg="#3498DB", fg="white", activebackground="#2980B9", padx=15, pady=10,
                  bd=0, command=lambda: self.add_parking(form_window)).grid(row=len(labels), columnspan=2, pady=10)

    def validate_inputs(self):
        cust_name = self.entries["Customer Name"].get().strip()
        veh_no = self.entries["Vehicle Number"].get().strip()
        contact_no = self.entries["Contact Number"].get().strip()
        aadhar_no = self.entries["Aadhar Number"].get().strip()
        duration = self.entries["Parking Duration (in hours)"].get().strip()

        if not cust_name.replace(" ", "").isalpha():
            messagebox.showerror("Error", "Customer Name should contain only alphabets!")
            return False

        vehicle_pattern = r"^[A-Z]{2}-\d{2}-[A-Z]{1,2}-\d{4}$"
        if not re.match(vehicle_pattern, veh_no):
            messagebox.showerror("Error", "Vehicle Number format: CC-NN-C-NNNN or CC-NN-CC-NNNN")
            return False

        if not contact_no.isdigit() or len(contact_no) != 10:
            messagebox.showerror("Error", "Contact Number should be exactly 10 digits!")
            return False

        if not aadhar_no.isdigit() or len(aadhar_no) != 12:
            messagebox.showerror("Error", "Aadhar Number must be exactly 12 digits!")
            return False

        if not duration.isdigit() or not (1 <= int(duration) <= 999):
            messagebox.showerror("Error", "Parking Hours should be a 3-digit number (max 999)!")
            return False

        return True

    def add_parking(self, form_window):
        if not self.validate_inputs():
            return

        cust_name = self.entries["Customer Name"].get().strip()
        veh_no = self.entries["Vehicle Number"].get().strip()
        contact_no = self.entries["Contact Number"].get().strip()
        aadhar_no = self.entries["Aadhar Number"].get().strip()
        slot_number = self.entries["Slot Number"].get().strip()
        duration = int(self.entries["Parking Duration (in hours)"].get().strip())

        conn = connect_to_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tbl_parking 
            (custname, veh_no, contact_no, aadhar_no, entry_time, date, status, slot_id, slot_number, exit_time) 
            VALUES (%s, %s, %s, %s, NOW(), NOW(), %s, %s, %s, DATE_ADD(NOW(), INTERVAL %s HOUR))
        """, (cust_name, veh_no, contact_no, aadhar_no, "Parked", self.slot_id, slot_number, duration))
        conn.commit()

        cursor.execute("SELECT LAST_INSERT_ID()")
        park_id = cursor.fetchone()[0]

        fare = duration * 10
        ticket_number = self.generate_ticket_number()
        cursor.execute("INSERT INTO tbl_payment (park_id, amount, ticket_number) VALUES (%s, %s, %s)",
                       (park_id, fare, ticket_number))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Parking entry added successfully!")
        form_window.destroy()
        self.go_to_payment(park_id, cust_name, veh_no, contact_no)

    def generate_ticket_number(self):
        conn = connect_to_db()
        cursor = conn.cursor()
        current_year = datetime.datetime.now().year % 100
        prefix = f"PK-{current_year}-"
        cursor.execute("SELECT ticket_number FROM tbl_payment WHERE ticket_number LIKE %s ORDER BY ticket_number DESC LIMIT 1", (prefix + "%",))
        last_ticket = cursor.fetchone()
        new_number = "0001" if not last_ticket else f"{int(last_ticket[0].split('-')[-1]) + 1:04d}"
        conn.close()
        return prefix + new_number

    def go_to_payment(self, park_id, cust_name, veh_no, contact_no):
        self.root.destroy()
        root = tk.Tk()
        PaymentPage(root, park_id, cust_name, veh_no, contact_no)
        root.mainloop()

    def load_parking_entries(self):
        for row in self.parking_table.get_children():
            self.parking_table.delete(row)

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT custname, veh_no, contact_no, aadhar_no, entry_time, exit_time, status, slot_number FROM tbl_parking")
        entries = cursor.fetchall()
        conn.close()

        for i, entry in enumerate(entries):
            row_tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.parking_table.insert("", tk.END, values=entry, tags=(row_tag,))

if __name__ == "__main__":
    root = tk.Tk()
    ParkingPage(root)
    root.mainloop()
