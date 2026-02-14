"""
Koperasi Brimob - Sistem Manajemen Inventaris & Keuangan
Main Application Entry Point

Compatible: Windows 7 x32 - Windows 11 x64
REFACTORED: Added Financial Reports, Fixed Change Division dialog
PHASE 3: Added Easter Egg reset, Admin logs dropdown
"""
import os
import sys
import ctypes
import platform
import subprocess
import tkinter.messagebox

# Enable DPI awareness for Windows
if sys.platform == 'win32':
    try:
        # Log OS Version for Debugging
        print(f"Starting Koperasi Brimob on: {platform.system()} {platform.release()} {platform.version()} ({platform.machine()})")
        print(f"Python: {sys.version}")
        print(f"Python: {sys.version}")
        
        # Check if we are on Windows 8.1 (6.3) or higher for shcore
        # Windows 7 is 6.1, Windows 8 is 6.2
        if sys.getwindowsversion().major > 6 or (sys.getwindowsversion().major == 6 and sys.getwindowsversion().minor >= 3):
            try:
                # SetProcessDpiAwareness(PROCESS_SYSTEM_DPI_AWARE=1)
                shcore = ctypes.windll.shcore
                # Verify argument types and values against C function signatures
                shcore.SetProcessDpiAwareness.argtypes = [ctypes.c_int]
                shcore.SetProcessDpiAwareness(1)
            except Exception:
                # Fallback to user32 if shcore fails
                ctypes.windll.user32.SetProcessDPIAware()
        else:
            # Windows 7 and older
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

import customtkinter as ctk
from app.utils.error_handler import setup_global_error_handler
from app.database.connection import init_database

# Initialize global error handling
setup_global_error_handler()

from app.utils.audit_log import log_audit
from app.ui.login_frame import LoginFrame
from app.ui.category_select_frame import CategorySelectFrame, ChangeDivisionDialog
from app.ui.dashboard_frame import DashboardFrame
from app.ui.store_frame import StoreFrame
from app.ui.history_frame import HistoryFrame
from app.ui.members_frame import MembersFrame
from app.ui.loans_frame import LoansFrame
from app.ui.financial_frame import FinancialReportsFrame
from app.ui.admin_panel import AuditLogViewer, DangerResetModal


# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class KoperasiBrimobApp(ctk.CTk):
    """Main Application Window"""
    
    def __init__(self):
        super().__init__()
        
        # Windows Version Detection
        win_ver = sys.getwindowsversion()
        is_win7 = win_ver.major == 6 and win_ver.minor == 1
        
        # Optimization for Win7 / 32-bit
        if is_win7:
            ctk.set_appearance_mode("Dark") # Force Dark mode
            # Set global font fallback for Windows 7
            self.default_font = ("Segoe UI", 12)
            self.title_font = ("Segoe UI", 18, "bold")
        else:
            self.default_font = ("Roboto", 12)
            self.title_font = ("Roboto", 18, "bold")
        
        # Initialize database
        init_database()
        
        # Window configuration
        self.title("Koperasi Brimob - Sistem Manajemen")
        
        # Calculate initial geometry based on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Dynamic width: 90% of screen or minimum 1200px
        window_width = max(1200, int(screen_width * 0.9))
        window_height = max(700, int(screen_height * 0.85))
        
        # Center window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2 - 30
        
        # Win7 Compatibility: Force update before geometry
        self.update_idletasks()
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.minsize(1000, 600)
        
        # Win7 Compatibility: Re-apply geometry after a short delay to ensure it sticks
        if win_ver.major == 6 and win_ver.minor == 1:
            self.after(100, lambda: self.geometry(f"{window_width}x{window_height}+{x}+{y}"))

        # Configure main grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # State variables
        self.current_user = None
        self.category_context = None
        self.current_frame = None
        self.sidebar = None
        self.content_frame = None
        
        # Active windows registry (for anti-duplicate)
        self.active_windows = {}
        
        # Easter egg counter for reset modal
        self.easter_egg_clicks = 0
        self.easter_egg_timer = None
        
        # Start with login
        self.show_login()
        
        # Bind main window close event
        self.protocol("WM_DELETE_WINDOW", self.on_app_closing)

    def on_app_closing(self):
        """Show custom confirmation before closing the entire application"""
        self.handle_exit_logic(is_logout=False)

    def handle_exit_logic(self, is_logout=False):
        """Unified logic for exit and logout with Save All option"""
        dialog = CustomExitDialog(self, is_logout=is_logout)
        self.wait_window(dialog)
        
        if dialog.result == "save_proceed":
            if self.save_all_dialogs():
                tkinter.messagebox.showinfo("Sukses", "Semua data telah berhasil disimpan.")
                if is_logout:
                    self.perform_logout()
                else:
                    self.destroy()
                    sys.exit(0)
        elif dialog.result == "proceed_only":
            if is_logout:
                self.perform_logout()
            else:
                self.destroy()
                sys.exit(0)
        # If 'cancel' or None, do nothing

    def save_all_dialogs(self) -> bool:
        """Find all active dialogs and trigger their save methods. Returns True if all saved."""
        all_saved = True
        
        def find_dialogs(parent):
            dialogs = []
            for child in parent.winfo_children():
                if isinstance(child, ctk.CTkToplevel):
                    dialogs.append(child)
                # Recurse into frames
                if hasattr(child, 'winfo_children'):
                    dialogs.extend(find_dialogs(child))
            return dialogs

        active_dialogs = find_dialogs(self)
        
        # Filter duplicates (sometimes winfo_children returns toplevels multiple times)
        unique_dialogs = []
        seen_ids = set()
        for d in active_dialogs:
            if id(d) not in seen_ids:
                unique_dialogs.append(d)
                seen_ids.add(id(d))

        for dialog in unique_dialogs:
            # Check for various save methods
            save_method = None
            for m in ['save', 'sell', 'process_return']:
                if hasattr(dialog, m) and callable(getattr(dialog, m)):
                    save_method = getattr(dialog, m)
                    break
            
            if save_method:
                try:
                    save_method()
                    # If dialog still exists, it means validation failed
                    if dialog.winfo_exists():
                        all_saved = False
                except Exception as e:
                    print(f"Error saving dialog {dialog}: {e}")
                    all_saved = False
        
        return all_saved

    def perform_logout(self):
        """Actual logout logic"""
        log_audit(
            self.current_user, "SYSTEM", "LOGOUT",
            None, None, None, None,
            f"User {self.current_user} logout", "INFO"
        )
        self.show_login()

    def show_login(self):
        """Show login frame"""
        self.clear_window()
        self.current_user = None
        self.category_context = None
        
        self.login_frame = LoginFrame(self, self.on_login_success)
        self.login_frame.grid(row=0, column=0, sticky="nsew")
        self.current_frame = self.login_frame
    
    def on_login_success(self, username: str):
        """Handle successful login"""
        self.current_user = username
        self.show_category_select()
    
    def show_category_select(self):
        """Show category selection frame"""
        self.clear_window()
        
        self.category_frame = CategorySelectFrame(
            self, 
            self.current_user,
            self.on_category_selected
        )
        self.category_frame.grid(row=0, column=0, sticky="nsew")
        self.current_frame = self.category_frame
    
    def on_category_selected(self, category: str):
        """Handle category selection"""
        self.category_context = category
        log_audit(
            self.current_user, "SYSTEM", "LOGIN",
            None, None, None, None,
            f"User memilih kategori: {category}", "INFO"
        )
        self.show_main_app()
    
    def show_main_app(self):
        """Show main application with sidebar"""
        self.clear_window()
        
        # Configure grid for sidebar layout
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create content area
        self.content_frame = ctk.CTkFrame(self, fg_color="#0f0f23")
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_sidebar(self):
        """Create sidebar navigation"""
        self.sidebar = ctk.CTkFrame(self, fg_color="#1a1a2e", width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        # Logo/Title
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(fill="x", pady=(20, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="🏛️ KOPERASI",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00d4ff"
        ).pack()
        
        ctk.CTkLabel(
            title_frame,
            text="BRIMOB",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        ).pack()
        
        # Category indicator
        category_label = "Sembako" if self.category_context == "SEMBAKO" else "Taktikal"
        category_color = "#4ade80" if self.category_context == "SEMBAKO" else "#f59e0b"
        
        ctk.CTkLabel(
            title_frame,
            text=f"● {category_label}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=category_color
        ).pack(pady=(5, 0))
        
        # Separator
        ctk.CTkFrame(self.sidebar, fg_color="#333333", height=1).pack(fill="x", pady=15, padx=15)
        
        # Navigation buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("dashboard", "🏠 Dashboard", self.show_dashboard),
            ("store", "📦 Inventaris", self.show_store),
            ("history", "📋 Riwayat", self.show_history),
            ("members", "👥 Anggota", self.show_members),
            ("loans", "💰 Pinjaman", self.show_loans),
            ("financial", "📊 Neraca", self.show_financial),  # NEW: Financial Reports
        ]
        
        for key, text, command in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                width=190,
                height=45,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                hover_color="#2d2d4a",
                text_color="#cccccc",
                corner_radius=8,
                command=command
            )
            btn.pack(pady=3, padx=10)
            self.nav_buttons[key] = btn
        
        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent", height=20).pack(fill="x", expand=True)
        
        # User info at bottom
        user_frame = ctk.CTkFrame(self.sidebar, fg_color="#16213e", corner_radius=10)
        user_frame.pack(fill="x", padx=10, pady=10)
        
        # User icon with click handlers
        self.user_icon_label = ctk.CTkLabel(
            user_frame,
            text=f"👤 {self.current_user}",
            font=ctk.CTkFont(size=12),
            text_color="#cccccc",
            cursor="hand2"
        )
        self.user_icon_label.pack(pady=(10, 5))
        
        # Bind events for user icon
        # Single click - show dropdown menu (View Logs)
        self.user_icon_label.bind("<Button-1>", self.on_user_icon_click)
        # Ctrl+Click - Easter egg counter
        self.user_icon_label.bind("<Control-Button-1>", self.on_easter_egg_click)
        
        # Change category button - FIXED: Opens proper dialog
        ctk.CTkButton(
            user_frame,
            text="🔄 Ganti Divisi",
            width=170,
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color="#374151",
            hover_color="#4b5563",
            corner_radius=8,
            command=self.open_change_division_dialog
        ).pack(pady=5, padx=10)
        
        # Logout button
        ctk.CTkButton(
            user_frame,
            text="🚪 Logout",
            width=170,
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color="#ef4444",
            hover_color="#dc2626",
            corner_radius=8,
            command=self.logout
        ).pack(pady=(5, 10), padx=10)
    
    def open_change_division_dialog(self):
        """Open dialog to change division - FIXED geometry bug"""
        window_key = "change_division"
        if window_key in self.active_windows:
            try:
                self.active_windows[window_key].lift()
                self.active_windows[window_key].focus_force()
                return
            except:
                pass
        
        dialog = ChangeDivisionDialog(
            self,
            self.category_context,
            self.on_division_changed
        )
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_dialog(window_key))
    
    def close_dialog(self, window_key: str):
        """Close a dialog window"""
        if window_key in self.active_windows:
            try:
                self.active_windows[window_key].destroy()
            except:
                pass
            del self.active_windows[window_key]
    
    def on_division_changed(self, new_division: str):
        """Handle division change from dialog"""
        self.close_dialog("change_division")
        
        if new_division != self.category_context:
            self.category_context = new_division
            log_audit(
                self.current_user, "SYSTEM", "UPDATE",
                None, None, None, None,
                f"User ganti divisi ke: {new_division}", "INFO"
            )
            # Reload main app with new division
            self.show_main_app()
    
    def set_active_nav(self, active_key: str):
        """Highlight active navigation button"""
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(fg_color="#00d4ff", text_color="#000000")
            else:
                btn.configure(fg_color="transparent", text_color="#cccccc")
    
    def clear_content(self):
        """Clear content frame"""
        if self.content_frame:
            for widget in self.content_frame.winfo_children():
                widget.destroy()
    
    def clear_window(self):
        """Clear entire window"""
        for widget in self.winfo_children():
            widget.destroy()
        self.sidebar = None
        self.content_frame = None
    
    def show_dashboard(self):
        """Show dashboard frame"""
        self.clear_content()
        self.set_active_nav("dashboard")
        
        dashboard = DashboardFrame(
            self.content_frame,
            self.category_context,
            self.current_user
        )
        dashboard.grid(row=0, column=0, sticky="nsew")
    
    def show_store(self):
        """Show store/inventory frame"""
        self.clear_content()
        self.set_active_nav("store")
        
        store = StoreFrame(
            self.content_frame,
            self.category_context,
            self.current_user
        )
        store.grid(row=0, column=0, sticky="nsew")
    
    def show_history(self):
        """Show transaction history frame"""
        self.clear_content()
        self.set_active_nav("history")
        
        history = HistoryFrame(
            self.content_frame,
            self.category_context,
            self.current_user
        )
        history.grid(row=0, column=0, sticky="nsew")
    
    def show_members(self):
        """Show members frame"""
        self.clear_content()
        self.set_active_nav("members")
        
        members = MembersFrame(
            self.content_frame,
            self.current_user
        )
        members.grid(row=0, column=0, sticky="nsew")
    
    def show_loans(self):
        """Show loans frame"""
        self.clear_content()
        self.set_active_nav("loans")
        
        loans = LoansFrame(
            self.content_frame,
            self.current_user
        )
        loans.grid(row=0, column=0, sticky="nsew")
    
    def show_financial(self):
        """Show financial reports frame - NEW"""
        self.clear_content()
        self.set_active_nav("financial")
        
        financial = FinancialReportsFrame(
            self.content_frame,
            self.category_context,
            self.current_user
        )
        financial.grid(row=0, column=0, sticky="nsew")
    
    def logout(self):
        """Logout and return to login with custom confirmation"""
        self.handle_exit_logic(is_logout=True)
    
    def on_user_icon_click(self, event):
        """Handle single click on user icon - show dropdown menu"""
        window_key = "user_menu"
        if window_key in self.active_windows:
            self.close_dialog(window_key)
            return
        
        # Get screen position of click
        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty()
        
        from app.ui.admin_panel import UserIconMenu
        
        menu = UserIconMenu(
            self,
            x, y,
            self.current_user,
            on_view_logs=self.open_audit_logs,
            on_close=lambda: self.close_dialog(window_key)
        )
        self.active_windows[window_key] = menu
    
    def on_easter_egg_click(self, event):
        """Handle Ctrl+Click on user icon for Easter Egg reset"""
        self.easter_egg_clicks += 1
        
        # Reset counter after 2 seconds of inactivity
        if self.easter_egg_timer:
            self.after_cancel(self.easter_egg_timer)
        self.easter_egg_timer = self.after(2000, self.reset_easter_egg)
        
        # Check if we hit 5 Ctrl+Clicks
        if self.easter_egg_clicks >= 5:
            self.reset_easter_egg()
            self.open_danger_reset_modal()
    
    def reset_easter_egg(self):
        """Reset Easter Egg counter"""
        self.easter_egg_clicks = 0
        self.easter_egg_timer = None
    
    def open_audit_logs(self):
        """Open audit log viewer"""
        window_key = "audit_logs"
        if window_key in self.active_windows:
            try:
                self.active_windows[window_key].lift()
                self.active_windows[window_key].focus_force()
                return
            except:
                pass
        
        dialog = AuditLogViewer(self, self.current_user)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_dialog(window_key))
    
    def open_danger_reset_modal(self):
        """Open the hidden danger reset modal (Easter Egg)"""
        window_key = "danger_reset"
        if window_key in self.active_windows:
            try:
                self.active_windows[window_key].lift()
                self.active_windows[window_key].focus_force()
                return
            except:
                pass
        
        dialog = DangerResetModal(
            self,
            self.current_user,
            on_reset_complete=self.on_reset_complete
        )
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_dialog(window_key))
    
    def on_reset_complete(self):
        """Handle after data reset - reload current view"""
        self.close_dialog("danger_reset")
        # Reload main app to reflect changes
        self.show_main_app()


