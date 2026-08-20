"""
Warehouse Module - CRUD Operations with Mutation Tracking
All operations are filtered by category_context (SEMBAKO/TAKTIKAL)
"""
from datetime import datetime
from app.database.connection import get_connection
from app.utils.audit_log import log_audit
from app.utils.decorators import handle_db_errors


class WarehouseManager:
    """Manager class for warehouse operations with category context"""
    
    def __init__(self, category_context: str, current_user: str = "admin"):
        """
        Initialize warehouse manager
        :param category_context: 'SEMBAKO' or 'TAKTIKAL'
        :param current_user: Current logged in user for logging
        """
        self.category_context = category_context
        self.current_user = current_user
    
    @handle_db_errors
    def get_all_items(self, search_term: str = None, limit: int = None, offset: int = 0,
                      sort_column: str = "name", sort_order: str = "ASC") -> list:
        """Get all items filtered by category context with pagination and sorting"""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM warehouse WHERE category_type = ?"
        params = [self.category_context]
        
        if search_term:
            query += " AND (name LIKE ? OR item_code LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
            
        # Validation for sort_column to prevent SQL injection
        allowed_columns = ["id", "item_code", "name", "stock", "buy_price", "sell_price", "status", "is_active"]
        if sort_column not in allowed_columns:
            sort_column = "name"
        
        if sort_order.upper() not in ["ASC", "DESC"]:
            sort_order = "ASC"
            
        query += f" ORDER BY {sort_column} {sort_order}"
        
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
        cursor.execute(query, params)
        
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items

    @handle_db_errors
    def get_items_count(self, search_term: str = None) -> int:
        """Get total count of items matching search criteria"""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) FROM warehouse WHERE category_type = ?"
        params = [self.category_context]
        
        if search_term:
            query += " AND (name LIKE ? OR item_code LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
            
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    @handle_db_errors
    def get_item_by_id(self, item_id: int) -> dict:
        """Get single item by ID"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM warehouse WHERE id = ? AND category_type = ?",
            (item_id, self.category_context)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @handle_db_errors
    def add_item(self, name: str, stock: int, buy_price: float, sell_price: float,
                 status: str = "Koperasi", description: str = "", 
                 item_code: str = "", is_active: int = 1) -> dict:
        """
        Add new item to warehouse
        Auto-creates 'IN' mutation record
        """
        # Validation
        if not name:
            return {"success": False, "message": "Nama barang wajib diisi"}
            
        try:
            stock = int(stock) if stock is not None else 0
            buy_price = float(buy_price) if buy_price is not None else 0.0
            sell_price = float(sell_price) if sell_price is not None else 0.0
        except (ValueError, TypeError):
            return {"success": False, "message": "Stok dan harga harus berupa angka"}

        if stock < 0 or buy_price < 0 or sell_price < 0:
            return {"success": False, "message": "Stok dan harga tidak boleh bernilai negatif"}

        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Insert item
            cursor.execute(
                """INSERT INTO warehouse 
                   (item_code, name, category_type, stock, buy_price, sell_price, status, is_active, description)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (item_code, name, self.category_context, stock, buy_price, sell_price, status, is_active, description)
            )
            item_id = cursor.lastrowid
            
            # Create initial IN mutation if stock > 0
            if stock > 0:
                cursor.execute(
                    """INSERT INTO warehouse_mutation (item_id, type, qty, description)
                       VALUES (?, 'IN', ?, ?)""",
                    (item_id, stock, f"Stok awal: {name}")
                )
            
            conn.commit()
            
            # Log activity
            log_audit(
                self.current_user, "INVENTORY", "CREATE",
                "warehouse", item_id, None, 
                {"name": name, "stock": stock, "category": self.category_context, "code": item_code},
                f"Menambah barang: {name} ({item_code}), Stok: {stock}", "INFO"
            )
            
            return {"success": True, "message": "Barang berhasil ditambahkan", "id": item_id}
        finally:
            conn.close()

    def create_item(self, data: dict) -> dict:
        """Alias for add_item to match UI expectations and handle dict input"""
        return self.add_item(
            name=data.get('name'),
            stock=data.get('stock', 0),
            buy_price=data.get('buy_price', 0),
            sell_price=data.get('sell_price', 0),
            status=data.get('status', 'Koperasi'),
            description=data.get('description', ''),
            item_code=data.get('item_code', ''),
            is_active=data.get('is_active', 1)
        )
    
    @handle_db_errors
    def update_item(self, item_id: int, name_or_data = None, stock: int = None, buy_price: float = None,
                    sell_price: float = None, status: str = None, description: str = None,
                    item_code: str = "", is_active: int = 1, name: str = None, **kwargs) -> dict:
        """
        Update item and create mutation if stock changed
        Supports positional arguments, keyword arguments, and dictionary input
        """
        # Handle dictionary input if passed as second argument
        if isinstance(name_or_data, dict):
            data = name_or_data
            name = data.get('name')
            stock = data.get('stock')
            buy_price = data.get('buy_price')
            sell_price = data.get('sell_price')
            status = data.get('status')
            description = data.get('description', '')
            item_code = data.get('item_code', '')
            is_active = data.get('is_active', 1)
        else:
            if name is None:
                name = name_or_data

        # Get old stock first
        old_item = self.get_item_by_id(item_id)
        if not old_item:
            return {"success": False, "message": "Barang tidak ditemukan"}
        
        try:
            stock = int(stock) if stock is not None else old_item['stock']
            buy_price = float(buy_price) if buy_price is not None else old_item['buy_price']
            sell_price = float(sell_price) if sell_price is not None else old_item['sell_price']
            status = status if status is not None else old_item.get('status', 'Koperasi')
            name = name if name is not None else old_item['name']
        except (ValueError, TypeError):
            return {"success": False, "message": "Stok dan harga harus berupa angka valid"}

        if stock < 0 or buy_price < 0 or sell_price < 0:
            return {"success": False, "message": "Stok dan harga tidak boleh bernilai negatif"}
        
        old_stock = old_item['stock']
        stock_diff = stock - old_stock
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Update item
            cursor.execute(
                """UPDATE warehouse 
                   SET item_code=?, name=?, stock=?, buy_price=?, sell_price=?, status=?, 
                       is_active=?, description=?, updated_at=CURRENT_TIMESTAMP
                   WHERE id=? AND category_type=?""",
                (item_code, name, stock, buy_price, sell_price, status, is_active, description, 
                 item_id, self.category_context)
            )
            
            # Create mutation if stock changed
            if stock_diff != 0:
                mutation_type = 'IN' if stock_diff > 0 else 'OUT'
                cursor.execute(
                    """INSERT INTO warehouse_mutation (item_id, type, qty, description)
                       VALUES (?, ?, ?, ?)""",
                    (item_id, mutation_type, abs(stock_diff), 
                     f"Koreksi stok: {old_stock} -> {stock}")
                )
            
            conn.commit()
            
            # Log activity
            log_audit(
                self.current_user, "INVENTORY", "UPDATE",
                "warehouse", item_id, old_item, 
                {"name": name, "stock": stock, "is_active": is_active},
                f"Edit barang ID {item_id}: {name}, Stok: {old_stock} -> {stock}, Aktif: {is_active}", "INFO"
            )
            
            return {"success": True, "message": "Data barang berhasil diupdate"}
        finally:
            conn.close()
    
    @handle_db_errors
    def delete_item(self, item_id: int) -> dict:
        """Delete item from warehouse"""
        item = self.get_item_by_id(item_id)
        if not item:
            return {"success": False, "message": "Barang tidak ditemukan"}
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM warehouse WHERE id = ? AND category_type = ?",
                (item_id, self.category_context)
            )
            conn.commit()
            
            log_audit(
                self.current_user, "INVENTORY", "DELETE",
                "warehouse", item_id, item, None,
                f"Hapus barang: {item['name']} (ID: {item_id})", "WARNING"
            )
            
            return {"success": True, "message": "Barang berhasil dihapus"}
        finally:
            conn.close()
    
    @handle_db_errors
    def sell_item(self, item_id: int, qty: int, member_id: int = None,
                  payment_method: str = "Tunai", current_user: str = None) -> dict:
        """
        Sell item - decreases stock atomically and creates transaction
        """
        if current_user:
            self.current_user = current_user

        try:
            qty = int(qty)
        except (ValueError, TypeError):
            return {"success": False, "message": "Jumlah harus berupa angka"}

        if qty <= 0:
            return {"success": False, "message": "Jumlah penjualan harus lebih dari 0"}

        item = self.get_item_by_id(item_id)
        if not item:
            return {"success": False, "message": "Barang tidak ditemukan"}
        
        if not item.get('is_active', 1):
            return {"success": False, "message": "Barang ini sudah tidak aktif dan tidak bisa dijual."}
        
        total_price = item['sell_price'] * qty
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Atomic stock deduction
            cursor.execute(
                "UPDATE warehouse SET stock = stock - ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND stock >= ?",
                (qty, item_id, qty)
            )
            if cursor.rowcount == 0:
                return {"success": False, "message": f"Stok tidak cukup. Tersedia: {item['stock']}"}
            
            new_stock = item['stock'] - qty
            
            # Create OUT mutation
            cursor.execute(
                """INSERT INTO warehouse_mutation (item_id, type, qty, description)
                   VALUES (?, 'OUT', ?, ?)""",
                (item_id, qty, f"Penjualan: {qty} unit")
            )
            
            # Create transaction record
            cursor.execute(
                """INSERT INTO transactions 
                   (item_id, member_id, qty, unit_price, total_price, category_type, payment_method)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (item_id, member_id, qty, item['sell_price'], total_price, 
                 self.category_context, payment_method)
            )
            transaction_id = cursor.lastrowid
            
            conn.commit()
            
            log_audit(
                self.current_user, "TRANSACTION", "CREATE",
                "warehouse", item_id, 
                {"stock": item['stock']}, {"stock": new_stock},
                f"Jual {item['name']} x{qty} = Rp {total_price:,.0f} ({payment_method})", "INFO"
            )
            
            return {
                "success": True, 
                "message": "Penjualan berhasil",
                "total": total_price,
                "remaining_stock": new_stock,
                "transaction_id": transaction_id
            }
        finally:
            conn.close()
    
    @handle_db_errors
    def sell_items_bulk(self, items_to_sell: list, member_id: int, 
                       payment_method: str = "Tunai") -> dict:
        """
        Sell multiple items in a single transaction process
        :param items_to_sell: List of dicts {'id': item_id, 'qty': quantity}
        :param member_id: ID of the member
        :param payment_method: Payment method used
        """
        if not items_to_sell:
            return {"success": False, "message": "Keranjang kosong"}
            
        conn = get_connection()
        try:
            cursor = conn.cursor()
            total_invoice = 0
            sold_items = []
            transaction_ids = []
            
            # 1. Validation phase
            for entry in items_to_sell:
                item_id = entry['id']
                try:
                    qty = int(entry['qty'])
                except (ValueError, TypeError):
                    return {"success": False, "message": f"Jumlah barang tidak valid untuk ID {item_id}"}

                if qty <= 0:
                    return {"success": False, "message": "Jumlah barang harus lebih dari 0"}
                
                cursor.execute("SELECT name, stock, sell_price, is_active FROM warehouse WHERE id = ?", (item_id,))
                row = cursor.fetchone()
                if not row:
                    return {"success": False, "message": f"Item ID {item_id} tidak ditemukan"}
                
                item = dict(row)
                if not item.get('is_active', 1):
                    return {"success": False, "message": f"Item '{item['name']}' sudah tidak aktif"}
                
                if item['stock'] < qty:
                    return {"success": False, "message": f"Stok '{item['name']}' tidak cukup. Tersedia: {item['stock']}"}
                
                total_invoice += item['sell_price'] * qty
                sold_items.append({
                    'id': item_id,
                    'name': item['name'],
                    'qty': qty,
                    'price': item['sell_price']
                })
            
            # 2. Execution phase (Atomic)
            for item in sold_items:
                cursor.execute(
                    "UPDATE warehouse SET stock = stock - ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND stock >= ?",
                    (item['qty'], item['id'], item['qty'])
                )
                if cursor.rowcount == 0:
                    conn.rollback()
                    return {"success": False, "message": f"Gagal: Stok '{item['name']}' berubah atau tidak cukup!"}
                
                # Create OUT mutation
                cursor.execute(
                    """INSERT INTO warehouse_mutation (item_id, type, qty, description)
                       VALUES (?, 'OUT', ?, ?)""",
                    (item['id'], item['qty'], f"Penjualan Bulk: {item['qty']} unit")
                )
                
                # Create transaction record
                cursor.execute(
                    """INSERT INTO transactions 
                       (item_id, member_id, qty, unit_price, total_price, category_type, payment_method)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (item['id'], member_id, item['qty'], item['price'], 
                     item['qty'] * item['price'], self.category_context, payment_method)
                )
                transaction_ids.append(cursor.lastrowid)
            
            conn.commit()
            
            log_audit(
                self.current_user, "TRANSACTION", "CREATE",
                "warehouse", None, None, None,
                f"Jual Bulk ke Member ID {member_id}: {len(sold_items)} jenis barang, Total: Rp {total_invoice:,.0f} ({payment_method})", "INFO"
            )
            
            return {
                "success": True, 
                "message": f"Penjualan {len(sold_items)} item berhasil!",
                "total": total_invoice,
                "items": sold_items,
                "transaction_ids": transaction_ids
            }
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @handle_db_errors
    def retur_barang(self, item_id: int, qty: int, reason: str) -> dict:
        """
        Return item - decreases stock (returns to supplier/disposal)
        Creates RETURN mutation
        """
        try:
            qty = int(qty)
        except (ValueError, TypeError):
            return {"success": False, "message": "Jumlah retur harus berupa angka"}

        if qty <= 0:
            return {"success": False, "message": "Jumlah retur harus lebih besar dari 0"}

        item = self.get_item_by_id(item_id)
        if not item:
            return {"success": False, "message": "Barang tidak ditemukan"}
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Atomic update
            cursor.execute(
                "UPDATE warehouse SET stock = stock - ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND stock >= ?",
                (qty, item_id, qty)
            )
            if cursor.rowcount == 0:
                return {"success": False, "message": f"Stok tidak cukup untuk retur. Tersedia: {item['stock']}"}
            
            new_stock = item['stock'] - qty
            
            # Create RETURN mutation
            cursor.execute(
                """INSERT INTO warehouse_mutation (item_id, type, qty, description)
                   VALUES (?, 'RETURN', ?, ?)""",
                (item_id, qty, f"Retur: {reason}")
            )
            
            conn.commit()
            
            log_audit(
                self.current_user, "INVENTORY", "RETURN",
                "warehouse", item_id, 
                {"stock": item['stock']}, {"stock": new_stock},
                f"Retur {item['name']} x{qty}. Alasan: {reason}", "WARNING"
            )
            
            return {
                "success": True, 
                "message": "Retur berhasil dicatat",
                "remaining_stock": new_stock
            }
        finally:
            conn.close()
    
    @handle_db_errors
    def return_item(self, item_id: int, qty: int, reason: str) -> dict:
        """Alias for retur_barang to match UI expectations"""
        return self.retur_barang(item_id, qty, reason)
    
    @handle_db_errors
    def add_stock(self, item_id: int, qty: int, description: str = "") -> dict:
        """Add stock to existing item"""
        try:
            qty = int(qty)
        except (ValueError, TypeError):
            return {"success": False, "message": "Jumlah tambah stok harus berupa angka"}

        if qty <= 0:
            return {"success": False, "message": "Jumlah tambah stok harus lebih dari 0"}

        item = self.get_item_by_id(item_id)
        if not item:
            return {"success": False, "message": "Barang tidak ditemukan"}
        
        new_stock = item['stock'] + qty
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE warehouse SET stock = stock + ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (qty, item_id)
            )
            
            cursor.execute(
                """INSERT INTO warehouse_mutation (item_id, type, qty, description)
                   VALUES (?, 'IN', ?, ?)""",
                (item_id, qty, description or f"Tambah stok: {qty} unit")
            )
            
            conn.commit()
            
            log_audit(
                self.current_user, "INVENTORY", "UPDATE",
                "warehouse", item_id, 
                {"stock": item['stock']}, {"stock": new_stock},
                f"Tambah stok {item['name']}: +{qty} (Total: {new_stock})", "INFO"
            )
            
            return {"success": True, "message": "Stok berhasil ditambah", "new_stock": new_stock}
        finally:
            conn.close()
    
    def get_mutations(self, item_id: int = None, limit: int = 100) -> list:
        """Get mutation history"""
        conn = get_connection()
        cursor = conn.cursor()
        
        if item_id:
            cursor.execute(
                """SELECT wm.*, w.name as item_name 
                   FROM warehouse_mutation wm
                   JOIN warehouse w ON wm.item_id = w.id
                   WHERE w.category_type = ? AND wm.item_id = ?
                   ORDER BY wm.date DESC LIMIT ?""",
                (self.category_context, item_id, limit)
            )
        else:
            cursor.execute(
                """SELECT wm.*, w.name as item_name 
                   FROM warehouse_mutation wm
                   JOIN warehouse w ON wm.item_id = w.id
                   WHERE w.category_type = ?
                   ORDER BY wm.date DESC LIMIT ?""",
                (self.category_context, limit)
            )
        
        mutations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return mutations
    
    def get_low_stock_items(self, threshold: int = 10) -> list:
        """Get items with low stock"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM warehouse 
               WHERE category_type = ? AND stock <= ?
               ORDER BY stock ASC""",
            (self.category_context, threshold)
        )
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    
    @handle_db_errors
    def get_statistics(self) -> dict:
        """Get warehouse statistics for dashboard"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Total items
        cursor.execute(
            "SELECT COUNT(*) FROM warehouse WHERE category_type = ?",
            (self.category_context,)
        )
        total_items = cursor.fetchone()[0]
        
        # Total stock value
        cursor.execute(
            "SELECT SUM(stock * buy_price) FROM warehouse WHERE category_type = ?",
            (self.category_context,)
        )
        total_value = cursor.fetchone()[0] or 0
        
        # Low stock count
        cursor.execute(
            "SELECT COUNT(*) FROM warehouse WHERE category_type = ? AND stock <= 10",
            (self.category_context,)
        )
        low_stock_count = cursor.fetchone()[0]
        
        # Today's sales
        cursor.execute(
            """SELECT COUNT(*), COALESCE(SUM(total_price), 0) FROM transactions 
               WHERE category_type = ? AND DATE(date) = DATE('now')""",
            (self.category_context,)
        )
        row = cursor.fetchone()
        today_sales_count = row[0]
        today_sales_total = row[1]
        
        conn.close()
        
        return {
            "total_items": total_items,
            "total_value": total_value,
            "low_stock_count": low_stock_count,
            "today_sales_count": today_sales_count,
            "today_sales_total": today_sales_total
        }
