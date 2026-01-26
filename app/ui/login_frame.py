"""
Login Frame - Admin Authentication UI
"""
import customtkinter as ctk
from app.database.connection import verify_login, log_activity


class LoginFrame(ctk.CTkFrame):
    """Login frame for admin authentication"""
    
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        
        self.configure(fg_color="transparent")
        
        # Center container
        self.center_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=20)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.center_frame,
            text="🏛️ KOPERASI BRIMOB",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#00d4ff"
        )
        self.title_label.pack(pady=(40, 10))
        
        self.subtitle_label = ctk.CTkLabel(
            self.center_frame,
            text="Sistem Manajemen Inventaris & Keuangan",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.subtitle_label.pack(pady=(0, 30))
        
        # Username
        self.username_label = ctk.CTkLabel(
            self.center_frame,
            text="Username",
            font=ctk.CTkFont(size=12),
            text_color="#cccccc"
        )
        self.username_label.pack(anchor="w", padx=40)
        
        self.username_entry = ctk.CTkEntry(
            self.center_frame,
            width=300,
            height=45,
            placeholder_text="Masukkan username",
            font=ctk.CTkFont(size=14),
            corner_radius=10
        )
        self.username_entry.pack(pady=(5, 15), padx=40)
        
        # Password
        self.password_label = ctk.CTkLabel(
            self.center_frame,
            text="Password",
            font=ctk.CTkFont(size=12),
            text_color="#cccccc"
        )
        self.password_label.pack(anchor="w", padx=40)
        
        self.password_entry = ctk.CTkEntry(
            self.center_frame,
            width=300,
            height=45,
            placeholder_text="Masukkan password",
            font=ctk.CTkFont(size=14),
            show="•",
            corner_radius=10
        )
        self.password_entry.pack(pady=(5, 20), padx=40)
        
        # Error message
        self.error_label = ctk.CTkLabel(
            self.center_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#ff4757"
        )
        self.error_label.pack()
        
        # Login button
        self.login_button = ctk.CTkButton(
            self.center_frame,
            text="MASUK",
            width=300,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#00d4ff",
            hover_color="#00a8cc",
            text_color="#000000",
            corner_radius=10,
            command=self.attempt_login
        )
        self.login_button.pack(pady=(10, 40), padx=40)
        
        # Bind Enter key
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.attempt_login())
        
        # Focus username on start
        self.after(100, lambda: self.username_entry.focus())
    
    def attempt_login(self):
        """Validate login credentials"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.show_error("Username dan password harus diisi!")
            return
        
        if verify_login(username, password):
            log_activity(username, "LOGIN", f"User {username} berhasil login")
            self.on_login_success(username)
        else:
            self.show_error("Username atau password salah!")
            self.password_entry.delete(0, "end")
    
    def show_error(self, message: str):
        """Display error message"""
        self.error_label.configure(text=message)
        self.after(3000, lambda: self.error_label.configure(text=""))
