"""
Members Module - CRUD Operations for Anggota Koperasi
REFACTORED: Added fuzzy search integration, autocomplete support
"""
from difflib import SequenceMatcher
from app.database.connection import get_connection
from app.utils.audit_log import log_audit


class MemberManager:
    """Manager class for member operations"""
    
    def __init__(self, current_user: str = "admin"):
        self.current_user = current_user
    
    def get_all_members(self, search_term: str = None) -> list:
        """Get all members with optional search"""
        conn = get_connection()
        cursor = conn.cursor()
        
        if search_term:
            cursor.execute(
                """SELECT * FROM members 
                   WHERE name LIKE ? OR nrp LIKE ? OR unit LIKE ?
                   ORDER BY name""",
                (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
            )
        else:
            cursor.execute("SELECT * FROM members ORDER BY name")
        
        members = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return members
    
    def autocomplete_search(self, partial_name: str, limit: int = 10) -> list:
        """Get autocomplete suggestions for member name"""
        if not partial_name or len(partial_name) < 2:
            return []
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Search by name prefix first
        cursor.execute(
            """SELECT * FROM members 
               WHERE name LIKE ? OR nrp LIKE ?
               ORDER BY name
               LIMIT ?""",
            (f"{partial_name}%", f"{partial_name}%", limit)
        )
        prefix_matches = [dict(row) for row in cursor.fetchall()]
        
        # If not enough, search with contains
        if len(prefix_matches) < limit:
            remaining = limit - len(prefix_matches)
            existing_ids = [m['id'] for m in prefix_matches]
            
            if existing_ids:
                placeholders = ','.join('?' * len(existing_ids))
                cursor.execute(
                    f"""SELECT * FROM members 
                       WHERE (name LIKE ? OR nrp LIKE ?)
                       AND id NOT IN ({placeholders})
                       ORDER BY name
                       LIMIT ?""",
                    (f"%{partial_name}%", f"%{partial_name}%", *existing_ids, remaining)
                )
            else:
                cursor.execute(
                    """SELECT * FROM members 
                       WHERE name LIKE ? OR nrp LIKE ?
                       ORDER BY name
                       LIMIT ?""",
                    (f"%{partial_name}%", f"%{partial_name}%", remaining)
                )
            
            prefix_matches.extend([dict(row) for row in cursor.fetchall()])
        
        conn.close()
        return prefix_matches
    
    def find_similar_members(self, search_name: str, threshold: float = 0.8) -> list:
        """Find members with similar names using fuzzy matching"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members ORDER BY name")
        members = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        similar = []
        for member in members:
            score = SequenceMatcher(None, search_name.lower(), member['name'].lower()).ratio()
            if score >= threshold:
                similar.append({'member': member, 'similarity': f"{score*100:.0f}%", 'score': score})
        
        # Sort by similarity score descending
        similar.sort(key=lambda x: x['score'], reverse=True)
        return similar[:5]  # Return top 5 matches
    
    def check_duplicate_before_create(self, name: str, nrp: str = None) -> dict:
        """Check for potential duplicates before creating a new member"""
        conn = get_connection()
        cursor = conn.cursor()
        
        result = {
            'has_duplicate': False,
            'exact_match': None,
            'similar_matches': []
        }
        
        # Check exact NRP match first
        if nrp:
            cursor.execute("SELECT * FROM members WHERE nrp = ?", (nrp,))
            exact_nrp = cursor.fetchone()
            if exact_nrp:
                result['has_duplicate'] = True
                result['exact_match'] = dict(exact_nrp)
                conn.close()
                return result
        
        # Check exact name match
        cursor.execute("SELECT * FROM members WHERE LOWER(name) = LOWER(?)", (name,))
        exact_name = cursor.fetchone()
        if exact_name:
            result['has_duplicate'] = True
            result['exact_match'] = dict(exact_name)
            conn.close()
            return result
        
        conn.close()
        
        # Check fuzzy matches
        similar = self.find_similar_members(name, threshold=0.8)
        if similar:
            result['has_duplicate'] = True
            result['similar_matches'] = similar
        
        return result
    
    def get_member_by_id(self, member_id: int) -> dict:
        """Get single member by ID"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def add_member(self, name: str, rank: str = "", unit: str = "", 
                   nrp: str = "", phone: str = "", address: str = "",
                   membership_status: str = "Anggota Koperasi") -> dict:
        """Add new member"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if NRP already exists
        if nrp:
            cursor.execute("SELECT id FROM members WHERE nrp = ?", (nrp,))
            if cursor.fetchone():
                conn.close()
                return {"success": False, "message": "NRP sudah terdaftar"}
        
        cursor.execute(
            """INSERT INTO members (name, rank, unit, nrp, phone, address, membership_status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, rank, unit, nrp, phone, address, membership_status)
        )
        member_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        log_audit(
            self.current_user, "MEMBER", "CREATE",
            "member", member_id, None,
            {"name": name, "nrp": nrp, "rank": rank, "unit": unit, "status": membership_status},
            f"Menambah anggota: {name} (NRP: {nrp}) - {membership_status}", "INFO"
        )
        
        return {"success": True, "message": "Anggota berhasil ditambah", "id": member_id}
    
    def update_member(self, member_id: int, name: str, rank: str, unit: str,
                      nrp: str, phone: str, address: str, 
                      membership_status: str = "Anggota Koperasi") -> dict:
        """Update member data"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if NRP already exists for other member
        if nrp:
            cursor.execute(
                "SELECT id FROM members WHERE nrp = ? AND id != ?", 
                (nrp, member_id)
            )
            if cursor.fetchone():
                conn.close()
                return {"success": False, "message": "NRP sudah digunakan anggota lain"}
        
        cursor.execute(
            """UPDATE members 
               SET name=?, rank=?, unit=?, nrp=?, phone=?, address=?, membership_status=?
               WHERE id=?""",
            (name, rank, unit, nrp, phone, address, membership_status, member_id)
        )
        conn.commit()
        conn.close()
        
        log_audit(
            self.current_user, "MEMBER", "UPDATE",
            "member", member_id, None, None,
            f"Edit anggota ID {member_id}: {name} ({membership_status})", "INFO"
        )
        
        return {"success": True, "message": "Data anggota berhasil diupdate"}
    
    def delete_member(self, member_id: int) -> dict:
        """Delete member"""
        member = self.get_member_by_id(member_id)
        if not member:
            return {"success": False, "message": "Anggota tidak ditemukan"}
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if member has active loans
        cursor.execute(
            "SELECT COUNT(*) FROM loans WHERE member_id = ? AND status = 'Aktif'",
            (member_id,)
        )
        if cursor.fetchone()[0] > 0:
            conn.close()
            return {"success": False, "message": "Anggota memiliki pinjaman aktif"}
        
        cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
        conn.commit()
        conn.close()
        
        log_audit(
            self.current_user, "MEMBER", "DELETE",
            "member", member_id, member, None,
            f"Hapus anggota: {member['name']} (ID: {member_id})", "WARNING"
        )
        
        return {"success": True, "message": "Anggota berhasil dihapus"}
    
    def get_member_transactions(self, member_id: int, category_type: str = None) -> list:
        """Get transaction history for a member"""
        conn = get_connection()
        cursor = conn.cursor()
        
        if category_type:
            cursor.execute(
                """SELECT t.*, w.name as item_name 
                   FROM transactions t
                   LEFT JOIN warehouse w ON t.item_id = w.id
                   WHERE t.member_id = ? AND t.category_type = ?
                   ORDER BY t.date DESC""",
                (member_id, category_type)
            )
        else:
            cursor.execute(
                """SELECT t.*, w.name as item_name 
                   FROM transactions t
                   LEFT JOIN warehouse w ON t.item_id = w.id
                   WHERE t.member_id = ?
                   ORDER BY t.date DESC""",
                (member_id,)
            )
        
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return transactions
    
    def get_statistics(self) -> dict:
        """Get member statistics"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM members")
        total_members = cursor.fetchone()[0]
        
        cursor.execute(
            "SELECT COUNT(DISTINCT member_id) FROM transactions WHERE DATE(date) = DATE('now')"
        )
        active_today = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_members": total_members,
            "active_today": active_today
        }
