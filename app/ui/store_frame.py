"""
Store Frame - Inventory Management UI with Grid System
Features: CRUD, Search, Refresh, Return, Anti-duplicate windows, Excel Import, Receipt Printing
REFACTORED: Synchronized header/row alignment, status badges, fluid full-width layout.
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from app.modules.warehouse import WarehouseManager
from app.utils.export import export_inventory_excel, export_inventory_pdf
from app.utils.excel_import import import_inventory_from_excel, get_workbook_sheets, preview_excel_data
from app.utils.receipt import generate_receipt


class StoreFrame(ctk.CTkFrame):
    """Inventory/Store management frame"""
    
    def __init__(self, master, category_context: str, current_user: str):
        super().__init__(master)
        self.category_context = category_context
        self.current_user = current_user
        self.warehouse = WarehouseManager(category_context, current_user)
        
        # Pagination state
        self.current_page = 1
        self.items_per_page = 50
        self.total_pages = 1
        
        # Window registry
        self.active_windows = {}
        
        # UI State
        self.sort_column = "id"
        self.sort_reverse = False
        
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.create_header()
        self.create_table()
        self.load_data()

    def create_header(self):
        """Create header section with search and actions"""
        self.header_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # Left side: Search
        search_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        search_frame.pack(side="left", padx=20, pady=15)
        
        self.search_entry = ctk.CTkEntry(
            search_frame, placeholder_text="Cari Nama/Kode Barang...",
            width=250, height=35
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search_items())
        
        ctk.CTkButton(
            search_frame, text="🔍 Cari", width=80, height=35,
            command=self.search_items
        ).pack(side="left")
        
        # Right side: Actions
        self.buttons_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.buttons_frame.pack(side="right", padx=20)
        
        # Export buttons
        self.export_excel_btn = ctk.CTkButton(
            self.buttons_frame,
            text="📊 Excel",
            width=80,
            height=35,
            fg_color="#22c55e",
            hover_color="#16a34a",
            text_color="#000000",
            corner_radius=8,
            command=self.export_excel
        )
        self.export_excel_btn.pack(side="left", padx=2)
        
        self.export_pdf_btn = ctk.CTkButton(
            self.buttons_frame,
            text="📄 PDF",
            width=70,
            height=35,
            fg_color="#ef4444",
            hover_color="#dc2626",
            corner_radius=8,
            command=self.export_pdf
        )
        self.export_pdf_btn.pack(side="left", padx=2)
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            self.buttons_frame,
            text="🔄",
            width=40,
            height=35,
            fg_color="#374151",
            hover_color="#4b5563",
            corner_radius=8,
            command=self.refresh_data
        )
        self.refresh_btn.pack(side="left", padx=5)
        
        # Add item button
        self.add_btn = ctk.CTkButton(
            self.buttons_frame,
            text="➕ Tambah Barang",
            width=140,
            height=35,
            fg_color="#4ade80",
            hover_color="#22c55e",
            text_color="#000000",
            corner_radius=8,
            command=self.open_add_dialog
        )
        self.add_btn.pack(side="left", padx=5)

    def create_table(self):
        """Create scrollable table for items with responsive columns"""
        self.table_container = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.table_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=1)
        
        # Table header with responsive columns - Fluid layout
        self.header_row = ctk.CTkFrame(self.table_container, fg_color="#16213e")
        self.header_row.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=(5, 0))
        self.header_row.grid_propagate(True)
        
        # Column config: (name, min_width, weight)
        self.columns_config = [
            ("ID", 45, 0),
            ("Kodebrg", 85, 0),
            ("Nama Barang", 180, 2),
            ("Stok", 60, 0),
            ("H. Pokok", 100, 1),
            ("H. Jual", 100, 1),
            ("Laba", 90, 1),
            ("Status", 90, 0),
            ("Aktif", 80, 0),
            ("H. Aset", 110, 1),
            ("Aksi", 180, 0)
        ]
        
        for i, (text, min_width, weight) in enumerate(self.columns_config):
            self.header_row.grid_columnconfigure(i, minsize=min_width, weight=weight)
            
            # Make Kodebrg, Status and Aktif clickable for sorting
            if text in ["Kodebrg", "Status", "Aktif"]:
                if text == "Kodebrg": col_key = "item_code"
                elif text == "Status": col_key = "status"
                else: col_key = "is_active"
                
                label = ctk.CTkButton(
                    self.header_row,
                    text=text.upper(),
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="#00d4ff",
                    fg_color="transparent",
                    hover_color="#1e293b",
                    width=min_width,
                    anchor="w",
                    command=lambda k=col_key: self.toggle_sort(k)
                )
            else:
                label = ctk.CTkLabel(
                    self.header_row,
                    text=text.upper(),
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="#00d4ff",
                    anchor="w"
                )
            label.grid(row=0, column=i, padx=10, pady=12, sticky="w")
        
        # Scrollable frame for data
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.table_container,
            fg_color="transparent",
            scrollbar_button_color="#374151",
            scrollbar_button_hover_color="#4b5563"
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Pagination Footer
        self.footer_frame = ctk.CTkFrame(self.table_container, fg_color="transparent", height=40)
        self.footer_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        self.prev_btn = ctk.CTkButton(
            self.footer_frame, text="< Prev", width=80, height=28,
            fg_color="#374151", hover_color="#4b5563",
            command=self.prev_page, state="disabled"
        )
        self.prev_btn.pack(side="left", padx=10)
        
        self.page_label = ctk.CTkLabel(
            self.footer_frame, text="Page 1 of 1",
            font=ctk.CTkFont(size=12)
        )
        self.page_label.pack(side="left", padx=10)
        
        self.next_btn = ctk.CTkButton(
            self.footer_frame, text="Next >", width=80, height=28,
            fg_color="#374151", hover_color="#4b5563",
            command=self.next_page, state="disabled"
        )
        self.next_btn.pack(side="left", padx=10)

    def load_data(self, search_term: str = None):
        """Load inventory items into table"""
        try:
            if not self.winfo_exists(): return
        except:
            return

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # Fetch items
        limit = self.items_per_page
        offset = (self.current_page - 1) * limit
        
        items = self.warehouse.get_all_items(search_term)
        
        # Handle sorting
        items.sort(key=lambda x: x.get(self.sort_column) if x.get(self.sort_column) is not None else "", 
                  reverse=self.sort_reverse)
        
        # Handle pagination locally for simplicity in this frame
        self.total_pages = max(1, (len(items) + limit - 1) // limit)
        page_items = items[offset:offset+limit]
        
        # Update footer
        self.page_label.configure(text=f"Page {self.current_page} of {self.total_pages}")
        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < self.total_pages else "disabled")
        
        if not page_items:
            ctk.CTkLabel(
                self.scroll_frame, text="Tidak ada barang ditemukan",
                font=ctk.CTkFont(size=14), text_color="#888888"
            ).pack(pady=50)
            return
            
        for idx, item in enumerate(page_items):
            try:
                self.create_row(idx, item)
            except Exception as e:
                print(f"ERROR rendering item row {idx}: {e}")

    def create_row(self, row_idx: int, item: dict):
        """Create an inventory row with synchronized grid and badges"""
        try:
            is_inactive = not item.get('is_active', 1)
            bg_color = "#1a1a2e" if row_idx % 2 == 0 else "#16213e"
            
            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, height=50, corner_radius=5)
            row_frame.pack(fill="x", pady=2)
            row_frame.grid_propagate(True)
            
            # LOCK GRID CONFIG to match header
            for i, (_, min_width, weight) in enumerate(self.columns_config):
                row_frame.grid_columnconfigure(i, minsize=min_width, weight=weight)
            
            # 0. ID
            ctk.CTkLabel(
                row_frame, text=f"#{item['id']}",
                font=ctk.CTkFont(size=11), text_color="#888"
            ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
            
            # 1. Kodebrg
            ctk.CTkLabel(
                row_frame, text=item.get('item_code', '-') or '-',
                font=ctk.CTkFont(size=11), text_color="#00d4ff"
            ).grid(row=0, column=1, padx=10, pady=10, sticky="w")
            
            # 2. Name
            ctk.CTkLabel(
                row_frame, text=item['name'][:30],
                font=ctk.CTkFont(size=11, weight="bold"), text_color="#ffffff" if not is_inactive else "#888"
            ).grid(row=0, column=2, padx=10, pady=10, sticky="w")
            
            # 3. Stock
            stock_color = "#ef4444" if item['stock'] <= 5 else "#4ade80"
            ctk.CTkLabel(
                row_frame, text=str(item['stock']),
                font=ctk.CTkFont(size=11, weight="bold"), text_color=stock_color
            ).grid(row=0, column=3, padx=10, pady=10, sticky="w")
            
            # 4. Harga Pokok
            ctk.CTkLabel(
                row_frame, text=f"{item['buy_price']:,.0f}",
                font=ctk.CTkFont(size=11), text_color="#cccccc"
            ).grid(row=0, column=4, padx=10, pady=10, sticky="w")
            
            # 5. Harga Jual
            ctk.CTkLabel(
                row_frame, text=f"{item['sell_price']:,.0f}",
                font=ctk.CTkFont(size=11), text_color="#4ade80"
            ).grid(row=0, column=5, padx=10, pady=10, sticky="w")
            
            # 6. Laba
            laba = item['sell_price'] - item['buy_price']
            ctk.CTkLabel(
                row_frame, text=f"{laba:,.0f}",
                font=ctk.CTkFont(size=11), text_color="#f59e0b"
            ).grid(row=0, column=6, padx=10, pady=10, sticky="w")
            
            # 7. Status Barang (BADGE)
            s_val = item.get('status', 'Koperasi')
            s_colors = {
                "Koperasi": ("#e0f2fe", "#0369a1"), # Blue
                "Titipan": ("#ffedd5", "#9a3412")   # Orange
            }
            bg, fg = s_colors.get(s_val, ("#374151", "#ffffff"))
            ctk.CTkLabel(
                row_frame, text=s_val.upper(), font=ctk.CTkFont(size=9, weight="bold"),
                fg_color=bg, text_color=fg, corner_radius=6, width=75, height=24
            ).grid(row=0, column=7, padx=10, pady=10, sticky="w")
            
            # 8. Status Aktif (BADGE)
            a_text = "AKTIF" if not is_inactive else "NONAKTIF"
            a_bg = "#dcfce7" if not is_inactive else "#fee2e2"
            a_fg = "#15803d" if not is_inactive else "#b91c1c"
            ctk.CTkLabel(
                row_frame, text=a_text, font=ctk.CTkFont(size=9, weight="bold"),
                fg_color=a_bg, text_color=a_fg, corner_radius=6, width=75, height=24
            ).grid(row=0, column=8, padx=10, pady=10, sticky="w")
            
            # 9. Harga Aset (Jual * Stok)
            asset_val = item['sell_price'] * item['stock']
            ctk.CTkLabel(
                row_frame, text=f"{asset_val:,.0f}",
                font=ctk.CTkFont(size=11, weight="bold"), text_color="#8b5cf6"
            ).grid(row=0, column=9, padx=10, pady=10, sticky="w")
            
            # 10. Action buttons
            action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_frame.grid(row=0, column=10, padx=10, pady=5, sticky="w")
            
            # Edit button
            edit_btn = ctk.CTkButton(
                action_frame, text="✏️", width=32, height=30,
                fg_color="#3b82f6", hover_color="#2563eb",
                corner_radius=5,
                command=lambda i=item: self.open_edit_dialog(i)
            )
            edit_btn.pack(side="left", padx=1)
            
            # Sell button (Only if active)
            sell_btn = ctk.CTkButton(
                action_frame, text="🛒", width=32, height=30,
                fg_color="#4ade80" if not is_inactive else "#374151", 
                hover_color="#22c55e" if not is_inactive else "#374151",
                state="normal" if not is_inactive else "disabled",
                corner_radius=5,
                command=lambda i=item: self.open_sell_dialog(i)
            )
            sell_btn.pack(side="left", padx=1)
            
            # Return button
            return_btn = ctk.CTkButton(
                action_frame, text="↩️", width=32, height=30,
                fg_color="#f59e0b", hover_color="#d97706",
                corner_radius=5,
                command=lambda i=item: self.open_return_dialog(i)
            )
            return_btn.pack(side="left", padx=1)
            
            # Delete button
            delete_btn = ctk.CTkButton(
                action_frame, text="Hapus", width=45, height=30,
                font=ctk.CTkFont(size=10),
                fg_color="#ef4444", hover_color="#dc2626",
                corner_radius=5,
                command=lambda i=item: self.delete_item(i)
            )
            delete_btn.pack(side="left", padx=1)
        except Exception as e:
            print(f"ERROR rendering item row {row_idx}: {e}")

    def toggle_sort(self, column):
        """Toggle sorting by column"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.load_data()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_data()

    def search_items(self):
        """Search items by name"""
        search_term = self.search_entry.get().strip()
        self.load_data(search_term if search_term else None)
    
    def refresh_data(self):
        """Refresh table data"""
        self.search_entry.delete(0, "end")
        self.load_data()
    
    def import_excel(self):
        """Import inventory from Excel file with preview"""
        filepath = filedialog.askopenfilename(
            title="Pilih File Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        # Check for multiple sheets
        sheets = get_workbook_sheets(filepath)
        
        if not sheets:
            messagebox.showerror("Error", "Gagal membaca file Excel atau file rusak")
            return
        
        # Open preview dialog
        window_key = "import_preview"
        if window_key in self.active_windows:
            self.active_windows[window_key].lift()
            return
        
        dialog = ImportPreviewDialog(
            self, filepath, sheets, self.category_context, 
            self.current_user, self.on_import_complete
        )
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def on_import_complete(self):
        """Handle import completion"""
        self.close_window("import_preview")
        self.load_data()
    
    def export_excel(self):
        """Export inventory to Excel"""
        items = self.warehouse.get_all_items()
        if not items:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk diexport!")
            return
        
        try:
            filepath = export_inventory_excel(items, f"Inventaris_{self.category_context}")
            messagebox.showinfo("Sukses", f"File berhasil disimpan:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export: {str(e)}")
    
    def export_pdf(self):
        """Export inventory to PDF"""
        items = self.warehouse.get_all_items()
        if not items:
            messagebox.showwarning("Peringatan", "Tidak ada data untuk diexport!")
            return
        
        try:
            filepath = export_inventory_pdf(items, self.category_context, f"Inventaris_{self.category_context}")
            messagebox.showinfo("Sukses", f"File berhasil disimpan:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal export: {str(e)}")
    
    def open_add_dialog(self):
        """Open dialog to add new item"""
        window_key = "add_item"
        if window_key in self.active_windows:
            self.active_windows[window_key].lift()
            return
            
        dialog = ItemDialog(self, None, self.on_save, self.category_context)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def open_edit_dialog(self, item: dict):
        """Open dialog to edit an item"""
        window_key = f"edit_{item['id']}"
        if window_key in self.active_windows:
            self.active_windows[window_key].lift()
            return
            
        dialog = ItemDialog(self, item, self.on_save, self.category_context)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def open_sell_dialog(self, item: dict):
        """Open sale dialog"""
        window_key = f"sell_{item['id']}"
        if window_key in self.active_windows:
            self.active_windows[window_key].lift()
            return
            
        dialog = SellDialog(self, item, self.on_transaction_saved, self.current_user)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def open_return_dialog(self, item: dict):
        """Open return dialog"""
        window_key = f"return_{item['id']}"
        if window_key in self.active_windows:
            self.active_windows[window_key].lift()
            return
            
        dialog = ReturDialog(self, item, self.on_transaction_saved, self.current_user)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def delete_item(self, item: dict):
        """Delete an item with confirmation"""
        if messagebox.askyesno("Konfirmasi", f"Hapus barang '{item['name']}'?"):
            result = self.warehouse.delete_item(item['id'])
            if result['success']:
                messagebox.showinfo("Sukses", result['message'])
                self.load_data()
            else:
                messagebox.showerror("Error", result['message'])
    
    def close_window(self, window_key: str):
        """Close window and remove from registry"""
        if window_key in self.active_windows:
            self.active_windows[window_key].destroy()
            del self.active_windows[window_key]
            
    def on_save(self, data: dict, item_id: int = None):
        """Handle save callback from ItemDialog"""
        try:
            is_quitting = getattr(self.winfo_toplevel(), 'is_quitting', False)
        except:
            is_quitting = False

        if not is_quitting:
            self.load_data()
            
        # Determine registry key
        key = f"edit_{item_id}" if item_id else "add_item"
        
        if is_quitting:
            self.close_window(key)
        elif messagebox.askyesno("Sukses", "Data barang berhasil disimpan.\n\nApakah Anda ingin menutup jendela ini?"):
            self.close_window(key)
            
    def on_transaction_saved(self, item_id: int, type: str = 'sell'):
        """Handle save callback from SellDialog or ReturDialog"""
        try:
            is_quitting = getattr(self.winfo_toplevel(), 'is_quitting', False)
        except:
            is_quitting = False

        if not is_quitting:
            self.load_data()
            
        # Determine registry key
        key = f"{type}_{item_id}"
        
        if is_quitting:
            self.close_window(key)
        elif messagebox.askyesno("Sukses", "Transaksi berhasil dicatat.\n\nApakah Anda ingin menutup jendela ini?"):
            self.close_window(key)


class ImportPreviewDialog(ctk.CTkToplevel):
    """Preview dialog for Excel import"""
    
    def __init__(self, parent, filepath, sheets, category, user, on_complete):
        super().__init__(parent)
        self.filepath = filepath
        self.sheets = sheets
        self.category = category
        self.user = user
        self.on_complete = on_complete
        
        self.title("🔍 Preview Import Excel")
        self.geometry("900x600")
        self.configure(fg_color="#1a1a2e")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.create_widgets()
        self.grab_set()
        
    def create_widgets(self):
        # Header
        top_frame = ctk.CTkFrame(self, fg_color="#16213e", height=60)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(top_frame, text="Pilih Sheet:", font=ctk.CTkFont(size=12)).pack(side="left", padx=20)
        
        self.sheet_var = ctk.StringVar(value=self.sheets[0])
        self.sheet_menu = ctk.CTkOptionMenu(
            top_frame, values=self.sheets, variable=self.sheet_var,
            command=lambda v: self.load_preview()
        )
        self.sheet_menu.pack(side="left", padx=10)
        
        # Table Preview
        self.preview_container = ctk.CTkFrame(self, fg_color="#111827")
        self.preview_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        self.load_preview()
        
        # Bottom Actions
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=15)
        
        ctk.CTkButton(
            btn_frame, text="Batal", fg_color="#374151",
            command=self.destroy
        ).pack(side="right", padx=10)
        
        ctk.CTkButton(
            btn_frame, text="🚀 Import Sekarang", fg_color="#4ade80", text_color="#000",
            font=ctk.CTkFont(weight="bold"), command=self.process_import
        ).pack(side="right", padx=10)
        
    def load_preview(self):
        for widget in self.preview_container.winfo_children():
            widget.destroy()
            
        data = preview_excel_data(self.filepath, self.sheet_var.get())
        if not data:
            ctk.CTkLabel(self.preview_container, text="Gagal memuat data").pack(pady=20)
            return
            
        # Simplified preview table
        scroll = ctk.CTkScrollableFrame(self.preview_container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        for r, row in enumerate(data[:15]): # Show first 15 rows
            for c, val in enumerate(row):
                lbl = ctk.CTkLabel(
                    scroll, text=str(val)[:20], 
                    font=ctk.CTkFont(size=10),
                    fg_color="#1e293b" if r == 0 else "transparent"
                )
                lbl.grid(row=r, column=c, padx=5, pady=2, sticky="w")
                
    def process_import(self):
        sheet = self.sheet_var.get()
        result = import_inventory_from_excel(self.filepath, sheet, self.category, self.user)
        
        if result['success']:
            messagebox.showinfo("Sukses", result['message'])
            self.on_complete()
            self.destroy()
        else:
            messagebox.showerror("Error", result['message'])


class ItemDialog(ctk.CTkToplevel):
    """Dialog for adding or editing an inventory item"""
    
    def __init__(self, parent, item: dict = None, on_save = None, category: str = "SEMBAKO"):
        super().__init__(parent)
        self.item = item
        self.on_save = on_save
        self.category = category
        
        title_text = "✏️ Edit Barang" if item else "➕ Tambah Barang Baru"
        self.title(title_text)
        self.configure(fg_color="#1a1a2e")
        self.resizable(False, False)
        
        # Size and positioning
        self.geometry("500x650")
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 650) // 2
        self.geometry(f"+{x}+{y}")
        
        # Managers
        self.warehouse = WarehouseManager(category, parent.current_user)
        
        self.create_form()
        if item:
            self.populate_form()
            
        self.grab_set()

    def create_form(self):
        """Create form fields with mandatory check"""
        # Scrollable container
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Item Code
        ctk.CTkLabel(self.scroll, text="Kode Barang *", text_color="#cccccc"
                     ).pack(anchor="w", padx=40, pady=(15, 5))
        self.code_entry = ctk.CTkEntry(self.scroll, width=400, height=40, corner_radius=8)
        self.code_entry.pack(padx=40)
        
        # Name
        ctk.CTkLabel(self.scroll, text="Nama Barang *", text_color="#cccccc"
                     ).pack(anchor="w", padx=40, pady=(15, 5))
        self.name_entry = ctk.CTkEntry(self.scroll, width=400, height=40, corner_radius=8)
        self.name_entry.pack(padx=40)
        
        # Stock
        ctk.CTkLabel(self.scroll, text="Stok Awal *", text_color="#cccccc"
                     ).pack(anchor="w", padx=40, pady=(15, 5))
        self.stock_entry = ctk.CTkEntry(self.scroll, width=400, height=40, corner_radius=8)
        self.stock_entry.pack(padx=40)
        if not self.item: self.stock_entry.insert(0, "0")
        
        # Buy Price
        ctk.CTkLabel(self.scroll, text="Harga Pokok *", text_color="#cccccc"
                     ).pack(anchor="w", padx=40, pady=(15, 5))
        self.buy_price_entry = ctk.CTkEntry(self.scroll, width=400, height=40, corner_radius=8)
        self.buy_price_entry.pack(padx=40)
        if not self.item: self.buy_price_entry.insert(0, "0")
        
        # Sell Price
        ctk.CTkLabel(self.scroll, text="Harga Jual *", text_color="#cccccc"
                     ).pack(anchor="w", padx=40, pady=(15, 5))
        self.sell_price_entry = ctk.CTkEntry(self.scroll, width=400, height=40, corner_radius=8)
        self.sell_price_entry.pack(padx=40)
        if not self.item: self.sell_price_entry.insert(0, "0")
        
        # Status (Koperasi/Titipan)
        ctk.CTkLabel(self.scroll, text="Status Barang", text_color="#cccccc"
                     ).pack(anchor="w", padx=40, pady=(15, 5))
        self.status_var = ctk.StringVar(value="Koperasi")
        self.status_menu = ctk.CTkOptionMenu(
            self.scroll, values=["Koperasi", "Titipan"],
            variable=self.status_var, width=400, height=40, corner_radius=8
        )
        self.status_menu.pack(padx=40)
        
        # Active Status (CheckBox)
        self.active_var = ctk.BooleanVar(value=True)
        self.active_cb = ctk.CTkCheckBox(
            self.scroll, text="Barang Aktif (Muncul di daftar jual)",
            variable=self.active_var, text_color="#cccccc"
        )
        self.active_cb.pack(padx=40, pady=20)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(
            btn_frame, text="Batal", width=100, height=45,
            fg_color="#374151", hover_color="#4b5563",
            command=self.destroy
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, text="💾 Simpan", width=140, height=45,
            fg_color="#4ade80", hover_color="#22c55e",
            text_color="#000000", font=ctk.CTkFont(weight="bold"),
            command=self.save
        ).pack(side="left", padx=10)

    def populate_form(self):
        """Fill form with existing item data"""
        self.code_entry.insert(0, self.item.get('item_code', ''))
        self.name_entry.insert(0, self.item.get('name', ''))
        self.stock_entry.delete(0, "end")
        self.stock_entry.insert(0, str(self.item.get('stock', 0)))
        self.buy_price_entry.delete(0, "end")
        self.buy_price_entry.insert(0, str(int(self.item.get('buy_price', 0))))
        self.sell_price_entry.delete(0, "end")
        self.sell_price_entry.insert(0, str(int(self.item.get('sell_price', 0))))
        self.status_var.set(self.item.get('status', 'Koperasi'))
        self.active_var.set(bool(self.item.get('is_active', 1)))

    def save(self):
        """Save item with mandatory field validation"""
        try:
            is_quitting = getattr(self.winfo_toplevel(), 'is_quitting', False)
        except:
            is_quitting = False

        # Get values
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        
        try:
            stock = int(self.stock_entry.get())
            buy_price = float(self.buy_price_entry.get())
            sell_price = float(self.sell_price_entry.get())
        except ValueError:
            if not is_quitting:
                messagebox.showerror("Error", "Stok dan Harga harus berupa angka!")
            return
            
        # MANDATORY CHECK
        if not all([code, name]):
            if not is_quitting:
                messagebox.showerror("Data Tidak Lengkap", "Kode Barang dan Nama Barang wajib diisi!")
            return
            
        data = {
            'item_code': code,
            'name': name,
            'stock': stock,
            'buy_price': buy_price,
            'sell_price': sell_price,
            'status': self.status_var.get(),
            'is_active': 1 if self.active_var.get() else 0,
            'category_type': self.category
        }
        
        if self.item:
            result = self.warehouse.update_item(self.item['id'], data)
        else:
            result = self.warehouse.create_item(data)
            
        if result['success']:
            if not is_quitting:
                messagebox.showinfo("Sukses", result['message'])
            self.on_save(data, self.item['id'] if self.item else None)
        else:
            if not is_quitting:
                messagebox.showerror("Error", result['message'])


