"""
Login & Registration Frame - Local User Authentication & Recovery UI
"""
import customtkinter as ctk
import tkinter.messagebox as messagebox
from app.database.connection import (
    verify_login_detailed, 
    register_user, 
    has_registered_users, 
    log_activity,
    get_user_security_info,
    reset_password_with_security,
    reset_password_with_pin,
    update_legacy_user_credentials
)

SECURITY_QUESTIONS = [
    "Apa nama kota tempat Anda lahir?",
    "Siapa nama guru favorit masa kecil Anda?",
    "Apa nama hewan peliharaan pertama Anda?",
    "Apa makanan tradisional favorit Anda?",
    "Apa nama jalan tempat tinggal masa kecil Anda?"
]


class ForgotPasswordModal(ctk.CTkToplevel):
    """Modal dialog to recover account password using security question, PIN, or legacy credentials"""
    
    def __init__(self, parent, on_reset_success=None):
        super().__init__(parent)
        self.on_reset_success = on_reset_success
        self.title("🔑 Pemulihan Kata Sandi (Lupa Password)")
        self.geometry("460x560")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 460) // 2
        y = (self.winfo_screenheight() - 560) // 2
        self.geometry(f"+{x}+{y}")
        
        self.user_info = None
        self.create_widgets()
        
    def create_widgets(self):
        """Create recovery dialog widgets"""
        # Container
        self.main_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=15)
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        self.header_label = ctk.CTkLabel(
            self.main_frame,
            text="🔑 PEMULIHAN KATA SANDI",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00d4ff"
        )
        self.header_label.pack(pady=(20, 5))
        
        self.sub_label = ctk.CTkLabel(
            self.main_frame,
            text="Pemulihan akun mandiri 100% lokal & offline",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        self.sub_label.pack(pady=(0, 15))
        
        # Step 1: Find Username
        self.step1_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.step1_frame.pack(fill="x", padx=25, pady=(0, 10))
        
        self.u_label = ctk.CTkLabel(self.step1_frame, text="Username Akun:", font=ctk.CTkFont(size=12))
        self.u_label.pack(anchor="w")
        
        self.u_search_row = ctk.CTkFrame(self.step1_frame, fg_color="transparent")
        self.u_search_row.pack(fill="x", pady=(4, 0))
        
        self.username_entry = ctk.CTkEntry(
            self.u_search_row, 
            width=260, 
            height=38, 
            placeholder_text="Masukkan username Anda"
        )
        self.username_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        self.search_btn = ctk.CTkButton(
            self.u_search_row,
            text="Cari Akun",
            width=95,
            height=38,
            fg_color="#00d4ff",
            hover_color="#00a8cc",
            text_color="#000000",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.search_account
        )
        self.search_btn.pack(side="right")
        
        # Step 2: Verification Frame (Dynamic based on user status)
        self.step2_frame = ctk.CTkFrame(self.main_frame, fg_color="#24243e", corner_radius=10)
        self.step2_frame.pack(fill="both", expand=True, padx=25, pady=5)
        
        self.step2_placeholder = ctk.CTkLabel(
            self.step2_frame,
            text="Masukkan username Anda di atas lalu klik 'Cari Akun'",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.step2_placeholder.pack(expand=True, pady=40)
        
        # Bottom Close Button
        self.close_btn = ctk.CTkButton(
            self.main_frame,
            text="Tutup",
            width=120,
            height=34,
            fg_color="#33334d",
            hover_color="#444466",
            command=self.destroy
        )
        self.close_btn.pack(pady=(10, 15))
        
        self.username_entry.bind("<Return>", lambda e: self.search_account())
        self.after(100, lambda: self.username_entry.focus())
        
    def search_account(self):
        """Look up user security status"""
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Perhatian", "Masukkan username terlebih dahulu!", parent=self)
            return
            
        res = get_user_security_info(username)
        if not res['success']:
            messagebox.showerror("Tidak Ditemukan", res['message'], parent=self)
            return
            
        self.user_info = res
        self.render_step2()
        
    def render_step2(self):
        """Render step 2 fields based on security options"""
        for w in self.step2_frame.winfo_children():
            w.destroy()
            
        username = self.user_info['username']
        has_security = self.user_info['has_security']
        is_legacy = self.user_info['is_legacy']
        
        if is_legacy and not has_security:
            # Legacy User Upgrade & Reset View
            info_text = (
                f"ℹ️ Akun '{username}' terdeteksi dari versi sebelumnya.\n"
                "Silakan masukkan password lama Anda untuk mengatur password baru dan mengaktifkan pertanyaan keamanan."
            )
            ctk.CTkLabel(
                self.step2_frame,
                text=info_text,
                font=ctk.CTkFont(size=11),
                text_color="#f59e0b",
                wraplength=360,
                justify="left"
            ).pack(anchor="w", padx=15, pady=(12, 8))
            
            # Old Password
            ctk.CTkLabel(self.step2_frame, text="Password Lama / Bawaan:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15)
            self.old_pw_entry = ctk.CTkEntry(self.step2_frame, height=34, show="•", placeholder_text="Password lama (default: admin123)")
            self.old_pw_entry.pack(fill="x", padx=15, pady=(2, 8))
            
            # New Password
            ctk.CTkLabel(self.step2_frame, text="Password Baru:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15)
            self.new_pw_entry = ctk.CTkEntry(self.step2_frame, height=34, show="•", placeholder_text="Minimal 4 karakter")
            self.new_pw_entry.pack(fill="x", padx=15, pady=(2, 8))
            
            # Security Question
            ctk.CTkLabel(self.step2_frame, text="Pilih Pertanyaan Keamanan Baru:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15)
            self.legacy_q_combo = ctk.CTkComboBox(self.step2_frame, values=SECURITY_QUESTIONS, height=34)
            self.legacy_q_combo.pack(fill="x", padx=15, pady=(2, 8))
            
            # Security Answer
            ctk.CTkLabel(self.step2_frame, text="Jawaban Pertanyaan:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15)
            self.legacy_ans_entry = ctk.CTkEntry(self.step2_frame, height=34, placeholder_text="Jawaban pemulihan Anda")
            self.legacy_ans_entry.pack(fill="x", padx=15, pady=(2, 8))
            
            # Save Button
            save_btn = ctk.CTkButton(
                self.step2_frame,
                text="Simpan & Perbarui Akun",
                height=38,
                fg_color="#22c55e",
                hover_color="#16a34a",
                font=ctk.CTkFont(size=13, weight="bold"),
                command=self.submit_legacy_upgrade
            )
            save_btn.pack(fill="x", padx=15, pady=(10, 15))
            
        else:
            # Modern Account Recovery with Question or PIN
            ctk.CTkLabel(
                self.step2_frame,
                text=f"Pertanyaan Keamanan Akun ({username}):",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#00d4ff"
            ).pack(anchor="w", padx=15, pady=(10, 2))
            
            q_label = ctk.CTkLabel(
                self.step2_frame,
                text=f'"{self.user_info["security_question"]}"',
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#ffffff",
                wraplength=360,
                justify="left"
            )
            q_label.pack(anchor="w", padx=15, pady=(0, 8))
            
            # Answer Entry
            ctk.CTkLabel(self.step2_frame, text="Jawaban Anda:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15)
            self.ans_entry = ctk.CTkEntry(self.step2_frame, height=34, placeholder_text="Masukkan jawaban keamanan")
            self.ans_entry.pack(fill="x", padx=15, pady=(2, 6))
            
            # Optional PIN Entry
            if self.user_info.get('has_pin'):
                ctk.CTkLabel(self.step2_frame, text="ATAU Masukkan PIN Pemulihan 6-Digit:", font=ctk.CTkFont(size=11, slant="italic")).pack(anchor="w", padx=15)
                self.pin_entry = ctk.CTkEntry(self.step2_frame, height=34, placeholder_text="Contoh: 123456 (Jika ingat PIN)")
                self.pin_entry.pack(fill="x", padx=15, pady=(2, 6))
            else:
                self.pin_entry = None
                
            # New Password Entry
            ctk.CTkLabel(self.step2_frame, text="Password Baru:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15)
            self.new_pw_entry = ctk.CTkEntry(self.step2_frame, height=34, show="•", placeholder_text="Minimal 4 karakter")
            self.new_pw_entry.pack(fill="x", padx=15, pady=(2, 6))
            
            # Confirm Password Entry
            ctk.CTkLabel(self.step2_frame, text="Konfirmasi Password Baru:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=15)
            self.conf_pw_entry = ctk.CTkEntry(self.step2_frame, height=34, show="•", placeholder_text="Ulangi password baru")
            self.conf_pw_entry.pack(fill="x", padx=15, pady=(2, 10))
            
            # Submit Button
            submit_btn = ctk.CTkButton(
                self.step2_frame,
                text="Reset Password Sekarang",
                height=38,
                fg_color="#00d4ff",
                hover_color="#00a8cc",
                text_color="#000000",
                font=ctk.CTkFont(size=13, weight="bold"),
                command=self.submit_modern_reset
            )
            submit_btn.pack(fill="x", padx=15, pady=(5, 15))

    def submit_legacy_upgrade(self):
        """Handle legacy account password extraction and update"""
        username = self.user_info['username']
        old_pw = self.old_pw_entry.get().strip()
        new_pw = self.new_pw_entry.get().strip()
        sec_q = self.legacy_q_combo.get()
        sec_ans = self.legacy_ans_entry.get().strip()
        
        if not old_pw or not new_pw:
            messagebox.showwarning("Perhatian", "Password lama dan password baru wajib diisi!", parent=self)
            return
            
        if not sec_ans:
            messagebox.showwarning("Perhatian", "Jawaban pertanyaan keamanan wajib diisi!", parent=self)
            return
            
        res = update_legacy_user_credentials(username, old_pw, new_pw, sec_q, sec_ans)
        if res['success']:
            messagebox.showinfo("Berhasil", res['message'], parent=self)
            if self.on_reset_success:
                self.on_reset_success(username)
            self.destroy()
        else:
            messagebox.showerror("Gagal", res['message'], parent=self)

    def submit_modern_reset(self):
        """Handle modern password reset"""
        username = self.user_info['username']
        ans = self.ans_entry.get().strip()
        pin = self.pin_entry.get().strip() if self.pin_entry else ""
        new_pw = self.new_pw_entry.get().strip()
        conf_pw = self.conf_pw_entry.get().strip()
        
        if not ans and not pin:
            messagebox.showwarning("Perhatian", "Masukkan jawaban pertanyaan keamanan atau PIN pemulihan!", parent=self)
            return
            
        if not new_pw:
            messagebox.showwarning("Perhatian", "Masukkan password baru!", parent=self)
            return
            
        if new_pw != conf_pw:
            messagebox.showwarning("Perhatian", "Konfirmasi password baru tidak cocok!", parent=self)
            return
            
        if pin:
            res = reset_password_with_pin(username, pin, new_pw)
        else:
            res = reset_password_with_security(username, ans, new_pw)
            
        if res['success']:
            messagebox.showinfo("Sukses", res['message'], parent=self)
            if self.on_reset_success:
                self.on_reset_success(username)
            self.destroy()
        else:
            messagebox.showerror("Gagal", res['message'], parent=self)


class LegacySetupModal(ctk.CTkToplevel):
    """Modal shown when legacy user logs in, prompting them to protect their existing data"""
    
    def __init__(self, parent, username: str, on_complete=None):
        super().__init__(parent)
        self.username = username
        self.on_complete = on_complete
        
        self.title("🛡️ Pembaruan Keamanan Akun")
        self.geometry("450x510")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 450) // 2
        y = (self.winfo_screenheight() - 510) // 2
        self.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        
    def create_widgets(self):
        container = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=15)
        container.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            container,
            text="🛡️ AMANKAN AKUN ANDA",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00d4ff"
        ).pack(pady=(20, 5))
        
        desc = (
            f"Halo {self.username}! Akun Anda berhasil dimigrasikan ke Sistem Koperasi v4.3.\n"
            "Untuk melindungi data lama Anda dan mengaktifkan fitur Pemulihan Lupa Password, "
            "silakan atur pertanyaan keamanan dan PIN pemulihan Anda."
        )
        ctk.CTkLabel(
            container,
            text=desc,
            font=ctk.CTkFont(size=11),
            text_color="#cccccc",
            wraplength=380,
            justify="left"
        ).pack(padx=20, pady=(5, 15))
        
        # Security Question
        ctk.CTkLabel(container, text="Pilih Pertanyaan Keamanan:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.q_combo = ctk.CTkComboBox(container, values=SECURITY_QUESTIONS, height=36, width=380)
        self.q_combo.pack(padx=20, pady=(4, 10))
        
        # Answer
        ctk.CTkLabel(container, text="Jawaban Keamanan:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.ans_entry = ctk.CTkEntry(container, height=36, width=380, placeholder_text="Jawaban yang mudah Anda ingat")
        self.ans_entry.pack(padx=20, pady=(4, 10))
        
        # Recovery PIN
        ctk.CTkLabel(container, text="PIN Pemulihan (6 Digit Angka):", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.pin_entry = ctk.CTkEntry(container, height=36, width=380, placeholder_text="Contoh: 882149")
        self.pin_entry.pack(padx=20, pady=(4, 15))
        
        # Action Button
        save_btn = ctk.CTkButton(
            container,
            text="Simpan & Lanjutkan ke Aplikasi",
            height=44,
            width=380,
            fg_color="#22c55e",
            hover_color="#16a34a",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.save_security
        )
        save_btn.pack(padx=20, pady=(5, 20))
        
    def save_security(self):
        sec_q = self.q_combo.get().strip()
        sec_ans = self.ans_entry.get().strip()
        pin = self.pin_entry.get().strip()
        
        if not sec_ans:
            messagebox.showwarning("Perhatian", "Jawaban pertanyaan keamanan wajib diisi!", parent=self)
            return
            
        from app.database.connection import get_connection, hash_password
        conn = get_connection()
        try:
            cursor = conn.cursor()
            hashed_ans = hash_password(sec_ans.lower())
            hashed_pin = hash_password(pin) if pin else None
            cursor.execute(
                "UPDATE users SET security_question = ?, security_answer = ?, recovery_pin = ?, is_legacy = 0 WHERE username = ?",
                (sec_q, hashed_ans, hashed_pin, self.username)
            )
            conn.commit()
            messagebox.showinfo("Berhasil", "Keamanan akun Anda telah aktif!", parent=self)
            if self.on_complete:
                self.on_complete()
            self.destroy()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Gagal", f"Gagal menyimpan: {str(e)}", parent=self)
        finally:
            conn.close()


class LoginFrame(ctk.CTkFrame):
    """Authentication frame supporting Login, User Registration, and Password Recovery"""
    
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.mode = "login"  # "login" or "register"
        
        self.configure(fg_color="transparent")
        
        # Center container
        self.center_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=20, width=440)
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
        self.title_label.pack(pady=(25, 5))
        
        self.subtitle_label = ctk.CTkLabel(
            self.center_frame,
            text="Sistem Manajemen Inventaris & Keuangan (Lokal)",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.subtitle_label.pack(pady=(0, 15))
        
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
            width=340,
            height=38
        )
        self.tab_frame.pack(pady=(0, 10), padx=35)
        
        # Notice Banner
        self.notice_label = ctk.CTkLabel(
            self.center_frame,
            text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#4ade80",
            wraplength=360
        )
        self.notice_label.pack(pady=(0, 5))
        
        # Form Scrollable/Standard Container
        self.form_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.form_frame.pack(fill="x", padx=35)
        
        # Username Field
        self.username_label = ctk.CTkLabel(self.form_frame, text="Username", font=ctk.CTkFont(size=12), text_color="#cccccc")
        self.username_label.pack(anchor="w")
        
        self.username_entry = ctk.CTkEntry(self.form_frame, width=360, height=40, placeholder_text="Masukkan username", font=ctk.CTkFont(size=13), corner_radius=8)
        self.username_entry.pack(pady=(2, 10))
        
        # Password Field
        self.password_label = ctk.CTkLabel(self.form_frame, text="Password", font=ctk.CTkFont(size=12), text_color="#cccccc")
        self.password_label.pack(anchor="w")
        
        self.password_entry = ctk.CTkEntry(self.form_frame, width=360, height=40, placeholder_text="Masukkan password", font=ctk.CTkFont(size=13), show="•", corner_radius=8)
        self.password_entry.pack(pady=(2, 10))
        
        # Register-Only Fields
        self.reg_fields_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        
        # Confirm Password
        ctk.CTkLabel(self.reg_fields_frame, text="Konfirmasi Password", font=ctk.CTkFont(size=12), text_color="#cccccc").pack(anchor="w")
        self.confirm_pw_entry = ctk.CTkEntry(self.reg_fields_frame, width=360, height=40, placeholder_text="Ulangi password", font=ctk.CTkFont(size=13), show="•", corner_radius=8)
        self.confirm_pw_entry.pack(pady=(2, 10))
        
        # Security Question
        ctk.CTkLabel(self.reg_fields_frame, text="Pertanyaan Pemulihan Sandi:", font=ctk.CTkFont(size=12), text_color="#cccccc").pack(anchor="w")
        self.sec_q_combo = ctk.CTkComboBox(self.reg_fields_frame, values=SECURITY_QUESTIONS, width=360, height=38, corner_radius=8)
        self.sec_q_combo.pack(pady=(2, 10))
        
        # Security Answer
        ctk.CTkLabel(self.reg_fields_frame, text="Jawaban Pertanyaan:", font=ctk.CTkFont(size=12), text_color="#cccccc").pack(anchor="w")
        self.sec_ans_entry = ctk.CTkEntry(self.reg_fields_frame, width=360, height=40, placeholder_text="Jawaban pemulihan", font=ctk.CTkFont(size=13), corner_radius=8)
        self.sec_ans_entry.pack(pady=(2, 10))
        
        # Status Message
        self.msg_label = ctk.CTkLabel(self.center_frame, text="", font=ctk.CTkFont(size=12), text_color="#ff4757", wraplength=360)
        self.msg_label.pack(pady=(2, 2))
        
        # Action Button (MASUK / DAFTAR AKUN)
        self.action_button = ctk.CTkButton(
            self.center_frame,
            text="MASUK",
            width=360,
            height=44,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#00d4ff",
            hover_color="#00a8cc",
            text_color="#000000",
            corner_radius=8,
            command=self.handle_action
        )
        self.action_button.pack(pady=(8, 10), padx=35)
        
        # Forgot Password Link (Only in Login Mode)
        self.forgot_pw_btn = ctk.CTkButton(
            self.center_frame,
            text="❓ Lupa Password atau Pemulihan Akun Lama?",
            font=ctk.CTkFont(size=11, underline=True),
            fg_color="transparent",
            hover_color="#24243e",
            text_color="#94a3b8",
            command=self.open_forgot_password
        )
        self.forgot_pw_btn.pack(pady=(0, 20))
        
        # Key bindings
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.handle_action())

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
            self.reg_fields_frame.pack(fill="x")
            self.forgot_pw_btn.pack_forget()
            
            if is_initial_setup:
                self.notice_label.configure(
                    text="👋 Setup Awal: Silakan daftarkan akun Administrator pertama Anda.",
                    text_color="#4ade80"
                )
            else:
                self.notice_label.configure(text="")
        else:
            self.tab_frame.set("🔐 Masuk")
            self.action_button.configure(text="MASUK", fg_color="#00d4ff", hover_color="#00a8cc")
            self.reg_fields_frame.pack_forget()
            self.forgot_pw_btn.pack(pady=(0, 20))
            self.notice_label.configure(text="")
            
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.confirm_pw_entry.delete(0, "end")
        self.sec_ans_entry.delete(0, "end")
        self.after(100, lambda: self.username_entry.focus())

    def open_forgot_password(self):
        """Open the Forgot Password modal"""
        def on_reset(username):
            self.set_mode("login")
            self.username_entry.insert(0, username)
            self.show_message("Password berhasil diperbarui! Silakan masuk.", is_error=False)
            self.password_entry.focus()
            
        ForgotPasswordModal(self.winfo_toplevel(), on_reset_success=on_reset)

    def handle_action(self):
        """Dispatch action based on current mode"""
        if self.mode == "register":
            self.attempt_register()
        else:
            self.attempt_login()

    def attempt_login(self):
        """Validate login credentials & detect legacy users"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.show_message("Username dan password harus diisi!", is_error=True)
            return
            
        result = verify_login_detailed(username, password)
        if result['success']:
            log_activity(username, "LOGIN", f"User {username} berhasil login")
            
            # If user needs security setup (legacy user migration)
            if result.get('needs_security_setup'):
                def proceed():
                    self.on_login_success(username)
                LegacySetupModal(self.winfo_toplevel(), username, on_complete=proceed)
            else:
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
        sec_q = self.sec_q_combo.get().strip()
        sec_ans = self.sec_ans_entry.get().strip()
        
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
            
        if not sec_ans:
            self.show_message("Jawaban pertanyaan pemulihan wajib diisi!", is_error=True)
            self.sec_ans_entry.focus()
            return
            
        result = register_user(
            username=username,
            password=password,
            security_question=sec_q,
            security_answer=sec_ans
        )
        if result['success']:
            self.show_message("Pendaftaran berhasil! Mengalihkan ke aplikasi...", is_error=False)
            self.after(1000, lambda: self.on_login_success(username))
        else:
            self.show_message(result['message'], is_error=True)

    def show_message(self, message: str, is_error: bool = True):
        """Display error or success message"""
        color = "#ff4757" if is_error else "#4ade80"
        self.msg_label.configure(text=message, text_color=color)
        if is_error:
            self.after(4000, lambda: self.msg_label.configure(text=""))

