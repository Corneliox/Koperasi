"""
Loans Frame - Loan Management with Simulation Engine & Visualizations
REFACTORED Phase 3: Added simulation, progress bars, due date color coding, phone display
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from app.modules.loans import LoanManager
from app.modules.members import MemberManager


class LoansFrame(ctk.CTkFrame):
    """Loan management frame with simulation and visualizations"""
    
    def __init__(self, master, current_user: str):
        super().__init__(master)
        self.current_user = current_user
        self.loan_manager = LoanManager(current_user)
        self.member_manager = MemberManager(current_user)
        
        self.active_windows = {}
        
        self.configure(fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self.create_header()
        self.create_stats_bar()
        self.create_table()
        self.load_data()
    
    def create_header(self):
        """Create header section"""
        self.header_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=15)
        
        ctk.CTkLabel(
            title_frame, text="💰 Manajemen Pinjaman",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00d4ff"
        ).pack(side="left")
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=20, pady=10)
        
        # Filter dropdown
        self.status_var = ctk.StringVar(value="Semua")
        ctk.CTkOptionMenu(
            btn_frame, values=["Semua", "Aktif", "Lunas"],
            variable=self.status_var, width=100, height=35,
            fg_color="#374151", button_color="#4b5563",
            command=lambda v: self.load_data()
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, text="🔄 Refresh", width=100, height=35,
            fg_color="#374151", hover_color="#4b5563",
            corner_radius=8, command=self.load_data
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, text="📊 Simulasi", width=100, height=35,
            fg_color="#8b5cf6", hover_color="#7c3aed",
            corner_radius=8, command=self.open_simulation
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, text="➕ Pinjaman Baru", width=150, height=35,
            fg_color="#4ade80", hover_color="#22c55e",
            text_color="#000000", corner_radius=8,
            command=self.open_add_dialog
        ).pack(side="left", padx=5)
    
    def create_stats_bar(self):
        """Create statistics bar showing loan summary"""
        self.stats_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=10, height=50)
        self.stats_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.stats_frame.grid_propagate(False)
        
        self.total_loans_label = ctk.CTkLabel(
            self.stats_frame, text="Total Pinjaman: 0",
            font=ctk.CTkFont(size=12), text_color="#ccc"
        )
        self.total_loans_label.pack(side="left", padx=20, pady=10)
        
        self.active_loans_label = ctk.CTkLabel(
            self.stats_frame, text="Aktif: 0",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#f59e0b"
        )
        self.active_loans_label.pack(side="left", padx=20, pady=10)
        
        self.near_due_label = ctk.CTkLabel(
            self.stats_frame, text="⚠️ Hampir Jatuh Tempo: 0",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#ef4444"
        )
        self.near_due_label.pack(side="left", padx=20, pady=10)
        
        self.total_amount_label = ctk.CTkLabel(
            self.stats_frame, text="Total Outstanding: Rp 0",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#4ade80"
        )
        self.total_amount_label.pack(side="right", padx=20, pady=10)
    
    def create_table(self):
        """Create loans table with phone and progress visualization"""
        self.table_container = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.table_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=1)
        
        # Header row
        self.header_row = ctk.CTkFrame(self.table_container, fg_color="#16213e", height=45)
        self.header_row.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header_row.grid_propagate(False)
        
        # Columns: ID, Nama, Telepon, Jumlah, Bunga, Total, Cicilan/bln, Progress, Jatuh Tempo, Status, Aksi
        columns = [
            ("ID", 45), ("Nama", 130), ("Telepon", 100), ("Pokok", 90),
            ("Bunga", 55), ("Total", 95), ("Cicilan", 80), ("Progress", 100),
            ("Jatuh Tempo", 90), ("Status", 65), ("Aksi", 100)
        ]
        
        for i, (text, width) in enumerate(columns):
            self.header_row.grid_columnconfigure(i, minsize=width)
            ctk.CTkLabel(
                self.header_row, text=text, width=width,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#00d4ff"
            ).grid(row=0, column=i, padx=3, pady=10, sticky="w")
        
        # Scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.table_container, fg_color="transparent"
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        for i, (_, width) in enumerate(columns):
            self.scroll_frame.grid_columnconfigure(i, minsize=width)
    
    def load_data(self):
        """Load loans into table"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        status_filter = self.status_var.get()
        status = None if status_filter == "Semua" else status_filter
        
        # Use new method with phone
        loans = self.loan_manager.get_all_loans_with_phone(status)
        near_due = self.loan_manager.get_near_due_loans(days=14)
        
        # Update stats
        active_loans = [loan for loan in loans if loan.get('status') == 'Aktif']
        total_amount = sum(loan.get('total_amount', 0) for loan in active_loans)
        
        self.total_loans_label.configure(text=f"Total Pinjaman: {len(loans)}")
        self.active_loans_label.configure(text=f"Aktif: {len(active_loans)}")
        self.near_due_label.configure(text=f"⚠️ Hampir Jatuh Tempo: {len(near_due)}")
        self.total_amount_label.configure(text=f"Total Outstanding: Rp {total_amount:,.0f}")
        
        if not loans:
            ctk.CTkLabel(
                self.scroll_frame, text="Tidak ada data pinjaman",
                font=ctk.CTkFont(size=14), text_color="#888888"
            ).grid(row=0, column=0, columnspan=11, pady=50)
            return
        
        for idx, loan in enumerate(loans):
            self.create_row(idx, loan)
    
    def get_due_color(self, due_date_str: str, status: str) -> str:
        """Get color based on due date proximity"""
        if status != "Aktif" or not due_date_str:
            return "#888"
        
        try:
            due_date = datetime.strptime(due_date_str[:10], '%Y-%m-%d').date()
            today = datetime.now().date()
            days_until = (due_date - today).days
            
            if days_until < 3:
                return "#ef4444"  # Red - < 3 days
            elif days_until <= 14:
                return "#f59e0b"  # Yellow - 7-14 days
            else:
                return "#4ade80"  # Green - > 14 days
        except Exception:
            return "#888"
    
    def create_row(self, row_idx: int, loan: dict):
        """Create a loan row with progress visualization"""
        bg_color = "#1e293b" if row_idx % 2 == 0 else "#16213e"
        
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, height=50, corner_radius=5)
        row_frame.grid(row=row_idx, column=0, columnspan=11, sticky="ew", pady=1)
        row_frame.grid_propagate(False)
        
        widths = [45, 130, 100, 90, 55, 95, 80, 100, 90, 65, 100]
        for i, width in enumerate(widths):
            row_frame.grid_columnconfigure(i, minsize=width)
        
        # ID
        ctk.CTkLabel(row_frame, text=str(loan['id']), width=widths[0],
                     font=ctk.CTkFont(size=10), text_color="#cccccc"
                     ).grid(row=0, column=0, padx=3, pady=12, sticky="w")
        
        # Member name
        member_name = loan.get('member_name', '-')[:18]
        ctk.CTkLabel(row_frame, text=member_name, width=widths[1],
                     font=ctk.CTkFont(size=10), text_color="#ffffff"
                     ).grid(row=0, column=1, padx=3, pady=12, sticky="w")
        
        # Phone (NEW)
        phone = loan.get('member_phone', '-') or '-'
        ctk.CTkLabel(row_frame, text=phone[:12], width=widths[2],
                     font=ctk.CTkFont(size=10), text_color="#00d4ff"
                     ).grid(row=0, column=2, padx=3, pady=12, sticky="w")
        
        # Principal
        principal = loan.get('principal', 0)
        ctk.CTkLabel(row_frame, text=f"Rp {principal:,.0f}", width=widths[3],
                     font=ctk.CTkFont(size=10), text_color="#cccccc"
                     ).grid(row=0, column=3, padx=3, pady=12, sticky="w")
        
        # Interest rate
        interest = loan.get('interest_rate', 0)
        ctk.CTkLabel(row_frame, text=f"{interest}%", width=widths[4],
                     font=ctk.CTkFont(size=10), text_color="#cccccc"
                     ).grid(row=0, column=4, padx=3, pady=12, sticky="w")
        
        # Total
        total = loan.get('total_amount', 0)
        ctk.CTkLabel(row_frame, text=f"Rp {total:,.0f}", width=widths[5],
                     font=ctk.CTkFont(size=10, weight="bold"), text_color="#f59e0b"
                     ).grid(row=0, column=5, padx=3, pady=12, sticky="w")
        
        # Monthly payment
        monthly = loan.get('monthly_payment', 0)
        ctk.CTkLabel(row_frame, text=f"Rp {monthly:,.0f}", width=widths[6],
                     font=ctk.CTkFont(size=10), text_color="#cccccc"
                     ).grid(row=0, column=6, padx=3, pady=12, sticky="w")
        
        # Progress bar (NEW)
        progress_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=widths[7])
        progress_frame.grid(row=0, column=7, padx=3, pady=8, sticky="w")
        
        paid = loan.get('paid_amount', 0)
        progress_pct = (paid / total * 100) if total > 0 else 0
        
        progress_bar = ctk.CTkProgressBar(progress_frame, width=70, height=12)
        progress_bar.set(progress_pct / 100)
        progress_bar.configure(progress_color="#4ade80" if progress_pct >= 50 else "#f59e0b")
        progress_bar.pack(side="left")
        
        ctk.CTkLabel(progress_frame, text=f"{progress_pct:.0f}%", width=25,
                     font=ctk.CTkFont(size=9), text_color="#ccc"
                     ).pack(side="left", padx=2)
        
        # Due date with color coding (NEW)
        due_date = loan.get('due_date', '-')
        due_display = due_date[:10] if due_date else '-'
        due_color = self.get_due_color(due_date, loan.get('status', ''))
        
        ctk.CTkLabel(row_frame, text=due_display, width=widths[8],
                     font=ctk.CTkFont(size=10, weight="bold"), text_color=due_color
                     ).grid(row=0, column=8, padx=3, pady=12, sticky="w")
        
        # Status
        status = loan.get('status', 'Aktif')
        status_color = "#4ade80" if status == "Lunas" else "#f59e0b"
        ctk.CTkLabel(row_frame, text=status, width=widths[9],
                     font=ctk.CTkFont(size=10, weight="bold"), text_color=status_color
                     ).grid(row=0, column=9, padx=3, pady=12, sticky="w")
        
        # Action buttons
        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=widths[10])
        action_frame.grid(row=0, column=10, padx=3, pady=8, sticky="w")
        
        if status == "Aktif":
            ctk.CTkButton(
                action_frame, text="💵", width=30, height=28,
                fg_color="#4ade80", hover_color="#22c55e",
                text_color="#000", corner_radius=5,
                command=lambda loan_data=loan: self.open_payment_dialog(loan_data)
            ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            action_frame, text="👁", width=30, height=28,
            fg_color="#3b82f6", hover_color="#2563eb",
            corner_radius=5,
            command=lambda loan_data=loan: self.view_loan_details(loan_data)
        ).pack(side="left", padx=2)
    
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
        """Close window"""
        if window_key in self.active_windows:
            self.active_windows[window_key].destroy()
            del self.active_windows[window_key]
    
    def on_loan_saved(self, data: dict):
        """Handle loan save"""
        self.close_window("add_loan")
        self.load_data()
    
    def on_payment_saved(self, loan_id: int):
        """Handle payment save"""
        self.close_window(f"payment_{loan_id}")
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
            amount = float(self.amount_entry.get().replace(',', '').replace('.', ''))
            interest = float(self.interest_entry.get())
            duration = int(self.duration_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Masukkan angka yang valid!")
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
        self.grab_set()
    
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
        ctk.CTkLabel(self.scroll, text="Durasi (Bulan)", text_color="#ccc"
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
            amount = float(self.amount_entry.get().replace(',', '').replace('.', ''))
            interest = float(self.interest_entry.get())
            duration = int(self.duration_entry.get())
            
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
        """Save new loan"""
        member_display = self.member_var.get()
        if member_display == "-- Pilih Anggota --":
            messagebox.showerror("Error", "Pilih anggota terlebih dahulu!")
            return
        
        member_id = self.member_map.get(member_display)
        
        try:
            amount = float(self.amount_entry.get().replace(',', '').replace('.', ''))
            interest = float(self.interest_entry.get())
            duration = int(self.duration_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Masukkan angka yang valid!")
            return
        
        notes = self.notes_text.get("1.0", "end-1c").strip()
        
        result = self.loan_manager.create_loan(member_id, amount, interest, duration, notes)
        
        if result['success']:
            messagebox.showinfo("Sukses", f"Pinjaman berhasil dibuat!\n\n{result.get('message', '')}")
            self.on_save({'loan_id': result.get('loan_id')})
        else:
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
        for method in ["Tunai", "Transfer", "QRIS"]:
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
        """Save payment"""
        try:
            amount = float(self.amount_entry.get().replace(',', '').replace('.', ''))
        except ValueError:
            messagebox.showerror("Error", "Masukkan jumlah yang valid!")
            return
        
        if amount <= 0:
            messagebox.showerror("Error", "Jumlah harus lebih dari 0!")
            return
        
        method = self.method_var.get()
        notes = self.notes_text.get("1.0", "end-1c").strip()
        
        result = self.loan_manager.record_payment(self.loan['id'], amount, method, notes)
        
        if result['success']:
            messagebox.showinfo("Sukses", result['message'])
            self.on_save(self.loan['id'])
        else:
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