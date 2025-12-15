import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import tkinter.font as tkFont
from datetime import datetime
import time
from db_connection import connect_to_db
from Main import AdminPanel

class ModernButton(tk.Frame):
    def __init__(self, parent, text, command, bg_color="#010f26", hover_color="#3b82f6", 
                 text_color="white", width=200, height=50, font=("Helvetica", 12, "bold")):
        super().__init__(parent, bg=parent.cget('bg'))
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        
        self.button = tk.Label(self, text=text, font=font, fg=text_color, bg=bg_color,
                              width=width//8, height=height//20, cursor="hand2")
        self.button.pack()
        
        self.button.bind("<Button-1>", lambda e: self.command())
        self.button.bind("<Enter>", self.on_enter)
        self.button.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event):
        self.button.config(bg=self.hover_color)
    
    def on_leave(self, event):
        self.button.config(bg=self.bg_color)

class AnimatedCounter(tk.Frame):
    def __init__(self, parent, label_text, target_value, color="#010f26"):
        super().__init__(parent, bg=parent.cget('bg'))
        
        self.target = target_value
        self.current = 0
        
        self.value_label = tk.Label(self, text="0", font=("Helvetica", 30, "bold"), 
                                   fg=color, bg=parent.cget('bg'))
        self.value_label.pack()
        
        self.label = tk.Label(self, text=label_text, font=("Helvetica", 14), 
                             fg="#4b5563", bg=parent.cget('bg'))
        self.label.pack()
        
        self.animate()
    
    def animate(self):
        if self.current < self.target:
            self.current += max(1, self.target // 20)
            if self.current > self.target:
                self.current = self.target
            self.value_label.config(text=str(self.current))
            self.after(50, self.animate)

class DigitalClock(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=parent.cget('bg'), bd=1, relief="solid")
        
        self.time_label = tk.Label(self, font=("Helvetica", 16, "bold"), 
                                  fg="white", bg="#010f26", padx=20, pady=8)
        self.time_label.pack()
        
        self.date_label = tk.Label(self, font=("Helvetica", 8), 
                                  fg="white", bg="#010f26", padx=20, pady=8)
        self.date_label.pack()
        
        self.update_time()
    
    def update_time(self):
        now = datetime.now()
        time_str = now.strftime("%I:%M:%S %p")
        date_str = now.strftime("%B %d, %Y | %A")
        
        self.time_label.config(text=time_str)
        self.date_label.config(text=date_str)
        
        self.after(1000, self.update_time)

class GradientFrame(tk.Canvas):
    def __init__(self, parent, color1="#010f26", color2="#1e40af", width=800, height=400):
        super().__init__(parent, width=width, height=height, highlightthickness=0)
        
        for i in range(height):
            ratio = i / height
            r = int((1-ratio) * int(color1[1:3], 16) + ratio * int(color2[1:3], 16))
            g = int((1-ratio) * int(color1[3:5], 16) + ratio * int(color2[3:5], 16))
            b = int((1-ratio) * int(color1[5:7], 16) + ratio * int(color2[5:7], 16))
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.create_line(0, i, width, i, fill=color)

class IndexPage(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SmartPark - Professional Parking Management")
        self.geometry("1400x800")
        self.state("zoomed")
        self.configure(bg="#f9fafb")
        
        self.title_font = tkFont.Font(family="Helvetica", size=36, weight="bold")
        self.subtitle_font = tkFont.Font(family="Helvetica", size=18)
        self.nav_font = tkFont.Font(family="Helvetica", size=14, weight="bold")
        
        self.setup_styles()
        self.create_navigation()
        self.create_main_content()
        self.create_footer()
        self.show_home()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Modern.TButton',
                       background='#010f26',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 12))
        
        style.map('Modern.TButton',
                 background=[('active', '#3b82f6'),
                           ('pressed', '#1e40af')])

    def create_navigation(self):
        nav_frame = tk.Frame(self, bg="#010f26", height=80)
        nav_frame.pack(fill="x")
        nav_frame.pack_propagate(False)
        
        container = tk.Frame(nav_frame, bg="#010f26")
        container.pack(expand=True, fill="x", padx=40)
        
        logo_frame = tk.Frame(container, bg="#010f26")
        logo_frame.pack(side="left", pady=20)
        
        logo_text = tk.Label(logo_frame, text="🅿️ SmartPark", 
                           font=("Helvetica", 20, "bold"), 
                           fg="white", bg="#010f26")
        logo_text.pack()
        
        nav_buttons_frame = tk.Frame(container, bg="#010f26")
        nav_buttons_frame.pack(side="left", expand=True, fill="x")
        
        nav_buttons = [
            ("Home", self.show_home, "#22c55e"),
            ("About", self.show_about, "#3b82f6"),
            ("Statistics", self.show_statistics, "#f59e0b"),
            ("Services", self.show_services, "#8b5cf6"),
        ]
        
        for text, command, color in nav_buttons:
            btn_frame = tk.Frame(nav_buttons_frame, bg="#010f26")
            btn_frame.pack(side="left", padx=60)
            
            btn = tk.Label(btn_frame, text=text, font=self.nav_font, 
                          fg="white", bg="#010f26", cursor="hand2",
                          padx=20, pady=15)
            btn.pack()
            
            btn.bind("<Button-1>", lambda e, cmd=command: cmd())
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=c))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#010f26"))
        
        right_frame = tk.Frame(container, bg="#010f26")
        right_frame.pack(side="right", padx=10)
        
        login_btn = ModernButton(right_frame, "Login", 
                               self.show_login_window, 
                               bg_color="#dc2626", hover_color="#b91c1c",
                               width=100, height=50, font=("Helvetica", 12, "bold"))
        login_btn.pack(side="right", padx=(20, 0))
        
        self.clock = DigitalClock(right_frame)
        self.clock.pack(side="right", padx=(0, 10))


    def create_main_content(self):
        self.content_frame = tk.Frame(self, bg="#f9fafb")
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=20)

    def create_footer(self):
        footer_frame = tk.Frame(self, bg="#010f26", height=60)
        footer_frame.pack(side="bottom", fill="x")
        footer_frame.pack_propagate(False)
        
        footer_content = tk.Frame(footer_frame, bg="#010f26")
        footer_content.pack(expand=True, fill="both")
        
        copyright_text = tk.Label(footer_content, 
                                text="© 2025 SmartPark Systems, Inc. All rights reserved.",
                                font=("Helvetica", 12), fg="white", bg="#010f26")
        copyright_text.pack(expand=True, padx=40, pady=20)  # Centered with expand=True, no side
        
        social_frame = tk.Frame(footer_content, bg="#010f26")
        social_frame.pack(side="right", padx=40, pady=20)  # Keep social icons on the right
        

    def show_home(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.content_frame)
        main_frame.pack(expand=True, fill="both")
        
        hero_frame = GradientFrame(main_frame, "#010f26", "#1e40af", 
                                self.winfo_screenwidth()-80, 400)
        hero_frame.pack(pady=10)
        
        center_x = hero_frame.winfo_reqwidth() // 2 if hero_frame.winfo_reqwidth() else (self.winfo_screenwidth() // 2 - 40)
        
        # Create text directly on canvas for transparency over gradient
        hero_frame.create_text(center_x, 100, text="Welcome to SmartPark", 
                            font=self.title_font, fill="white", anchor="center")
        
        hero_frame.create_text(center_x, 160, text="Intelligent Parking Management Solutions",
                            font=self.subtitle_font, fill="#93c5fd", anchor="center")
        
        hero_frame.create_text(center_x, 200, 
                            text="Transforming urban mobility with AI-driven parking optimization,\nreal-time availability, and seamless user experiences.",
                            font=("Helvetica", 14), fill="white", justify="center", anchor="center")
        
        features_frame = tk.Frame(main_frame, bg="#f9fafb")
        features_frame.pack(pady=20, fill="x")
        
        features_title = tk.Label(features_frame, text="Key Features", 
                                font=("Helvetica", 28, "bold"), fg="#010f26", bg="#f9fafb")
        features_title.pack(pady=1)
        
        cards_frame = tk.Frame(features_frame, bg="#f9fafb")
        cards_frame.pack(fill="x")
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        features = [
            ("AI-Powered", "Smart algorithms for optimal space allocation", "#22c55e"),
            ("Mobile Ready", "Access from any device, anywhere", "#3b82f6"),
            ("Real-Time", "Live updates on parking availability", "#f59e0b"),
            ("Secure", "Advanced security and payment systems", "#dc2626"),
        ]
        
        for i, (title, desc, color) in enumerate(features):
            card = tk.Frame(cards_frame, bg="white", relief="raised", bd=2, padx=20, pady=20)
            card.grid(row=0, column=i, padx=20, pady=20, sticky="nsew")
            
            shadow = tk.Frame(cards_frame, bg="#e5e7eb", height=2)
            shadow.grid(row=1, column=i, sticky="ew", padx=22)
            
            icon_title = tk.Label(card, text=title, font=("Helvetica", 18, "bold"), 
                                fg=color, bg="white")
            icon_title.pack(pady=(0, 10))
            
            description = tk.Label(card, text=desc, font=("Helvetica", 12), 
                                fg="#4b5563", bg="white", wraplength=200, justify="center")
            description.pack()

    def show_about(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.content_frame, bg="#f9fafb")
        main_frame.pack(expand=True, fill="both")
        
        header_frame = tk.Frame(main_frame, bg="#f9fafb")
        header_frame.pack(fill="x", pady=20)
        
        title = tk.Label(header_frame, text="About SmartPark Systems", 
                        font=("Helvetica", 32, "bold"), fg="#010f26", bg="#f9fafb")
        title.pack(pady=20)
        
        content_frame = tk.Frame(main_frame, bg="#f9fafb")
        content_frame.pack(fill="both", expand=True, padx=40)
        
        sections = [
            ("Our Mission", "To revolutionize urban parking through innovative technology, reducing congestion and enhancing city mobility.", "#22c55e"),
            ("Technology", "Advanced AI algorithms and real-time data processing for unmatched parking solutions.", "#3b82f6"),
            ("Impact", "Serving 10,000+ vehicles daily across 50+ locations, reducing parking search time by 75%.", "#f59e0b"),
        ]
        
        for title, text, color in sections:
            section_frame = tk.Frame(content_frame, bg="white", relief="solid", bd=1, padx=30, pady=25)
            section_frame.pack(fill="x", pady=15)
            
            section_title = tk.Label(section_frame, text=title, 
                                   font=("Helvetica", 20, "bold"), fg=color, bg="white")
            section_title.pack(anchor="w", pady=(0, 15))
            
            section_text = tk.Label(section_frame, text=text, font=("Helvetica", 14), 
                                  fg="#4b5563", bg="white", wraplength=1000, justify="left")
            section_text.pack(anchor="w")

    def show_statistics(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.content_frame, bg="#f9fafb")
        main_frame.pack(expand=True, fill="both")
        
        title = tk.Label(main_frame, text="System Statistics", 
                        font=("Helvetica", 32, "bold"), fg="#010f26", bg="#f9fafb")
        title.pack(pady=30)
        
        stats_frame = tk.Frame(main_frame, bg="#f9fafb")
        stats_frame.pack(pady=40)
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        stats_data = [
            ("Total Parking Spots", 500, "#22c55e"),
            ("Available Now", 127, "#3b82f6"),
            ("Daily Users", 1250, "#f59e0b"),
            ("Monthly Revenue", 85000, "#dc2626"),
        ]
        
        for i, (label, value, color) in enumerate(stats_data):
            stat_card = tk.Frame(stats_frame, bg="white", relief="raised", bd=3, padx=40, pady=30)
            stat_card.grid(row=0, column=i, padx=20, pady=20, sticky="nsew")
            
            counter = AnimatedCounter(stat_card, label, value, color)
            counter.pack()

    def show_services(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.content_frame, bg="#f9fafb")
        main_frame.pack(expand=True, fill="both")
        
        title = tk.Label(main_frame, text="Our Services", 
                        font=("Helvetica", 32, "bold"), fg="#010f26", bg="#f9fafb")
        title.pack(pady=30)
        
        services_frame = tk.Frame(main_frame, bg="#f9fafb")
        services_frame.pack(fill="both", expand=True, padx=40, pady=20)
        services_frame.grid_columnconfigure((0, 1), weight=1)
        
        services = [
            ("Valet Parking", "Premium valet service with professional attendants", "#8b5cf6"),
            ("EV Charging", "Electric vehicle charging stations available", "#22c55e"),
            ("Mobile App", "Complete parking management through our mobile app", "#3b82f6"),
            ("Digital Payments", "Contactless payment options for convenience", "#f59e0b"),
            ("Security", "24/7 CCTV monitoring and security personnel", "#dc2626"),
            ("GPS Navigation", "Turn-by-turn directions to your parking spot", "#06b6d4"),
        ]
        
        for i, (title, desc, color) in enumerate(services):
            service_card = tk.Frame(services_frame, bg="white", relief="solid", bd=2, padx=25, pady=20)
            service_card.grid(row=i//2, column=i%2, padx=20, pady=15, sticky="nsew")
            
            service_title = tk.Label(service_card, text=title, font=("Helvetica", 18, "bold"), 
                                   fg=color, bg="white")
            service_title.pack(anchor="w", pady=(0, 10))
            
            service_desc = tk.Label(service_card, text=desc, font=("Helvetica", 12), 
                                  fg="#4b5563", bg="white", wraplength=300, justify="left")
            service_desc.pack(anchor="w")

    def show_login_window(self):
        login_window = tk.Toplevel(self)
        login_window.title("Admin Login - SmartPark Systems")
        login_window.geometry("450x450")
        login_window.configure(bg="#f9fafb")
        login_window.resizable(False, False)
        
        login_window.transient(self)
        login_window.grab_set()
        
        header_frame = tk.Frame(login_window, bg="#010f26", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_title = tk.Label(header_frame, text="Administrator Login", 
                              font=("Helvetica", 18, "bold"), fg="white", bg="#010f26")
        header_title.pack(expand=True)
        
        form_frame = tk.Frame(login_window, bg="white", padx=40, pady=30)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(form_frame, text="Username:", font=("Helvetica", 12, "bold"), 
                bg="white", fg="#010f26").pack(anchor="w", pady=(0, 5))
        username_entry = tk.Entry(form_frame, font=("Helvetica", 12), width=30, relief="solid", bd=1)
        username_entry.pack(fill="x", pady=(0, 20), ipady=8)
        
        tk.Label(form_frame, text="Password:", font=("Helvetica", 12, "bold"), 
                bg="white", fg="#010f26").pack(anchor="w", pady=(0, 5))
        password_entry = tk.Entry(form_frame, show="*", font=("Helvetica", 12), width=30, relief="solid", bd=1)
        password_entry.pack(fill="x", pady=(0, 30), ipady=8)
        
        def check_login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if not username or not password:
                messagebox.showwarning("Warning", "Please enter both username and password.")
                return

            try:
                db = connect_to_db()
                cursor = db.cursor()
                cursor.execute("SELECT * FROM tbl_login WHERE username=%s AND password=%s AND status='Active'", 
                             (username, password))
                user = cursor.fetchone()
                db.close()

                if user:
                    messagebox.showinfo("Success", "Login successful. Accessing Admin Panel...")
                    login_window.destroy()
                    self.destroy()
                    app = AdminPanel()
                    app.mainloop()
                else:
                    messagebox.showerror("Error", "Invalid credentials or inactive account.")
            except Exception as e:
                messagebox.showerror("Error", f"Database connection failed: {str(e)}")
        
        login_btn = tk.Button(form_frame, text="LOGIN", font=("Helvetica", 12, "bold"),
                            bg="#010f26", fg="white", relief="flat", cursor="hand2",
                            command=check_login, pady=12)
        login_btn.pack(fill="x")
        
        def on_enter(e):
            login_btn.config(bg="#3b82f6")
        def on_leave(e):
            login_btn.config(bg="#010f26")
            
        login_btn.bind("<Enter>", on_enter)
        login_btn.bind("<Leave>", on_leave)
        
        username_entry.focus()

if __name__ == "__main__":
    app = IndexPage()
    app.mainloop()