class SellDialog(ctk.CTkToplevel):
    """Dialog for processing a sale - REDESIGNED: MEMBER REQUIRED"""
    
    def __init__(self, parent, item: dict, on_save, current_user: str):
        super().__init__(parent)
        self.item = item
        self.on_save = on_save
        self.current_user = current_user
        
        # Managers
        from app.modules.members import MemberManager
        self.member_manager = MemberManager(current_user)
        self.warehouse = WarehouseManager(item['category_type'], current_user)
        
        self.selected_member_id = None
        self.member_data = None
        
        self.title(f"🛒 Jual - {item['name']}")
        self.geometry("500x700")
        self.configure(fg_color="#1a1a2e")
        self.resizable(False, False)
        
        # Center dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 500) // 2
        y = (self.winfo_screenheight() - 700) // 2
        self.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        self.grab_set()

    def create_widgets(self):
        """Create selling form with autocomplete member search"""
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Item Summary
        info_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#16213e", corner_radius=10)
        info_frame.pack(fill="x", padx=40, pady=15)
        
        item_title = self.item['name'][:25]
        ctk.CTkLabel(info_frame, text=item_title, 
                    font=ctk.CTkFont(size=16, weight="bold"), text_color="#00d4ff").pack(pady=(10, 2))
        ctk.CTkLabel(info_frame, text=f"Stok Tersedia: {self.item['stock']}", text_color="#888").pack(pady=(0, 10))
        
        # Member Search (MANDATORY)
        ctk.CTkLabel(self.scroll_frame, text="Pilih Anggota *", text_color="#cccccc"
                     ).pack(anchor="w", padx=40, pady=(15, 5))
        
        self.member_search = ctk.CTkEntry(
            self.scroll_frame, placeholder_text="Ketik nama anggota...",
            width=400, height=40, corner_radius=8
        )
        self.member_search.pack(padx=40)
        self.member_search.bind("<KeyRelease>", self.on_member_search)
        
        # Autocomplete dropdown (initially hidden)
        self.autocomplete_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1e293b", corner_radius=8)
        
        self.selected_member_label = ctk.CTkLabel(
            self.scroll_frame, text="Silakan pilih anggota dari daftar",
            text_color="#ef4444", font=ctk.CTkFont(size=11, slant="italic")
        )
        self.selected_member_label.pack(anchor="w", padx=40, pady=2)
        
        # Qty
        ctk.CTkLabel(self.scroll_frame, text="Jumlah Beli *", text_color="#cccccc"
                     ).pack(anchor="w", padx=40, pady=(15, 5))
        self.qty_entry = ctk.CTkEntry(self.scroll_frame, width=400, height=40, corner_radius=8)
        self.qty_entry.pack(padx=40)
        self.qty_entry.insert(0, "1")
        self.qty_entry.bind("<KeyRelease>", self.update_total)
        
        # Payment Method
        ctk.CTkLabel(self.scroll_frame, text="Metode Pembayaran", text_color="#cccccc"
                     ).pack(anchor="w", padx=40, pady=(15, 5))
        
        payment_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        payment_frame.pack(padx=40)
        
        self.payment_var = ctk.StringVar(value="Tunai")
        
        for method, color in [("Tunai", "#4ade80"), ("Kredit", "#00d4ff"), ("QRIS", "#8b5cf6")]:
            ctk.CTkRadioButton(
                payment_frame, text=method, variable=self.payment_var,
                value=method, fg_color=color, hover_color=color,
                text_color="#ccc"
            ).pack(side="left", padx=10, pady=5)
        
        # Total
        self.total_label = ctk.CTkLabel(
            self.scroll_frame, text=f"Total: Rp {self.item['sell_price']:,.0f}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4ade80"
        )
        self.total_label.pack(pady=20)
        
        # Print receipt checkbox
        self.print_receipt_var = ctk.BooleanVar(value=True)
        self.print_checkbox = ctk.CTkCheckBox(
            self.scroll_frame, text="Cetak Struk/Invoice",
            variable=self.print_receipt_var,
            fg_color="#4ade80", hover_color="#22c55e",
            text_color="#cccccc"
        )
        self.print_checkbox.pack(pady=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        btn_frame.pack(pady=25)
        
        ctk.CTkButton(
            btn_frame, text="Batal", width=100, height=45,
            fg_color="#374151", hover_color="#4b5563",
            command=self.destroy
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, text="🛒 Jual", width=140, height=45,
            fg_color="#4ade80", hover_color="#22c55e",
            text_color="#000000", font=ctk.CTkFont(weight="bold"),
            command=self.sell
        ).pack(side="left", padx=10)

    def on_member_search(self, event=None):
        """Filter members as user types"""
        query = self.member_search.get().strip()
        if len(query) < 2:
            self.hide_autocomplete()
            return
            
        members = self.member_manager.get_all_members(query)
        if not members:
            self.hide_autocomplete()
            return
            
        self.show_autocomplete(members[:5])

    def show_autocomplete(self, members):
        """Display dropdown with member results"""
        for widget in self.autocomplete_frame.winfo_children():
            widget.destroy()
            
        for m in members:
            btn = ctk.CTkButton(
                self.autocomplete_frame, 
                text=f"{m['name']} ({m.get('nrp', '-')})",
                fg_color="transparent", hover_color="#374151",
                anchor="w", height=30, corner_radius=0,
                command=lambda member=m: self.select_member(member)
            )
            btn.pack(fill="x")
            
        self.autocomplete_frame.pack(padx=40, fill="x", after=self.member_search)

    def hide_autocomplete(self):
        """Hide the dropdown"""
        self.autocomplete_frame.pack_forget()

    def select_member(self, member):
        """Mark member as selected"""
        self.selected_member_id = member['id']
        self.member_data = member
        display = f"Terpilih: {member['name']} ({member.get('nrp', '-')})"
        self.selected_member_label.configure(text=display, text_color="#4ade80")
        self.member_search.delete(0, "end")
        self.member_search.insert(0, member['name'])
        self.hide_autocomplete()
    
    def update_total(self, event=None):
        """Update total price display"""
        try:
            qty_str = self.qty_entry.get().strip()
            qty = int(qty_str) if qty_str else 0
            total = qty * self.item['sell_price']
            self.total_label.configure(text=f"Total: Rp {total:,.0f}")
        except ValueError:
            pass
    
    def sell(self):
        """Process sale - MEMBER REQUIRED"""
        # Check member selection
        if not self.selected_member_id:
            search_text = self.member_search.get().strip()
            # Try to find exactly by name if not selected from list
            if search_text:
                exact_matches = self.member_manager.get_all_members(search_text)
                for m in exact_matches:
                    if m['name'].lower() == search_text.lower():
                        self.select_member(m)
                        break
            
            # Re-check after attempt
            if not self.selected_member_id:
                messagebox.showerror("Error", "Wajib memilih Anggota untuk transaksi ini!")
                return
        
        try:
            qty = int(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Jumlah harus berupa angka!")
            return
            
        if qty <= 0:
            messagebox.showerror("Error", "Jumlah harus lebih dari 0!")
            return
            
        if qty > self.item['stock']:
            messagebox.showerror("Error", f"Stok tidak mencukupi! Tersedia: {self.item['stock']}")
            return
            
        method = self.payment_var.get()
        
        result = self.warehouse.sell_item(
            self.item['id'], qty, self.selected_member_id, 
            method, self.current_user
        )
        
        if result['success']:
            # Handle receipt printing
            if self.print_receipt_var.get():
                try:
                    # Enrich data for receipt
                    receipt_data = {
                        'transaction_id': result.get('transaction_id', 'N/A'),
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'member_name': self.member_data['name'],
                        'member_nrp': self.member_data.get('nrp', '-'),
                        'items': [{
                            'name': self.item['name'],
                            'qty': qty,
                            'price': self.item['sell_price'],
                            'total': qty * self.item['sell_price']
                        }],
                        'grand_total': qty * self.item['sell_price'],
                        'payment_method': method,
                        'cashier': self.current_user
                    }
                    filepath = generate_receipt(receipt_data)
                    messagebox.showinfo("Sukses", f"Transaksi Berhasil!\nStruk disimpan di: {filepath}")
                except Exception as e:
                    messagebox.showwarning("Peringatan", f"Transaksi berhasil tapi gagal cetak struk: {e}")
            else:
                messagebox.showinfo("Sukses", result['message'])
                
            self.on_save(self.item['id'], 'sell')
        else:
            messagebox.showerror("Error", result['message'])


class ReturDialog(ctk.CTkToplevel):
    """Dialog for processing an inventory return (Retur)"""
    
    def __init__(self, parent, item: dict, on_save, current_user: str):
        super().__init__(parent)
        self.item = item
        self.on_save = on_save
        self.current_user = current_user
        self.warehouse = WarehouseManager(item['category_type'], current_user)
        
        self.title(f"↩️ Retur Barang - {item['name']}")
        self.geometry("450x450")
        self.configure(fg_color="#1a1a2e")
        self.resizable(False, False)
        
        # Center dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 450) // 2
        y = (self.winfo_screenheight() - 450) // 2
        self.geometry(f"+{x}+{y}")
        
        self.create_widgets()
        self.grab_set()

    def create_widgets(self):
        """Create return form"""
        ctk.CTkLabel(self, text=f"Retur: {self.item['name']}", 
                    font=ctk.CTkFont(size=16, weight="bold"), text_color="#f59e0b").pack(pady=20)
        
        # Qty
        ctk.CTkLabel(self, text="Jumlah Retur *", text_color="#cccccc").pack(anchor="w", padx=50, pady=(15, 5))
        self.qty_entry = ctk.CTkEntry(self, width=350, height=40, corner_radius=8)
        self.qty_entry.pack(padx=50)
        self.qty_entry.insert(0, "1")
        
        # Reason
        ctk.CTkLabel(self, text="Alasan Retur *", text_color="#cccccc").pack(anchor="w", padx=50, pady=(15, 5))
        self.reason_text = ctk.CTkTextbox(self, width=350, height=80, corner_radius=8)
        self.reason_text.pack(padx=50)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=30)
        
        ctk.CTkButton(
            btn_frame, text="Batal", width=100, height=40,
            fg_color="#374151", command=self.destroy
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, text="Konfirmasi Retur", width=150, height=40,
            fg_color="#f59e0b", hover_color="#d97706",
            text_color="#000000", font=ctk.CTkFont(weight="bold"),
            command=self.confirm_retur
        ).pack(side="left", padx=10)

    def confirm_retur(self):
        """Process the return"""
        try:
            qty = int(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Jumlah harus berupa angka!")
            return
            
        reason = self.reason_text.get("1.0", "end-1c").strip()
        if not reason:
            messagebox.showerror("Error", "Alasan retur wajib diisi!")
            return
            
        result = self.warehouse.return_item(self.item['id'], qty, reason)
        
        if result['success']:
            messagebox.showinfo("Sukses", result['message'])
            self.on_save(self.item['id'], 'return')
        else:
            messagebox.showerror("Error", result['message'])
