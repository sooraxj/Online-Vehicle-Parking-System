import tkinter as tk
from tkinter import messagebox
from db_connection import connect_to_db  

class PaymentPage:
    def __init__(self, root, parking_id, cust_name, veh_no, contact_no):
        self.root = root
        self.parking_id = parking_id
        self.cust_name = cust_name
        self.veh_no = veh_no
        self.contact_no = contact_no

        self.entry_time, self.exit_time, self.duration, self.amount, self.ticket_number = self.get_parking_details()
  
        self.root.title("Payment Page")
        self.root.geometry("400x450")
        self.root.configure(bg="#010f26")

        self.build_page()

    def get_parking_details(self):
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.entry_time, p.exit_time, TIMESTAMPDIFF(HOUR, p.entry_time, IFNULL(p.exit_time, NOW())), 
                s.fare, pay.ticket_number
            FROM tbl_parking p
            JOIN tbl_slots s ON p.slot_id = s.slot_id
            JOIN tbl_payment pay ON p.park_id = pay.park_id  -- ✅ Corrected join
            WHERE p.park_id = %s
        """, (self.parking_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            entry_time, exit_time, duration, fare, ticket_number = result  # ✅ FIXED
            duration = max(duration, 1)
            amount = duration * fare
            self.update_payment_table(amount)
            return entry_time, exit_time, duration, amount, ticket_number
        else:
            return "N/A", "N/A", "N/A", "N/A"

    def update_payment_table(self, amount):
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE tbl_payment SET amount = %s WHERE park_id = %s", (amount, self.parking_id))
        conn.commit()
        conn.close()

    def build_page(self):
        tk.Label(self.root, text="Payment for Parking", font=("Arial", 18, "bold"), fg="white").pack(pady=10)

        details_frame = tk.Frame(self.root, bd=2, relief="solid", padx=10, pady=10, bg="white")
        details_frame.pack(pady=10, padx=20, fill="both")

        fields = [
            ("Ticket Number:", self.ticket_number),
            ("Customer Name:", self.cust_name),
            ("Vehicle Number:", self.veh_no),
            ("Contact Number:", self.contact_no),
            ("Entry Time:", self.entry_time),
            ("Exit Time:", self.exit_time),
            ("Hours Parked:", self.duration),
            ("Total Amount:", f"${self.amount}")
        ]

        for i, (label, value) in enumerate(fields):
            tk.Label(details_frame, text=label, font=("Arial", 10, "bold"), bg="white").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            tk.Label(details_frame, text=value, font=("Arial", 10), bg="white").grid(row=i, column=1, sticky="w", padx=5, pady=2)

        btn_frame = tk.Frame(self.root, bg="#010f26")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Pay with Cash", command=self.pay_with_cash, font=("Arial", 12),
                  bg="#4CAF50", fg="white", width=15, relief="flat").pack(pady=5)

        tk.Button(btn_frame, text="Pay with Card", command=self.pay_with_card, font=("Arial", 12),
                  bg="#2196F3", fg="white", width=15, relief="flat").pack(pady=5)

    def pay_with_cash(self):
        if messagebox.askyesno("Cash Payment", "Confirm cash payment?"):
            self.complete_payment()

    def pay_with_card(self):
        if messagebox.askyesno("Card Payment", "Proceed with card payment?"):
            self.complete_payment()

    def complete_payment(self):
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE tbl_parking SET status = %s WHERE park_id = %s", ('Parked', self.parking_id))
        cursor.execute("UPDATE tbl_payment SET status = %s WHERE park_id = %s", ('Paid', self.parking_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Payment completed!")
        self.go_back_to_parking()

    def go_back_to_parking(self):
        self.root.destroy()  # Close the current payment window

        # Check if there is an existing Tk root window and close it
        if tk._default_root:
            tk._default_root.quit()  # Quit the mainloop safely
            tk._default_root.destroy()  # Destroy any remaining windows

        # Reopen the Admin Panel with Payment View
        import Main
        app = Main.AdminPanel()
        app.show_payment_view()
        app.mainloop()




if __name__ == "__main__":
    root = tk.Tk()
    PaymentPage(root, 1, "John Doe", "ABC123", "1234567890")
    root.mainloop()