"""
Members Frame - Member Management UI
REFACTORED: Added fuzzy search for duplicate detection on new member registration
"""
import customtkinter as ctk
from tkinter import messagebox
from app.modules.members import MemberManager
from app.modules.warehouse import WarehouseManager
from app.utils.receipt import generate_invoice
from app.utils.error_handler import clean_numeric


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
        """Create members table - Fluid layout"""
        self.table_container = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.table_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=1)
        
        # Header row - Fluid
        self.header_row = ctk.CTkFrame(self.table_container, fg_color="#16213e")
        self.header_row.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=(5, 0))
        self.header_row.grid_propagate(True)
        
        # Column config: (name, min_width, weight)
        self.columns_config = [
            ("ID", 50, 0),
            ("Nama", 200, 3),    # Stretches most
            ("Pangkat", 100, 1), # Stretches a bit
            ("Satuan", 120, 1),  # Stretches a bit
            ("NRP", 100, 0),
            ("Telepon", 110, 0),
            ("Aksi", 150, 0)
        ]
        
        for i, (text, width, weight) in enumerate(self.columns_config):
            self.header_row.grid_columnconfigure(i, minsize=width, weight=weight)
            label = ctk.CTkLabel(
                self.header_row, text=text,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#00d4ff"
            )
            label.grid(row=0, column=i, padx=5, pady=12, sticky="w")
        
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
        # print(f"DEBUG: Found {len(members)} members")
        
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
        try:
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
            
            purchase_btn = ctk.CTkButton(
                action_frame, text="🛒", width=35, height=30,
                fg_color="#4ade80", hover_color="#22c55e",
                text_color="#000",
                corner_radius=5, command=lambda m=member: self.open_purchase_dialog(m)
            )
            purchase_btn.pack(side="left", padx=2)
            
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
        except Exception as e:
            print(f"ERROR rendering member row {row_idx}: {e}")
    
    def search_members(self):
        """Search members safely"""
        try:
            if not self.winfo_exists():
                return
            search = self.search_entry.get().strip()
            self.load_data(search if search else None)
        except Exception as e:
            print(f"Error in search_members: {e}")
    
    def refresh_data(self):
        """Refresh table"""
        try:
            if not self.winfo_exists():
                return
            self.search_entry.delete(0, "end")
            self.load_data()
        except Exception as e:
            print(f"Error in refresh_data: {e}")
    
    def open_purchase_dialog(self, member: dict):
        """Open purchase dialog for a member"""
        window_key = f"purchase_member_{member['id']}"
        if window_key in self.active_windows:
            self.active_windows[window_key].lift()
            return
        
        dialog = MemberPurchaseDialog(self, member, self.current_user)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def open_add_dialog(self):
        """Open add member dialog"""
        window_key = "add_member"
        if window_key in self.active_windows:
            self.active_windows[window_key].lift()
            return
        
        dialog = MemberDialog(self, "➕ Tambah Anggota Baru", self.on_member_saved, 
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
        """Close window safely"""
        if window_key in self.active_windows:
            win = self.active_windows[window_key]
            del self.active_windows[window_key]
            try:
                if win and win.winfo_exists():
                    win.destroy()
            except Exception:
                pass
    
    def on_member_saved(self, data: dict, member_id: int = None):
        """Handle member save with stay or close option"""
        # Check if we are quitting to avoid multiple popups
        try:
            is_quitting = getattr(self.winfo_toplevel(), 'is_quitting', False)
        except:
            is_quitting = False

        if member_id:
            result = self.member_manager.update_member(
                member_id, data['name'], data['rank'], data['unit'],
                data['nrp'], data['phone'], data['address'], data['membership_status']
            )
            if result['success']:
                if is_quitting:
                    self.close_window(f"edit_member_{member_id}")
                    self.load_data()
                    return

                if messagebox.askyesno("Sukses", "Data anggota berhasil diupdate.\n\nApakah Anda ingin menutup jendela ini?"):
                    self.close_window(f"edit_member_{member_id}")
                    self.after(100, self.load_data)
                else:
                    self.load_data()
            else:
                if not is_quitting:
                    messagebox.showerror("Error", result['message'])
        else:
            result = self.member_manager.add_member(
                data['name'], data['rank'], data['unit'],
                data['nrp'], data['phone'], data['address'], data['membership_status']
            )
            if result['success']:
                if is_quitting:
                    self.close_window("add_member")
                    self.load_data()
                    return

                if messagebox.askyesno("Sukses", "Data berhasil disimpan.\n\nApakah Anda ingin menutup jendela ini?"):
                    self.close_window("add_member")
                    self.after(100, self.load_data)
                else:
                    self.load_data()
            else:
                if not is_quitting:
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
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.grab_set()
        self.focus_force()
    
    def on_closing(self):
        """Ask to save before closing if data changed"""
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
            value="Anggota Koperasi"
        )
        self.radio_anggota.pack(side="left", padx=(0, 20))
        
        self.radio_umum = ctk.CTkRadioButton(
            status_frame, text="Umum", variable=self.membership_status_var, 
            value="Umum"
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
        try:
            if not self.winfo_exists():
                return
            name = self.name_entry.get().strip()
            nrp = self.nrp_entry.get().strip()
        except Exception:
            return
        
        if not name or len(name) < 3 or not self.member_manager:
            try:
                if self.winfo_exists():
                    self.warning_frame.pack_forget()
            except Exception:
                pass
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
        """Save member with duplicate check and optional fields handling"""
        try:
            is_quitting = getattr(self.winfo_toplevel(), 'is_quitting', False)
        except:
            is_quitting = False

        name = self.name_entry.get().strip()
        if not name:
            if not is_quitting:
                messagebox.showerror("Error", "Nama Lengkap wajib diisi!")
            return
        
        # Check other fields for optional warning
        rank = self.rank_entry.get().strip()
        unit = self.unit_entry.get().strip()
        nrp = self.nrp_entry.get().strip()
        phone = self.phone_entry.get().strip()
        address = self.address_text.get("1.0", "end-1c").strip()
        
        if not all([rank, unit, nrp, phone, address]):
            if not is_quitting:
                if not messagebox.askyesno("Data Belum Lengkap", 
                                          "Beberapa data (Pangkat, Satuan, NRP, dll) masih kosong.\n\n"
                                          "Apakah Anda ingin tetap menyimpan dengan data seadanya?"):
                    return

        # Check duplicate warning for new members
        if not self.member and not self.duplicate_confirmed:
            # Re-check duplicate
            result = self.member_manager.check_duplicate_before_create(
                name, nrp
            )
            if result['has_duplicate']:
                if not is_quitting:
                    if messagebox.askyesno(
                        "Peringatan Duplikat", 
                        "Terdapat anggota dengan nama serupa di database.\n\n"
                        "Apakah Anda yakin ingin tetap membuat anggota baru?"
                    ):
                        self.duplicate_confirmed = True
                    else:
                        self.check_duplicate_name()
                        return
        
        # Final data preparation - Default to '-' for empty fields
        data = {
            'name': name,
            'rank': rank if rank else "-",
            'unit': unit if unit else "-",
            'nrp': nrp if nrp else "-",
            'phone': phone if phone else "-",
            'address': address if address else "-",
            'membership_status': self.membership_status_var.get()
        }
        
        self.on_save(data, self.member['id'] if self.member else None)
        
class MemberPurchaseDialog(ctk.CTkToplevel):
    """
    Dialog for bulk purchasing items for a specific member.
    Allows selecting multiple items across categories and checkout.
    """
    
    def __init__(self, parent, member: dict, current_user: str):
        super().__init__(parent)
        self.member = member
        self.current_user = current_user
        self.parent = parent
        
        # Managers
        self.warehouse_sembako = WarehouseManager("SEMBAKO", current_user)
        self.warehouse_taktikal = WarehouseManager("TAKTIKAL", current_user)
        self.current_warehouse = self.warehouse_sembako
        
        # Shopping Cart: {item_id: {'name': name, 'qty': qty, 'price': price, 'category': cat}}
        self.cart = {}
        
        self.title(f"🛒 Belanja: {member['name']}")
        self.configure(fg_color="#1a1a2e")
        self.minsize(900, 700)
        
        # Center window
        self.update_idletasks()
        window_width = 1000
        window_height = 750
        x = (self.winfo_screenwidth() - window_width) // 2
        y = (self.winfo_screenheight() - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=3) # Product list
        self.grid_columnconfigure(1, weight=2) # Cart
        self.grid_rowconfigure(0, weight=1)
        
        self.create_widgets()
        self.load_items()
        
        self.grab_set()
        self.focus_force()

    def create_widgets(self):
        """Create UI components"""
        # --- LEFT SIDE: PRODUCT LIST ---
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(1, weight=1)
        
        # Search & Filter Header
        header = ctk.CTkFrame(self.left_panel, fg_color="#16213e", corner_radius=10)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(header, text="Cari Barang:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=15, pady=15)
        
        self.search_entry = ctk.CTkEntry(header, width=250, placeholder_text="Ketik nama barang...")
        self.search_entry.pack(side="left", padx=5, pady=15)
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_items())
        
        self.category_var = ctk.StringVar(value="SEMBAKO")
        self.cat_menu = ctk.CTkOptionMenu(
            header, values=["SEMBAKO", "TAKTIKAL"],
            variable=self.category_var,
            command=self.on_category_change,
            fg_color="#374151", button_color="#4b5563"
        )
        self.cat_menu.pack(side="left", padx=10, pady=15)
        
        # Product Table
        self.items_scroll = ctk.CTkScrollableFrame(self.left_panel, fg_color="#16213e", corner_radius=10)
        self.items_scroll.grid(row=1, column=0, sticky="nsew")
        self.items_scroll.grid_columnconfigure(0, weight=1)
        
        # --- RIGHT SIDE: SHOPPING CART ---
        self.right_panel = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=10)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(2, weight=1)
        
        # Cart Header
        ctk.CTkLabel(
            self.right_panel, text="🛒 Keranjang Belanja",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00d4ff"
        ).grid(row=0, column=0, pady=15)
        
        member_info = ctk.CTkLabel(
            self.right_panel, text=f"Anggota: {self.member['name']}\nNRP: {self.member.get('nrp','-')}",
            font=ctk.CTkFont(size=12), text_color="#aaa"
        )
        member_info.grid(row=1, column=0, pady=(0, 10))
        
        # Cart Items List
        self.cart_scroll = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        self.cart_scroll.grid(row=2, column=0, sticky="nsew", padx=5)
        self.cart_scroll.grid_columnconfigure(0, weight=1)
        
        # Checkout Summary
        self.summary_frame = ctk.CTkFrame(self.right_panel, fg_color="#1e293b", corner_radius=10)
        self.summary_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        
        self.total_label = ctk.CTkLabel(
            self.summary_frame, text="Total: Rp 0",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4ade80"
        )
        self.total_label.pack(pady=10)
        
        # Payment Method
        method_frame = ctk.CTkFrame(self.summary_frame, fg_color="transparent")
        method_frame.pack(pady=5)
        self.payment_var = ctk.StringVar(value="Tunai")
        for m in ["Tunai", "Kredit", "QRIS"]:
            ctk.CTkRadioButton(method_frame, text=m, variable=self.payment_var, value=m, font=ctk.CTkFont(size=11)).pack(side="left", padx=5)
            
        self.invoice_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.summary_frame, text="Cetak Invoice PDF", variable=self.invoice_var).pack(pady=5)
        
        self.checkout_btn = ctk.CTkButton(
            self.summary_frame, text="CHECKOUT & SIMPAN",
            height=45, fg_color="#4ade80", hover_color="#22c55e",
            text_color="#000", font=ctk.CTkFont(weight="bold"),
            command=self.process_checkout
        )
        self.checkout_btn.pack(fill="x", padx=20, pady=15)

    def on_category_change(self, cat):
        """Switch warehouse category"""
        self.current_warehouse = self.warehouse_sembako if cat == "SEMBAKO" else self.warehouse_taktikal
        self.load_items()

    def load_items(self):
        """Load items from current warehouse category safely"""
        try:
            for widget in self.items_scroll.winfo_children():
                widget.destroy()
                
            search = self.search_entry.get().strip()
            items = self.current_warehouse.get_all_items(search if search else None)
            
            if not items:
                ctk.CTkLabel(self.items_scroll, text="Tidak ada barang ditemukan", text_color="#888").pack(pady=20)
                return
                
            for item in items:
                self.create_item_row(item)
        except Exception:
            pass

    def create_item_row(self, item: dict):
        """Create a row for product selection"""
        if not item.get('is_active', 1): return
        
        row = ctk.CTkFrame(self.items_scroll, fg_color="#1e293b", height=50)
        row.pack(fill="x", pady=2, padx=5)
        row.pack_propagate(False)
        
        # Info
        name_lbl = ctk.CTkLabel(row, text=item['name'][:30], font=ctk.CTkFont(size=12))
        name_lbl.pack(side="left", padx=10)
        
        stock_lbl = ctk.CTkLabel(row, text=f"Stok: {item['stock']}", font=ctk.CTkFont(size=11), text_color="#aaa")
        stock_lbl.pack(side="left", padx=10)
        
        price_lbl = ctk.CTkLabel(row, text=f"Rp {item['sell_price']:,.0f}", font=ctk.CTkFont(size=12, weight="bold"), text_color="#4ade80")
        price_lbl.pack(side="left", padx=10)
        
        # Add to cart controls
        add_frame = ctk.CTkFrame(row, fg_color="transparent")
        add_frame.pack(side="right", padx=10)
        
        qty_input = ctk.CTkEntry(add_frame, width=50, height=28)
        qty_input.insert(0, "1")
        qty_input.pack(side="left", padx=5)
        
        add_btn = ctk.CTkButton(
            add_frame, text="+", width=30, height=28,
            fg_color="#3b82f6", hover_color="#2563eb",
            command=lambda i=item, q=qty_input: self.add_to_cart(i, q)
        )
        add_btn.pack(side="left")

    def add_to_cart(self, item: dict, qty_input):
        """Add item to shopping cart"""
        try:
            qty = int(clean_numeric(qty_input.get()))
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Jumlah harus berupa angka valid")
            return
            
        if qty <= 0: return
        if qty > item['stock']:
            messagebox.showerror("Error", f"Stok tidak cukup. Tersedia: {item['stock']}")
            return
            
        cart_id = f"{self.category_var.get()}_{item['id']}"
        
        if cart_id in self.cart:
            new_qty = self.cart[cart_id]['qty'] + qty
            if new_qty > item['stock']:
                messagebox.showerror("Error", "Total di keranjang melebihi stok")
                return
            self.cart[cart_id]['qty'] = new_qty
        else:
            self.cart[cart_id] = {
                'id': item['id'],
                'name': item['name'],
                'qty': qty,
                'price': item['sell_price'],
                'category': self.category_var.get()
            }
            
        self.update_cart_display()
        qty_input.delete(0, "end")
        qty_input.insert(0, "1")

    def update_cart_display(self):
        """Refresh the cart items list and total"""
        for widget in self.cart_scroll.winfo_children():
            widget.destroy()
            
        total = 0
        for cart_id, data in self.cart.items():
            subtotal = data['qty'] * data['price']
            total += subtotal
            
            row = ctk.CTkFrame(self.cart_scroll, fg_color="#1e293b", corner_radius=5)
            row.pack(fill="x", pady=2, padx=2)
            
            lbl_text = f"{data['name'][:20]}\nRp {data['price']:,.0f}"
            ctk.CTkLabel(row, text=lbl_text, font=ctk.CTkFont(size=11), justify="left", anchor="w").pack(side="left", padx=10, pady=5)
            
            # Action controls (Right side)
            ctrl_frame = ctk.CTkFrame(row, fg_color="transparent")
            ctrl_frame.pack(side="right", padx=5)
            
            # Remove entirely
            ctk.CTkButton(
                ctrl_frame, text="X", width=25, height=25,
                fg_color="#ef4444", hover_color="#dc2626",
                command=lambda cid=cart_id: self.remove_from_cart(cid)
            ).pack(side="right", padx=5)
            
            # Qty Controls
            qty_frame = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
            qty_frame.pack(side="right", padx=5)
            
            ctk.CTkButton(qty_frame, text="-", width=25, height=25, 
                          fg_color="#374151", command=lambda cid=cart_id: self.change_cart_qty(cid, -1)).pack(side="left")
            
            ctk.CTkLabel(qty_frame, text=str(data['qty']), width=30, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=2)
            
            ctk.CTkButton(qty_frame, text="+", width=25, height=25, 
                          fg_color="#374151", command=lambda cid=cart_id: self.change_cart_qty(cid, 1)).pack(side="left")

            ctk.CTkLabel(row, text=f"Rp {subtotal:,.0f}", font=ctk.CTkFont(size=11, weight="bold")).pack(side="right", padx=5)
            
        self.total_label.configure(text=f"Total: Rp {total:,.0f}")

    def change_cart_qty(self, cart_id, delta):
        """Increase or decrease quantity in cart"""
        if cart_id not in self.cart: return
        
        new_qty = self.cart[cart_id]['qty'] + delta
        if new_qty <= 0:
            self.remove_from_cart(cart_id)
        else:
            # Check stock if increasing
            if delta > 0:
                # We need to find the item in warehouse to check stock
                cat = self.cart[cart_id]['category']
                wh = self.warehouse_sembako if cat == "SEMBAKO" else self.warehouse_taktikal
                item = wh.get_item_by_id(self.cart[cart_id]['id'])
                if item and new_qty > item['stock']:
                    messagebox.showerror("Error", f"Stok tidak cukup. Tersedia: {item['stock']}")
                    return
            
            self.cart[cart_id]['qty'] = new_qty
            self.update_cart_display()

    def remove_from_cart(self, cart_id):
        """Remove item from cart"""
        if cart_id in self.cart:
            del self.cart[cart_id]
            self.update_cart_display()

    def process_checkout(self, silent=False):
        """Execute checkout process across categories"""
        try:
            is_quitting = getattr(self.winfo_toplevel(), 'is_quitting', False)
        except:
            is_quitting = False
            
        if silent: is_quitting = True

        if not self.cart:
            if not is_quitting: messagebox.showwarning("Keranjang Kosong", "Pilih barang terlebih dahulu!")
            return
            
        if not is_quitting and not messagebox.askyesno("Konfirmasi", f"Proses checkout untuk {len(self.cart)} item?"):
            return
            
        # Group by category for backend calls (although we added sell_items_bulk, 
        # it's bound to a specific manager's category context)
        sembako_items = [v for k, v in self.cart.items() if v['category'] == "SEMBAKO"]
        taktikal_items = [v for k, v in self.cart.items() if v['category'] == "TAKTIKAL"]
        
        success_items = []
        total_billed = 0
        payment_method = self.payment_var.get()
        
        # Process Sembako
        if sembako_items:
            res = self.warehouse_sembako.sell_items_bulk(sembako_items, self.member['id'], payment_method)
            if res['success']:
                success_items.extend(res['items'])
                total_billed += res['total']
                # Immediately remove processed Sembako items from cart to prevent duplicate checkout on retry
                self.cart = {k: v for k, v in self.cart.items() if v['category'] != "SEMBAKO"}
                try:
                    if self.winfo_exists():
                        self.update_cart_display()
                except Exception:
                    pass
            else:
                if not is_quitting: messagebox.showerror("Error Sembako", res['message'])
                return
                
        # Process Taktikal
        if taktikal_items:
            res = self.warehouse_taktikal.sell_items_bulk(taktikal_items, self.member['id'], payment_method)
            if res['success']:
                # Tag items with category for invoice
                for item in res['items']:
                    item['category'] = 'TAKTIKAL'
                success_items.extend(res['items'])
                total_billed += res['total']
                # Immediately remove processed Taktikal items from cart
                self.cart = {k: v for k, v in self.cart.items() if v['category'] != "TAKTIKAL"}
                try:
                    if self.winfo_exists():
                        self.update_cart_display()
                except Exception:
                    pass
            else:
                if not is_quitting: messagebox.showerror("Error Taktikal", res['message'])
                return
        
        # Success Handling
        if success_items:
            msg = f"Checkout Berhasil!\nTotal: Rp {total_billed:,.0f}"
            
            if self.invoice_var.get():
                try:
                    # Format for generate_invoice
                    inv_items = []
                    for it in success_items:
                        inv_items.append({
                            'item_name': it['name'],
                            'qty': it['qty'],
                            'unit_price': it['price']
                        })
                    
                    path = generate_invoice(inv_items, self.member)
                    msg += f"\n\nInvoice disimpan di:\n{path}"
                except Exception as e:
                    msg += f"\n\n(Gagal cetak invoice: {str(e)})"
            
            if not is_quitting: messagebox.showinfo("Sukses", msg)
            
            # Safe destroy
            try:
                if self.winfo_exists():
                    self.destroy()
            except:
                pass
                
            # If parent frame exists and is not destroyed, refresh it
            try:
                if not is_quitting and self.parent and self.parent.winfo_exists():
                    self.parent.load_data()
            except:
                pass

    def sell(self):
        """Alias for save_all_dialogs to find during quit"""
        self.process_checkout(silent=True)
        
