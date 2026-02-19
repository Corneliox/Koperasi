"""
Dashboard Frame - Main dashboard with statistics and quick actions
"""
import customtkinter as ctk
from app.modules.warehouse import WarehouseManager
from app.modules.members import MemberManager
from app.modules.loans import LoanManager


class DashboardFrame(ctk.CTkFrame):
    """Dashboard frame with statistics overview"""
    
    def __init__(self, master, category_context: str, current_user: str):
        super().__init__(master)
        self.category_context = category_context
        self.current_user = current_user
        
        self.warehouse = WarehouseManager(category_context, current_user)
        self.member_manager = MemberManager(current_user)
        self.loan_manager = LoanManager(current_user)
        
        self.configure(fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main scrollable container
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.main_scroll.grid_columnconfigure(0, weight=1)
        
        self.create_header()
        self.create_stats_section()
        self.create_quick_info()
    
    def create_header(self):
        """Create dashboard header"""
        self.header_frame = ctk.CTkFrame(self.main_scroll, fg_color="#1a1a2e", corner_radius=10)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # Welcome message
        category_label = "Sembako" if self.category_context == "SEMBAKO" else "Taktikal"
        category_color = "#4ade80" if self.category_context == "SEMBAKO" else "#f59e0b"
        
        self.welcome_label = ctk.CTkLabel(
            self.header_frame,
            text=f"🏠 Dashboard - Divisi {category_label}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#00d4ff"
        )
        self.welcome_label.pack(side="left", padx=20, pady=20)
        
        # Category badge
        self.category_badge = ctk.CTkLabel(
            self.header_frame,
            text=f"● {category_label.upper()}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=category_color
        )
        self.category_badge.pack(side="right", padx=20, pady=20)
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            self.header_frame,
            text="🔄 Refresh",
            width=100,
            height=35,
            fg_color="#374151",
            hover_color="#4b5563",
            corner_radius=8,
            command=self.refresh_stats
        )
        self.refresh_btn.pack(side="right", padx=10, pady=20)
    
    def create_stats_section(self):
        """Create statistics cards"""
        self.stats_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.stats_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        # Configure grid for cards - Ensure they don't squash too much
        for i in range(4):
            self.stats_frame.grid_columnconfigure(i, weight=1, minsize=200)
        
        self.load_stats()
    
    def load_stats(self):
        """Load and display statistics"""
        # Clear existing cards
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Get statistics
        warehouse_stats = self.warehouse.get_statistics()
        member_stats = self.member_manager.get_statistics()
        loan_stats = self.loan_manager.get_statistics()
        
        # Card 1: Total Items
        self.create_stat_card(
            self.stats_frame,
            "📦 Total Barang",
            str(warehouse_stats['total_items']),
            f"Nilai: Rp {warehouse_stats['total_value']:,.0f}",
            "#3b82f6",
            0
        )
        
        # Card 2: Low Stock Alert
        self.create_stat_card(
            self.stats_frame,
            "⚠️ Stok Rendah",
            str(warehouse_stats['low_stock_count']),
            "Barang perlu restock",
            "#ef4444",
            1
        )
        
        # Card 3: Today's Sales
        self.create_stat_card(
            self.stats_frame,
            "🛒 Penjualan Hari Ini",
            str(warehouse_stats['today_sales_count']),
            f"Total: Rp {warehouse_stats['today_sales_total']:,.0f}",
            "#4ade80",
            2
        )
        
        # Card 4: Total Members
        self.create_stat_card(
            self.stats_frame,
            "👥 Total Anggota",
            str(member_stats['total_members']),
            f"Aktif hari ini: {member_stats['active_today']}",
            "#8b5cf6",
            3
        )
        
        # Row 2 - Loan Statistics
        # Card 5: Active Loans
        self.create_stat_card(
            self.stats_frame,
            "💰 Pinjaman Aktif",
            str(loan_stats['active_count']),
            f"Total: Rp {loan_stats['active_remaining']:,.0f}",
            "#f59e0b",
            0,
            row=1
        )
        
        # Card 6: Bad Debts
        self.create_stat_card(
            self.stats_frame,
            "❌ Pinjaman Macet",
            str(loan_stats['bad_debt_count']),
            f"Total: Rp {loan_stats['bad_debt_amount']:,.0f}",
            "#ef4444",
            1,
            row=1
        )
        
        # Card 7: Paid This Month
        self.create_stat_card(
            self.stats_frame,
            "✅ Dibayar Bulan Ini",
            "",
            f"Rp {loan_stats['paid_this_month']:,.0f}",
            "#4ade80",
            2,
            row=1
        )
    
    def create_stat_card(self, parent, title: str, value: str, subtitle: str, 
                         color: str, col: int, row: int = 0):
        """Create a statistics card"""
        # Detection for Windows 7 performance
        import sys
        win_ver = sys.getwindowsversion()
        is_win7 = win_ver.major == 6 and win_ver.minor == 1
        radius = 8 if is_win7 else 15
        
        card = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=radius)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        title_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        # Value
        if value:
            value_label = ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=36, weight="bold"),
                text_color=color
            )
            value_label.pack(anchor="w", padx=20, pady=5)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            card,
            text=subtitle,
            font=ctk.CTkFont(size=12),
            text_color="#cccccc"
        )
        subtitle_label.pack(anchor="w", padx=20, pady=(5, 20))
    
    def create_quick_info(self):
        """Create quick info section with low stock items"""
        self.info_frame = ctk.CTkFrame(self.main_scroll, fg_color="#1a1a2e", corner_radius=10)
        self.info_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        # Title
        ctk.CTkLabel(
            self.info_frame,
            text="⚠️ Barang Stok Rendah (≤10)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f59e0b"
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Low stock items
        low_stock = self.warehouse.get_low_stock_items(threshold=10)
        
        if not low_stock:
            ctk.CTkLabel(
                self.info_frame,
                text="✅ Tidak ada barang dengan stok rendah",
                font=ctk.CTkFont(size=13),
                text_color="#4ade80"
            ).pack(anchor="w", padx=20, pady=10)
        else:
            # Create scrollable list
            list_frame = ctk.CTkScrollableFrame(
                self.info_frame, 
                fg_color="transparent",
                height=150
            )
            list_frame.pack(fill="x", padx=10, pady=(0, 15))
            
            for item in low_stock[:10]:  # Show max 10 items
                item_frame = ctk.CTkFrame(list_frame, fg_color="#16213e", corner_radius=8)
                item_frame.pack(fill="x", pady=2, padx=5)
                
                ctk.CTkLabel(
                    item_frame,
                    text=f"• {item['name'][:40]}",
                    font=ctk.CTkFont(size=12),
                    text_color="#ffffff"
                ).pack(side="left", padx=10, pady=8)
                
                stock_color = "#ef4444" if item['stock'] <= 5 else "#f59e0b"
                ctk.CTkLabel(
                    item_frame,
                    text=f"Stok: {item['stock']}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=stock_color
                ).pack(side="right", padx=10, pady=8)
    
    def refresh_stats(self):
        """Refresh all statistics"""
        self.load_stats()
        self.create_quick_info()
