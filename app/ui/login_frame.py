"""
Login & Registration Frame - Local User Authentication UI
"""
import customtkinter as ctk
from app.database.connection import verify_login, register_user, has_registered_users, log_activity


class LoginFrame(ctk.CTkFrame):
    """Authentication frame supporting Login and User Registration"""
    
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.mode = "login"  # "login" or "register"
        
        self.configure(fg_color="transparent")
        
        # Center container
        self.center_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=20, width=420)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.create_widgets()
        
        # Check if any user exists. If not, auto-switch to registration mode!
        if not has_registered_users():
            self.set_mode("register", is_initial_setup=True)
        else:
            self.set_mode("login")
            
    def create_widgets(self):
        """Create all login and register UI widgets"""
        # Header Branding
        self.title_label = ctk.CTkLabel(
            self.center_frame,
            text="🏛️ SISTEM KOPERASI",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#00d4ff"
        )
        self.title_label.pack(pady=(30, 5))
        
        self.subtitle_label = ctk.CTkLabel(
            self.center_frame,
            text="Sistem Manajemen Inventaris & Keuangan (Lokal)",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.subtitle_label.pack(pady=(0, 20))
        
        # Mode Switcher (Tab)
        self.tab_frame = ctk.CTkSegmentedButton(
            self.center_frame,
            values=["🔐 Masuk", "📝 Daftar Akun"],
            command=self.on_tab_changed,
            font=ctk.CTkFont(size=13, weight="bold"),
            selected_color="#00d4ff",
            selected_hover_color="#00a8cc",
            unselected_color="#262640",
            unselected_hover_color="#323254",
            text_color="#ffffff",
            width=320,
            height=38
        )
        self.tab_frame.pack(pady=(0, 15), padx=40)
        
        # Notice Banner (e.g. for Initial Setup)
        self.notice_label = ctk.CTkLabel(
            self.center_frame,
            text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#4ade80",
            wraplength=340
        )
        self.notice_label.pack(pady=(0, 5))
        
        # Form Container
        self.form_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.form_frame.pack(fill="x", padx=40)
        
        # Username Field
        self.username_label = ctk.CTkLabel(
            self.form_frame,
            text="Username",
            font=ctk.CTkFont(size=12),
            text_color="#cccccc"
        )
        self.username_label.pack(anchor="w")
        
        self.username_entry = ctk.CTkEntry(
            self.form_frame,
            width=340,
            height=42,
            placeholder_text="Masukkan username",
            font=ctk.CTkFont(size=13),
            corner_radius=8
        )
        self.username_entry.pack(pady=(4, 12))
        
        # Password Field
        self.password_label = ctk.CTkLabel(
            self.form_frame,
            text="Password",
            font=ctk.CTkFont(size=12),
            text_color="#cccccc"
        )
        self.password_label.pack(anchor="w")
        
        self.password_entry = ctk.CTkEntry(
            self.form_frame,
            width=340,
            height=42,
            placeholder_text="Masukkan password",
            font=ctk.CTkFont(size=13),
            show="•",
            corner_radius=8
        )
        self.password_entry.pack(pady=(4, 12))
        
        # Confirm Password Field (Only in Register Mode)
        self.confirm_pw_label = ctk.CTkLabel(
            self.form_frame,
            text="Konfirmasi Password",
            font=ctk.CTkFont(size=12),
            text_color="#cccccc"
        )
        
        self.confirm_pw_entry = ctk.CTkEntry(
            self.form_frame,
            width=340,
            height=42,
            placeholder_text="Ulangi password",
            font=ctk.CTkFont(size=13),
            show="•",
            corner_radius=8
        )
        
        # Status / Feedback Message
        self.msg_label = ctk.CTkLabel(
            self.center_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#ff4757",
            wraplength=340
        )
        self.msg_label.pack(pady=(5, 5))
        
        # Action Button (MASUK / DAFTAR AKUN)
        self.action_button = ctk.CTkButton(
            self.center_frame,
            text="MASUK",
            width=340,
            height=46,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#00d4ff",
            hover_color="#00a8cc",
            text_color="#000000",
            corner_radius=8,
            command=self.handle_action
        )
        self.action_button.pack(pady=(10, 30), padx=40)
        
        # Key bindings
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.on_password_enter())
        self.confirm_pw_entry.bind("<Return>", lambda e: self.handle_action())

    def on_password_enter(self):
        """Handle Enter on password field based on mode"""
        if self.mode == "register":
            self.confirm_pw_entry.focus()
        else:
            self.handle_action()

    def on_tab_changed(self, value):
        """Handle tab button click"""
        if "Daftar" in value:
            self.set_mode("register")
        else:
            self.set_mode("login")

    def set_mode(self, mode: str, is_initial_setup: bool = False):
        """Switch between login and register UI states"""
        self.mode = mode
        self.msg_label.configure(text="")
        
        if mode == "register":
            self.tab_frame.set("📝 Daftar Akun")
            self.action_button.configure(text="DAFTAR SEKARANG", fg_color="#22c55e", hover_color="#16a34a")
            self.confirm_pw_label.pack(anchor="w", before=self.form_frame.winfo_children()[-1])
            self.confirm_pw_entry.pack(pady=(4, 12), before=self.form_frame.winfo_children()[-1])
            
            if is_initial_setup:
                self.notice_label.configure(
                    text="👋 Setup Awal: Silakan buat akun Administrator pertama Anda.",
                    text_color="#4ade80"
                )
            else:
                self.notice_label.configure(text="")
        else:
            self.tab_frame.set("🔐 Masuk")
            self.action_button.configure(text="MASUK", fg_color="#00d4ff", hover_color="#00a8cc")
            self.confirm_pw_label.pack_forget()
            self.confirm_pw_entry.pack_forget()
            self.notice_label.configure(text="")
            
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.confirm_pw_entry.delete(0, "end")
        self.after(100, lambda: self.username_entry.focus())

    def handle_action(self):
        """Dispatch action based on current mode"""
        if self.mode == "register":
            self.attempt_register()
        else:
            self.attempt_login()

    def attempt_login(self):
        """Validate login credentials"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.show_message("Username dan password harus diisi!", is_error=True)
            return
        
        if verify_login(username, password):
            log_activity(username, "LOGIN", f"User {username} berhasil login")
            self.on_login_success(username)
        else:
            self.show_message("Username atau password salah!", is_error=True)
            self.password_entry.delete(0, "end")
            self.password_entry.focus()

    def attempt_register(self):
        """Validate and create new account"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_pw = self.confirm_pw_entry.get().strip()
        
        if not username or not password:
            self.show_message("Username dan password wajib diisi!", is_error=True)
            return
            
        if len(username) < 3:
            self.show_message("Username minimal 3 karakter!", is_error=True)
            return
            
        if len(password) < 4:
            self.show_message("Password minimal 4 karakter!", is_error=True)
            return
            
        if password != confirm_pw:
            self.show_message("Konfirmasi password tidak cocok!", is_error=True)
            self.confirm_pw_entry.delete(0, "end")
            self.confirm_pw_entry.focus()
            return
            
        result = register_user(username, password)
        if result['success']:
            self.show_message("Pendaftaran berhasil! Mengalihkan ke aplikasi...", is_error=False)
            # Auto login immediately after successful registration
            self.after(1000, lambda: self.on_login_success(username))
        else:
            self.show_message(result['message'], is_error=True)

    def show_message(self, message: str, is_error: bool = True):
        """Display error or success message"""
        color = "#ff4757" if is_error else "#4ade80"
        self.msg_label.configure(text=message, text_color=color)
        if is_error:
            self.after(4000, lambda: self.msg_label.configure(text=""))
