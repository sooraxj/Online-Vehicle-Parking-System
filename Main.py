import os
import tkinter as tk
from slots import SlotsPage
from parking import ParkingPage
from payment_view import PaymentViewPage
from slot_layout import SlotLayoutPage
from graphs import RevenueSalesGraph

class AdminPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vehicle Parking Management System")
        self.state("zoomed")
        self.configure(bg="#f4f4f4")

        self.sidebar = tk.Frame(self, bg="#010f26", width=180)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(self.sidebar, text="Admin Panel", fg="white", bg="#010f26", font=("Arial", 14, "bold"), pady=15).pack()

        self.buttons = {}
        menu_items = {
            "Home": self.show_home,
            "Slots": self.show_slots,
            "Parking": self.show_slot_layout,
            "Payment": self.show_payment_view
        }
        for text, command in menu_items.items():
            btn = tk.Button(
                self.sidebar, text=text, font=("Arial", 12, "bold"),
                fg="white", bg="#011c47",
                activebackground="white", activeforeground="black",
                bd=0, relief="flat", padx=10, pady=5, width=18,
                command=command
            )
            btn.pack(pady=10)
            self.buttons[text] = btn

        tk.Button(
            self.sidebar, text="Logout", font=("Arial", 12, "bold"),
            fg="white", bg="red",
            activebackground="white", activeforeground="black",
            bd=0, relief="flat", padx=10, pady=5, width=18,
            command=self.logout
        ).pack(pady=20)

        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.show_home()

    def show_home(self):
        self.clear_content()
        tk.Label(
            self.content_frame, text="📊 Revenue & Sales Graphs",
            font=("Arial", 20, "bold"), bg="#010f26", fg="white",
            padx=20, pady=15, relief="raised", bd=3
        ).pack(fill="x", padx=0, pady=20)
        RevenueSalesGraph(self.content_frame)

    def show_slots(self):
        self.clear_content()
        SlotsPage(self.content_frame)

    def show_slot_layout(self):
        self.clear_content()
        SlotLayoutPage(self.content_frame)

    def show_parking(self):
        self.clear_content()
        ParkingPage(self.content_frame)

    def show_payment_view(self):
        self.clear_content()
        PaymentViewPage(self.content_frame)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def logout(self):
        self.destroy()
        os.system("python index.py")  # Redirects to the main index page

if __name__ == "__main__":
    app = AdminPanel()
    app.mainloop()
