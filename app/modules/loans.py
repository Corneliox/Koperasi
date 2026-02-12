"""
Loans Module - Advanced Loan Management for Members
REFACTORED: Added simulation engine, near-due tracking, phone display
"""
from datetime import datetime, timedelta
from app.database.connection import get_connection
from app.utils.audit_log import log_audit


class LoanManager:
    """Manager class for loan operations"""
    
    def __init__(self, current_user: str = "admin"):
        self.current_user = current_user
    
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
        if amount <= 0 or duration_months <= 0:
            return {"success": False, "message": "Invalid input values"}
        
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
        cursor = conn.cursor()
        
        # Check if member exists
        cursor.execute("SELECT name FROM members WHERE id = ?", (member_id,))
        member = cursor.fetchone()
        if not member:
            conn.close()
            return {"success": False, "message": "Anggota tidak ditemukan"}
        
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
        conn.close()
        
        log_audit(
            self.current_user, "LOAN", "CREATE",
            "loan", loan_id, None,
            {"member_id": member_id, "amount": amount, "total": total_amount},
            f"Pinjaman baru untuk {member['name']}: Rp {amount:,.0f} "
            f"(Total: Rp {total_amount:,.0f}, Cicilan: Rp {monthly_payment:,.0f}/bln)", "INFO"
        )
        
        return {
            "success": True, 
            "message": f"Pinjaman berhasil dibuat!\n"
                      f"Total: Rp {total_amount:,.0f}\n"
                      f"Cicilan: Rp {monthly_payment:,.0f}/bulan",
            "loan_id": loan_id,
            "total_amount": total_amount,
            "monthly_payment": monthly_payment
        }
    
    def update_loan(self, loan_id: int, amount: float, interest_rate: float, 
                    duration_months: int, notes: str = "") -> dict:
        """Update existing loan with new calculations"""
        sim = self.simulate_loan(amount, interest_rate, duration_months)
        if not sim['success']:
            return sim
            
        total_amount = sim['total_amount']
        monthly_payment = sim['monthly_payment']
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """UPDATE loans 
               SET principal=?, interest_rate=?, duration_months=?, 
                   total_amount=?, monthly_payment=?, notes=?
               WHERE id=?""",
            (amount, interest_rate, duration_months,
             total_amount, monthly_payment, notes, loan_id)
        )
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Pinjaman berhasil diupdate"}
    
    def record_payment(self, loan_id: int, amount: float, payment_method: str = "Tunai", 
                       notes: str = "") -> dict:
        """Record a payment for a loan with payment method"""
        loan = self.get_loan_by_id(loan_id)
        if not loan:
            return {"success": False, "message": "Pinjaman tidak ditemukan"}
        
        if loan['status'] == 'Lunas':
            return {"success": False, "message": "Pinjaman sudah lunas"}
        
        remaining = loan['total_amount'] - loan['paid_amount']
        if amount > remaining:
            return {"success": False, "message": f"Jumlah melebihi sisa pinjaman (Rp {remaining:,.0f})"}
        
        new_paid = loan['paid_amount'] + amount
        new_status = 'Lunas' if new_paid >= loan['total_amount'] else 'Aktif'
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Update loan
        cursor.execute(
            "UPDATE loans SET paid_amount = ?, status = ? WHERE id = ?",
            (new_paid, new_status, loan_id)
        )
        
        # Record payment with method
        cursor.execute(
            """INSERT INTO loan_payments (loan_id, amount, payment_method, notes)
               VALUES (?, ?, ?, ?)""",
            (loan_id, amount, payment_method, notes or f"Pembayaran angsuran via {payment_method}")
        )
        
        conn.commit()
        conn.close()
        
        log_audit(
            self.current_user, "LOAN", "UPDATE",
            "loan", loan_id, 
            {"paid": loan['paid_amount'], "status": loan['status']},
            {"paid": new_paid, "status": new_status},
            f"Pembayaran pinjaman ID {loan_id}: Rp {amount:,.0f} via {payment_method}", "INFO"
        )
        
        remaining_after = remaining - amount
        status_msg = "🎉 LUNAS!" if new_status == 'Lunas' else f"Sisa: Rp {remaining_after:,.0f}"
        
        return {
            "success": True,
            "message": f"Pembayaran Rp {amount:,.0f} berhasil dicatat!\n{status_msg}",
            "new_status": new_status,
            "remaining": remaining_after
        }

    def make_payment(self, loan_id: int, amount: float, description: str = "") -> dict:
        """Record a payment for a loan (backward compatibility)"""
        return self.record_payment(loan_id, amount, "Tunai", description)
    
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
    
    def mark_as_bad_debt(self, loan_id: int) -> dict:
        """Mark loan as bad debt (Macet)"""
        loan = self.get_loan_by_id(loan_id)
        if not loan:
            return {"success": False, "message": "Pinjaman tidak ditemukan"}
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE loans SET status = 'Macet' WHERE id = ?",
            (loan_id,)
        )
        conn.commit()
        conn.close()
        
        log_audit(
            self.current_user, "LOAN", "UPDATE",
            "loan", loan_id, 
            {"status": loan['status']}, {"status": "Macet"},
            f"Pinjaman ID {loan_id} ditandai macet", "WARNING"
        )
        
        return {"success": True, "message": "Pinjaman ditandai sebagai macet"}
    
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

