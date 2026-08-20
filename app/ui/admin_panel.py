"""
Admin Panel - Immutable Audit Logs Viewer & Admin Controls
Contains:
- View Logs (read-only, no delete)
- Easter Egg Reset Modal (Ctrl+Click x5)
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from app.utils.audit_log import get_audit_logs, get_audit_statistics
from app.database.connection import get_connection


class AuditLogViewer(ctk.CTkToplevel):
    """
    Immutable Audit Log Viewer - READ ONLY
    No delete or clear functions available
    """
    
    def __init__(self, parent, current_user: str):
        super().__init__(parent)
        self.current_user = current_user
        
        self.title("📋 Audit Log - Riwayat Aktivitas (Read-Only)")
        self.configure(fg_color="#1a1a2e")
        self.resizable(True, True)
        
        self.update_idletasks()
        
        window_width = 1000
        window_height = 650
        x = (self.winfo_screenwidth() - window_width) // 2
        y = (self.winfo_screenheight() - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.minsize(800, 500)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self.create_header()
        self.create_filters()
        self.create_table()
        self.load_data()
        
        self.grab_set()
    
    def create_header(self):
        """Create header with statistics"""
        header = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=10)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header.grid_columnconfigure(0, weight=1)
        
        # Title
        ctk.CTkLabel(
            header, text="📋 Audit Log - Riwayat Aktivitas Sistem",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00d4ff"
        ).pack(side="left", padx=20, pady=15)
        
        # Archive Button
        ctk.CTkButton(
            header, text="🗄️ Archive Logs", width=120, height=32,
            fg_color="#f59e0b", hover_color="#d97706",
            text_color="#000", command=self.archive_logs
        ).pack(side="right", padx=20, pady=15)
        
        # Warning badge
        ctk.CTkLabel(
            header, text="🔒 READ-ONLY",
            font=ctk.CTkFont(size=11),
            text_color="#f59e0b"
        ).pack(side="right", padx=5, pady=15)
    
    def create_filters(self):
        """Create filter controls"""
        filter_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=10)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Category filter
        ctk.CTkLabel(filter_frame, text="Kategori:", text_color="#ccc").pack(side="left", padx=(20, 5), pady=10)
        self.category_var = ctk.StringVar(value="Semua")
        ctk.CTkOptionMenu(
            filter_frame,
            values=["Semua", "INVENTORY", "MEMBER", "LOAN", "TRANSACTION", "SYSTEM"],
            variable=self.category_var,
            width=130, height=32,
            fg_color="#374151", button_color="#4b5563"
        ).pack(side="left", padx=5, pady=10)
        
        # Level filter
        ctk.CTkLabel(filter_frame, text="Level:", text_color="#ccc").pack(side="left", padx=(15, 5), pady=10)
        self.level_var = ctk.StringVar(value="Semua")
        ctk.CTkOptionMenu(
            filter_frame,
            values=["Semua", "INFO", "WARNING", "DANGER", "ERROR"],
            variable=self.level_var,
            width=100, height=32,
            fg_color="#374151", button_color="#4b5563"
        ).pack(side="left", padx=5, pady=10)
        
        # User filter
        ctk.CTkLabel(filter_frame, text="User:", text_color="#ccc").pack(side="left", padx=(15, 5), pady=10)
        self.user_filter = ctk.CTkEntry(filter_frame, width=120, height=32, placeholder_text="Semua")
        self.user_filter.pack(side="left", padx=5, pady=10)
        
        # Limit
        ctk.CTkLabel(filter_frame, text="Limit:", text_color="#ccc").pack(side="left", padx=(15, 5), pady=10)
        self.limit_var = ctk.StringVar(value="200")
        ctk.CTkOptionMenu(
            filter_frame,
            values=["50", "100", "200", "500"],
            variable=self.limit_var,
            width=80, height=32,
            fg_color="#374151", button_color="#4b5563"
        ).pack(side="left", padx=5, pady=10)
        
        # Apply filter button
        ctk.CTkButton(
            filter_frame, text="🔍 Filter", width=80, height=32,
            fg_color="#00d4ff", hover_color="#00a8cc",
            text_color="#000", command=self.load_data
        ).pack(side="left", padx=15, pady=10)
        
        # Refresh button
        ctk.CTkButton(
            filter_frame, text="🔄", width=35, height=32,
            fg_color="#374151", hover_color="#4b5563",
            command=self.refresh_data
        ).pack(side="left", padx=5, pady=10)
        
        # Stats
        self.stats_label = ctk.CTkLabel(filter_frame, text="", text_color="#4ade80")
        self.stats_label.pack(side="right", padx=20, pady=10)
    
    def create_table(self):
        """Create log table"""
        container = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        container.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ctk.CTkFrame(container, fg_color="#16213e", height=40)
        header.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        header.grid_propagate(False)
        
        columns = [
            ("ID", 50), ("Waktu", 140), ("User", 80), ("Level", 80), ("Kategori", 100),
            ("Aksi", 80), ("Entitas", 80), ("Detail", 350)
        ]
        
        for i, (text, width) in enumerate(columns):
            header.grid_columnconfigure(i, minsize=width)
            ctk.CTkLabel(
                header, text=text, width=width,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#00d4ff"
            ).grid(row=0, column=i, padx=3, pady=8, sticky="w")
        
        # Scrollable content
        self.scroll_frame = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        for i, (_, width) in enumerate(columns):
            self.scroll_frame.grid_columnconfigure(i, minsize=width)
    
    def load_data(self):
        """Load audit logs"""
        # Clear existing
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # Get filter values
        category = self.category_var.get()
        level = self.level_var.get()
        user = self.user_filter.get().strip()
        limit = int(self.limit_var.get())
        
        logs = get_audit_logs(
            limit=limit,
            user_filter=user if user else None,
            category_filter=category if category != "Semua" else None,
            level_filter=level if level != "Semua" else None
        )
        
        if not logs:
            ctk.CTkLabel(
                self.scroll_frame, text="Tidak ada data log",
                font=ctk.CTkFont(size=14), text_color="#888"
            ).grid(row=0, column=0, columnspan=8, pady=50)
            self.stats_label.configure(text="Total: 0 log")
            return
        
        for idx, log in enumerate(logs):
            self.create_row(idx, log)
        
        # Update stats
        stats = get_audit_statistics()
        self.stats_label.configure(
            text=f"Total: {stats['total_logs']} log | Hari ini: {stats['today_logs']}"
        )
    
    def create_row(self, idx: int, log: dict):
        """Create log row"""
        bg = "#1e293b" if idx % 2 == 0 else "#16213e"
        
        row = ctk.CTkFrame(self.scroll_frame, fg_color=bg, height=35, corner_radius=3)
        row.grid(row=idx, column=0, columnspan=8, sticky="ew", pady=1)
        row.grid_propagate(False)
        
        widths = [50, 140, 80, 80, 100, 80, 80, 350]
        for i, w in enumerate(widths):
            row.grid_columnconfigure(i, minsize=w)
        
        # Category colors
        cat_colors = {
            "INVENTORY": "#4ade80",
            "MEMBER": "#00d4ff",
            "LOAN": "#f59e0b",
            "TRANSACTION": "#8b5cf6",
            "SYSTEM": "#ef4444"
        }
        
        # Level colors
        level_colors = {
            "INFO": "#cccccc",
            "WARNING": "#f59e0b",
            "DANGER": "#ef4444",
            "ERROR": "#ef4444"
        }
        
        # ID
        ctk.CTkLabel(row, text=str(log.get('id', '')), width=widths[0],
                     font=ctk.CTkFont(size=9), text_color="#888"
                     ).grid(row=0, column=0, padx=3, pady=6, sticky="w")
        
        # Timestamp
        ts = log.get('timestamp', '')[:16] if log.get('timestamp') else '-'
        ctk.CTkLabel(row, text=ts, width=widths[1],
                     font=ctk.CTkFont(size=9), text_color="#ccc"
                     ).grid(row=0, column=1, padx=3, pady=6, sticky="w")
        
        # User
        ctk.CTkLabel(row, text=log.get('user', '-')[:10], width=widths[2],
                     font=ctk.CTkFont(size=9), text_color="#00d4ff"
                     ).grid(row=0, column=2, padx=3, pady=6, sticky="w")
        
        # Level
        lvl = log.get('level', 'INFO')
        lvl_color = level_colors.get(lvl, "#ccc")
        ctk.CTkLabel(row, text=lvl, width=widths[3],
                     font=ctk.CTkFont(size=9, weight="bold"), text_color=lvl_color
                     ).grid(row=0, column=3, padx=3, pady=6, sticky="w")
        
        # Category
        cat = log.get('action_category', '-')
        cat_color = cat_colors.get(cat, "#888")
        ctk.CTkLabel(row, text=cat, width=widths[4],
                     font=ctk.CTkFont(size=9, weight="bold"), text_color=cat_color
                     ).grid(row=0, column=4, padx=3, pady=6, sticky="w")
        
        # Action type
        ctk.CTkLabel(row, text=log.get('action_type', '-'), width=widths[5],
                     font=ctk.CTkFont(size=9), text_color="#ccc"
                     ).grid(row=0, column=5, padx=3, pady=6, sticky="w")
        
        # Entity
        entity = f"{log.get('entity_type', '-')[:8]}:{log.get('entity_id', '')}" if log.get('entity_id') else '-'
        ctk.CTkLabel(row, text=entity[:12], width=widths[6],
                     font=ctk.CTkFont(size=9), text_color="#888"
                     ).grid(row=0, column=6, padx=3, pady=6, sticky="w")
        
        # Details
        details = log.get('details', '-') or '-'
        ctk.CTkLabel(row, text=details[:60], width=widths[7],
                     font=ctk.CTkFont(size=9), text_color="#ccc"
                     ).grid(row=0, column=7, padx=3, pady=6, sticky="w")
    
    def archive_logs(self):
        """Archive old logs to file and clear from DB"""
        if not messagebox.askyesno("Archive Logs", "Arsipkan log lama ke file JSON dan hapus dari database?"):
            return
            
        dialog = ctk.CTkInputDialog(
            text="Masukkan umur log (hari) untuk diarsipkan:\n(Default: 90 hari)",
            title="Archive Config"
        )
        days_str = dialog.get_input()
        
        if not days_str:
            return
            
        try:
            days = int(days_str)
            if days < 1:
                raise ValueError
        except:
            messagebox.showerror("Error", "Masukkan angka valid (min 1 hari)")
            return
            
        from app.utils.audit_log import archive_old_logs
        result = archive_old_logs(days)
        
        if result['success']:
            if result['count'] > 0:
                messagebox.showinfo(
                    "Sukses", 
                    f"Berhasil mengarsipkan {result['count']} log.\n\n"
                    f"File tersimpan di:\n{result['filepath']}"
                )
                self.load_data()
            else:
                messagebox.showinfo("Info", "Tidak ada log yang memenuhi kriteria untuk diarsipkan.")
        else:
            messagebox.showerror("Error", f"Gagal mengarsipkan log: {result['message']}")

    def refresh_data(self):
        """Refresh with default filters"""
        self.category_var.set("Semua")
        self.user_filter.delete(0, "end")
        self.limit_var.set("200")
        self.load_data()


class DangerResetModal(ctk.CTkToplevel):
    """
    Hidden Admin Reset Modal - Triggered by Easter Egg (Ctrl+Click x5)
    Allows deletion of data with DANGER confirmation
    """
    
    def __init__(self, parent, current_user: str, on_reset_complete=None):
        super().__init__(parent)
        self.current_user = current_user
        self.on_reset_complete = on_reset_complete
        
        self.title("⚠️ DANGER ZONE - Admin Reset")
        self.configure(fg_color="#1a1a2e")
        self.resizable(False, False)
        
        self.update_idletasks()
        
        window_width = 450
        window_height = 480
        x = (self.winfo_screenwidth() - window_width) // 2
        y = (self.winfo_screenheight() - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.create_content()
        self.grab_set()
    
    def create_content(self):
        """Create danger modal content"""
        # Warning header
        warning_frame = ctk.CTkFrame(self, fg_color="#7f1d1d", corner_radius=10)
        warning_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            warning_frame, text="⚠️ DANGER ZONE",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#fca5a5"
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            warning_frame, text="Operasi berikut TIDAK DAPAT DIBATALKAN!",
            font=ctk.CTkFont(size=12),
            text_color="#fecaca"
        ).pack(pady=(0, 15))
        
        # Options
        ctk.CTkLabel(
            self, text="Pilih operasi reset:",
            font=ctk.CTkFont(size=14), text_color="#ccc"
        ).pack(pady=(0, 15))
        
        # Option buttons
        options_frame = ctk.CTkFrame(self, fg_color="transparent")
        options_frame.pack(fill="x", padx=30)
        
        # Delete Sembako only
        ctk.CTkButton(
            options_frame, text="🛒 Hapus Data SEMBAKO",
            width=380, height=45,
            fg_color="#f59e0b", hover_color="#d97706",
            text_color="#000", font=ctk.CTkFont(weight="bold"),
            command=lambda: self.confirm_reset("SEMBAKO")
        ).pack(pady=5)
        
        # Delete Taktikal only
        ctk.CTkButton(
            options_frame, text="🎯 Hapus Data TAKTIKAL",
            width=380, height=45,
            fg_color="#f59e0b", hover_color="#d97706",
            text_color="#000", font=ctk.CTkFont(weight="bold"),
            command=lambda: self.confirm_reset("TAKTIKAL")
        ).pack(pady=5)
        
        # Delete ALL
        ctk.CTkButton(
            options_frame, text="💀 HAPUS SEMUA DATA",
            width=380, height=55,
            fg_color="#dc2626", hover_color="#b91c1c",
            text_color="#fff", font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self.confirm_reset("ALL")
        ).pack(pady=15)
        
        # Cancel button
        ctk.CTkButton(
            self, text="← Batal (Keluar)",
            width=150, height=40,
            fg_color="#374151", hover_color="#4b5563",
            command=self.destroy
        ).pack(pady=20)
        
        # Logged in as
        ctk.CTkLabel(
            self, text=f"Logged in as: {self.current_user}",
            font=ctk.CTkFont(size=10), text_color="#666"
        ).pack(pady=(0, 10))
    
    def confirm_reset(self, reset_type: str):
        """Show confirmation dialog"""
        type_text = {
            "SEMBAKO": "semua data SEMBAKO (inventaris & transaksi)",
            "TAKTIKAL": "semua data TAKTIKAL (inventaris & transaksi)",
            "ALL": "SEMUA DATA APLIKASI (inventaris, transaksi, anggota, pinjaman)"
        }
        
        confirm = messagebox.askyesno(
            "⚠️ KONFIRMASI FINAL",
            f"Anda akan MENGHAPUS PERMANEN:\n\n"
            f">> {type_text[reset_type]} <<\n\n"
            f"Operasi ini TIDAK DAPAT DIBATALKAN!\n\n"
            f"Apakah Anda yakin?",
            icon='warning'
        )
        
        if confirm:
            # Double confirmation
            final = messagebox.askyesno(
                "🔴 KONFIRMASI TERAKHIR",
                "Apakah Anda benar-benar yakin ingin melanjutkan penghapusan permanen ini?\n\n"
                "Ini adalah kesempatan terakhir untuk membatalkan.",
                icon='warning'
            )
            
            if final:
                self.execute_reset(reset_type)
    
    def execute_reset(self, reset_type: str):
        """Execute the reset operation"""
        from app.utils.audit_log import log_audit
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            if reset_type == "SEMBAKO":
                # Delete Sembako data in correct FK order
                cursor.execute("DELETE FROM transactions WHERE category_type = 'SEMBAKO'")
                cursor.execute("DELETE FROM warehouse_mutation WHERE item_id IN (SELECT id FROM warehouse WHERE category_type = 'SEMBAKO')")
                cursor.execute("DELETE FROM warehouse WHERE category_type = 'SEMBAKO'")
                
            elif reset_type == "TAKTIKAL":
                # Delete Taktikal data in correct FK order
                cursor.execute("DELETE FROM transactions WHERE category_type = 'TAKTIKAL'")
                cursor.execute("DELETE FROM warehouse_mutation WHERE item_id IN (SELECT id FROM warehouse WHERE category_type = 'TAKTIKAL')")
                cursor.execute("DELETE FROM warehouse WHERE category_type = 'TAKTIKAL'")
                
            elif reset_type == "ALL":
                # Delete all operational data in correct FK dependency order
                cursor.execute("DELETE FROM transactions")
                cursor.execute("DELETE FROM warehouse_mutation")
                cursor.execute("DELETE FROM warehouse")
                cursor.execute("DELETE FROM loan_payments")
                cursor.execute("DELETE FROM loans")
                cursor.execute("DELETE FROM members")
            
            conn.commit()
            
            # Log this critical action (immutable)
            log_audit(
                self.current_user, "SYSTEM", "RESET",
                None, None, None,
                {"reset_type": reset_type},
                f"DANGER: Data reset executed - {reset_type}",
                level="DANGER"
            )
            
            messagebox.showinfo("Reset Berhasil", f"Data {reset_type} telah berhasil di-reset.")
            self.destroy()
            
            if self.on_reset_complete:
                self.on_reset_complete()
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Gagal menghapus data: {str(e)}")
        finally:
            conn.close()


class UserIconMenu(ctk.CTkToplevel):
    """
    Dropdown menu appearing above user icon
    Contains: View Logs option
    """
    
    def __init__(self, parent, x: int, y: int, current_user: str, 
                 on_view_logs, on_close):
        super().__init__(parent)
        self.current_user = current_user
        self.on_view_logs = on_view_logs
        self.on_close_callback = on_close
        
        # Remove window decorations
        self.overrideredirect(True)
        self.configure(fg_color="#16213e")
        
        # Position above the click point (expanding upwards)
        menu_width = 160
        menu_height = 50
        self.geometry(f"{menu_width}x{menu_height}+{x}+{y - menu_height - 5}")
        
        # Content
        ctk.CTkButton(
            self, text="📋 View Logs",
            width=150, height=40,
            font=ctk.CTkFont(size=12),
            fg_color="#374151", hover_color="#4b5563",
            command=self.open_logs
        ).pack(pady=5, padx=5)
        
        # Close on click outside
        self.bind("<FocusOut>", lambda e: self.close_menu())
        self.after(100, self.focus_set)
    
    def open_logs(self):
        """Open audit log viewer"""
        self.close_menu()
        self.on_view_logs()
    
    def close_menu(self):
        """Close menu"""
        self.on_close_callback()
        self.destroy()
