"""
Store Frame - Inventory Management UI with Grid System
Features: CRUD, Search, Refresh, Return, Anti-duplicate windows, Excel Import, Receipt Printing
REFACTORED: Responsive table, scrollable dialogs, wider action column
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
        
        # Sorting state
        self.sort_column = "name"
        self.sort_order = "ASC"
        
        # Anti-duplicate window registry
        self.active_windows = {}
        
        self.configure(fg_color="transparent")
        
        # Configure grid for responsive layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.create_header()
        self.create_table()
        self.load_data()

    def toggle_sort(self, column: str):
        """Toggle sorting order for a column"""
        if self.sort_column == column:
            self.sort_order = "DESC" if self.sort_order == "ASC" else "ASC"
        else:
            self.sort_column = column
            self.sort_order = "ASC"
        
        self.load_data(self.search_entry.get().strip())

    def create_header(self):
        """Create header with search and action buttons"""
        self.header_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # Title
        title_text = "📦 Inventaris Sembako" if self.category_context == "SEMBAKO" else "🎯 Inventaris Taktikal"
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00d4ff"
        )
        self.title_label.pack(side="left", padx=20, pady=15)
        
        # Right side buttons
        self.buttons_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.buttons_frame.pack(side="right", padx=20, pady=10)
        
        # Search
        self.search_entry = ctk.CTkEntry(
            self.buttons_frame,
            width=200,
            height=35,
            placeholder_text="🔍 Cari barang...",
            corner_radius=8
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.search_items())
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_items())
        
        # Import Excel button
        self.import_btn = ctk.CTkButton(
            self.buttons_frame,
            text="📥 Import Excel",
            width=120,
            height=35,
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            corner_radius=8,
            command=self.import_excel
        )
        self.import_btn.pack(side="left", padx=5)
        
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
        
        # Table header with responsive columns
        self.header_row = ctk.CTkFrame(self.table_container, fg_color="#16213e", height=45)
        self.header_row.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        self.header_row.grid_propagate(False)
        
        # Column config: (name, min_width, weight) - weight for responsive sizing
        self.columns_config = [
            ("ID", 40, 0),
            ("Kodebrg", 80, 0),
            ("Nama Barang", 180, 2),
            ("Stok", 60, 0),
            ("H. Pokok", 100, 1),
            ("H. Jual", 100, 1),
            ("Laba", 90, 1),
            ("Status", 90, 0),
            ("Aktif", 60, 0),
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
                    text=text,
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
                    text=text,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="#00d4ff",
                    anchor="w"
                )
            label.grid(row=0, column=i, padx=3, pady=10, sticky="w")
        
        # Scrollable frame for data
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.table_container,
            fg_color="transparent",
            scrollbar_button_color="#374151",
            scrollbar_button_hover_color="#4b5563"
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure scroll frame columns with same weights
        for i, (_, min_width, weight) in enumerate(self.columns_config):
            self.scroll_frame.grid_columnconfigure(i, minsize=min_width, weight=weight)
            
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
        """Load items into table with pagination"""
        try:
            if not self.winfo_exists(): return
        except:
            return
            
        # Clear existing rows
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # Calculate pagination
        total_items = self.warehouse.get_items_count(search_term)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        if self.current_page > self.total_pages:
            self.current_page = self.total_pages
            
        offset = (self.current_page - 1) * self.items_per_page
        
        items = self.warehouse.get_all_items(
            search_term, limit=self.items_per_page, offset=offset,
            sort_column=self.sort_column, sort_order=self.sort_order
        )
        
        # Update pagination controls
        self.page_label.configure(text=f"Page {self.current_page} of {self.total_pages}")
        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < self.total_pages else "disabled")
        
        if not items:
            no_data_label = ctk.CTkLabel(
                self.scroll_frame,
                text="Tidak ada data barang",
                font=ctk.CTkFont(size=14),
                text_color="#888888"
            )
            no_data_label.grid(row=0, column=0, columnspan=11, pady=50)
            return
        
        for idx, item in enumerate(items):
            self.create_row(idx, item)

    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data(self.search_entry.get().strip())

    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_data(self.search_entry.get().strip())

    def create_row(self, row_idx: int, item: dict):
        """Create a single data row with calculations"""
        try:
            bg_color = "#1e293b" if row_idx % 2 == 0 else "#16213e"
            is_inactive = not item.get('is_active', 1)
            if is_inactive:
                bg_color = "#2a1a1a" # Subtle dark red for inactive
                
            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, height=45, corner_radius=5)
            row_frame.grid(row=row_idx, column=0, columnspan=11, sticky="ew", pady=1)
            row_frame.grid_propagate(False)
            
            # Apply same column configuration
            for i, (_, min_width, weight) in enumerate(self.columns_config):
                row_frame.grid_columnconfigure(i, minsize=min_width, weight=weight)
            
            # ID
            ctk.CTkLabel(
                row_frame, text=str(item['id']),
                font=ctk.CTkFont(size=11), text_color="#888"
            ).grid(row=0, column=0, padx=3, pady=8, sticky="w")
            
            # Kodebrg
            ctk.CTkLabel(
                row_frame, text=item.get('item_code', '-') or '-',
                font=ctk.CTkFont(size=11), text_color="#00d4ff"
            ).grid(row=0, column=1, padx=3, pady=8, sticky="w")
            
            # Name
            ctk.CTkLabel(
                row_frame, text=item['name'][:35],
                font=ctk.CTkFont(size=11), text_color="#ffffff" if not is_inactive else "#888"
            ).grid(row=0, column=2, padx=3, pady=8, sticky="w")
            
            # Stock
            stock_color = "#ef4444" if item['stock'] <= 5 else "#4ade80"
            ctk.CTkLabel(
                row_frame, text=str(item['stock']),
                font=ctk.CTkFont(size=11, weight="bold"), text_color=stock_color
            ).grid(row=0, column=3, padx=3, pady=8, sticky="w")
            
            # Harga Pokok
            ctk.CTkLabel(
                row_frame, text=f"{item['buy_price']:,.0f}",
                font=ctk.CTkFont(size=11), text_color="#cccccc"
            ).grid(row=0, column=4, padx=3, pady=8, sticky="w")
            
            # Harga Jual
            ctk.CTkLabel(
                row_frame, text=f"{item['sell_price']:,.0f}",
                font=ctk.CTkFont(size=11), text_color="#4ade80"
            ).grid(row=0, column=5, padx=3, pady=8, sticky="w")
            
            # Laba
            laba = item['sell_price'] - item['buy_price']
            ctk.CTkLabel(
                row_frame, text=f"{laba:,.0f}",
                font=ctk.CTkFont(size=11), text_color="#f59e0b"
            ).grid(row=0, column=6, padx=3, pady=8, sticky="w")
            
            # Status Barang
            status_color = "#00d4ff" if item['status'] == 'Koperasi' else "#f59e0b"
            ctk.CTkLabel(
                row_frame, text=item['status'],
                font=ctk.CTkFont(size=10), text_color=status_color
            ).grid(row=0, column=7, padx=3, pady=8, sticky="w")
            
            # Status Aktif
            aktif_text = "Ya" if not is_inactive else "Tidak"
            aktif_color = "#4ade80" if not is_inactive else "#ef4444"
            ctk.CTkLabel(
                row_frame, text=aktif_text,
                font=ctk.CTkFont(size=10, weight="bold"), text_color=aktif_color
            ).grid(row=0, column=8, padx=3, pady=8, sticky="w")
            
            # Harga Aset (Jual * Stok)
            asset_val = item['sell_price'] * item['stock']
            ctk.CTkLabel(
                row_frame, text=f"{asset_val:,.0f}",
                font=ctk.CTkFont(size=11, weight="bold"), text_color="#8b5cf6"
            ).grid(row=0, column=9, padx=3, pady=8, sticky="w")
            
            # Action buttons
            action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            action_frame.grid(row=0, column=10, padx=3, pady=5, sticky="w")
            
            # Edit button
            edit_btn = ctk.CTkButton(
                action_frame, text="✏️", width=32, height=28,
                fg_color="#3b82f6", hover_color="#2563eb",
                corner_radius=5,
                command=lambda i=item: self.open_edit_dialog(i)
            )
            edit_btn.pack(side="left", padx=1)
            
            # Sell button (Only if active)
            sell_btn = ctk.CTkButton(
                action_frame, text="🛒", width=32, height=28,
                fg_color="#4ade80" if not is_inactive else "#374151", 
                hover_color="#22c55e" if not is_inactive else "#374151",
                state="normal" if not is_inactive else "disabled",
                corner_radius=5,
                command=lambda i=item: self.open_sell_dialog(i)
            )
            sell_btn.pack(side="left", padx=1)
            
            # Return button
            return_btn = ctk.CTkButton(
                action_frame, text="↩️", width=32, height=28,
                fg_color="#f59e0b", hover_color="#d97706",
                corner_radius=5,
                command=lambda i=item: self.open_return_dialog(i)
            )
            return_btn.pack(side="left", padx=1)
            
            # Delete button
            delete_btn = ctk.CTkButton(
                action_frame, text="Hapus", width=45, height=28,
                font=ctk.CTkFont(size=9),
                fg_color="#ef4444", hover_color="#dc2626",
                corner_radius=5,
                command=lambda i=item: self.delete_item(i)
            )
            delete_btn.pack(side="left", padx=1)
        except Exception as e:
            print(f"ERROR rendering item row {row_idx}: {e}")
    
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
            if not self.active_windows[window_key].winfo_exists():
                del self.active_windows[window_key]
            else:
                self.active_windows[window_key].lift()
                self.active_windows[window_key].focus()
                return
        
        dialog = ItemDialog(self, "Tambah Barang Baru", self.on_item_saved)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def open_edit_dialog(self, item: dict):
        """Open dialog to edit item"""
        window_key = f"edit_item_{item['id']}"
        if window_key in self.active_windows:
            if not self.active_windows[window_key].winfo_exists():
                del self.active_windows[window_key]
            else:
                self.active_windows[window_key].lift()
                self.active_windows[window_key].focus()
                return
        
        dialog = ItemDialog(self, f"Edit Barang: {item['name']}", self.on_item_saved, item)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def open_sell_dialog(self, item: dict):
        """Open dialog to sell item"""
        window_key = f"sell_item_{item['id']}"
        if window_key in self.active_windows:
            if not self.active_windows[window_key].winfo_exists():
                del self.active_windows[window_key]
            else:
                self.active_windows[window_key].lift()
                self.active_windows[window_key].focus()
                return
        
        dialog = SellDialog(self, item, self.on_sale_complete)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def open_return_dialog(self, item: dict):
        """Open dialog to return item"""
        window_key = f"return_item_{item['id']}"
        if window_key in self.active_windows:
            if not self.active_windows[window_key].winfo_exists():
                del self.active_windows[window_key]
            else:
                self.active_windows[window_key].lift()
                self.active_windows[window_key].focus()
                return
        
        dialog = ReturDialog(self, item, self.warehouse, self.on_return_complete)
        self.active_windows[window_key] = dialog
        dialog.protocol("WM_DELETE_WINDOW", lambda: self.close_window(window_key))
    
    def close_window(self, window_key: str):
        """Close and remove window from registry"""
        if window_key in self.active_windows:
            try:
                window = self.active_windows[window_key]
                if window.winfo_exists():
                    window.destroy()
            except Exception:
                pass
            finally:
                if window_key in self.active_windows:
                    del self.active_windows[window_key]
    
    def on_item_saved(self, item_data: dict, item_id: int = None):
        """Handle item save (add or edit) with stay or close option"""
        try:
            is_quitting = getattr(self.winfo_toplevel(), 'is_quitting', False)
        except:
            is_quitting = False

        if item_id:
            # Update existing
            self.warehouse.update_item(
                item_id,
                item_data['name'],
                item_data['stock'],
                item_data['buy_price'],
                item_data['sell_price'],
                item_data['status'],
                item_data['description'],
                item_code=item_data.get('item_code', ''),
                is_active=item_data.get('is_active', 1)
            )
            if not is_quitting:
                self.load_data()
            
            if is_quitting:
                self.close_window(f"edit_item_{item_id}")
            elif messagebox.askyesno("Sukses", "Data barang berhasil diupdate.\n\nApakah Anda ingin menutup jendela ini?"):
                self.close_window(f"edit_item_{item_id}")
        else:
            # Add new
            self.warehouse.add_item(
                item_data['name'], item_data['stock'],
                item_data['buy_price'], item_data['sell_price'],
                item_data['status'], item_data['description'],
                item_code=item_data.get('item_code', ''),
                is_active=item_data.get('is_active', 1)
            )
            if not is_quitting:
                self.load_data()
            
            if is_quitting:
                self.close_window("add_item")
            elif messagebox.askyesno("Sukses", "Barang berhasil ditambah.\n\nApakah Anda ingin menutup jendela ini?"):
                self.close_window("add_item")
    
    def on_sale_complete(self, item_id: int, sale_data: dict = None):
        """Handle sale completion"""
        self.close_window(f"sell_item_{item_id}")
        self.load_data()
    
    def on_return_complete(self, item_id: int):
        """Handle return completion"""
        self.close_window(f"return_item_{item_id}")
        self.load_data()
    
    def delete_item(self, item: dict):
        """Delete item with confirmation"""
        if messagebox.askyesno("Konfirmasi", f"Hapus barang '{item['name']}'?"):
            self.warehouse.delete_item(item['id'])
            self.load_data()


class ImportPreviewDialog(ctk.CTkToplevel):
    """Dialog for previewing Excel data before import"""
    
    def __init__(self, parent, filepath: str, sheets: list, 
                 category_context: str, current_user: str, on_complete):
        super().__init__(parent)
        self.filepath = filepath
        self.sheets = sheets
        self.category_context = category_context
        self.current_user = current_user
        self.on_complete = on_complete
        
        self.title("📥 Preview Import Excel")
        self.configure(fg_color="#1a1a2e")
        self.minsize(800, 600)
        
        self.update_idletasks()
        
        window_width = 900
        window_height = 700
        x = (self.winfo_screenwidth() - window_width) // 2
        y = (self.winfo_screenheight() - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.create_controls()
        self.create_preview_table()
        
        # Load initial data (first sheet)
        if self.sheets:
            self.load_sheet_preview(self.sheets[0])
            
        self.grab_set()
    
    def create_controls(self):
        """Create top controls"""
        control_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=10, height=80)
        control_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        
        ctk.CTkLabel(
            control_frame, text="Pilih Worksheet:", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#cccccc"
        ).pack(side="left", padx=20, pady=20)
        
        self.sheet_var = ctk.StringVar(value=self.sheets[0] if self.sheets else "")
        self.sheet_menu = ctk.CTkOptionMenu(
            control_frame, values=self.sheets,
            variable=self.sheet_var, width=250, height=35,
            fg_color="#374151", button_color="#4b5563",
            command=self.load_sheet_preview
        )
        self.sheet_menu.pack(side="left", padx=10, pady=20)
        
        self.info_label = ctk.CTkLabel(
            control_frame, text="", 
            font=ctk.CTkFont(size=12), text_color="#00d4ff"
        )
        self.info_label.pack(side="left", padx=20, pady=20)
        
        # Action buttons
        ctk.CTkButton(
            control_frame, text="❌ Batal", width=100, height=35,
            fg_color="#374151", hover_color="#4b5563",
            command=self.destroy
        ).pack(side="right", padx=10, pady=20)
        
        self.import_btn = ctk.CTkButton(
            control_frame, text="💾 Import Data", width=150, height=35,
            fg_color="#22c55e", hover_color="#16a34a",
            text_color="#000", font=ctk.CTkFont(weight="bold"),
            command=self.process_import
        )
        self.import_btn.pack(side="right", padx=10, pady=20)
    
    def create_preview_table(self):
        """Create scrollable preview table with bidirectional scrolling support"""
        # Outer container
        preview_container = ctk.CTkFrame(self, fg_color="#1a1a2e")
        preview_container.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        preview_container.grid_columnconfigure(0, weight=1)
        preview_container.grid_rowconfigure(1, weight=1)
        
        # Header for preview
        ctk.CTkLabel(
            preview_container, text="👁️ Preview Data (20 Baris Pertama)",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="#888"
        ).grid(row=0, column=0, sticky="w", padx=5, pady=(0, 5))
        
        # Horizontal Scroll Frame (Outer)
        self.horiz_scroll = ctk.CTkScrollableFrame(
            preview_container, 
            orientation="horizontal",
            fg_color="#1e293b",
            height=400 # Default height constraint
        )
        self.horiz_scroll.grid(row=1, column=0, sticky="nsew")
        
        # Container for Headers + Data inside Horizontal Scroll
        self.inner_container = ctk.CTkFrame(self.horiz_scroll, fg_color="transparent")
        self.inner_container.pack(fill="both", expand=True)
        
        # Header Row Frame
        self.header_frame = ctk.CTkFrame(self.inner_container, fg_color="#374151", height=40)
        self.header_frame.pack(fill="x", pady=(0, 2), anchor="n")
        
        # Vertical Scroll Frame (Inner) - for Data Rows
        self.data_scroll = ctk.CTkScrollableFrame(
            self.inner_container, 
            orientation="vertical",
            fg_color="transparent",
            height=350 # Ensure it has height to scroll
        )
        self.data_scroll.pack(fill="both", expand=True)
    
    def load_sheet_preview(self, sheet_name):
        """Load and display preview data for selected sheet"""
        # Clear current preview
        for widget in self.header_frame.winfo_children():
            widget.destroy()
        for widget in self.data_scroll.winfo_children():
            widget.destroy()
        
        # Fetch data - Increased to 20 rows
        result = preview_excel_data(self.filepath, sheet_name, max_rows=20)
        
        if not result['success']:
            ctk.CTkLabel(
                self.data_scroll, text=f"Error: {result['message']}",
                text_color="#ef4444"
            ).pack(pady=20)
            self.import_btn.configure(state="disabled")
            return
        
        self.import_btn.configure(state="normal")
        self.info_label.configure(text=f"Total Baris: {result['total_rows']}")
        
        headers = result['headers']
        data = result['data']
        
        # Calculate column widths based on content
        col_widths = []
        for i, header in enumerate(headers):
            # Start with header length
            max_len = len(str(header))
            # Check data rows for this column
            for row in data:
                if i < len(row):
                    max_len = max(max_len, len(str(row[i])))
            
            # Convert length to pixel width (approx 9px per char + padding)
            width = min(max(max_len * 9 + 20, 80), 350)
            col_widths.append(width)
        
        # Display Headers
        for i, header in enumerate(headers):
            lbl = ctk.CTkLabel(
                self.header_frame, text=str(header), width=col_widths[i],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#00d4ff"
            )
            lbl.grid(row=0, column=i, padx=2, pady=8)
        
        # Display Rows
        for row_idx, row_data in enumerate(data):
            row_frame = ctk.CTkFrame(self.data_scroll, fg_color="transparent")
            row_frame.pack(fill="x", pady=1)
            
            for col_idx, cell_value in enumerate(row_data):
                lbl = ctk.CTkLabel(
                    row_frame, text=str(cell_value), width=col_widths[col_idx],
                    font=ctk.CTkFont(size=11), text_color="#ccc"
                )
                lbl.grid(row=0, column=col_idx, padx=2, pady=2)
    
    def process_import(self):
        """Execute the import for selected sheet"""
        sheet_name = self.sheet_var.get()
        
        if messagebox.askyesno("Konfirmasi", f"Import data dari sheet '{sheet_name}'?"):
            try:
                result = import_inventory_from_excel(
                    self.filepath, self.category_context, 
                    self.current_user, sheet_name
                )
                
                if result['success']:
                    msg = (
                        f"Import berhasil!\n\n"
                        f"Sheet: {sheet_name}\n"
                        f"Total Item: {result['total_items']}\n"
                        f"Ditambah: {result['added']}\n"
                        f"Diupdate: {result['updated']}"
                    )
                    if "warnings" in result:
                        msg += "\n\nPeringatan (sebagian):\n" + "\n".join(result['warnings'])
                        
                    messagebox.showinfo("Sukses", msg)
                    self.on_complete()
                else:
                    messagebox.showerror("Error", f"Gagal import: {result['message']}")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")


class ItemDialog(ctk.CTkToplevel):
    """Dialog for adding/editing items - SCROLLABLE VERSION"""
    
    def __init__(self, parent, title: str, on_save, item: dict = None):
        super().__init__(parent)
        self.on_save = on_save
        self.item = item
        
        self.title(title)
        
        # Window setup
        self.configure(fg_color="#1a1a2e")
        self.resizable(True, True)
        self.minsize(450, 450)
        
        # Win7 Compatibility: Set transient and lift
        self.transient(parent)
        self.lift()
        
        self.update_idletasks()
        
        # Calculate center position
        window_width = 480
        window_height = 650
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Win7 Compatibility: Re-apply geometry to ensure it shows
        import sys
        if sys.platform == 'win32' and sys.getwindowsversion().major == 6:
            self.after(200, lambda: self.geometry(f"{window_width}x{window_height}+{x}+{y}"))
            
        # Main container grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # SCROLLABLE FRAME for form content
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#374151",
            scrollbar_button_hover_color="#4b5563"
        )
        self.scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.create_form()
        
        if item:
            self.populate_form()
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.grab_set()
        self.focus_force()
        
        # Lock to prevent double saving
        self.saving_in_progress = False

    def on_closing(self):
        """Ask to save before closing"""
        if not self.name_entry.get().strip():
            self.destroy()
            return

        response = messagebox.askyesnocancel("Simpan Perubahan", "Apakah Anda ingin menyimpan perubahan sebelum keluar?")
        if response is True: # Yes
            self.save()
        elif response is False: # No
            self.destroy()

    def create_form(self):
        """Create form fields inside scrollable frame"""
        # Kode Barang
        ctk.CTkLabel(
            self.scroll_frame, text="Kode Barang", 
            text_color="#cccccc", anchor="w"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        
        self.code_entry = ctk.CTkEntry(
            self.scroll_frame, height=40, corner_radius=8,
            placeholder_text="Masukkan kode barang"
        )
        self.code_entry.grid(row=1, column=0, sticky="ew", padx=20)

        # Name
        ctk.CTkLabel(
            self.scroll_frame, text="Nama Barang *", 
            text_color="#cccccc", anchor="w"
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(15, 5))
        
        self.name_entry = ctk.CTkEntry(
            self.scroll_frame, height=40, corner_radius=8,
            placeholder_text="Masukkan nama barang"
        )
        self.name_entry.grid(row=3, column=0, sticky="ew", padx=20)
        
        # Stock
        ctk.CTkLabel(
            self.scroll_frame, text="Stok Awal *", 
            text_color="#cccccc", anchor="w"
        ).grid(row=4, column=0, sticky="w", padx=20, pady=(15, 5))
        
        self.stock_entry = ctk.CTkEntry(
            self.scroll_frame, height=40, corner_radius=8,
            placeholder_text="0"
        )
        self.stock_entry.grid(row=5, column=0, sticky="ew", padx=20)
        
        # Buy Price
        ctk.CTkLabel(
            self.scroll_frame, text="Harga Pokok (Rp) *", 
            text_color="#cccccc", anchor="w"
        ).grid(row=6, column=0, sticky="w", padx=20, pady=(15, 5))
        
        self.buy_price_entry = ctk.CTkEntry(
            self.scroll_frame, height=40, corner_radius=8,
            placeholder_text="0"
        )
        self.buy_price_entry.grid(row=7, column=0, sticky="ew", padx=20)
        
        # Sell Price
        ctk.CTkLabel(
            self.scroll_frame, text="Harga Jual (Rp) *", 
            text_color="#cccccc", anchor="w"
        ).grid(row=8, column=0, sticky="w", padx=20, pady=(15, 5))
        
        self.sell_price_entry = ctk.CTkEntry(
            self.scroll_frame, height=40, corner_radius=8,
            placeholder_text="0"
        )
        self.sell_price_entry.grid(row=9, column=0, sticky="ew", padx=20)
        
        # Status Barang
        ctk.CTkLabel(
            self.scroll_frame, text="Status Barang (Kepemilikan)", 
            text_color="#cccccc", anchor="w"
        ).grid(row=10, column=0, sticky="w", padx=20, pady=(15, 5))
        
        self.status_var = ctk.StringVar(value="Koperasi")
        self.status_menu = ctk.CTkOptionMenu(
            self.scroll_frame, values=["Koperasi", "Konsinyasi"],
            variable=self.status_var, height=40,
            fg_color="#374151", button_color="#4b5563"
        )
        self.status_menu.grid(row=11, column=0, sticky="ew", padx=20)

        # Status Aktif
        ctk.CTkLabel(
            self.scroll_frame, text="Status Aktif", 
            text_color="#cccccc", anchor="w"
        ).grid(row=12, column=0, sticky="w", padx=20, pady=(15, 5))
        
        self.active_var = ctk.StringVar(value="Ya")
        active_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        active_frame.grid(row=13, column=0, sticky="w", padx=20)
        
        ctk.CTkRadioButton(
            active_frame, text="Ya (Aktif)", variable=self.active_var, 
            value="Ya"
        ).pack(side="left", padx=(0, 20))
        
        ctk.CTkRadioButton(
            active_frame, text="Tidak (Nonaktif)", variable=self.active_var, 
            value="Tidak"
        ).pack(side="left")
        
        # Description
        ctk.CTkLabel(
            self.scroll_frame, text="Keterangan / Deskripsi", 
            text_color="#cccccc", anchor="w"
        ).grid(row=14, column=0, sticky="w", padx=20, pady=(15, 5))
        
        self.desc_entry = ctk.CTkTextbox(
            self.scroll_frame, height=80, corner_radius=8,
            fg_color="#374151"
        )
        self.desc_entry.grid(row=15, column=0, sticky="ew", padx=20)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        btn_frame.grid(row=16, column=0, pady=30)
        
        ctk.CTkButton(
            btn_frame, text="Batal", width=120, height=45,
            fg_color="#374151", hover_color="#4b5563",
            font=ctk.CTkFont(size=14),
            command=self.destroy
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame, text="💾 Simpan", width=120, height=45,
            fg_color="#4ade80", hover_color="#22c55e",
            text_color="#000000",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.save
        ).pack(side="left", padx=10)
    
    def populate_form(self):
        """Populate form with existing item data"""
        self.code_entry.delete(0, "end")
        if self.item.get('item_code'):
            self.code_entry.insert(0, self.item['item_code'])

        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, self.item['name'])
        
        self.stock_entry.delete(0, "end")
        self.stock_entry.insert(0, str(self.item['stock']))
        
        self.buy_price_entry.delete(0, "end")
        self.buy_price_entry.insert(0, str(int(self.item['buy_price'])))
        
        self.sell_price_entry.delete(0, "end")
        self.sell_price_entry.insert(0, str(int(self.item['sell_price'])))
        
        self.status_var.set(self.item['status'])
        self.active_var.set("Ya" if self.item.get('is_active', 1) else "Tidak")
        
        self.desc_entry.delete("1.0", "end")
        if self.item.get('description'):
            self.desc_entry.insert("1.0", self.item['description'])
    
    def save(self):
        """Validate and save item manually"""
        if self.saving_in_progress:
            return
            
        try:
            is_quitting = getattr(self.winfo_toplevel(), 'is_quitting', False)
        except:
            is_quitting = False

        name = self.name_entry.get().strip()
        
        try:
            stock = int(self.stock_entry.get() or 0)
            buy_price = float(self.buy_price_entry.get() or 0)
            sell_price = float(self.sell_price_entry.get() or 0)
        except ValueError:
            if not is_quitting:
                messagebox.showerror("Error", "Stok dan harga harus berupa angka!")
            return
        
        if not name:
            if not is_quitting:
                messagebox.showerror("Error", "Nama barang harus diisi!")
            return
        
        if stock < 0 or buy_price < 0 or sell_price < 0:
            if not is_quitting:
                messagebox.showerror("Error", "Nilai tidak boleh negatif!")
            return
        
        self.saving_in_progress = True
        try:
            item_data = {
                'item_code': self.code_entry.get().strip(),
                'name': name,
                'stock': stock,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'status': self.status_var.get(),
                'is_active': 1 if self.active_var.get() == "Ya" else 0,
                'description': self.desc_entry.get("1.0", "end-1c").strip()
            }
            
            self.on_save(item_data, self.item['id'] if self.item else None)
        finally:
            self.saving_in_progress = False


class SellDialog(ctk.CTkToplevel):
    """
    Dialog for selling items with receipt option
    REFACTORED: Member-only checkout with autocomplete search, payment methods
    """
    
    def __init__(self, parent, item: dict, on_sale):
        super().__init__(parent)
        self.item = item
        self.on_sale = on_sale
        self.warehouse = parent.warehouse
        self.category_context = parent.category_context
        self.current_user = parent.current_user
        
        # Import member manager
        from app.modules.members import MemberManager
        self.member_manager = MemberManager(self.current_user)
        
        self.selected_member_id = None
        self.autocomplete_window = None
        
        self.title(f"Jual: {item['name']}")
        self.configure(fg_color="#1a1a2e")
        self.resizable(True, True)
        self.minsize(450, 600)
        
        # CRITICAL: update_idletasks before geometry
        self.update_idletasks()
        
        window_width = 480
        window_height = 650
        x = (self.winfo_screenwidth() - window_width) // 2
        y = (self.winfo_screenheight() - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Scrollable container
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.create_form()
        self.grab_set()
    
    def create_form(self):
        """Create sale form with member selection and payment method"""
        # Item info
        ctk.CTkLabel(
            self.scroll_frame, text=self.item['name'],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00d4ff"
        ).pack(pady=(20, 5))
        
        ctk.CTkLabel(
            self.scroll_frame, text=f"Stok tersedia: {self.item['stock']}",
            text_color="#888888"
        ).pack()
        
        ctk.CTkLabel(
            self.scroll_frame, text=f"Harga: Rp {self.item['sell_price']:,.0f}",
            text_color="#4ade80"
        ).pack(pady=(0, 15))
        
        # Member selection with autocomplete (REQUIRED)
        member_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#16213e", corner_radius=10)
        member_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            member_frame, text="👤 Pilih Anggota (WAJIB)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#f59e0b"
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Autocomplete search entry
        self.member_search = ctk.CTkEntry(
            member_frame, width=380, height=40, corner_radius=8,
            placeholder_text="Ketik nama/NRP anggota..."
        )
        self.member_search.pack(padx=15, pady=(0, 5))
        self.member_search.bind("<KeyRelease>", self.on_member_search)
        self.member_search.bind("<FocusOut>", lambda e: self.after(200, self.hide_autocomplete))
        
        # Selected member display
        self.selected_member_label = ctk.CTkLabel(
            member_frame, text="Belum dipilih",
            font=ctk.CTkFont(size=11),
            text_color="#888"
        )
        self.selected_member_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Autocomplete listbox container (will be positioned relatively)
        self.autocomplete_frame = ctk.CTkFrame(member_frame, fg_color="#374151", corner_radius=5)
        
        # Quantity
        ctk.CTkLabel(self.scroll_frame, text="Jumlah *", text_color="#cccccc"
                     ).pack(anchor="w", padx=40, pady=(15, 5))
        self.qty_entry = ctk.CTkEntry(self.scroll_frame, width=380, height=40, corner_radius=8)
        self.qty_entry.pack(padx=40)
        self.qty_entry.insert(0, "1")
        self.qty_entry.bind("<KeyRelease>", self.update_total)
        
        # Payment Method
        ctk.CTkLabel(self.scroll_frame, text="Metode Pembayaran", text_color="#cccccc"
                     ).pack(anchor="w", padx=40, pady=(15, 5))
        
        payment_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        payment_frame.pack(padx=40)
        
        self.payment_var = ctk.StringVar(value="Tunai")
        
        for method, color in [("Tunai", "#4ade80"), ("Transfer", "#00d4ff"), ("QRIS", "#8b5cf6")]:
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
            text_color="#000000",
            font=ctk.CTkFont(weight="bold"),
            command=self.sell
        ).pack(side="left", padx=10)
    
    def on_member_search(self, event):
        """Handle member search with autocomplete"""
        search_text = self.member_search.get().strip()
        
        if len(search_text) < 2:
            self.hide_autocomplete()
            return
        
        # Get autocomplete suggestions
        suggestions = self.member_manager.autocomplete_search(search_text, limit=8)
        
        if suggestions:
            self.show_autocomplete(suggestions)
        else:
            self.hide_autocomplete()
    
    def show_autocomplete(self, suggestions: list):
        """Show autocomplete dropdown"""
        # Clear existing
        for widget in self.autocomplete_frame.winfo_children():
            widget.destroy()
        
        for member in suggestions:
            display = f"{member['name']} ({member.get('nrp', '-')})"
            btn = ctk.CTkButton(
                self.autocomplete_frame, text=display,
                width=360, height=32, anchor="w",
                font=ctk.CTkFont(size=11),
                fg_color="transparent", hover_color="#4b5563",
                text_color="#ccc",
                command=lambda m=member: self.select_member(m)
            )
            btn.pack(fill="x", padx=5, pady=1)
        
        self.autocomplete_frame.pack(fill="x", padx=15, pady=(0, 10))
    
    def hide_autocomplete(self):
        """Hide autocomplete dropdown"""
        self.autocomplete_frame.pack_forget()
    
    def select_member(self, member: dict):
        """Select a member from autocomplete"""
        self.selected_member_id = member['id']
        display = f"✓ {member['name']} ({member.get('nrp', '-')}) - {member.get('unit', '-')}"
        self.selected_member_label.configure(text=display, text_color="#4ade80")
        self.member_search.delete(0, "end")
        self.member_search.insert(0, member['name'])
        self.hide_autocomplete()
    
    def update_total(self, event=None):
        """Update total price display"""
        try:
            qty = int(self.qty_entry.get())
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
                if messagebox.askyesno("No Anggota available for selection.", 
                                      "Anggota tidak ditemukan atau belum dipilih.\n\n"
                                      "Apakah Anda ingin menambah Anggota baru?"):
                    self.redirect_to_add_member(search_text)
                return
        
        try:
            qty = int(self.qty_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Jumlah harus berupa angka!")
            return
        
        if qty <= 0:
            messagebox.showerror("Error", "Jumlah harus lebih dari 0!")
            return
        
        payment_method = self.payment_var.get()
        
        result = self.warehouse.sell_item(
            self.item['id'], qty, 
            member_id=self.selected_member_id,
            payment_method=payment_method
        )
        
        if result['success']:
            # Generate receipt if checkbox is checked
            if self.print_receipt_var.get():
                try:
                    sale_data = {
                        'item_name': self.item['name'],
                        'qty': qty,
                        'unit_price': self.item['sell_price'],
                        'total': result['total'],
                        'category': self.category_context,
                        'payment_method': payment_method
                    }
                    receipt_path = generate_receipt(sale_data)
                    messagebox.showinfo("Sukses", 
                        f"Penjualan berhasil!\n"
                        f"Total: Rp {result['total']:,.0f}\n"
                        f"Metode: {payment_method}\n\n"
                        f"Struk disimpan di:\n{receipt_path}")
                except Exception as e:
                    messagebox.showinfo("Sukses", 
                        f"Penjualan berhasil!\n"
                        f"Total: Rp {result['total']:,.0f}\n"
                        f"Metode: {payment_method}\n\n"
                        f"(Gagal cetak struk: {str(e)})")
            else:
                messagebox.showinfo("Sukses", f"Penjualan berhasil!\nTotal: Rp {result['total']:,.0f}\nMetode: {payment_method}")
            
            self.on_sale(self.item['id'], {'qty': qty, 'total': result['total'], 'payment_method': payment_method})
        else:
            messagebox.showerror("Error", result['message'])

    def redirect_to_add_member(self, name_input: str):
        """Open MemberDialog specifically for the sell process flow"""
        from app.ui.members_frame import MemberDialog
        
        # Check for similar members first before opening dialog
        check = self.member_manager.check_duplicate_before_create(name_input)
        if check['has_duplicate']:
            if check['exact_match']:
                m = check['exact_match']
                if messagebox.askyesno("Anggota Ditemukan", 
                                      f"Anggota dengan nama '{m['name']}' sudah ada.\n"
                                      f"Gunakan anggota ini?"):
                    self.select_member(m)
                    return
            elif check['similar_matches']:
                similar = check['similar_matches'][0]['member']
                if messagebox.askyesno("Nama Mirip Ditemukan", 
                                      f"Ditemukan anggota dengan nama serupa: '{similar['name']}'\n"
                                      f"Apakah ini orang yang sama?"):
                    self.select_member(similar)
                    return

        # If user says it's different or no matches found, open dialog
        dialog = MemberDialog(self, "Tambah Anggota (Dari Penjualan)", 
                             self.on_member_created_from_sell, 
                             member_manager=self.member_manager)
        dialog.name_entry.insert(0, name_input)
        # Ensure it focuses
        dialog.focus_force()

    def on_member_created_from_sell(self, data: dict, member_id: int = None):
        """Handle member creation completion and select the new member"""
        result = self.member_manager.add_member(
            data['name'], data['rank'], data['unit'],
            data['nrp'], data['phone'], data['address'],
            data['membership_status']
        )
        
        if result['success']:
            new_member = self.member_manager.get_member_by_id(result['id'])
            self.select_member(new_member)
            messagebox.showinfo("Sukses", f"Anggota '{data['name']}' berhasil ditambah dan dipilih.")
        else:
            messagebox.showerror("Error", result['message'])


class ReturDialog(ctk.CTkToplevel):
    """Dialog for returning items - SCROLLABLE VERSION"""
    
    def __init__(self, parent, item: dict, warehouse: WarehouseManager, on_return):
        super().__init__(parent)
        self.item = item
        self.warehouse = warehouse
        self.on_return = on_return
        
        self.title(f"Retur: {item['name']}")
        self.configure(fg_color="#1a1a2e")
        self.resizable(True, True)
        self.minsize(450, 450)
        
        # CRITICAL: update_idletasks before geometry
        self.update_idletasks()
        
        window_width = 480
        window_height = 500
        x = (self.winfo_screenwidth() - window_width) // 2
        y = (self.winfo_screenheight() - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Scrollable container
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.create_form()
        self.grab_set()
        self.focus_force()
    
    def create_form(self):
        """Create return form inside scrollable frame"""
        # Header info
        ctk.CTkLabel(
            self.scroll_frame, text="↩️ Form Retur Barang",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f59e0b"
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            self.scroll_frame, text=self.item['name'],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff"
        ).pack()
        
        ctk.CTkLabel(
            self.scroll_frame, text=f"Stok saat ini: {self.item['stock']}",
            text_color="#888888"
        ).pack(pady=(0, 20))
        
        # Quantity
        ctk.CTkLabel(self.scroll_frame, text="Jumlah Retur *", text_color="#cccccc"
                     ).pack(anchor="w", padx=30, pady=(10, 5))
        self.qty_entry = ctk.CTkEntry(self.scroll_frame, height=40, corner_radius=8)
        self.qty_entry.pack(padx=30, fill="x")
        
        # Reason
        ctk.CTkLabel(self.scroll_frame, text="Alasan Retur *", text_color="#cccccc"
                     ).pack(anchor="w", padx=30, pady=(15, 5))
        self.reason_text = ctk.CTkTextbox(self.scroll_frame, height=100, corner_radius=8)
        self.reason_text.pack(padx=30, fill="x")
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        btn_frame.pack(pady=30, fill="x", padx=30)
        
        ctk.CTkButton(
            btn_frame, text="Batal", width=100, height=40,
            fg_color="#374151", hover_color="#4b5563",
            command=self.destroy
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame, text="Submit", width=120, height=40,
            fg_color="#f59e0b", hover_color="#d97706",
            text_color="#000000",
            font=ctk.CTkFont(weight="bold"),
            command=self.process_return
        ).pack(side="right")
    
    def process_return(self):
        """Process return"""
        try:
            qty_str = ''.join(filter(str.isdigit, self.qty_entry.get()))
            qty = int(qty_str) if qty_str else 0
        except ValueError:
            messagebox.showerror("Error", "Jumlah harus berupa angka!")
            return
        
        reason = self.reason_text.get("1.0", "end-1c").strip()
        
        if qty <= 0:
            messagebox.showerror("Error", "Jumlah harus lebih dari 0!")
            return
        
        if not reason:
            messagebox.showerror("Error", "Alasan retur harus diisi!")
            return
        
        result = self.warehouse.retur_barang(self.item['id'], qty, reason)
        
        if result['success']:
            messagebox.showinfo("Sukses", f"Retur berhasil dicatat!\nSisa stok: {result['remaining_stock']}")
            self.on_return(self.item['id'])
        else:
            messagebox.showerror("Error", result['message'])
