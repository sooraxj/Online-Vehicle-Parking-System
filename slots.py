import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from db_connection import connect_to_db

class SlotsPage:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#EAF2F8")  # Light background
        self.build_page()

    def build_page(self):
        tk.Label(self.root, text="Slot Management", font=("Arial", 16, "bold"), bg="#010f26", fg="white", pady=10).pack(fill=tk.X)

        # Add Slot Button
        tk.Button(self.root, text="➕ Add Slot", font=("Arial", 12, "bold"), bg="#27AE60", fg="white", padx=10, pady=5,
                  activebackground="#229954", command=self.show_add_slot_form).pack(pady=10)

        # Slot Table Styling
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#010f26", foreground="black")

        self.slot_table = ttk.Treeview(self.root, columns=("slot_id", "Name", "Fare", "Number of Slots", "Status"), show='headings')
        self.slot_table.heading("slot_id", text="ID")
        self.slot_table.heading("Name", text="Slot Name")
        self.slot_table.heading("Fare", text="Fare (₹)")
        self.slot_table.heading("Number of Slots", text="Number of Slots")
        self.slot_table.heading("Status", text="Status")

        # Alternating row colors
        self.slot_table.tag_configure('oddrow', background="#f9f9f9")
        self.slot_table.tag_configure('evenrow', background="white")

        for col in ("slot_id", "Name", "Fare", "Number of Slots", "Status"):
            self.slot_table.column(col, anchor='center')

        self.slot_table.pack(pady=10, padx=10)
        self.load_slots()

        # Edit Slot Button
        tk.Button(self.root, text="✏️ Edit Selected Slot", font=("Arial", 12, "bold"), bg="#2980B9", fg="white", padx=10, pady=5,
                  activebackground="#2471A3", command=self.on_edit_slot).pack(pady=10)

    def show_add_slot_form(self):
        self._create_slot_form("Add Slot", self.add_slot)

    def show_edit_slot_form(self, slot_id, current_name, current_fare, current_number):
        self._create_slot_form("Edit Slot", lambda name, fare, number, win: self.update_slot(slot_id, name, fare, number, win),
                               current_name, current_fare, current_number)

    def _create_slot_form(self, title, submit_command, current_name="", current_fare="", current_number=""):
        form_window = tk.Toplevel(self.root)
        form_window.title(title)
        form_window.geometry("400x300")
        form_window.configure(bg="#EAF2F8")
        form_window.resizable(False, False)

        tk.Label(form_window, text=title, font=("Arial", 16, "bold"), bg="#010f26", fg="white", pady=10).pack(fill=tk.X)

        form_frame = tk.Frame(form_window, bg="#EAF2F8", padx=20, pady=10)
        form_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(form_frame, text="Slot Name", font=("Arial", 12, "bold"), bg="#EAF2F8", fg="#010f26").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        slot_name_var = tk.StringVar(value=current_name)
        slot_name_dropdown = ttk.Combobox(form_frame, textvariable=slot_name_var, font=("Arial", 12), state="readonly")
        slot_name_dropdown['values'] = ("Two Wheeler", "Three Wheeler", "Four Wheeler", "Six Wheeler")
        slot_name_dropdown.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        tk.Label(form_frame, text="Fare (₹)", font=("Arial", 12, "bold"), bg="#EAF2F8", fg="#010f26").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        fare_entry = tk.Entry(form_frame, font=("Arial", 12), bd=2, relief="solid")
        fare_entry.insert(0, current_fare)
        fare_entry.grid(row=1, column=1, padx=10, pady=8, ipadx=5, sticky="ew")

        tk.Label(form_frame, text="Number of Slots", font=("Arial", 12, "bold"), bg="#EAF2F8", fg="#010f26").grid(row=2, column=0, padx=10, pady=8, sticky="w")
        number_entry = tk.Entry(form_frame, font=("Arial", 12), bd=2, relief="solid")
        number_entry.insert(0, current_number)
        number_entry.grid(row=2, column=1, padx=10, pady=8, ipadx=5, sticky="ew")

        submit_text = "✅ Add Slot" if title == "Add Slot" else "✅ Update Slot"
        submit_color = "#27AE60" if title == "Add Slot" else "#3498DB"

        tk.Button(form_frame, text=submit_text, font=("Arial", 13, "bold"), bg=submit_color, fg="white",
                  activebackground="#229954" if title == "Add Slot" else "#2980B9",
                  padx=10, pady=5, bd=0,
                  command=lambda: submit_command(slot_name_var.get(), fare_entry.get(), number_entry.get(), form_window)).grid(row=3, columnspan=2, pady=10)

    def add_slot(self, slot_name, fare, number_of_slots, form_window):
        if not slot_name or not fare or not number_of_slots:
            messagebox.showerror("Error", "All fields are required!")
            return

        if not fare.isdigit() or not number_of_slots.isdigit():
            messagebox.showerror("Error", "Fare and Number of Slots must be valid numbers!")
            return

        fare = float(fare)
        number_of_slots = int(number_of_slots)

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tbl_slots (slotname, fare, number_of_slots, status) VALUES (%s, %s, %s, %s)", 
                       (slot_name, fare, number_of_slots, 'Active'))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Slot added successfully!")
        form_window.destroy()
        self.load_slots()

    def update_slot(self, slot_id, slot_name, fare, number_of_slots, form_window):
        if not slot_name or not fare or not number_of_slots:
            messagebox.showerror("Error", "All fields are required!")
            return

        if not fare.isdigit() or not number_of_slots.isdigit():
            messagebox.showerror("Error", "Fare and Number of Slots must be valid numbers!")
            return

        fare = float(fare)
        number_of_slots = int(number_of_slots)

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE tbl_slots SET slotname = %s, fare = %s, number_of_slots = %s WHERE slot_id = %s", 
                       (slot_name, fare, number_of_slots, slot_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Slot updated successfully!")
        form_window.destroy()
        self.load_slots()

    def on_edit_slot(self):
        selected_item = self.slot_table.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a slot to edit.")
            return

        item = self.slot_table.item(selected_item)
        values = item['values']
        if values:
            self.show_edit_slot_form(values[0], values[1], values[2], values[3])

    def load_slots(self):
        for row in self.slot_table.get_children():
            self.slot_table.delete(row)

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tbl_slots")
        slots = cursor.fetchall()
        conn.close()

        for i, slot in enumerate(slots):
            self.slot_table.insert('', tk.END, values=slot, tags=("evenrow" if i % 2 == 0 else "oddrow"))
