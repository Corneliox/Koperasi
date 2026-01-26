"""
Category Select Frame - Choose between SEMBAKO or TAKTIKAL
REFACTORED: Fixed "Ganti Divisi" popup geometry bug
"""
import customtkinter as ctk


class CategorySelectFrame(ctk.CTkFrame):
    """Frame for selecting category (SEMBAKO/TAKTIKAL)"""
    
    def __init__(self, master, username: str, on_category_selected):
        super().__init__(master)
        self.username = username
        self.on_category_selected = on_category_selected
        
        self.configure(fg_color="transparent")
        
        # Center container
        self.center_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=20)
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Welcome
        self.welcome_label = ctk.CTkLabel(
            self.center_frame,
            text=f"Selamat Datang, {username}!",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00d4ff"
        )
        self.welcome_label.pack(pady=(40, 10))
        
        self.instruction_label = ctk.CTkLabel(
            self.center_frame,
            text="Pilih Divisi yang akan dikelola:",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        self.instruction_label.pack(pady=(0, 30))
        
        # Category buttons container
        self.buttons_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.buttons_frame.pack(pady=20, padx=40)
        
        # SEMBAKO Button
        self.sembako_frame = ctk.CTkFrame(self.buttons_frame, fg_color="#16213e", corner_radius=15)
        self.sembako_frame.grid(row=0, column=0, padx=15, pady=10)
        
        self.sembako_icon = ctk.CTkLabel(
            self.sembako_frame,
            text="🛒",
            font=ctk.CTkFont(size=48)
        )
        self.sembako_icon.pack(pady=(20, 10))
        
        self.sembako_title = ctk.CTkLabel(
            self.sembako_frame,
            text="SEMBAKO",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4ade80"
        )
        self.sembako_title.pack()
        
        self.sembako_desc = ctk.CTkLabel(
            self.sembako_frame,
            text="Kebutuhan Pokok\n& Sembilan Bahan Pokok",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            justify="center"
        )
        self.sembako_desc.pack(pady=(5, 10))
        
        self.sembako_button = ctk.CTkButton(
            self.sembako_frame,
            text="Pilih Sembako",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4ade80",
            hover_color="#22c55e",
            text_color="#000000",
            corner_radius=8,
            command=lambda: self.select_category("SEMBAKO")
        )
        self.sembako_button.pack(pady=(10, 20), padx=20)
        
        # TAKTIKAL Button
        self.taktikal_frame = ctk.CTkFrame(self.buttons_frame, fg_color="#16213e", corner_radius=15)
        self.taktikal_frame.grid(row=0, column=1, padx=15, pady=10)
        
        self.taktikal_icon = ctk.CTkLabel(
            self.taktikal_frame,
            text="🎯",
            font=ctk.CTkFont(size=48)
        )
        self.taktikal_icon.pack(pady=(20, 10))
        
        self.taktikal_title = ctk.CTkLabel(
            self.taktikal_frame,
            text="TAKTIKAL",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f59e0b"
        )
        self.taktikal_title.pack()
        
        self.taktikal_desc = ctk.CTkLabel(
            self.taktikal_frame,
            text="Perlengkapan Taktis\n& Peralatan Operasional",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            justify="center"
        )
        self.taktikal_desc.pack(pady=(5, 10))
        
        self.taktikal_button = ctk.CTkButton(
            self.taktikal_frame,
            text="Pilih Taktikal",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#f59e0b",
            hover_color="#d97706",
            text_color="#000000",
            corner_radius=8,
            command=lambda: self.select_category("TAKTIKAL")
        )
        self.taktikal_button.pack(pady=(10, 20), padx=20)
        
        # Logout button
        self.logout_button = ctk.CTkButton(
            self.center_frame,
            text="← Logout",
            width=100,
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color="#333333",
            text_color="#888888",
            border_width=1,
            border_color="#444444",
            corner_radius=8,
            command=self.logout
        )
        self.logout_button.pack(pady=(10, 30))
    
    def select_category(self, category: str):
        """Handle category selection"""
        self.on_category_selected(category)
    
    def logout(self):
        """Return to login"""
        # This will be handled by main app
        self.master.show_login()


class ChangeDivisionDialog(ctk.CTkToplevel):
    """
    Standalone dialog for changing division
    FIXED: Proper geometry handling to prevent tiny/cut-off window
    """
    
    def __init__(self, parent, current_division: str, on_change):
        super().__init__(parent)
        self.on_change = on_change
        self.current_division = current_division
        
        self.title("Ganti Divisi")
        self.configure(fg_color="#1a1a2e")
        self.resizable(False, False)
        
        # CRITICAL FIX: Call update_idletasks BEFORE setting geometry
        self.update_idletasks()
        
        # Set explicit window size
        window_width = 400
        window_height = 320
        
        # Calculate center of screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set geometry with size AND position
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Force minimum size
        self.minsize(window_width, window_height)
        
        self.create_content()
        self.grab_set()
        
        # Ensure window is visible and raised
        self.lift()
        self.focus_force()
    
    def create_content(self):
        """Create dialog content"""
        # Title
        ctk.CTkLabel(
            self,
            text="🔄 Ganti Divisi",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00d4ff"
        ).pack(pady=(30, 10))
        
        # Current division
        current_text = "SEMBAKO" if self.current_division == "SEMBAKO" else "TAKTIKAL"
        current_color = "#4ade80" if self.current_division == "SEMBAKO" else "#f59e0b"
        
        ctk.CTkLabel(
            self,
            text=f"Divisi saat ini: {current_text}",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        ).pack(pady=(0, 20))
        
        # Options
        ctk.CTkLabel(
            self,
            text="Pilih divisi baru:",
            font=ctk.CTkFont(size=14),
            text_color="#cccccc"
        ).pack(pady=(0, 15))
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        # SEMBAKO button
        sembako_btn = ctk.CTkButton(
            btn_frame,
            text="🛒 SEMBAKO",
            width=150,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4ade80" if self.current_division != "SEMBAKO" else "#22c55e",
            hover_color="#22c55e",
            text_color="#000000",
            corner_radius=10,
            command=lambda: self.change_to("SEMBAKO")
        )
        sembako_btn.pack(side="left", padx=10)
        
        # TAKTIKAL button
        taktikal_btn = ctk.CTkButton(
            btn_frame,
            text="🎯 TAKTIKAL",
            width=150,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#f59e0b" if self.current_division != "TAKTIKAL" else "#d97706",
            hover_color="#d97706",
            text_color="#000000",
            corner_radius=10,
            command=lambda: self.change_to("TAKTIKAL")
        )
        taktikal_btn.pack(side="left", padx=10)
        
        # Cancel button
        ctk.CTkButton(
            self,
            text="Batal",
            width=100,
            height=35,
            fg_color="#374151",
            hover_color="#4b5563",
            corner_radius=8,
            command=self.destroy
        ).pack(pady=20)
    
    def change_to(self, new_division: str):
        """Handle division change"""
        if new_division != self.current_division:
            self.on_change(new_division)
        self.destroy()
