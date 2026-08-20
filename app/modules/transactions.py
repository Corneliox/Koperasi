"""
Transactions Module - Transaction History and Reporting
"""
from datetime import datetime, timedelta
from app.database.connection import get_connection
from app.utils.decorators import handle_db_errors


class TransactionManager:
    """Manager class for transaction queries and reporting"""
    
    def __init__(self, category_context: str):
        """
        Initialize transaction manager
        :param category_context: 'SEMBAKO' or 'TAKTIKAL'
        """
        self.category_context = category_context
    
    @handle_db_errors
    def get_transactions(self, member_id: int = None, 
                         start_date: str = None, end_date: str = None,
                         payment_method: str = None, search_text: str = None,
                         sort_by: str = None, limit: int = 500, offset: int = 0) -> list:
        """
        Get transactions with filters, search, sorting, and pagination at SQL level
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT t.*, w.name as item_name, m.name as member_name, m.nrp as member_nrp
                FROM transactions t
                LEFT JOIN warehouse w ON t.item_id = w.id
                LEFT JOIN members m ON t.member_id = m.id
                WHERE t.category_type = ?
            """
            params = [self.category_context]
            
            if member_id:
                query += " AND t.member_id = ?"
                params.append(member_id)
            
            if start_date:
                query += " AND DATE(t.date) >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(t.date) <= ?"
                params.append(end_date)
            
            if payment_method and payment_method != "Semua":
                query += " AND t.payment_method = ?"
                params.append(payment_method)
                
            if search_text:
                search_term = f"%{search_text.strip().lower()}%"
                query += " AND (LOWER(COALESCE(w.name, '')) LIKE ? OR LOWER(COALESCE(m.name, '')) LIKE ? OR LOWER(COALESCE(m.nrp, '')) LIKE ?)"
                params.extend([search_term, search_term, search_term])
            
            # Apply sorting
            if sort_by == "Qty (Tinggi)":
                order_clause = " ORDER BY t.qty DESC, t.date DESC"
            elif sort_by == "Qty (Rendah)":
                order_clause = " ORDER BY t.qty ASC, t.date DESC"
            elif sort_by == "Profit (Tinggi)":
                order_clause = " ORDER BY (t.total_price - (t.unit_price * 0.85 * t.qty)) DESC, t.date DESC"
            elif sort_by == "Profit (Rendah)":
                order_clause = " ORDER BY (t.total_price - (t.unit_price * 0.85 * t.qty)) ASC, t.date DESC"
            else:
                order_clause = " ORDER BY t.date DESC, t.id DESC"
            
            query += order_clause
            
            if limit is not None:
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])
            
            cursor.execute(query, params)
            transactions = [dict(row) for row in cursor.fetchall()]
            return transactions
        finally:
            conn.close()

    def get_transaction_count(self, member_id: int = None, 
                              start_date: str = None, end_date: str = None,
                              payment_method: str = None, search_text: str = None) -> int:
        """Get total count of transactions matching filters at SQL level"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT COUNT(*) 
                FROM transactions t 
                LEFT JOIN warehouse w ON t.item_id = w.id
                LEFT JOIN members m ON t.member_id = m.id
                WHERE t.category_type = ?
            """
            params = [self.category_context]
            
            if member_id:
                query += " AND t.member_id = ?"
                params.append(member_id)
            
            if start_date:
                query += " AND DATE(t.date) >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(t.date) <= ?"
                params.append(end_date)
                
            if payment_method and payment_method != "Semua":
                query += " AND t.payment_method = ?"
                params.append(payment_method)
                
            if search_text:
                search_term = f"%{search_text.strip().lower()}%"
                query += " AND (LOWER(COALESCE(w.name, '')) LIKE ? OR LOWER(COALESCE(m.name, '')) LIKE ? OR LOWER(COALESCE(m.nrp, '')) LIKE ?)"
                params.extend([search_term, search_term, search_term])
                
            cursor.execute(query, params)
            row = cursor.fetchone()
            count = row[0] if row else 0
            return count
        finally:
            conn.close()
    
    def get_monthly_summary(self, year: int, month: int) -> dict:
        """Get monthly transaction summary"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            date_pattern = f"{year}-{month:02d}%"
            
            cursor.execute(
                """SELECT COUNT(*), COALESCE(SUM(total_price), 0), COALESCE(SUM(qty), 0)
                   FROM transactions 
                   WHERE category_type = ? AND date LIKE ?""",
                (self.category_context, date_pattern)
            )
            row = cursor.fetchone()
            
            return {
                "transaction_count": row[0] if row else 0,
                "total_revenue": row[1] if row else 0.0,
                "total_items_sold": row[2] if row else 0
            }
        finally:
            conn.close()
    
    def get_yearly_summary(self, year: int) -> dict:
        """Get yearly transaction summary"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT COUNT(*), COALESCE(SUM(total_price), 0), COALESCE(SUM(qty), 0)
                   FROM transactions 
                   WHERE category_type = ? AND strftime('%Y', date) = ?""",
                (self.category_context, str(year))
            )
            row = cursor.fetchone()
            
            return {
                "transaction_count": row[0] if row else 0,
                "total_revenue": row[1] if row else 0.0,
                "total_items_sold": row[2] if row else 0
            }
        finally:
            conn.close()
    
    def get_top_selling_items(self, limit: int = 10, days: int = 30) -> list:
        """Get top selling items in the past N days"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute(
                """SELECT w.name, SUM(t.qty) as total_qty, SUM(t.total_price) as total_revenue
                   FROM transactions t
                   JOIN warehouse w ON t.item_id = w.id
                   WHERE t.category_type = ? AND DATE(t.date) >= ?
                   GROUP BY t.item_id
                   ORDER BY total_qty DESC
                   LIMIT ?""",
                (self.category_context, start_date, limit)
            )
            
            items = [dict(row) for row in cursor.fetchall()]
            return items
        finally:
            conn.close()
    
    def get_daily_sales(self, days: int = 30) -> list:
        """Get daily sales for chart"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT DATE(date) as sale_date, SUM(total_price) as revenue, COUNT(*) as count
                   FROM transactions 
                   WHERE category_type = ? AND DATE(date) >= DATE('now', ?)
                   GROUP BY DATE(date)
                   ORDER BY sale_date""",
                (self.category_context, f'-{days} days')
            )
            
            sales = [dict(row) for row in cursor.fetchall()]
            return sales
        finally:
            conn.close()
    
    def get_member_ranking(self, limit: int = 10) -> list:
        """Get top members by transaction value"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT m.name, m.nrp, COUNT(t.id) as transaction_count, 
                          SUM(t.total_price) as total_spent
                   FROM transactions t
                   JOIN members m ON t.member_id = m.id
                   WHERE t.category_type = ?
                   GROUP BY t.member_id
                   ORDER BY total_spent DESC
                   LIMIT ?""",
                (self.category_context, limit)
            )
            
            members = [dict(row) for row in cursor.fetchall()]
            return members
        finally:
            conn.close()
