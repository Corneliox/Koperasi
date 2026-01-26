"""
Warehouse Module - CRUD Operations with Mutation Tracking
All operations are filtered by category_context (SEMBAKO/TAKTIKAL)
"""
from datetime import datetime
from app.database.connection import get_connection, log_activity


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
    
    def get_all_items(self, search_term: str = None, limit: int = None, offset: int = 0) -> list:
        """Get all items filtered by category context with pagination"""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM warehouse WHERE category_type = ?"
        params = [self.category_context]
        
        if search_term:
            query += " AND name LIKE ?"
            params.append(f"%{search_term}%")
            
        query += " ORDER BY name"
        
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
        cursor.execute(query, params)
        
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items

    def get_items_count(self, search_term: str = None) -> int:
        """Get total count of items matching search criteria"""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) FROM warehouse WHERE category_type = ?"
        params = [self.category_context]
        
        if search_term:
            query += " AND name LIKE ?"
            params.append(f"%{search_term}%")
            
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
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
    
    def add_item(self, name: str, stock: int, buy_price: float, sell_price: float,
                 status: str = "Koperasi", description: str = "") -> int:
        """
        Add new item to warehouse
        Auto-creates 'IN' mutation record
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        # Insert item
        cursor.execute(
            """INSERT INTO warehouse 
               (name, category_type, stock, buy_price, sell_price, status, description)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, self.category_context, stock, buy_price, sell_price, status, description)
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
        conn.close()
        
        # Log activity
        log_activity(
            self.current_user, 
            "TAMBAH_BARANG",
            f"Menambah barang: {name}, Stok: {stock}, Kategori: {self.category_context}"
        )
        
        return item_id
    
    def update_item(self, item_id: int, name: str, stock: int, buy_price: float,
                    sell_price: float, status: str, description: str) -> bool:
        """
        Update item and create mutation if stock changed
        """
        # Get old stock first
        old_item = self.get_item_by_id(item_id)
        if not old_item:
            return False
        
        old_stock = old_item['stock']
        stock_diff = stock - old_stock
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Update item
        cursor.execute(
            """UPDATE warehouse 
               SET name=?, stock=?, buy_price=?, sell_price=?, status=?, 
                   description=?, updated_at=CURRENT_TIMESTAMP
               WHERE id=? AND category_type=?""",
            (name, stock, buy_price, sell_price, status, description, 
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
        conn.close()
        
        # Log activity
        log_activity(
            self.current_user,
            "EDIT_BARANG",
            f"Edit barang ID {item_id}: {name}, Stok: {old_stock} -> {stock}"
        )
        
        return True
    
    def delete_item(self, item_id: int) -> bool:
        """Delete item from warehouse"""
        item = self.get_item_by_id(item_id)
        if not item:
            return False
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM warehouse WHERE id = ? AND category_type = ?",
            (item_id, self.category_context)
        )
        conn.commit()
        conn.close()
        
        log_activity(
            self.current_user,
            "HAPUS_BARANG",
            f"Hapus barang: {item['name']} (ID: {item_id})"
        )
        
        return True
    
    def sell_item(self, item_id: int, qty: int, member_id: int = None,
                  payment_method: str = "Tunai") -> dict:
        """
        Sell item - decreases stock and creates transaction
        """
        item = self.get_item_by_id(item_id)
        if not item:
            return {"success": False, "message": "Barang tidak ditemukan"}
        
        if item['stock'] < qty:
            return {"success": False, "message": f"Stok tidak cukup. Tersedia: {item['stock']}"}
        
        new_stock = item['stock'] - qty
        total_price = item['sell_price'] * qty
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Update stock
        cursor.execute(
            "UPDATE warehouse SET stock = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_stock, item_id)
        )
        
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
        
        conn.commit()
        conn.close()
        
        log_activity(
            self.current_user,
            "PENJUALAN",
            f"Jual {item['name']} x{qty} = Rp {total_price:,.0f}"
        )
        
        return {
            "success": True, 
            "message": "Penjualan berhasil",
            "total": total_price,
            "remaining_stock": new_stock
        }
    
    def retur_barang(self, item_id: int, qty: int, reason: str) -> dict:
        """
        Return item - decreases stock (returns to supplier/disposal)
        Creates RETURN mutation
        """
        item = self.get_item_by_id(item_id)
        if not item:
            return {"success": False, "message": "Barang tidak ditemukan"}
        
        if item['stock'] < qty:
            return {"success": False, "message": f"Stok tidak cukup untuk retur. Tersedia: {item['stock']}"}
        
        new_stock = item['stock'] - qty
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Update stock
        cursor.execute(
            "UPDATE warehouse SET stock = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_stock, item_id)
        )
        
        # Create RETURN mutation
        cursor.execute(
            """INSERT INTO warehouse_mutation (item_id, type, qty, description)
               VALUES (?, 'RETURN', ?, ?)""",
            (item_id, qty, f"Retur: {reason}")
        )
        
        conn.commit()
        conn.close()
        
        log_activity(
            self.current_user,
            "RETUR_BARANG",
            f"Retur {item['name']} x{qty}. Alasan: {reason}"
        )
        
        return {
            "success": True,
            "message": "Retur berhasil dicatat",
            "remaining_stock": new_stock
        }
    
    def add_stock(self, item_id: int, qty: int, description: str = "") -> dict:
        """Add stock to existing item"""
        item = self.get_item_by_id(item_id)
        if not item:
            return {"success": False, "message": "Barang tidak ditemukan"}
        
        new_stock = item['stock'] + qty
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE warehouse SET stock = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_stock, item_id)
        )
        
        cursor.execute(
            """INSERT INTO warehouse_mutation (item_id, type, qty, description)
               VALUES (?, 'IN', ?, ?)""",
            (item_id, qty, description or f"Tambah stok: {qty} unit")
        )
        
        conn.commit()
        conn.close()
        
        log_activity(
            self.current_user,
            "TAMBAH_STOK",
            f"Tambah stok {item['name']}: +{qty} (Total: {new_stock})"
        )
        
        return {"success": True, "message": "Stok berhasil ditambah", "new_stock": new_stock}
    
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