class CustomExitDialog(ctk.CTkToplevel):
    """Custom confirmation dialog with Save All, Exit Only, and Cancel options"""
    
    def __init__(self, parent, is_logout=False):
        super().__init__(parent)
        self.result = "cancel"
        
        action = "Logout" if is_logout else "Keluar"
        self.title(f"Konfirmasi {action}")
        self.configure(fg_color="#1a1a2e")
        self.resizable(False, False)
        
        # Center dialog
        self.update_idletasks()
        w, h = 450, 220
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (w // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        
        # UI Elements
        ctk.CTkLabel(
            self, text="⚠️ Konfirmasi Pekerjaan",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f59e0b"
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            self, 
            text=f"Apakah Anda ingin menyimpan semua perubahan sebelum {action.lower()}?",
            font=ctk.CTkFont(size=13),
            text_color="#ccc",
            wraplength=400
        ).pack(pady=10)
        
        # Buttons Frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        # Save & Proceed
        ctk.CTkButton(
            btn_frame, text="💾 Save All & Proceed",
            fg_color="#22c55e", hover_color="#16a34a",
            text_color="#000", font=ctk.CTkFont(weight="bold"),
            command=self.on_save_all
        ).pack(side="left", padx=5)
        
        # Proceed Only
        ctk.CTkButton(
            btn_frame, text=f"🚪 {action} Tanpa Simpan",
            fg_color="#ef4444", hover_color="#dc2626",
            command=self.on_proceed_only
        ).pack(side="left", padx=5)
        
        # Cancel
        ctk.CTkButton(
            btn_frame, text="Batal",
            fg_color="#374151", hover_color="#4b5563",
            command=self.destroy
        ).pack(side="left", padx=5)
        
        self.grab_set()
        self.focus_force()

    def on_save_all(self):
        self.result = "save_proceed"
        self.destroy()

    def on_proceed_only(self):
        self.result = "proceed_only"
        self.destroy()


def main():
    """Application entry point"""
    app = KoperasiBrimobApp()
    app.mainloop()


if __name__ == "__main__":
    main()
