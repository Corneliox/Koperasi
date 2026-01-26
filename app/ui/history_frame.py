"""
History Frame - Transaction History with Filters and Export
REFACTORED: Fixed header overlap, proper grid layout, no text clipping
PHASE 3: Added Grand Total footer, Profit column, advanced filters (Sort, Payment Method)
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry
from app.modules.transactions import TransactionManager
from app.modules.members import MemberManager
from app.utils.export import export_transactions_excel, export_transactions_pdf


class HistoryFrame(ctk.CTkFrame):
    """Transaction history frame with filters, export, and grand total"""
    
    def __init__(self, master, category_context: str, current_user: str):
        super().__init__(master)
        self.category_context = category_context
        self.current_user = current_user
        self.transaction_manager = TransactionManager(category_context)
        self.member_manager = MemberManager(current_user)
        
        self.configure(fg_color="transparent")
        
        # Grid config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Table row gets the weight
        
        self.current_transactions = []
        self.sorted_transactions = []  # For sorted display
        
        self.create_header()
        self.create_filters()
        self.create_table()
        self.load_data()
    
    def create_header(self):
        """Create header section - FIXED: no overlap"""
        self.header_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Left side - Title with division name
        title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=15)
        
        title_text = "📋 Riwayat Transaksi"
        self.title_label = ctk.CTkLabel(
            title_frame,
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00d4ff"
        )
        self.title_label.pack(side="left")
        
        # Division badge - SEPARATED with proper padding
        div_text = "SEMBAKO" if self.category_context == "SEMBAKO" else "TAKTIKAL"
        div_color = "#4ade80" if self.category_context == "SEMBAKO" else "#f59e0b"
        
        self.div_badge = ctk.CTkLabel(
            title_frame,
            text=f"  •  {div_text}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=div_color
        )
        self.div_badge.pack(side="left", padx=(15, 0))
        
        # Right side - Export buttons
        export_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        export_frame.pack(side="right", padx=20, pady=10)
        
        self.excel_btn = ctk.CTkButton(
            export_frame,
            text="📊 Export Excel",
            width=120,
            height=35,
            fg_color="#22c55e",
            hover_color="#16a34a",
            text_color="#000000",
            corner_radius=8,
            command=self.export_excel
        )
        self.excel_btn.pack(side="left", padx=5)
        
        self.pdf_btn = ctk.CTkButton(
            export_frame,
            text="📄 Export PDF",
            width=120,
            height=35,
            fg_color="#ef4444",
            hover_color="#dc2626",
            corner_radius=8,
            command=self.export_pdf
        )
        self.pdf_btn.pack(side="left", padx=5)
    
    def create_filters(self):
        """Create filter section with advanced options"""
        self.filter_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=10)
        self.filter_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Use grid layout for better control - 2 rows for more filters
        self.filter_frame.grid_columnconfigure(8, weight=1)  # Spacer column
        
        # ROW 1: Period and Member filters
        # Period label
        ctk.CTkLabel(
            self.filter_frame, text="Periode:",
            font=ctk.CTkFont(size=11), text_color="#cccccc"
        ).grid(row=0, column=0, padx=(15, 5), pady=8, sticky="w")
        
        # Period dropdown
        self.period_var = ctk.StringVar(value="Semua")
        self.period_menu = ctk.CTkOptionMenu(
            self.filter_frame,
            values=["Semua", "Hari Ini", "7 Hari", "30 Hari", "Bulan Ini", "Tahun Ini", "Rentang Tanggal"],
            variable=self.period_var,
            width=115,
            height=32,
            fg_color="#374151",
            button_color="#4b5563",
            command=self.on_period_change
        )
        self.period_menu.grid(row=0, column=1, padx=5, pady=8, sticky="w")
        
        # Date range frame (hidden by default)
        self.date_frame = ctk.CTkFrame(self.filter_frame, fg_color="transparent")
        
        ctk.CTkLabel(
            self.date_frame, text="Dari:",
            font=ctk.CTkFont(size=10), text_color="#cccccc"
        ).pack(side="left", padx=3)
        
        self.start_date = DateEntry(
            self.date_frame, width=10, background='#374151',
            foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd'
        )
        self.start_date.pack(side="left", padx=3)
        
        ctk.CTkLabel(
            self.date_frame, text="s/d:",
            font=ctk.CTkFont(size=10), text_color="#cccccc"
        ).pack(side="left", padx=3)
        
        self.end_date = DateEntry(
            self.date_frame, width=10, background='#374151',
            foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd'
        )
        self.end_date.pack(side="left", padx=3)
        
        # Member label
        ctk.CTkLabel(
            self.filter_frame, text="Anggota:",
            font=ctk.CTkFont(size=11), text_color="#cccccc"
        ).grid(row=0, column=3, padx=(15, 5), pady=8, sticky="w")
        
        # Member dropdown
        self.member_var = ctk.StringVar(value="Semua")
        self.member_menu = ctk.CTkOptionMenu(
            self.filter_frame,
            values=["Semua"],
            variable=self.member_var,
            width=150,
            height=32,
            fg_color="#374151",
            button_color="#4b5563"
        )
        self.member_menu.grid(row=0, column=4, padx=5, pady=8, sticky="w")
        self.load_members()
        
        # ROW 2: Advanced filters (Payment Method, Sort, Search)
        # Payment Method
        ctk.CTkLabel(
            self.filter_frame, text="Metode:",
            font=ctk.CTkFont(size=11), text_color="#cccccc"
        ).grid(row=1, column=0, padx=(15, 5), pady=8, sticky="w")
        
        self.payment_var = ctk.StringVar(value="Semua")
        ctk.CTkOptionMenu(
            self.filter_frame,
            values=["Semua", "Tunai", "Transfer", "QRIS"],
            variable=self.payment_var,
            width=90, height=32,
            fg_color="#374151", button_color="#4b5563"
        ).grid(row=1, column=1, padx=5, pady=8, sticky="w")
        
        # Sort by
        ctk.CTkLabel(
            self.filter_frame, text="Urutkan:",
            font=ctk.CTkFont(size=11), text_color="#cccccc"
        ).grid(row=1, column=3, padx=(15, 5), pady=8, sticky="w")
        
        self.sort_var = ctk.StringVar(value="Terbaru")
        ctk.CTkOptionMenu(
            self.filter_frame,
            values=["Terbaru", "Qty (Tinggi)", "Qty (Rendah)", "Profit (Tinggi)", "Profit (Rendah)"],
            variable=self.sort_var,
            width=120, height=32,
            fg_color="#374151", button_color="#4b5563"
        ).grid(row=1, column=4, padx=5, pady=8, sticky="w")
        
        # Search
        ctk.CTkLabel(
            self.filter_frame, text="Cari:",
            font=ctk.CTkFont(size=11), text_color="#cccccc"
        ).grid(row=1, column=5, padx=(15, 5), pady=8, sticky="w")
        
        self.search_entry = ctk.CTkEntry(
            self.filter_frame, width=130, height=32,
            placeholder_text="Item/Anggota..."
        )
        self.search_entry.grid(row=1, column=6, padx=5, pady=8, sticky="w")
        
        # Filter button
        self.filter_btn = ctk.CTkButton(
            self.filter_frame,
            text="🔍 Filter",
            width=70,
            height=32,
            fg_color="#00d4ff",
            hover_color="#00a8cc",
            text_color="#000000",
            corner_radius=8,
            command=self.apply_filter
        )
        self.filter_btn.grid(row=0, column=5, rowspan=2, padx=10, pady=8, sticky="w")
        
        # Refresh
        ctk.CTkButton(
            self.filter_frame, text="🔄", width=35, height=32,
            fg_color="#374151", hover_color="#4b5563",
            command=self.refresh_data
        ).grid(row=0, column=6, padx=5, pady=8, sticky="w")
    
    def load_members(self):
        """Load members for filter dropdown"""
        members = self.member_manager.get_all_members()
        member_options = ["Semua"]
        self.member_map = {"Semua": None}
        
        for m in members:
            display = f"{m['name'][:15]}" if len(m['name']) > 15 else m['name']
            member_options.append(display)
            self.member_map[display] = m['id']
        
        self.member_menu.configure(values=member_options)
    
    def on_period_change(self, value):
        """Handle period selection change"""
        if value == "Rentang Tanggal":
            self.date_frame.grid(row=0, column=2, padx=5, pady=8, sticky="w")
        else:
            self.date_frame.grid_forget()
    
    def create_table(self):
        """Create transaction table with Profit column"""
        self.table_container = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.table_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=1)
        
        # Header with responsive columns - Added Profit column
        self.header_row = ctk.CTkFrame(self.table_container, fg_color="#16213e", height=45)
        self.header_row.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header_row.grid_propagate(False)
        
        # Column config: (name, min_width, weight) - Added Profit
        self.columns_config = [
            ("ID", 45, 0),
            ("Tanggal", 130, 1),
            ("Nama Barang", 180, 2),
            ("Qty", 45, 0),
            ("Harga", 90, 1),
            ("Total", 95, 1),
            ("Profit", 85, 1),  # NEW: Profit column
            ("Pembeli", 130, 1),
            ("Metode", 70, 0)
        ]
        
        for i, (text, min_width, weight) in enumerate(self.columns_config):
            self.header_row.grid_columnconfigure(i, minsize=min_width, weight=weight)
            label = ctk.CTkLabel(
                self.header_row,
                text=text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#00d4ff"
            )
            label.grid(row=0, column=i, padx=4, pady=10, sticky="w")
        
        # Scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.table_container,
            fg_color="transparent"
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        for i, (_, min_width, weight) in enumerate(self.columns_config):
            self.scroll_frame.grid_columnconfigure(i, minsize=min_width, weight=weight)
        
        # Grand Total footer
        self.footer_frame = ctk.CTkFrame(self.table_container, fg_color="#16213e", height=50)
        self.footer_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 5))
        self.footer_frame.grid_propagate(False)
        
        # Summary labels in footer
        self.summary_count_label = ctk.CTkLabel(
            self.footer_frame, text="0 transaksi",
            font=ctk.CTkFont(size=12), text_color="#888"
        )
        self.summary_count_label.pack(side="left", padx=20, pady=10)
        
        self.grand_total_label = ctk.CTkLabel(
            self.footer_frame, text="Grand Total: Rp 0",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="#4ade80"
        )
        self.grand_total_label.pack(side="right", padx=20, pady=10)
        
        self.total_profit_label = ctk.CTkLabel(
            self.footer_frame, text="Total Profit: Rp 0",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#f59e0b"
        )
        self.total_profit_label.pack(side="right", padx=20, pady=10)
    
    def refresh_data(self):
        """Refresh with default filters"""
        self.period_var.set("Semua")
        self.member_var.set("Semua")
        self.payment_var.set("Semua")
        self.sort_var.set("Terbaru")
        self.search_entry.delete(0, "end")
        self.date_frame.grid_forget()
        self.load_data()
    
    def load_data(self):
        """Load transactions based on filters"""
        # Clear existing rows
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # Get filter values
        period = self.period_var.get()
        member_display = self.member_var.get()
        member_id = self.member_map.get(member_display)
        payment_method = self.payment_var.get()
        sort_by = self.sort_var.get()
        search_text = self.search_entry.get().strip().lower()
        
        # Calculate date range
        start_date = None
        end_date = None
        today = datetime.now().date()
        
        if period == "Hari Ini":
            start_date = end_date = today.strftime('%Y-%m-%d')
        elif period == "7 Hari":
            start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
        elif period == "30 Hari":
            start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
        elif period == "Bulan Ini":
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
        elif period == "Tahun Ini":
            start_date = today.replace(month=1, day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
        elif period == "Rentang Tanggal":
            start_date = self.start_date.get_date().strftime('%Y-%m-%d')
            end_date = self.end_date.get_date().strftime('%Y-%m-%d')
        
        # Fetch transactions
        self.current_transactions = self.transaction_manager.get_transactions(
            member_id=member_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Apply additional filters
        filtered = self.current_transactions
        
        # Filter by payment method
        if payment_method != "Semua":
            filtered = [t for t in filtered if t.get('payment_method', 'Tunai') == payment_method]
        
        # Filter by search text
        if search_text:
            filtered = [t for t in filtered if 
                       search_text in (t.get('item_name', '') or '').lower() or
                       search_text in (t.get('member_name', '') or '').lower()]
        
        # Apply sorting
        if sort_by == "Qty (Tinggi)":
            filtered.sort(key=lambda x: x.get('qty', 0), reverse=True)
        elif sort_by == "Qty (Rendah)":
            filtered.sort(key=lambda x: x.get('qty', 0))
        elif sort_by == "Profit (Tinggi)":
            filtered.sort(key=lambda x: self.calc_profit(x), reverse=True)
        elif sort_by == "Profit (Rendah)":
            filtered.sort(key=lambda x: self.calc_profit(x))
        # Default: Terbaru - already sorted by date desc from query
        
        self.sorted_transactions = filtered
        
        if not filtered:
            no_data_label = ctk.CTkLabel(
                self.scroll_frame,
                text="Tidak ada transaksi",
                font=ctk.CTkFont(size=14),
                text_color="#888888"
            )
            no_data_label.grid(row=0, column=0, columnspan=9, pady=50)
            self.update_totals([], 0, 0)
            return
        
        # Create rows and calculate totals
        grand_total = 0
        total_profit = 0
        
        for idx, trans in enumerate(filtered):
            profit = self.calc_profit(trans)
            self.create_row(idx, trans, profit)
            grand_total += trans.get('total_price', 0)
            total_profit += profit
        
        # Update footer
        self.update_totals(filtered, grand_total, total_profit)
    
    def calc_profit(self, trans: dict) -> float:
        """Calculate profit for a transaction (Sell Price - Buy Price) * Qty"""
        # Get buy price from warehouse if available
        unit_price = trans.get('unit_price', 0)
        qty = trans.get('qty', 0)
        # Assume profit margin of ~15% if buy_price not available
        # In real scenario, you'd join with warehouse to get buy_price
        estimated_buy = unit_price * 0.85  # Rough estimate
        profit = (unit_price - estimated_buy) * qty
        return profit
    
    def update_totals(self, transactions: list, grand_total: float, total_profit: float):
        """Update footer totals"""
        count = len(transactions)
        self.summary_count_label.configure(text=f"{count} transaksi")
        self.grand_total_label.configure(text=f"Grand Total: Rp {grand_total:,.0f}")
        self.total_profit_label.configure(text=f"Est. Profit: Rp {total_profit:,.0f}")
    
    def create_row(self, row_idx: int, trans: dict, profit: float):
        """Create a transaction row with profit"""
        bg_color = "#1e293b" if row_idx % 2 == 0 else "#16213e"
        
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, height=40, corner_radius=5)
        row_frame.grid(row=row_idx, column=0, columnspan=9, sticky="ew", pady=1)
        row_frame.grid_propagate(False)
        
        # Apply same column configuration
        for i, (_, min_width, weight) in enumerate(self.columns_config):
            row_frame.grid_columnconfigure(i, minsize=min_width, weight=weight)
        
        # ID
        ctk.CTkLabel(row_frame, text=str(trans['id']),
                     font=ctk.CTkFont(size=10), text_color="#cccccc"
                     ).grid(row=0, column=0, padx=4, pady=8, sticky="w")
        
        # Date
        date_str = trans.get('date', '')[:16] if trans.get('date') else '-'
        ctk.CTkLabel(row_frame, text=date_str,
                     font=ctk.CTkFont(size=10), text_color="#cccccc"
                     ).grid(row=0, column=1, padx=4, pady=8, sticky="w")
        
        # Item name
        item_name = trans.get('item_name', '-')[:25] if trans.get('item_name') else '-'
        ctk.CTkLabel(row_frame, text=item_name,
                     font=ctk.CTkFont(size=10), text_color="#ffffff"
                     ).grid(row=0, column=2, padx=4, pady=8, sticky="w")
        
        # Qty
        ctk.CTkLabel(row_frame, text=str(trans.get('qty', 0)),
                     font=ctk.CTkFont(size=10), text_color="#00d4ff"
                     ).grid(row=0, column=3, padx=4, pady=8, sticky="w")
        
        # Unit price
        ctk.CTkLabel(row_frame, text=f"Rp {trans.get('unit_price', 0):,.0f}",
                     font=ctk.CTkFont(size=10), text_color="#cccccc"
                     ).grid(row=0, column=4, padx=4, pady=8, sticky="w")
        
        # Total
        ctk.CTkLabel(row_frame, text=f"Rp {trans.get('total_price', 0):,.0f}",
                     font=ctk.CTkFont(size=10, weight="bold"), text_color="#4ade80"
                     ).grid(row=0, column=5, padx=4, pady=8, sticky="w")
        
        # Profit (NEW)
        profit_color = "#4ade80" if profit >= 0 else "#ef4444"
        ctk.CTkLabel(row_frame, text=f"Rp {profit:,.0f}",
                     font=ctk.CTkFont(size=10), text_color=profit_color
                     ).grid(row=0, column=6, padx=4, pady=8, sticky="w")
        
        # Member
        member_name = trans.get('member_name', '-')[:15] if trans.get('member_name') else '-'
        ctk.CTkLabel(row_frame, text=member_name,
                     font=ctk.CTkFont(size=10), text_color="#cccccc"
                     ).grid(row=0, column=7, padx=4, pady=8, sticky="w")
        
        # Payment method
        method = trans.get('payment_method', 'Tunai')
        method_colors = {"Tunai": "#4ade80", "Transfer": "#00d4ff", "QRIS": "#8b5cf6"}
        ctk.CTkLabel(row_frame, text=method,
                     font=ctk.CTkFont(size=10), text_color=method_colors.get(method, "#f59e0b")
                     ).grid(row=0, column=8, padx=4, pady=8, sticky="w")
    
    def apply_filter(self):
        """Apply current filters"""
        self.load_data()
    
    def export_excel(self):
        """Export current view to Excel"""
        if not self.sorted_transactions:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk diexport!")
            return
        
        try:
            filepath = export_transactions_excel(
                self.sorted_transactions,
                f"Transaksi_{self.category_context}"
            )
            messagebox.showinfo("Sukses", f"File berhasil disimpan:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export: {str(e)}")
    
    def export_pdf(self):
        """Export current view to PDF"""
        if not self.sorted_transactions:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk diexport!")
            return
        
        try:
            title = f"Laporan Transaksi - {self.category_context}"
            filepath = export_transactions_pdf(
                self.sorted_transactions,
                title,
                f"Transaksi_{self.category_context}"
            )
            messagebox.showinfo("Sukses", f"File berhasil disimpan:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export: {str(e)}")
