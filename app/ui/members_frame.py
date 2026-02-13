"""
Members Frame - Member Management UI
REFACTORED: Added fuzzy search for duplicate detection on new member registration
"""
import customtkinter as ctk
from tkinter import messagebox
from app.modules.members import MemberManager


class MembersFrame(ctk.CTkFrame):
    """Member management frame"""
    
    def __init__(self, master, current_user: str):
        super().__init__(master)
        self.current_user = current_user
        self.member_manager = MemberManager(current_user)
        
        self.active_windows = {}
        
        self.configure(fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.create_header()
        self.create_table()
        self.load_data()
    
    def create_header(self):
        """Create header section"""
        self.header_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="👥 Manajemen Anggota",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00d4ff"
        )
        self.title_label.pack(side="left", padx=20, pady=15)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=20, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            btn_frame, width=200, height=35,
            placeholder_text="🔍 Cari anggota...",
            corner_radius=8
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_members())
        
        self.refresh_btn = ctk.CTkButton(
            btn_frame, text="🔄 Refresh", width=100, height=35,
            fg_color="#374151", hover_color="#4b5563",
            corner_radius=8, command=self.refresh_data
        )
        self.refresh_btn.pack(side="left", padx=5)
        
        self.add_btn = ctk.CTkButton(
            btn_frame, text="➕ Tambah Anggota", width=150, height=35,
            fg_color="#4ade80", hover_color="#22c55e",
            text_color="#000000", corner_radius=8,
            command=self.open_add_dialog
        )
        self.add_btn.pack(side="left", padx=5)
    
    def create_table(self):
        """Create members table"""
        self.table_container = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.table_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=1)
        
        # Header row
        self.header_row = ctk.CTkFrame(self.table_container, fg_color="#16213e", height=45)
        self.header_row.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header_row.grid_propagate(False)
        
        # Column config: (name, min_width, weight)
        self.columns_config = [
            ("ID", 50, 0),
            ("Nama", 200, 3),    # Stretches most
            ("Pangkat", 100, 1), # Stretches a bit
            ("Satuan", 120, 1),  # Stretches a bit
            ("NRP", 100, 0),
            ("Telepon", 110, 0),
            ("Aksi", 120, 0)
        ]
        
        for i, (text, width, weight) in enumerate(self.columns_config):
            self.header_row.grid_columnconfigure(i, minsize=width, weight=weight)
            label = ctk.CTkLabel(
                self.header_row, text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#00d4ff"
            )
            label.grid(row=0, column=i, padx=5, pady=10, sticky="w")
        
        # Scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.table_container, fg_color="transparent"
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        for i, (_, width, weight) in enumerate(self.columns_config):
            self.scroll_frame.grid_columnconfigure(i, minsize=width, weight=weight)
    
    def load_data(self, search_term: str = None):
        """Load members into table"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        members = self.member_manager.get_all_members(search_term)
        
        if not members:
            no_data = ctk.CTkLabel(
                self.scroll_frame, text="Tidak ada data anggota",
                font=ctk.CTkFont(size=14), text_color="#888888"
            )
            no_data.grid(row=0, column=0, columnspan=7, pady=50)
            return
        
        for idx, member in enumerate(members):
            self.create_row(idx, member)
    
    def create_row(self, row_idx: int, member: dict):
        """Create a member row"""
        bg_color = "#1e293b" if row_idx % 2 == 0 else "#16213e"
        
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, height=45, corner_radius=5)
        row_frame.grid(row=row_idx, column=0, columnspan=7, sticky="ew", pady=1)
        row_frame.grid_propagate(False)
        
        for i, (_, width, weight) in enumerate(self.columns_config):
            row_frame.grid_columnconfigure(i, minsize=width, weight=weight)
        
        # Data cells
        ctk.CTkLabel(row_frame, text=str(member['id']),
                     font=ctk.CTkFont(size=11), text_color="#cccccc"
                     ).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        
        ctk.CTkLabel(row_frame, text=member['name'][:25],
                     font=ctk.CTkFont(size=11), text_color="#ffffff"
                     ).grid(row=0, column=1, padx=5, pady=8, sticky="w")
        
        ctk.CTkLabel(row_frame, text=member.get('rank', '-') or '-',
                     font=ctk.CTkFont(size=11), text_color="#cccccc"
                     ).grid(row=0, column=2, padx=5, pady=8, sticky="w")
        
        ctk.CTkLabel(row_frame, text=member.get('unit', '-') or '-',
                     font=ctk.CTkFont(size=11), text_color="#cccccc"
                     ).grid(row=0, column=3, padx=5, pady=8, sticky="w")
        
        ctk.CTkLabel(row_frame, text=member.get('nrp', '-') or '-',
                     font=ctk.CTkFont(size=11), text_color="#00d4ff"
                     ).grid(row=0, column=4, padx=5, pady=8, sticky="w")
        
        ctk.CTkLabel(row_frame, text=member.get('phone', '-') or '-',
                     font=ctk.CTkFont(size=11), text_color="#cccccc"
                     ).grid(row=0, column=5, padx=5, pady=8, sticky="w")
        
        # Action buttons
        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        action_frame.grid(row=0, column=6, padx=5, pady=5, sticky="w")
        
        edit_btn = ctk.CTkButton(
            action_frame, text="✏️", width=35, height=30,
            fg_color="#3b82f6", hover_color="#2563eb",
            corner_radius=5, command=lambda m=member: self.open_edit_dialog(m)
        )
        edit_btn.pack(side="left", padx=2)
        
        delete_btn = ctk.CTkButton(
            action_frame, text="🗑️", width=35, height=30,
            fg_color="#ef4444", hover_color="#dc2626",
            corner_radius=5, command=lambda m=member: self.delete_member(m)
        )
        delete_btn.pack(side="left", padx=2)
    
    def search_members(self):
        """Search members"""
        search = self.search_entry.get().strip()
        self.load_data(search if search else None)
    
    def refresh_data(self):
        """Refresh table"""
        self.search_entry.delete(0, "end")
        self.load_data()
    
    def open_add_dialog(self):
        """Open add member dialog"""
        window_key = "add_member"
        if window_key in self.active_windows:
            self.active_windows[window_key].lift()
            return
        
        dialog = MemberDialog(self, "Tambah Anggota Baru", self.on_member_saved, 
                             member_manager=self.member_manager)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def open_edit_dialog(self, member: dict):
        """Open edit member dialog"""
        window_key = f"edit_member_{member['id']}"
        if window_key in self.active_windows:
            self.active_windows[window_key].lift()
            return
        
        dialog = MemberDialog(self, f"Edit: {member['name']}", self.on_member_saved, 
                             member, member_manager=self.member_manager)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def close_window(self, window_key: str):
        """Close window"""
        if window_key in self.active_windows:
            self.active_windows[window_key].destroy()
            del self.active_windows[window_key]
    
    def on_member_saved(self, data: dict, member_id: int = None):
        """Handle member save"""
        if member_id:
            result = self.member_manager.update_member(
                member_id, data['name'], data['rank'], data['unit'],
                data['nrp'], data['phone'], data['address'], data['membership_status']
            )
            self.close_window(f"edit_member_{member_id}")
        else:
            result = self.member_manager.add_member(
                data['name'], data['rank'], data['unit'],
                data['nrp'], data['phone'], data['address'], data['membership_status']
            )
            self.close_window("add_member")
        
        if result['success']:
            self.load_data()
        else:
            messagebox.showerror("Error", result['message'])
    
    def delete_member(self, member: dict):
        """Delete member"""
        if messagebox.askyesno("Konfirmasi", f"Hapus anggota '{member['name']}'?"):
            result = self.member_manager.delete_member(member['id'])
            if result['success']:
                self.load_data()
            else:
                messagebox.showerror("Error", result['message'])


class MemberDialog(ctk.CTkToplevel):
    """
    Dialog for adding/editing members
    REFACTORED: Added fuzzy search duplicate detection for new members
    WIN7 FIXED: Added transient, lifted focus, and forced geometry
    """
    
    def __init__(self, parent, title: str, on_save, member: dict = None, member_manager=None):
        super().__init__(parent)
        self.on_save = on_save
        self.member = member
        self.member_manager = member_manager
        self.duplicate_confirmed = False
        
        self.title(title)
        self.configure(fg_color="#1a1a2e")
        self.resizable(True, True)
        self.minsize(450, 600)
        
        # Win7 Compatibility: Set transient and lift
        self.transient(parent)
        self.lift()
        
        self.update_idletasks()
        
        window_width = 480
        window_height = 680
        x = (self.winfo_screenwidth() - window_width) // 2
        y = (self.winfo_screenheight() - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Win7 Compatibility: Re-apply geometry to ensure it shows
        import sys
        if sys.platform == 'win32' and sys.getwindowsversion().major == 6:
            self.after(200, lambda: self.geometry(f"{window_width}x{window_height}+{x}+{y}"))
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Scrollable container
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.create_form()
        if member:
            self.populate_form()
        
        # Bind events for auto-save
        self.bind_auto_save()
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.grab_set()
        self.focus_force()
    
    def bind_auto_save(self):
        """Bind input fields to auto-save on focus out"""
        self.name_entry.bind("<FocusOut>", lambda e: self.auto_save(), add="+")
        self.rank_entry.bind("<FocusOut>", lambda e: self.auto_save())
        self.unit_entry.bind("<FocusOut>", lambda e: self.auto_save())
        self.nrp_entry.bind("<FocusOut>", lambda e: self.auto_save())
        self.phone_entry.bind("<FocusOut>", lambda e: self.auto_save())
        self.address_text.bind("<FocusOut>", lambda e: self.auto_save())

    def auto_save(self):
        """Silently save data as user moves between fields"""
        name = self.name_entry.get().strip()
        if not name or len(name) < 2: # Don't auto-save empty/short names
            return
            
        data = {
            'name': name,
            'rank': self.rank_entry.get().strip(),
            'unit': self.unit_entry.get().strip(),
            'nrp': self.nrp_entry.get().strip(),
            'phone': self.phone_entry.get().strip(),
            'address': self.address_text.get("1.0", "end-1c").strip(),
            'membership_status': self.membership_status_var.get()
        }
        
        # If new member and we have a name, create it
        if not self.member:
            result = self.member_manager.add_member(
                data['name'], data['rank'], data['unit'],
                data['nrp'], data['phone'], data['address'],
                data['membership_status']
            )
            if result['success']:
                # Now it's an existing member for subsequent auto-saves
                self.member = self.member_manager.get_member_by_id(result['id'])
                self.duplicate_confirmed = True # Since it's created
        else:
            # Update existing
            self.member_manager.update_member(
                self.member['id'], data['name'], data['rank'], data['unit'],
                data['nrp'], data['phone'], data['address'],
                data['membership_status']
            )

    def on_closing(self):
        """Ask to save before closing"""
        # Simple check for empty name to avoid unnecessary prompts on empty dialogs
        if not self.name_entry.get().strip():
            self.destroy()
            return

        response = messagebox.askyesnocancel("Simpan Perubahan", "Apakah Anda ingin menyimpan perubahan sebelum keluar?")
        if response is True: # Yes
            self.save()
        elif response is False: # No
            self.destroy()
        # If None (Cancel), do nothing

    def create_form(self):
        """Create form fields with duplicate warning area"""
        # Name
        ctk.CTkLabel(self.scroll_frame, text="Nama Lengkap *", text_color="#cccccc"
                     ).pack(anchor="w", padx=20, pady=(20, 5))
        self.name_entry = ctk.CTkEntry(self.scroll_frame, width=400, height=40, corner_radius=8)
        self.name_entry.pack(padx=20)
        
        # Bind name entry for duplicate check (only for new members)
        if not self.member:
            self.name_entry.bind("<FocusOut>", self.check_duplicate_name, add="+")
        
        # Status Keanggotaan (NEW)
        ctk.CTkLabel(self.scroll_frame, text="Status Keanggotaan Koperasi", text_color="#cccccc"
                     ).pack(anchor="w", padx=20, pady=(15, 5))
        self.membership_status_var = ctk.StringVar(value="Anggota Koperasi")
        status_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        status_frame.pack(padx=20, anchor="w")
        
        self.radio_anggota = ctk.CTkRadioButton(
            status_frame, text="Anggota Koperasi", variable=self.membership_status_var, 
            value="Anggota Koperasi", command=self.auto_save
        )
        self.radio_anggota.pack(side="left", padx=(0, 20))
        
        self.radio_umum = ctk.CTkRadioButton(
            status_frame, text="Umum", variable=self.membership_status_var, 
            value="Umum", command=self.auto_save
        )
        self.radio_umum.pack(side="left")

        # Duplicate warning frame (hidden by default)
        self.warning_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#7f1d1d", corner_radius=8)
        self.warning_label = ctk.CTkLabel(
            self.warning_frame, text="",
            font=ctk.CTkFont(size=11), text_color="#fecaca",
            wraplength=360
        )
        self.warning_label.pack(padx=15, pady=10)
        
        # Confirm button for duplicates
        self.confirm_dup_btn = ctk.CTkButton(
            self.warning_frame, text="Tetap Buat Baru",
            width=130, height=30,
            fg_color="#f59e0b", hover_color="#d97706",
            text_color="#000",
            command=self.confirm_duplicate
        )
        self.confirm_dup_btn.pack(pady=(0, 10))
        
        # Rank
        ctk.CTkLabel(self.scroll_frame, text="Pangkat", text_color="#cccccc"
                     ).pack(anchor="w", padx=20, pady=(15, 5))
        self.rank_entry = ctk.CTkEntry(self.scroll_frame, width=400, height=40, corner_radius=8,
                                       placeholder_text="Contoh: Bripka, Briptu, IPDA")
        self.rank_entry.pack(padx=20)
        
        # Unit
        ctk.CTkLabel(self.scroll_frame, text="Satuan/Unit", text_color="#cccccc"
                     ).pack(anchor="w", padx=20, pady=(15, 5))
        self.unit_entry = ctk.CTkEntry(self.scroll_frame, width=400, height=40, corner_radius=8,
                                       placeholder_text="Contoh: Detasemen A, Detasemen B")
        self.unit_entry.pack(padx=20)
        
        # NRP
        ctk.CTkLabel(self.scroll_frame, text="NRP", text_color="#cccccc"
                     ).pack(anchor="w", padx=20, pady=(15, 5))
        self.nrp_entry = ctk.CTkEntry(self.scroll_frame, width=400, height=40, corner_radius=8)
        self.nrp_entry.pack(padx=20)
        
        # Phone
        ctk.CTkLabel(self.scroll_frame, text="No. Telepon", text_color="#cccccc"
                     ).pack(anchor="w", padx=20, pady=(15, 5))
        self.phone_entry = ctk.CTkEntry(self.scroll_frame, width=400, height=40, corner_radius=8)
        self.phone_entry.pack(padx=20)
        
        # Address
        ctk.CTkLabel(self.scroll_frame, text="Alamat", text_color="#cccccc"
                     ).pack(anchor="w", padx=20, pady=(15, 5))
        self.address_text = ctk.CTkTextbox(self.scroll_frame, width=400, height=60, corner_radius=8)
        self.address_text.pack(padx=20)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        btn_frame.pack(pady=25)
        
        ctk.CTkButton(
            btn_frame, text="Batal", width=100, height=40,
            fg_color="#374151", hover_color="#4b5563",
            command=self.destroy
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, text="💾 Simpan", width=100, height=40,
            fg_color="#4ade80", hover_color="#22c55e",
            text_color="#000000", command=self.save
        ).pack(side="left", padx=10)
    
    def check_duplicate_name(self, event=None):
        """Check for duplicate/similar names (fuzzy search)"""
        name = self.name_entry.get().strip()
        nrp = self.nrp_entry.get().strip()
        
        if not name or len(name) < 3 or not self.member_manager:
            self.warning_frame.pack_forget()
            return
        
        result = self.member_manager.check_duplicate_before_create(name, nrp)
        
        if result['has_duplicate']:
            if result['exact_match']:
                match = result['exact_match']
                warning_text = (
                    f"⚠️ DUPLIKAT TERDETEKSI!\n\n"
                    f"Anggota dengan data serupa sudah ada:\n"
                    f"• {match['name']} ({match.get('nrp', '-')})\n"
                    f"• Unit: {match.get('unit', '-')}"
                )
            elif result['similar_matches']:
                matches = result['similar_matches'][:3]
                match_text = "\n".join([
                    f"• {m['member']['name']} - {m['similarity']} mirip" 
                    for m in matches
                ])
                warning_text = (
                    f"⚠️ NAMA MIRIP DITEMUKAN!\n\n"
                    f"Anggota dengan nama serupa:\n{match_text}\n\n"
                    f"Apakah ini orang yang sama?"
                )
            
            self.warning_label.configure(text=warning_text)
            self.warning_frame.pack(padx=20, pady=10, fill="x")
            self.duplicate_confirmed = False
        else:
            self.warning_frame.pack_forget()
            self.duplicate_confirmed = True
    
    def confirm_duplicate(self):
        """User confirms they want to create despite duplicate warning"""
        self.duplicate_confirmed = True
        self.warning_frame.pack_forget()
        messagebox.showinfo("OK", "Anda dapat melanjutkan pendaftaran.")
    
    def populate_form(self):
        """Populate with existing data"""
        self.name_entry.insert(0, self.member['name'])
        if self.member.get('membership_status'):
            self.membership_status_var.set(self.member['membership_status'])
        if self.member.get('rank'):
            self.rank_entry.insert(0, self.member['rank'])
        if self.member.get('unit'):
            self.unit_entry.insert(0, self.member['unit'])
        if self.member.get('nrp'):
            self.nrp_entry.insert(0, self.member['nrp'])
        if self.member.get('phone'):
            self.phone_entry.insert(0, self.member['phone'])
        if self.member.get('address'):
            self.address_text.insert("1.0", self.member['address'])
    
    def save(self):
        """Save member with duplicate check"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Nama harus diisi!")
            return
        
        # Check duplicate warning for new members
        if not self.member and not self.duplicate_confirmed:
            # Re-check duplicate
            result = self.member_manager.check_duplicate_before_create(
                name, self.nrp_entry.get().strip()
            )
            if result['has_duplicate']:
                messagebox.showwarning(
                    "Peringatan", 
                    "Terdapat anggota dengan nama serupa.\n\n"
                    "Klik 'Tetap Buat Baru' pada peringatan jika ingin melanjutkan."
                )
                self.check_duplicate_name()
                return
        
        data = {
            'name': name,
            'rank': self.rank_entry.get().strip(),
            'unit': self.unit_entry.get().strip(),
            'nrp': self.nrp_entry.get().strip(),
            'phone': self.phone_entry.get().strip(),
            'address': self.address_text.get("1.0", "end-1c").strip(),
            'membership_status': self.membership_status_var.get()
        }
        
        self.on_save(data, self.member['id'] if self.member else None)

