"""
Loans Module - Advanced Loan Management for Members
REFACTORED: Added simulation engine, near-due tracking, phone display
"""
from datetime import datetime, timedelta
from app.database.connection import get_connection
from app.utils.audit_log import log_audit
from app.utils.decorators import handle_db_errors


class LoanManager:
    """Manager class for loan operations"""
    
    def __init__(self, current_user: str = "admin"):
        self.current_user = current_user
    
    @handle_db_errors
    def get_all_loans(self, status_filter: str = None) -> list:
        """Get all loans with optional status filter"""
        conn = get_connection()
        cursor = conn.cursor()
        
        if status_filter:
            cursor.execute(
                """SELECT l.*, m.name as member_name, m.nrp as member_nrp
                   FROM loans l
                   JOIN members m ON l.member_id = m.id
                   WHERE l.status = ?
                   ORDER BY l.created_at DESC""",
                (status_filter,)
            )
        else:
            cursor.execute(
                """SELECT l.*, m.name as member_name, m.nrp as member_nrp
                   FROM loans l
                   JOIN members m ON l.member_id = m.id
                   ORDER BY l.created_at DESC"""
            )
        
        loans = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return loans
    
    @handle_db_errors
    def get_all_loans_with_phone(self, status_filter: str = None) -> list:
        """Get all loans with member phone numbers"""
        conn = get_connection()
        cursor = conn.cursor()
        
        if status_filter:
            cursor.execute(
                """SELECT l.*, m.name as member_name, m.nrp as member_nrp, m.phone as member_phone
                   FROM loans l
                   JOIN members m ON l.member_id = m.id
                   WHERE l.status = ?
                   ORDER BY l.created_at DESC""",
                (status_filter,)
            )
        else:
            cursor.execute(
                """SELECT l.*, m.name as member_name, m.nrp as member_nrp, m.phone as member_phone
                   FROM loans l
                   JOIN members m ON l.member_id = m.id
                   ORDER BY l.created_at DESC"""
            )
        
        loans = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return loans
    
    @handle_db_errors
    def get_near_due_loans(self, days: int = 14) -> list:
        """Get loans near due date within N days"""
        conn = get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().date()
        target_date = (today + timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute(
            """SELECT l.*, m.name as member_name, m.nrp as member_nrp, m.phone as member_phone
               FROM loans l
               JOIN members m ON l.member_id = m.id
               WHERE l.status = 'Aktif' 
               AND l.due_date IS NOT NULL
               AND DATE(l.due_date) <= ?
               AND DATE(l.due_date) >= DATE('now')
               ORDER BY l.due_date ASC""",
            (target_date,)
        )
        
        loans = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return loans
    
    def simulate_loan(self, amount: float, interest_rate: float, duration_months: int) -> dict:
        """
        Simulate loan calculation before creation
        Returns breakdown of payments
        """
        try:
            # Ensure numeric values
            amount = float(amount) if amount is not None else 0
            interest_rate = float(interest_rate) if interest_rate is not None else 0
            duration_months = int(duration_months) if duration_months is not None else 0
        except (ValueError, TypeError):
            return {"success": False, "message": "Input harus berupa angka"}

        if amount <= 0 or duration_months <= 0:
            return {"success": False, "message": "Jumlah dan durasi harus lebih dari 0"}
        
        interest_amount = amount * (interest_rate / 100)
        total_amount = amount + interest_amount
        monthly_payment = total_amount / duration_months
        
        # Generate monthly breakdown
        breakdown = []
        remaining = total_amount
        
        for month in range(1, duration_months + 1):
            remaining -= monthly_payment
            if remaining < 0:
                remaining = 0
            
            breakdown.append({
                'month': month,
                'payment': monthly_payment,
                'remaining': remaining,
                'progress': (month / duration_months) * 100
            })
        
        return {
            "success": True,
            "principal": amount,
            "interest_rate": interest_rate,
            "interest_amount": interest_amount,
            "total_amount": total_amount,
            "duration_months": duration_months,
            "monthly_payment": monthly_payment,
            "breakdown": breakdown
        }
    
    @handle_db_errors
    def get_loan_by_id(self, loan_id: int) -> dict:
        """Get single loan by ID"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT l.*, m.name as member_name, m.nrp as member_nrp
               FROM loans l
               JOIN members m ON l.member_id = m.id
               WHERE l.id = ?""",
            (loan_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    @handle_db_errors
    def get_member_loans(self, member_id: int) -> list:
        """Get all loans for a specific member"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM loans 
               WHERE member_id = ? 
               ORDER BY created_at DESC""",
            (member_id,)
        )
        loans = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return loans
    
    @handle_db_errors
    def create_loan(self, member_id: int, amount: float, interest_rate: float = 0,
                    duration_months: int = 12, notes: str = "") -> dict:
        """Create new loan for a member with full calculation"""
        # Calculate using simulation logic
        sim = self.simulate_loan(amount, interest_rate, duration_months)
        if not sim['success']:
            return sim
        
        total_amount = sim['total_amount']
        monthly_payment = sim['monthly_payment']
        
        # Calculate due date
        due_date = (datetime.now() + timedelta(days=duration_months * 30)).strftime('%Y-%m-%d')
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if member exists
            cursor.execute("SELECT name FROM members WHERE id = ?", (member_id,))
            member = cursor.fetchone()
            if not member:
                return {"success": False, "message": "Anggota tidak ditemukan"}
            
            cursor.execute("PRAGMA table_info(loans)")
            cols = [c[1] for c in cursor.fetchall()]
            
            if 'amount' in cols:
                cursor.execute(
                    """INSERT INTO loans 
                       (member_id, amount, principal, interest_rate, duration_months, 
                        total_amount, monthly_payment, due_date, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (member_id, amount, amount, interest_rate, duration_months,
                     total_amount, monthly_payment, due_date, notes)
                )
            else:
                cursor.execute(
                    """INSERT INTO loans 
                       (member_id, principal, interest_rate, duration_months, 
                        total_amount, monthly_payment, due_date, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (member_id, amount, interest_rate, duration_months,
                     total_amount, monthly_payment, due_date, notes)
                )
            loan_id = cursor.lastrowid
            conn.commit()
            
            log_audit(
                self.current_user, "LOAN", "CREATE",
                "loan", loan_id, None,
                {"member_id": member_id, "principal": amount, "total": total_amount},
                f"Pinjaman baru untuk {member['name']}: Rp {amount:,.0f} "
                f"(Total: Rp {total_amount:,.0f}, Cicilan: Rp {monthly_payment:,.0f}/bln)", "INFO"
            )
            
            return {
                "success": True, 
                "message": f"Pinjaman berhasil dibuat!\n"
                          f"Total: Rp {total_amount:,.0f}\n"
                          f"Cicilan: Rp {monthly_payment:,.0f}/bulan",
                "loan_id": loan_id,
                "id": loan_id,
                "total_amount": total_amount,
                "monthly_payment": monthly_payment
            }
        finally:
            conn.close()
    
    @handle_db_errors
    def update_loan(self, loan_id: int, amount: float, interest_rate: float, 
                    duration_months: int, notes: str = "") -> dict:
        """Update existing loan with new calculations and status sync"""
        try:
            amount = float(amount)
            interest_rate = float(interest_rate)
            duration_months = int(duration_months)
        except (ValueError, TypeError):
            return {"success": False, "message": "Nominal, bunga, dan durasi harus berupa angka valid"}

        if amount <= 0 or duration_months <= 0 or interest_rate < 0:
            return {"success": False, "message": "Nominal dan durasi pinjaman harus lebih dari 0"}

        sim = self.simulate_loan(amount, interest_rate, duration_months)
        if not sim['success']:
            return sim
            
        total_amount = sim['total_amount']
        monthly_payment = sim['monthly_payment']
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Fetch existing loan
            cursor.execute("SELECT paid_amount, created_at FROM loans WHERE id = ?", (loan_id,))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "message": "Pinjaman tidak ditemukan"}
                
            paid_amount = row['paid_amount'] or 0
            created_at = row['created_at'] or datetime.now().strftime('%Y-%m-%d')
            
            # Recalculate due date from creation date or today
            try:
                base_dt = datetime.strptime(str(created_at)[:10], '%Y-%m-%d')
            except Exception:
                base_dt = datetime.now()
            new_due_date = (base_dt + timedelta(days=duration_months * 30)).strftime('%Y-%m-%d')
            
            # Recalculate status
            new_status = 'Lunas' if paid_amount >= total_amount else 'Aktif'
            
            cursor.execute("PRAGMA table_info(loans)")
            cols = [c[1] for c in cursor.fetchall()]
            
            if 'amount' in cols:
                cursor.execute(
                    """UPDATE loans 
                       SET amount=?, principal=?, interest_rate=?, duration_months=?, 
                           total_amount=?, monthly_payment=?, due_date=?, status=?, notes=?
                       WHERE id=?""",
                    (amount, amount, interest_rate, duration_months,
                     total_amount, monthly_payment, new_due_date, new_status, notes, loan_id)
                )
            else:
                cursor.execute(
                    """UPDATE loans 
                       SET principal=?, interest_rate=?, duration_months=?, 
                           total_amount=?, monthly_payment=?, due_date=?, status=?, notes=?
                       WHERE id=?""",
                    (amount, interest_rate, duration_months,
                     total_amount, monthly_payment, new_due_date, new_status, notes, loan_id)
                )
            conn.commit()
            
            log_audit(
                self.current_user, "LOAN", "UPDATE",
                "loan", loan_id, None,
                {"principal": amount, "total": total_amount, "status": new_status},
                f"Update data pinjaman ID {loan_id}: Total Rp {total_amount:,.0f}, Status: {new_status}", "INFO"
            )
            
            return {"success": True, "message": "Pinjaman berhasil diupdate"}
        finally:
            conn.close()
    
    @handle_db_errors
    def record_payment(self, loan_id: int, amount: float, payment_method: str = "Tunai", 
                        notes: str = "") -> dict:
        """Record a payment for a loan with atomic update and validation"""
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return {"success": False, "message": "Jumlah pembayaran harus berupa angka"}

        if amount <= 0:
            return {"success": False, "message": "Jumlah pembayaran harus lebih dari 0"}

        loan = self.get_loan_by_id(loan_id)
        if not loan:
            return {"success": False, "message": "Pinjaman tidak ditemukan"}
        
        if loan['status'] == 'Lunas':
            return {"success": False, "message": "Pinjaman sudah lunas"}
        
        remaining = loan['total_amount'] - loan['paid_amount']
        if amount > remaining:
            return {"success": False, "message": f"Jumlah melebihi sisa pinjaman (Rp {remaining:,.0f})"}
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Atomic update
            cursor.execute(
                """UPDATE loans 
                   SET paid_amount = paid_amount + ?,
                       status = CASE WHEN paid_amount + ? >= total_amount THEN 'Lunas' ELSE 'Aktif' END
                   WHERE id = ? AND (total_amount - paid_amount) >= ?""",
                (amount, amount, loan_id, amount)
            )
            if cursor.rowcount == 0:
                return {"success": False, "message": "Gagal: Pembayaran melebihi sisa pinjaman atau status pinjaman berubah!"}
            
            # Record payment in payments table
            cursor.execute(
                """INSERT INTO loan_payments (loan_id, amount, payment_method, notes)
                   VALUES (?, ?, ?, ?)""",
                (loan_id, amount, payment_method, notes or f"Pembayaran angsuran via {payment_method}")
            )
            
            conn.commit()
            
            # Fetch updated values for response
            cursor.execute("SELECT total_amount, paid_amount, status FROM loans WHERE id = ?", (loan_id,))
            updated_row = cursor.fetchone()
            new_paid = updated_row['paid_amount']
            new_status = updated_row['status']
            remaining_after = updated_row['total_amount'] - new_paid
            
            log_audit(
                self.current_user, "LOAN", "UPDATE",
                "loan", loan_id, 
                {"paid": loan['paid_amount'], "status": loan['status']},
                {"paid": new_paid, "status": new_status},
                f"Pembayaran pinjaman ID {loan_id}: Rp {amount:,.0f} via {payment_method}", "INFO"
            )
            
            status_msg = "🎉 LUNAS!" if new_status == 'Lunas' else f"Sisa: Rp {remaining_after:,.0f}"
            
            return {
                "success": True,
                "message": f"Pembayaran Rp {amount:,.0f} berhasil dicatat!\n{status_msg}",
                "new_status": new_status,
                "remaining": remaining_after
            }
        finally:
            conn.close()

    def make_payment(self, loan_id: int, amount: float, description: str = "") -> dict:
        """Record a payment for a loan (backward compatibility)"""
        return self.record_payment(loan_id, amount, "Tunai", description)
    
    @handle_db_errors
    def get_loan_payments(self, loan_id: int) -> list:
        """Get payment history for a loan"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM loan_payments 
               WHERE loan_id = ? 
               ORDER BY payment_date DESC""",
            (loan_id,)
        )
        payments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return payments
    
    @handle_db_errors
    def mark_as_bad_debt(self, loan_id: int) -> dict:
        """Mark loan as bad debt (Macet)"""
        loan = self.get_loan_by_id(loan_id)
        if not loan:
            return {"success": False, "message": "Pinjaman tidak ditemukan"}
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE loans SET status = 'Macet' WHERE id = ?",
                (loan_id,)
            )
            conn.commit()
            
            log_audit(
                self.current_user, "LOAN", "UPDATE",
                "loan", loan_id, 
                {"status": loan['status']}, {"status": "Macet"},
                f"Pinjaman ID {loan_id} ditandai macet", "WARNING"
            )
            
            return {"success": True, "message": "Pinjaman ditandai sebagai macet"}
        finally:
            conn.close()
    
    @handle_db_errors
    def get_statistics(self) -> dict:
        """Get loan statistics"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Total active loans
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(total_amount - paid_amount), 0) FROM loans WHERE status = 'Aktif'")
        row = cursor.fetchone()
        active_count = row[0]
        active_remaining = row[1]
        
        # Total bad debts
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(total_amount - paid_amount), 0) FROM loans WHERE status = 'Macet'")
        row = cursor.fetchone()
        bad_debt_count = row[0]
        bad_debt_amount = row[1]
        
        # Paid this month
        cursor.execute(
            """SELECT COALESCE(SUM(amount), 0) FROM loan_payments 
               WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')"""
        )
        paid_this_month = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "active_count": active_count,
            "active_remaining": active_remaining,
            "bad_debt_count": bad_debt_count,
            "bad_debt_amount": bad_debt_amount,
            "paid_this_month": paid_this_month
        }

