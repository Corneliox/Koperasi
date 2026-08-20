"""
Loans Frame - Loan Management with Uniform Grid System & Status Badges
REFACTORED: Synchronized header/row alignment, colored status badges, enhanced progress bars.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from app.modules.loans import LoanManager
from app.modules.members import MemberManager
from app.utils.error_handler import clean_numeric

class LoansFrame(ctk.CTkFrame):
    def __init__(self, master, current_user: str):
        super().__init__(master)
        self.current_user = current_user
        self.loan_manager = LoanManager(current_user)
        self.member_manager = MemberManager(current_user)
        self.active_windows = {}
        
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Color Palette - Brimob Style
        self.colors = {
            "primary": "#00d4ff",
            "accent": "#f59e0b",
            "success": "#4ade80",
            "danger": "#ef4444",
            "bg_dark": "#1a1a2e",
            "row_alt": "#16213e"
        }

        # Definisi Kolom yang Konsisten (Sama untuk Header & Row)
        self.columns_config = [
            {"text": "ID", "width": 45, "weight": 0},
            {"text": "Nama Anggota", "width": 160, "weight": 2},      
            {"text": "Telepon", "width": 115, "weight": 1},
            {"text": "Pokok", "width": 100, "weight": 1},      
            {"text": "Total", "width": 110, "weight": 1},      
            {"text": "Progress", "width": 130, "weight": 1},
            {"text": "Jatuh Tempo", "width": 100, "weight": 1},
            {"text": "Status", "width": 90, "weight": 0},
            {"text": "Aksi", "width": 100, "weight": 0}
        ]
        
        self.create_header()
        self.create_stats_bar()
        self.create_table_structure()
        self.load_data()

    def create_header(self):
        self.header_frame = ctk.CTkFrame(self, fg_color=self.colors["bg_dark"], corner_radius=10)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # Title with Icon style
        title_lbl = ctk.CTkLabel(
            self.header_frame, text="💰 MANAJEMEN PINJAMAN",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.colors["primary"]
        )
        title_lbl.pack(side="left", padx=20, pady=15)
        
        btn_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=20)
        
        self.status_var = ctk.StringVar(value="Semua Status")
        ctk.CTkOptionMenu(
            btn_frame, values=["Semua Status", "Aktif", "Lunas", "Macet"],
            variable=self.status_var, width=130,
            command=lambda v: self.load_data()
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, text="📊 Simulasi", width=100, height=35,
            fg_color="#8b5cf6", hover_color="#7c3aed",
            corner_radius=8, command=self.open_simulation
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame, text="+ Pinjaman Baru", fg_color=self.colors["success"],
            text_color="#000", font=ctk.CTkFont(weight="bold"),
            command=self.open_add_dialog
        ).pack(side="left", padx=5)

    def create_stats_bar(self):
        self.stats_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=10, height=60)
        self.stats_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.stats_frame.grid_propagate(False)
        
        # Stats Labels
        self.total_loans_label = self._create_stat_item("Total Pinjaman", "0", "#ccc")
        self.active_loans_label = self._create_stat_item("Aktif", "0", self.colors["accent"])
        self.total_amount_label = self._create_stat_item("Outstanding", "Rp 0", self.colors["success"], side="right")

    def _create_stat_item(self, label, value, color, side="left"):
        container = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        container.pack(side=side, padx=30, pady=10)
        ctk.CTkLabel(container, text=f"{label}: ", font=ctk.CTkFont(size=12)).pack(side="left")
        lbl = ctk.CTkLabel(container, text=value, font=ctk.CTkFont(size=13, weight="bold"), text_color=color)
        lbl.pack(side="left")
        return lbl

    def create_table_structure(self):
        self.table_container = ctk.CTkFrame(self, fg_color=self.colors["bg_dark"], corner_radius=10)
        self.table_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=1)
        
        # Header Row
        self.header_row = ctk.CTkFrame(self.table_container, fg_color="#111827", height=45)
        self.header_row.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header_row.grid_propagate(True)
        
        for i, config in enumerate(self.columns_config):
            self.header_row.grid_columnconfigure(i, weight=config["weight"], minsize=config["width"])
            ctk.CTkLabel(
                self.header_row, text=config["text"].upper(),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=self.colors["primary"]
            ).grid(row=0, column=i, padx=10, pady=12, sticky="w")
        
        self.scroll_frame = ctk.CTkScrollableFrame(self.table_container, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def load_data(self):
        try:
            if not self.winfo_exists(): return
        except:
            return

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        f = self.status_var.get()
        status_filter = None if f == "Semua Status" else f
        loans = self.loan_manager.get_all_loans_with_phone(status_filter)
        
        # Update Stats logic
        active_loans = [l for l in loans if l.get('status') != 'Lunas']
        total_sum = sum(
            float(l.get('total_amount') or 0) - float(l.get('paid_amount') or 0)
            for l in active_loans
        )
        
        self.total_loans_label.configure(text=str(len(loans)))
        self.active_loans_label.configure(text=str(len(active_loans)))
        self.total_amount_label.configure(text=f"Rp {total_sum:,.0f}")

        for idx, loan in enumerate(loans):
            try:
                self.create_row(idx, loan)
            except Exception as e:
                print(f"ERROR rendering loan row {idx}: {e}")

    def create_row(self, idx, loan):
        bg = self.colors["bg_dark"] if idx % 2 == 0 else self.colors["row_alt"]
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=bg, height=60, corner_radius=5)
        row_frame.pack(fill="x", pady=2)
        row_frame.grid_propagate(True)
        
        # Config grid row sesuai header
        for i, config in enumerate(self.columns_config):
            row_frame.grid_columnconfigure(i, weight=config["weight"], minsize=config["width"])

        # Data Parsing with ZeroDivisionError Protection
        total = float(loan.get('total_amount') or 0)
        paid = float(loan.get('paid_amount') or 0)
        prog = min(1.0, max(0.0, paid / total)) if total > 0 else 0.0
        
        # ID & Nama
        ctk.CTkLabel(row_frame, text=f"#{loan['id']}", font=ctk.CTkFont(size=11)).grid(row=0, column=0, padx=10, sticky="w")
        ctk.CTkLabel(row_frame, text=str(loan.get('member_name', '-'))[:20], font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=1, padx=10, sticky="w")
        ctk.CTkLabel(row_frame, text=str(loan.get('member_phone', '-')), font=ctk.CTkFont(size=11), text_color="#00d4ff").grid(row=0, column=2, padx=10, sticky="w")
        
        # Financials
        principal_val = float(loan.get('principal') or 0)
        ctk.CTkLabel(row_frame, text=f"Rp {principal_val:,.0f}", font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=10, sticky="w")
        ctk.CTkLabel(row_frame, text=f"Rp {total:,.0f}", text_color=self.colors["accent"], font=ctk.CTkFont(size=11, weight="bold")).grid(row=0, column=4, padx=10, sticky="w")

        # Progress Section (ENHANCED)
        p_container = ctk.CTkFrame(row_frame, fg_color="transparent")
        p_container.grid(row=0, column=5, padx=10, sticky="ew")
        
        # Color gradient logic
        if prog >= 0.9: p_color = "#22c55e"
        elif prog >= 0.5: p_color = "#4ade80"
        elif prog >= 0.25: p_color = "#f59e0b"
        else: p_color = "#ef4444"

        pb = ctk.CTkProgressBar(p_container, width=80, height=10)
        pb.set(prog)
        pb.configure(progress_color=p_color)
        pb.pack(side="left", padx=5)
        ctk.CTkLabel(p_container, text=f"{prog*100:.0f}%", font=ctk.CTkFont(size=10, weight="bold"), width=30).pack(side="left")

        # Due Date with Color Logic
        due_date_str = loan.get('due_date', '-') or '-'
        due_col = self.get_due_color(due_date_str, loan.get('status', 'Aktif'))
        ctk.CTkLabel(row_frame, text=str(due_date_str)[:10], font=ctk.CTkFont(size=11, weight="bold"), text_color=due_col).grid(row=0, column=6, padx=10, sticky="w")

        # Status Badge
        status_text = str(loan.get('status', 'Aktif'))
        st_colors = {
            "Aktif": ("#fef3c7", "#d97706"), # Yellow
            "Lunas": ("#dcfce7", "#15803d"), # Green
            "Macet": ("#fee2e2", "#b91c1c")  # Red
        }
        bg_st, fg_st = st_colors.get(status_text, ("#374151", "#ffffff"))
        
        st_badge = ctk.CTkLabel(
            row_frame, text=status_text.upper(), 
            fg_color=bg_st, text_color=fg_st,
            font=ctk.CTkFont(size=9, weight="bold"),
            corner_radius=6, width=75, height=24
        )
        st_badge.grid(row=0, column=7, padx=10, sticky="w")

        # Actions
        a_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        a_frame.grid(row=0, column=8, padx=10, sticky="w")
        
        ctk.CTkButton(a_frame, text="👁", width=32, height=30, fg_color="#3b82f6",
                      command=lambda ld=loan: self.view_loan_details(ld)).pack(side="left", padx=2)
        if loan.get('status') != 'Lunas':
            ctk.CTkButton(a_frame, text="💵", width=32, height=30, fg_color=self.colors["success"], text_color="#000",
                          command=lambda ld=loan: self.open_payment_dialog(ld)).pack(side="left", padx=2)

    def get_due_color(self, date_str, status):
        if not date_str or date_str == '-' or status == "Lunas":
            return "#888888"
        try:
            due_date = datetime.strptime(str(date_str)[:10], '%Y-%m-%d')
            diff = (due_date.date() - datetime.now().date()).days
            if diff < 0:
                return self.colors["danger"]
            if diff < 7:
                return self.colors["accent"]
            return self.colors["success"]
        except Exception:
            return "#888888"

    def open_simulation(self):
        """Open loan simulation dialog"""
        window_key = "loan_simulation"
        if window_key in self.active_windows:
            self.active_windows[window_key].lift()
            return
        
        dialog = LoanSimulationDialog(self, self.loan_manager)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def open_add_dialog(self):
        """Open add loan dialog"""
        window_key = "add_loan"
        if window_key in self.active_windows:
            self.active_windows[window_key].lift()
            return
        
        dialog = NewLoanDialog(self, self.on_loan_saved, self.loan_manager, self.member_manager)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def open_payment_dialog(self, loan: dict):
        """Open payment dialog"""
        window_key = f"payment_{loan['id']}"
        if window_key in self.active_windows:
            self.active_windows[window_key].lift()
            return
        
        dialog = LoanPaymentDialog(self, loan, self.on_payment_saved, self.loan_manager)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def view_loan_details(self, loan: dict):
        """View loan details"""
        window_key = f"details_{loan['id']}"
        if window_key in self.active_windows:
            self.active_windows[window_key].lift()
            return
        
        dialog = LoanDetailsDialog(self, loan, self.loan_manager)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def close_window(self, window_key: str):
        """Close window safely"""
        if window_key in self.active_windows:
            win = self.active_windows[window_key]
            del self.active_windows[window_key]
            try:
                if win and win.winfo_exists():
                    win.destroy()
            except Exception:
                pass
    
    def on_loan_saved(self, data: dict):
        """Handle loan save with stay or close option"""
        try:
            is_quitting = getattr(self.winfo_toplevel(), 'is_quitting', False)
        except:
            is_quitting = False

        if is_quitting:
            self.close_window("add_loan")
            self.load_data()
            return

        if messagebox.askyesno("Sukses", "Pinjaman berhasil disimpan.\n\nApakah Anda ingin menutup jendela ini?"):
            self.close_window("add_loan")
            self.after(100, self.load_data)
        else:
            self.load_data()    
    def on_payment_saved(self, loan_id: int):
        """Handle payment save with stay or close option"""
        try:
            is_quitting = getattr(self.winfo_toplevel(), 'is_quitting', False)
        except:
            is_quitting = False

        # Determine registry key
        key = f"payment_{loan_id}"

        if is_quitting:
            self.close_window(key)
            self.load_data()
            return

        if messagebox.askyesno("Sukses", "Pembayaran berhasil dicatat.\n\nApakah Anda ingin menutup jendela ini?"):
            self.close_window(key)
            self.after(100, self.load_data)
        else:
            self.load_data()

class LoanSimulationDialog(ctk.CTkToplevel):
    """Loan simulation dialog - Pre-calculate before creating"""
    
    def __init__(self, parent, loan_manager: LoanManager):
        super().__init__(parent)
        self.loan_manager = loan_manager
        
        self.title("📊 Simulasi Pinjaman")
        self.configure(fg_color="#1a1a2e")
        self.resizable(True, True)
        self.minsize(500, 600)
        
        self.update_idletasks()
        
        window_width = 550
        window_height = 650
        x = (self.winfo_screenwidth() - window_width) // 2
        y = (self.winfo_screenheight() - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.create_content()
        self.grab_set()
    
    def create_content(self):
        """Create simulation content"""
        # Input section
        input_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=10)
        input_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        
        ctk.CTkLabel(
            input_frame, text="📊 Simulasi Pinjaman",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00d4ff"
        ).pack(pady=(15, 10))
        
        # Amount
        ctk.CTkLabel(input_frame, text="Jumlah Pinjaman (Rp)", text_color="#ccc"
                     ).pack(anchor="w", padx=30, pady=(10, 5))
        self.amount_entry = ctk.CTkEntry(input_frame, width=400, height=40, corner_radius=8)
        self.amount_entry.pack(padx=30)
        self.amount_entry.insert(0, "1000000")
        
        # Interest rate
        ctk.CTkLabel(input_frame, text="Bunga (%)", text_color="#ccc"
                     ).pack(anchor="w", padx=30, pady=(10, 5))
        self.interest_entry = ctk.CTkEntry(input_frame, width=400, height=40, corner_radius=8)
        self.interest_entry.pack(padx=30)
        self.interest_entry.insert(0, "10")
        
        # Duration
        ctk.CTkLabel(input_frame, text="Durasi (Bulan)", text_color="#ccc"
                     ).pack(anchor="w", padx=30, pady=(10, 5))
        self.duration_entry = ctk.CTkEntry(input_frame, width=400, height=40, corner_radius=8)
        self.duration_entry.pack(padx=30)
        self.duration_entry.insert(0, "12")
        
        # Calculate button
        ctk.CTkButton(
            input_frame, text="🔢 Hitung Simulasi",
            width=200, height=40,
            fg_color="#8b5cf6", hover_color="#7c3aed",
            text_color="#fff", font=ctk.CTkFont(weight="bold"),
            command=self.calculate
        ).pack(pady=20)
        
        # Result section (scrollable)
        self.result_frame = ctk.CTkScrollableFrame(self, fg_color="#16213e", corner_radius=10)
        self.result_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            self.result_frame, text="Masukkan data dan klik 'Hitung Simulasi'",
            font=ctk.CTkFont(size=12), text_color="#888"
        ).pack(pady=30)
    
    def calculate(self):
        """Calculate loan simulation"""
        try:
            amount = clean_numeric(self.amount_entry.get())
            interest = clean_numeric(self.interest_entry.get())
            duration = int(clean_numeric(self.duration_entry.get()))
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Masukkan angka yang valid!")
            return
        
        if amount <= 0 or duration <= 0:
            messagebox.showerror("Error", "Jumlah dan durasi pinjaman harus lebih dari 0!")
            return
        
        result = self.loan_manager.simulate_loan(amount, interest, duration)
        
        if not result['success']:
            messagebox.showerror("Error", result['message'])
            return
        
        self.display_result(result)
    
    def display_result(self, result: dict):
        """Display simulation result"""
        # Clear previous
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        
        # Summary header
        ctk.CTkLabel(
            self.result_frame, text="📋 Hasil Simulasi",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00d4ff"
        ).pack(pady=(10, 15))
        
        # Summary cards
        summary_frame = ctk.CTkFrame(self.result_frame, fg_color="#1e293b", corner_radius=8)
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        summary_data = [
            ("Pokok Pinjaman", f"Rp {result['principal']:,.0f}", "#ccc"),
            ("Bunga", f"{result['interest_rate']}% = Rp {result['interest_amount']:,.0f}", "#f59e0b"),
            ("Total Bayar", f"Rp {result['total_amount']:,.0f}", "#4ade80"),
            ("Cicilan/Bulan", f"Rp {result['monthly_payment']:,.0f}", "#00d4ff"),
            ("Durasi", f"{result['duration_months']} Bulan", "#ccc")
        ]
        
        for label, value, color in summary_data:
            row = ctk.CTkFrame(summary_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=5)
            
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=11),
                        text_color="#888").pack(side="left")
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=color).pack(side="right")
        
        # Breakdown header
        ctk.CTkLabel(
            self.result_frame, text="📅 Rincian Pembayaran Bulanan",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00d4ff"
        ).pack(pady=(20, 10))
        
        # Breakdown table
        for item in result['breakdown']:
            self.create_breakdown_row(item)
    
    def create_breakdown_row(self, item: dict):
        """Create breakdown row"""
        row = ctk.CTkFrame(self.result_frame, fg_color="#1e293b", corner_radius=5, height=35)
        row.pack(fill="x", padx=10, pady=2)
        row.pack_propagate(False)
        
        ctk.CTkLabel(
            row, text=f"Bulan {item['month']}",
            font=ctk.CTkFont(size=10), text_color="#ccc"
        ).pack(side="left", padx=15, pady=8)
        
        ctk.CTkLabel(
            row, text=f"Bayar: Rp {item['payment']:,.0f}",
            font=ctk.CTkFont(size=10), text_color="#4ade80"
        ).pack(side="left", padx=15, pady=8)
        
        # Progress bar
        progress = ctk.CTkProgressBar(row, width=80, height=10)
        progress.set(item['progress'] / 100)
        progress.configure(progress_color="#4ade80")
        progress.pack(side="left", padx=10, pady=10)
        
        ctk.CTkLabel(
            row, text=f"Sisa: Rp {item['remaining']:,.0f}",
            font=ctk.CTkFont(size=10), text_color="#888"
        ).pack(side="right", padx=15, pady=8)


class NewLoanDialog(ctk.CTkToplevel):
    """Dialog for creating new loan with simulation"""
    
    def __init__(self, parent, on_save, loan_manager: LoanManager, member_manager: MemberManager):
        super().__init__(parent)
        self.on_save = on_save
        self.loan_manager = loan_manager
        self.member_manager = member_manager
        self.selected_member_id = None
        
        self.title("➕ Pinjaman Baru")
        self.configure(fg_color="#1a1a2e")
        self.resizable(True, True)
        self.minsize(480, 650)
        
        self.update_idletasks()
        
        window_width = 500
        window_height = 700
        x = (self.winfo_screenwidth() - window_width) // 2
        y = (self.winfo_screenheight() - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Scrollable container
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.create_form()
        self.load_members()
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.grab_set()

    def on_closing(self):
        """Ask to save before closing if member is selected"""
        member_display = self.member_var.get()
        if member_display == "-- Pilih Anggota --":
            self.destroy()
            return

        response = messagebox.askyesnocancel("Simpan Perubahan", "Apakah Anda ingin menyimpan pinjaman ini sebelum keluar?")
        if response is True: # Yes
            self.save()
        elif response is False: # No
            self.destroy()

    def create_form(self):
        """Create loan form"""
        ctk.CTkLabel(
            self.scroll, text="➕ Buat Pinjaman Baru",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00d4ff"
        ).pack(pady=(10, 20))
        
        # Member selection
        ctk.CTkLabel(self.scroll, text="Pilih Anggota *", text_color="#ccc"
                     ).pack(anchor="w", padx=20, pady=(0, 5))
        self.member_var = ctk.StringVar(value="-- Pilih Anggota --")
        self.member_menu = ctk.CTkOptionMenu(
            self.scroll, values=["-- Pilih Anggota --"],
            variable=self.member_var, width=420, height=40,
            fg_color="#374151", button_color="#4b5563"
        )
        self.member_menu.pack(padx=20)
        
        # Amount
        ctk.CTkLabel(self.scroll, text="Jumlah Pinjaman (Rp) *", text_color="#ccc"
                     ).pack(anchor="w", padx=20, pady=(15, 5))
        self.amount_entry = ctk.CTkEntry(self.scroll, width=420, height=40, corner_radius=8)
        self.amount_entry.pack(padx=20)
        self.amount_entry.bind("<KeyRelease>", lambda e: self.update_preview())
        
        # Interest
        ctk.CTkLabel(self.scroll, text="Bunga (%)", text_color="#ccc"
                     ).pack(anchor="w", padx=20, pady=(15, 5))
        self.interest_entry = ctk.CTkEntry(self.scroll, width=420, height=40, corner_radius=8)
        self.interest_entry.pack(padx=20)
        self.interest_entry.insert(0, "10")
        self.interest_entry.bind("<KeyRelease>", lambda e: self.update_preview())
        
        # Duration
        ctk.CTkLabel(self.scroll, text="Durasi (Bulan) *", text_color="#ccc"
                     ).pack(anchor="w", padx=20, pady=(15, 5))
        self.duration_entry = ctk.CTkEntry(self.scroll, width=420, height=40, corner_radius=8)
        self.duration_entry.pack(padx=20)
        self.duration_entry.insert(0, "12")
        self.duration_entry.bind("<KeyRelease>", lambda e: self.update_preview())
        
        # Preview frame
        self.preview_frame = ctk.CTkFrame(self.scroll, fg_color="#16213e", corner_radius=10)
        self.preview_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            self.preview_frame, text="📊 Preview",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00d4ff"
        ).pack(pady=(10, 5))
        
        self.preview_label = ctk.CTkLabel(
            self.preview_frame, text="Masukkan data untuk melihat preview",
            font=ctk.CTkFont(size=11), text_color="#888",
            wraplength=380
        )
        self.preview_label.pack(pady=(0, 10))
        
        # Notes
        ctk.CTkLabel(self.scroll, text="Catatan", text_color="#ccc"
                     ).pack(anchor="w", padx=20, pady=(0, 5))
        self.notes_text = ctk.CTkTextbox(self.scroll, width=420, height=60, corner_radius=8)
        self.notes_text.pack(padx=20)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame, text="Batal", width=100, height=40,
            fg_color="#374151", hover_color="#4b5563",
            command=self.destroy
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, text="💾 Simpan", width=120, height=40,
            fg_color="#4ade80", hover_color="#22c55e",
            text_color="#000", font=ctk.CTkFont(weight="bold"),
            command=self.save
        ).pack(side="left", padx=10)
    
    def load_members(self):
        """Load members for dropdown"""
        members = self.member_manager.get_all_members()
        self.member_map = {}
        options = ["-- Pilih Anggota --"]
        
        for m in members:
            display = f"{m['name']} ({m.get('nrp', '-')})"
            options.append(display)
            self.member_map[display] = m['id']
        
        self.member_menu.configure(values=options)
    
    def update_preview(self):
        """Update loan preview calculation"""
        try:
            amount = clean_numeric(self.amount_entry.get())
            interest = clean_numeric(self.interest_entry.get())
            duration = int(clean_numeric(self.duration_entry.get()))
            
            result = self.loan_manager.simulate_loan(amount, interest, duration)
            
            if result['success']:
                preview_text = (
                    f"Pokok: Rp {result['principal']:,.0f}\n"
                    f"Bunga ({interest}%): Rp {result['interest_amount']:,.0f}\n"
                    f"Total Bayar: Rp {result['total_amount']:,.0f}\n"
                    f"Cicilan/Bulan: Rp {result['monthly_payment']:,.0f}"
                )
                self.preview_label.configure(text=preview_text, text_color="#4ade80")
            else:
                self.preview_label.configure(text=result['message'], text_color="#ef4444")
        except Exception:
            self.preview_label.configure(text="Masukkan data yang valid", text_color="#888")
    
    def save(self):
        """Save new loan - MANDATORY FIELDS"""
        try:
            is_quitting = getattr(self.winfo_toplevel(), 'is_quitting', False)
        except:
            is_quitting = False

        member_display = self.member_var.get()
        if member_display == "-- Pilih Anggota --":
            if not is_quitting:
                messagebox.showerror("Error", "Pilih anggota terlebih dahulu!")
            return
        
        member_id = self.member_map.get(member_display)
        
        try:
            amount = clean_numeric(self.amount_entry.get())
            interest = clean_numeric(self.interest_entry.get())
            duration = int(clean_numeric(self.duration_entry.get()))
        except (ValueError, TypeError):
            if not is_quitting:
                messagebox.showerror("Error", "Masukkan angka yang valid!")
            return
            
        if amount <= 0 or duration <= 0:
            if not is_quitting:
                messagebox.showerror("Data Tidak Lengkap", "Jumlah pinjaman dan durasi wajib diisi!")
            return
        
        notes = self.notes_text.get("1.0", "end-1c").strip()
        
        result = self.loan_manager.create_loan(member_id, amount, interest, duration, notes)
        
        if result['success']:
            self.on_save({'loan_id': result.get('loan_id')})
        else:
            if not is_quitting:
                messagebox.showerror("Error", result['message'])


class LoanPaymentDialog(ctk.CTkToplevel):
    """Dialog for recording loan payment"""
    
    def __init__(self, parent, loan: dict, on_save, loan_manager: LoanManager):
        super().__init__(parent)
        self.loan = loan
        self.on_save = on_save
        self.loan_manager = loan_manager
        
        self.title(f"💵 Pembayaran - {loan.get('member_name', '')}")
        self.configure(fg_color="#1a1a2e")
        self.resizable(True, True)
        self.minsize(420, 500)
        
        self.update_idletasks()
        
        window_width = 450
        window_height = 550
        x = (self.winfo_screenwidth() - window_width) // 2
        y = (self.winfo_screenheight() - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Scrollable container
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.create_form()
        self.grab_set()
    
    def create_form(self):
        """Create payment form"""
        ctk.CTkLabel(
            self.scroll, text="💵 Catat Pembayaran",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00d4ff"
        ).pack(pady=(10, 15))
        
        # Loan info
        info_frame = ctk.CTkFrame(self.scroll, fg_color="#16213e", corner_radius=10)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        remaining = self.loan.get('total_amount', 0) - self.loan.get('paid_amount', 0)
        monthly = self.loan.get('monthly_payment', 0)
        
        info_data = [
            ("Anggota", self.loan.get('member_name', '-')),
            ("Total Pinjaman", f"Rp {self.loan.get('total_amount', 0):,.0f}"),
            ("Sudah Dibayar", f"Rp {self.loan.get('paid_amount', 0):,.0f}"),
            ("Sisa", f"Rp {remaining:,.0f}"),
            ("Cicilan/Bulan", f"Rp {monthly:,.0f}")
        ]
        
        for label, value in info_data:
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=3)
            
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=11),
                        text_color="#888").pack(side="left")
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=11, weight="bold"),
                        text_color="#4ade80").pack(side="right")
        
        # Payment amount
        ctk.CTkLabel(self.scroll, text="Jumlah Bayar (Rp) *", text_color="#ccc"
                     ).pack(anchor="w", padx=20, pady=(20, 5))
        self.amount_entry = ctk.CTkEntry(self.scroll, width=380, height=40, corner_radius=8)
        self.amount_entry.pack(padx=20)
        self.amount_entry.insert(0, str(int(monthly)))
        
        # Quick fill buttons
        quick_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        quick_frame.pack(pady=10)
        
        ctk.CTkButton(
            quick_frame, text="1 Cicilan", width=90, height=30,
            fg_color="#374151", hover_color="#4b5563",
            command=lambda: self.set_amount(monthly)
        ).pack(side="left", padx=3)
        
        ctk.CTkButton(
            quick_frame, text="3 Cicilan", width=90, height=30,
            fg_color="#374151", hover_color="#4b5563",
            command=lambda: self.set_amount(monthly * 3)
        ).pack(side="left", padx=3)
        
        ctk.CTkButton(
            quick_frame, text="Lunas", width=90, height=30,
            fg_color="#4ade80", hover_color="#22c55e",
            text_color="#000",
            command=lambda: self.set_amount(remaining)
        ).pack(side="left", padx=3)
        
        # Payment method
        ctk.CTkLabel(self.scroll, text="Metode Pembayaran", text_color="#ccc"
                     ).pack(anchor="w", padx=20, pady=(15, 5))
        
        method_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        method_frame.pack(padx=20)
        
        self.method_var = ctk.StringVar(value="Tunai")
        for method in ["Tunai", "Kredit", "QRIS"]:
            ctk.CTkRadioButton(
                method_frame, text=method, variable=self.method_var,
                value=method, fg_color="#4ade80", hover_color="#22c55e"
            ).pack(side="left", padx=10)
        
        # Notes
        ctk.CTkLabel(self.scroll, text="Catatan", text_color="#ccc"
                     ).pack(anchor="w", padx=20, pady=(15, 5))
        self.notes_text = ctk.CTkTextbox(self.scroll, width=380, height=50, corner_radius=8)
        self.notes_text.pack(padx=20)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_frame.pack(pady=25)
        
        ctk.CTkButton(
            btn_frame, text="Batal", width=100, height=40,
            fg_color="#374151", hover_color="#4b5563",
            command=self.destroy
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, text="💾 Simpan", width=120, height=40,
            fg_color="#4ade80", hover_color="#22c55e",
            text_color="#000", font=ctk.CTkFont(weight="bold"),
            command=self.save
        ).pack(side="left", padx=10)
    
    def set_amount(self, amount: float):
        """Set payment amount"""
        self.amount_entry.delete(0, "end")
        self.amount_entry.insert(0, str(int(amount)))
    
    def save(self):
        """Save payment - MANDATORY AMOUNT"""
        try:
            is_quitting = getattr(self.winfo_toplevel(), 'is_quitting', False)
        except:
            is_quitting = False

        try:
            amount = clean_numeric(self.amount_entry.get())
        except (ValueError, TypeError):
            if not is_quitting:
                messagebox.showerror("Error", "Masukkan jumlah yang valid!")
            return
        
        if amount <= 0:
            if not is_quitting:
                messagebox.showerror("Error", "Jumlah pembayaran harus lebih dari 0!")
            return
        
        method = self.method_var.get()
        notes = self.notes_text.get("1.0", "end-1c").strip()
        
        result = self.loan_manager.record_payment(self.loan['id'], amount, method, notes)
        
        if result['success']:
            self.on_save(self.loan['id'])
        else:
            if not is_quitting:
                messagebox.showerror("Error", result['message'])


class LoanDetailsDialog(ctk.CTkToplevel):
    """Dialog for viewing loan details and payment history"""
    
    def __init__(self, parent, loan: dict, loan_manager: LoanManager):
        super().__init__(parent)
        self.loan = loan
        self.loan_manager = loan_manager
        
        self.title(f"📋 Detail Pinjaman - {loan.get('member_name', '')}")
        self.configure(fg_color="#1a1a2e")
        self.resizable(True, True)
        self.minsize(550, 500)
        
        self.update_idletasks()
        
        window_width = 600
        window_height = 550
        x = (self.winfo_screenwidth() - window_width) // 2
        y = (self.winfo_screenheight() - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Scrollable container
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.create_content()
        self.grab_set()
    
    def create_content(self):
        """Create detail content"""
        ctk.CTkLabel(
            self.scroll, text="📋 Detail Pinjaman",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00d4ff"
        ).pack(pady=(10, 15))
        
        # Loan summary
        summary_frame = ctk.CTkFrame(self.scroll, fg_color="#16213e", corner_radius=10)
        summary_frame.pack(fill="x", padx=20, pady=10)
        
        total = self.loan.get('total_amount', 0)
        paid = self.loan.get('paid_amount', 0)
        remaining = total - paid
        progress = (paid / total * 100) if total > 0 else 0
        
        summary_data = [
            ("Anggota", self.loan.get('member_name', '-'), "#fff"),
            ("Telepon", self.loan.get('member_phone', '-') or '-', "#00d4ff"),
            ("Pokok", f"Rp {self.loan.get('principal', 0):,.0f}", "#ccc"),
            ("Bunga", f"{self.loan.get('interest_rate', 0)}%", "#ccc"),
            ("Total", f"Rp {total:,.0f}", "#f59e0b"),
            ("Sudah Bayar", f"Rp {paid:,.0f}", "#4ade80"),
            ("Sisa", f"Rp {remaining:,.0f}", "#ef4444" if remaining > 0 else "#4ade80"),
            ("Status", self.loan.get('status', '-'), "#4ade80" if self.loan.get('status') == 'Lunas' else "#f59e0b")
        ]
        
        for label, value, color in summary_data:
            row = ctk.CTkFrame(summary_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=3)
            
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=11),
                        text_color="#888").pack(side="left")
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=color).pack(side="right")
        
        # Progress bar
        ctk.CTkLabel(
            self.scroll, text=f"Progress Pembayaran: {progress:.1f}%",
            font=ctk.CTkFont(size=12), text_color="#ccc"
        ).pack(pady=(15, 5))
        
        progress_bar = ctk.CTkProgressBar(self.scroll, width=500, height=20)
        progress_bar.set(progress / 100)
        progress_bar.configure(progress_color="#4ade80")
        progress_bar.pack(pady=5)
        
        # Payment history
        ctk.CTkLabel(
            self.scroll, text="📜 Riwayat Pembayaran",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00d4ff"
        ).pack(pady=(20, 10))
        
        payments = self.loan_manager.get_loan_payments(self.loan['id'])
        
        if not payments:
            ctk.CTkLabel(
                self.scroll, text="Belum ada pembayaran",
                font=ctk.CTkFont(size=11), text_color="#888"
            ).pack(pady=20)
        else:
            for idx, payment in enumerate(payments):
                self.create_payment_row(idx, payment)
    
    def create_payment_row(self, idx: int, payment: dict):
        """Create payment history row"""
        bg = "#1e293b" if idx % 2 == 0 else "#16213e"
        
        row = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=5, height=40)
        row.pack(fill="x", padx=20, pady=2)
        row.pack_propagate(False)
        
        date = payment.get('payment_date', '')[:10] if payment.get('payment_date') else '-'
        ctk.CTkLabel(row, text=date, font=ctk.CTkFont(size=10),
                    text_color="#888").pack(side="left", padx=15, pady=10)
        
        ctk.CTkLabel(row, text=f"Rp {payment.get('amount', 0):,.0f}",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color="#4ade80").pack(side="left", padx=15, pady=10)
        
        method = payment.get('payment_method', 'Tunai')
        ctk.CTkLabel(row, text=method, font=ctk.CTkFont(size=10),
                    text_color="#00d4ff").pack(side="left", padx=15, pady=10)
        
        notes = payment.get('notes', '-')[:30] if payment.get('notes') else '-'
        ctk.CTkLabel(row, text=notes, font=ctk.CTkFont(size=10),
                    text_color="#888").pack(side="right", padx=15, pady=10)
