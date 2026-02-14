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
                         limit: int = 500, offset: int = 0) -> list:
        """
        Get transactions with filters and pagination
        """
        conn = get_connection()
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
        
        query += " ORDER BY t.date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return transactions

    def get_transaction_count(self, member_id: int = None, 
                              start_date: str = None, end_date: str = None) -> int:
        """Get total count of transactions matching filters"""
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) FROM transactions t WHERE t.category_type = ?"
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
            
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_monthly_summary(self, year: int, month: int) -> dict:
        """Get monthly transaction summary"""
        conn = get_connection()
        cursor = conn.cursor()
        
        date_pattern = f"{year}-{month:02d}%"
        
        cursor.execute(
            """SELECT COUNT(*), COALESCE(SUM(total_price), 0), COALESCE(SUM(qty), 0)
               FROM transactions 
               WHERE category_type = ? AND date LIKE ?""",
            (self.category_context, date_pattern)
        )
        row = cursor.fetchone()
        
        conn.close()
        
        return {
            "transaction_count": row[0],
            "total_revenue": row[1],
            "total_items_sold": row[2]
        }
    
    def get_yearly_summary(self, year: int) -> dict:
        """Get yearly transaction summary"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT COUNT(*), COALESCE(SUM(total_price), 0), COALESCE(SUM(qty), 0)
               FROM transactions 
               WHERE category_type = ? AND strftime('%Y', date) = ?""",
            (self.category_context, str(year))
        )
        row = cursor.fetchone()
        
        conn.close()
        
        return {
            "transaction_count": row[0],
            "total_revenue": row[1],
            "total_items_sold": row[2]
        }
    
    def get_top_selling_items(self, limit: int = 10, days: int = 30) -> list:
        """Get top selling items in the past N days"""
        conn = get_connection()
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
        conn.close()
        return items
    
    def get_daily_sales(self, days: int = 30) -> list:
        """Get daily sales for chart"""
        conn = get_connection()
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
        conn.close()
        return sales
    
    def get_member_ranking(self, limit: int = 10) -> list:
        """Get top members by transaction value"""
        conn = get_connection()
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
        conn.close()
        return members
