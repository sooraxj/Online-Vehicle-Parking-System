import tkinter as tk
from tkinter import messagebox
from db_connection import connect_to_db
from parking import ParkingPage

class SlotLayoutPage:
    def __init__(self, root, slot_id=None):
        self.root = root
        self.slot_id = slot_id
        self.root.configure(bg="#EAF2F8")
        self.build_page()

    def build_page(self):
        tk.Label(self.root, text="Slot Selection", font=("Arial", 16, "bold"), bg="#010f26", fg="white", pady=10).pack(fill=tk.X)

        # Create a scrollable frame
        container = tk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        canvas = tk.Canvas(container, bg="white")
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg="white")

        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=self.root.winfo_width())

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_slot_categories()

    def load_slot_categories(self):
        """Loads slot categories and arranges buttons from left to right in a row."""
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT slot_id, slotname, number_of_slots FROM tbl_slots WHERE status = 'Active'")
        slots = cursor.fetchall()
        conn.close()

        # Create a frame to hold the buttons horizontally
        button_container = tk.Frame(self.scroll_frame, bg="white")
        button_container.pack(pady=10)

        max_columns = 5  # Number of buttons in a row before wrapping
        row, col = 0, 0

        for slot_id, slotname, number_of_slots in slots:
            btn = tk.Button(button_container, text=f"{slotname}\n({number_of_slots} slots)",
                            font=("Arial", 20, "bold"), bg="#010f26", fg="white",
                            width=20, height=4, relief="raised", bd=3,
                            command=lambda sid=slot_id: self.show_slot_layout(sid))
            btn.grid(row=row, column=col, padx=10, pady=10)

            col += 1
            if col >= max_columns:  # Wrap to the next row after max columns
                col = 0
                row += 1

        if self.slot_id:
            self.show_slot_layout(self.slot_id)  # Reload the last viewed slot layout

    def show_slot_layout(self, slot_id):
        """Displays a movie/bus seat-style layout based on number of slots, with disabled occupied slots."""
        self.slot_id = slot_id  # Store the selected slot category for reload
        self.clear_frame()

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT slotname, number_of_slots FROM tbl_slots WHERE slot_id = %s", (slot_id,))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Slot category not found!")
            return

        slotname, total_slots = result

        tk.Label(self.scroll_frame, text=f"{slotname} Slot Layout", 
                font=("Arial", 20, "bold"), 
                bg="white",  # Dark red Background
                fg="black",    # White Text
                padx=10, pady=5
                ).pack(fill=tk.X, pady=5)

        # Fetch slot statuses from tbl_parking and check if status is 'Parked'
        cursor.execute("SELECT slot_number, status FROM tbl_parking WHERE slot_id = %s", (slot_id,))
        occupied_slots = {row[0] for row in cursor.fetchall() if row[1] == 'Parked'}
        conn.close()

        # Grid container with padding for better visibility
        grid_container = tk.Frame(self.scroll_frame, bg="white", padx=10, pady=10, bd=2, relief="solid")
        grid_container.pack(pady=10)

        rows = total_slots // 10 + (1 if total_slots % 10 else 0)
        cols = min(10, total_slots)  # Max 10 slots per row

        for i in range(rows):
            row_frame = tk.Frame(grid_container, bg="white")
            row_frame.pack(pady=3)

            for j in range(cols):
                slot_number = i * 10 + j + 1
                if slot_number > total_slots:
                    break

                is_occupied = slot_number in occupied_slots
                color = "red" if is_occupied else "green"  # Dark blue for free slots
                btn = tk.Button(row_frame, text=str(slot_number), bg=color, fg="white",
                                font=("Arial", 10, "bold"), width=5, height=2,
                                bd=3, relief="raised",  # Border for slot buttons
                                command=lambda sn=slot_number, occupied=is_occupied: self.handle_slot_click(slot_id, sn, occupied))
                btn.pack(side="left", padx=5, pady=3)
   
    def handle_slot_click(self, slot_id, slot_number, is_occupied):
        """Handles clicking on a slot - Either Reserve or Remove from Parking."""
        if is_occupied:
            self.remove_from_parking(slot_id, slot_number)
        else:
            self.reserve_slot(slot_id, slot_number)

    def remove_from_parking(self, slot_id, slot_number):
        """Removes the vehicle from parking and frees the slot."""
        confirm = messagebox.askyesno("Remove Parking", f"Do you want to remove vehicle from Slot {slot_number}?")
        if not confirm:
            return

        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE tbl_parking SET status = 'Exited' WHERE slot_id = %s AND slot_number = %s", (slot_id, slot_number))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Slot {slot_number} is now free!")
        self.show_slot_layout(slot_id)  # Reload same slot layout after removing parking

    def reserve_slot(self, slot_id, slot_number):
        """Opens the parking form in full-screen mode when a free slot is clicked."""
        self.root.destroy()
        root = tk.Tk()
        root.attributes('-fullscreen', True)  # Full-screen mode
        ParkingPage(root, slot_id, slot_number)
        root.mainloop()

    def clear_frame(self):
        """Clears the frame to dynamically update content."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
