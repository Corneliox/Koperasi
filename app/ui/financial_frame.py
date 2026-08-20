"""
Financial Reports Frame - Neraca Keuangan UI
Displays financial balance sheet with export options
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry
from app.utils.financial_report import (
    FinancialReportManager,
    export_balance_sheet_excel,
    export_balance_sheet_pdf
)


class FinancialReportsFrame(ctk.CTkFrame):
    """Financial reports frame with balance sheet view"""
    
    def __init__(self, master, category_context: str, current_user: str):
        super().__init__(master)
        self.category_context = category_context
        self.current_user = current_user
        self.report_manager = FinancialReportManager(category_context)
        
        self.configure(fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.current_balance = None
        
        self.create_header()
        self.create_content()
        self.load_data()
    
    def create_header(self):
        """Create header with filters and export buttons"""
        self.header_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # Title
        title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=20, pady=15)
        
        ctk.CTkLabel(
            title_frame,
            text="📊 Neraca Keuangan",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00d4ff"
        ).pack(side="left")
        
        # Category badge
        div_text = "SEMBAKO" if self.category_context == "SEMBAKO" else "TAKTIKAL"
        div_color = "#4ade80" if self.category_context == "SEMBAKO" else "#f59e0b"
        
        ctk.CTkLabel(
            title_frame,
            text=f"  •  {div_text}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=div_color
        ).pack(side="left", padx=(15, 0))
        
        # Right side - filters and export
        controls_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        controls_frame.pack(side="right", padx=20, pady=10)
        
        # Period filter
        ctk.CTkLabel(
            controls_frame, text="Periode:",
            font=ctk.CTkFont(size=12), text_color="#cccccc"
        ).pack(side="left", padx=(0, 5))
        
        self.period_var = ctk.StringVar(value="15-15 (Bulanan)")
        self.period_menu = ctk.CTkOptionMenu(
            controls_frame,
            values=["15-15 (Bulanan)", "Hari Ini", "7 Hari", "Bulan Ini", "Tahun Ini", "Custom"],
            variable=self.period_var,
            width=140,
            height=35,
            fg_color="#8b5cf6", # Purple to highlight it's the main one
            button_color="#7c3aed",
            command=self.on_period_change
        )
        self.period_menu.pack(side="left", padx=5)
        
        # Custom date range (hidden by default)
        self.date_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        
        self.start_date = DateEntry(
            self.date_frame, width=10, background='#374151',
            foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd'
        )
        self.start_date.pack(side="left", padx=2)
        
        ctk.CTkLabel(self.date_frame, text="-", text_color="#888").pack(side="left")
        
        self.end_date = DateEntry(
            self.date_frame, width=10, background='#374151',
            foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd'
        )
        self.end_date.pack(side="left", padx=2)
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄",
            width=40,
            height=35,
            fg_color="#374151",
            hover_color="#4b5563",
            corner_radius=8,
            command=self.load_data
        )
        self.refresh_btn.pack(side="left", padx=5)
        
        # Export buttons
        self.excel_btn = ctk.CTkButton(
            controls_frame,
            text="📊 Excel",
            width=90,
            height=35,
            fg_color="#22c55e",
            hover_color="#16a34a",
            text_color="#000000",
            corner_radius=8,
            command=self.export_excel
        )
        self.excel_btn.pack(side="left", padx=3)
        
        self.pdf_btn = ctk.CTkButton(
            controls_frame,
            text="📄 PDF",
            width=80,
            height=35,
            fg_color="#ef4444",
            hover_color="#dc2626",
            corner_radius=8,
            command=self.export_pdf
        )
        self.pdf_btn.pack(side="left", padx=3)
    
    def on_period_change(self, value):
        """Handle period change"""
        if value == "Custom":
            self.date_frame.pack(side="left", padx=10)
        else:
            self.date_frame.pack_forget()
            self.load_data()
    
    def get_date_range(self):
        """Get date range based on selected period"""
        today = datetime.now().date()
        period = self.period_var.get()
        
        if period == "15-15 (Bulanan)":
            # If today is >= 15, range is 15th this month to 15th next month
            # If today is < 15, range is 15th last month to 15th this month
            if today.day >= 15:
                start = today.replace(day=15)
                # Next month handling
                if today.month == 12:
                    end = today.replace(year=today.year + 1, month=1, day=15)
                else:
                    end = today.replace(month=today.month + 1, day=15)
            else:
                end = today.replace(day=15)
                # Last month handling
                if today.month == 1:
                    start = today.replace(year=today.year - 1, month=12, day=15)
                else:
                    start = today.replace(month=today.month - 1, day=15)
            return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')
            
        elif period == "Hari Ini":
            return today.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        elif period == "7 Hari":
            return (today - timedelta(days=7)).strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        elif period == "Bulan Ini":
            return today.replace(day=1).strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        elif period == "Tahun Ini":
            return today.replace(month=1, day=1).strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        elif period == "Custom":
            return (
                self.start_date.get_date().strftime('%Y-%m-%d'),
                self.end_date.get_date().strftime('%Y-%m-%d')
            )
        
        return None, None
    
    def create_content(self):
        """Create main content area"""
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#1a1a2e",
            corner_radius=10
        )
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)
    
    def load_data(self):
        """Load and display balance sheet"""
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        start_date, end_date = self.get_date_range()
        self.current_balance = self.report_manager.get_balance_sheet(start_date, end_date)
        
        if not self.current_balance:
            ctk.CTkLabel(
                self.content_frame,
                text="Gagal memuat data",
                text_color="#ef4444"
            ).grid(row=0, column=0, pady=50)
            return
        
        # Period info
        period_frame = ctk.CTkFrame(self.content_frame, fg_color="#16213e", corner_radius=10)
        period_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            period_frame,
            text=f"📅 Periode: {self.current_balance['period']['start_date']} s/d {self.current_balance['period']['end_date']}",
            font=ctk.CTkFont(size=14),
            text_color="#00d4ff"
        ).pack(pady=15)
        
        # Assets Section
        self.create_section(
            row=1, column=0,
            title="💰 AKTIVA (ASSETS)",
            color="#4ade80",
            items=[
                ("Nilai Persediaan Barang", self.current_balance['assets']['inventory_value'], True),
                ("Jumlah Jenis Barang", self.current_balance['assets']['total_items'], False),
                ("Total Unit Stok", self.current_balance['assets']['total_stock'], False),
                ("Piutang Pinjaman Aktif", self.current_balance['assets']['outstanding_loans'], True),
                ("Piutang Macet", self.current_balance['assets']['bad_debts'], True),
            ],
            total=("TOTAL AKTIVA", self.current_balance['assets']['total_assets'])
        )
        
        # Income Section
        self.create_section(
            row=1, column=1,
            title="📈 PENDAPATAN (INCOME)",
            color="#00d4ff",
            items=[
                ("Pendapatan Penjualan", self.current_balance['income']['sales_revenue'], True),
                ("Jumlah Transaksi", self.current_balance['income']['sales_count'], False),
                ("Unit Terjual", self.current_balance['income']['items_sold'], False),
                ("Harga Pokok Penjualan", self.current_balance['income']['cogs'], True),
                ("Laba Kotor", self.current_balance['income']['gross_profit'], True),
                ("Pendapatan Bunga", self.current_balance['income']['loan_interest'], True),
            ],
            total=("LABA BERSIH", self.current_balance['income']['net_income'])
        )
        
        # Mutations Section
        self.create_section(
            row=2, column=0,
            title="📦 MUTASI STOK",
            color="#f59e0b",
            items=[
                ("Barang Masuk (IN)", self.current_balance['mutations']['stock_in'], False),
                ("Barang Keluar (OUT)", self.current_balance['mutations']['stock_out'], False),
                ("Retur", self.current_balance['mutations']['returns'], False),
                ("Koreksi", self.current_balance['mutations']['corrections'], False),
            ]
        )
        
        # Summary Card
        self.create_summary_card(row=2, column=1)
    
    def create_section(self, row: int, column: int, title: str, color: str,
                       items: list, total: tuple = None):
        """Create a section card"""
        section = ctk.CTkFrame(self.content_frame, fg_color="#16213e", corner_radius=10)
        section.grid(row=row, column=column, sticky="nsew", padx=10, pady=10)
        
        # Title
        ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=color
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Items
        for label, value, is_currency in items:
            item_frame = ctk.CTkFrame(section, fg_color="transparent")
            item_frame.pack(fill="x", padx=20, pady=3)
            
            ctk.CTkLabel(
                item_frame,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color="#cccccc"
            ).pack(side="left")
            
            if is_currency:
                value_text = f"Rp {(value or 0):,.0f}"
            else:
                value_text = f"{(value or 0):,}"
            
            ctk.CTkLabel(
                item_frame,
                text=value_text,
                font=ctk.CTkFont(size=12),
                text_color="#ffffff"
            ).pack(side="right")
        
        # Total
        if total:
            ctk.CTkFrame(section, fg_color="#333", height=1).pack(fill="x", padx=20, pady=10)
            
            total_frame = ctk.CTkFrame(section, fg_color="#1e293b", corner_radius=8)
            total_frame.pack(fill="x", padx=15, pady=(0, 15))
            
            ctk.CTkLabel(
                total_frame,
                text=total[0],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=color
            ).pack(side="left", padx=10, pady=10)
            
            ctk.CTkLabel(
                total_frame,
                text=f"Rp {(total[1] or 0):,.0f}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=color
            ).pack(side="right", padx=10, pady=10)
    
    def create_summary_card(self, row: int, column: int):
        """Create summary highlights card"""
        summary = ctk.CTkFrame(self.content_frame, fg_color="#16213e", corner_radius=10)
        summary.grid(row=row, column=column, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(
            summary,
            text="📊 RINGKASAN",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#8b5cf6"
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Net Profit highlight
        profit = self.current_balance['income']['net_income'] or 0
        profit_color = "#4ade80" if profit >= 0 else "#ef4444"
        
        profit_frame = ctk.CTkFrame(summary, fg_color="#1e293b", corner_radius=8)
        profit_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            profit_frame,
            text="Laba Bersih Periode Ini",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        ).pack(anchor="w", padx=15, pady=(10, 0))
        
        ctk.CTkLabel(
            profit_frame,
            text=f"Rp {profit:,.0f}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=profit_color
        ).pack(anchor="w", padx=15, pady=(5, 15))
        
        # Profit margin
        revenue = self.current_balance['income']['sales_revenue'] or 0
        if revenue > 0:
            margin = (profit / revenue) * 100
            margin_text = f"{margin:.1f}%"
        else:
            margin_text = "N/A"
        
        margin_frame = ctk.CTkFrame(summary, fg_color="transparent")
        margin_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            margin_frame,
            text="Margin Keuntungan:",
            font=ctk.CTkFont(size=12),
            text_color="#cccccc"
        ).pack(side="left")
        
        ctk.CTkLabel(
            margin_frame,
            text=margin_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#4ade80"
        ).pack(side="right")
        
        # Asset utilization
        asset_frame = ctk.CTkFrame(summary, fg_color="transparent")
        asset_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(
            asset_frame,
            text="Total Aset:",
            font=ctk.CTkFont(size=12),
            text_color="#cccccc"
        ).pack(side="left")
        
        ctk.CTkLabel(
            asset_frame,
            text=f"Rp {(self.current_balance['assets']['total_assets'] or 0):,.0f}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00d4ff"
        ).pack(side="right")
        
        # Generated timestamp
        ctk.CTkLabel(
            summary,
            text=f"Diperbarui: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            font=ctk.CTkFont(size=10),
            text_color="#666666"
        ).pack(anchor="w", padx=20, pady=(15, 15))
    
    def export_excel(self):
        """Export balance sheet to Excel"""
        if not self.current_balance:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk diexport!")
            return
        
        try:
            filepath = export_balance_sheet_excel(self.current_balance)
            messagebox.showinfo("Sukses", f"File berhasil disimpan:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export: {str(e)}")
    
    def export_pdf(self):
        """Export balance sheet to PDF"""
        if not self.current_balance:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk diexport!")
            return
        
        try:
            filepath = export_balance_sheet_pdf(self.current_balance)
            messagebox.showinfo("Sukses", f"File berhasil disimpan:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export: {str(e)}")
