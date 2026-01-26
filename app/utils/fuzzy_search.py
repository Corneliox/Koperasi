"""
Fuzzy Search Utilities for Member Matching
Uses difflib for string similarity matching
"""
from difflib import SequenceMatcher
from typing import List, Tuple, Optional
from app.database.connection import get_connection


def similarity_ratio(str1: str, str2: str) -> float:
    """
    Calculate similarity ratio between two strings
    :return: Float between 0.0 and 1.0
    """
    if not str1 or not str2:
        return 0.0
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def find_similar_members(search_name: str, threshold: float = 0.8) -> List[Tuple[dict, float]]:
    """
    Find members with similar names using fuzzy matching
    
    :param search_name: Name to search for
    :param threshold: Minimum similarity ratio (0.0 to 1.0), default 0.8 (80%)
    :return: List of (member_dict, similarity_score) tuples, sorted by score desc
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members ORDER BY name")
    members = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    similar = []
    for member in members:
        score = similarity_ratio(search_name, member['name'])
        if score >= threshold:
            similar.append((member, score))
    
    # Sort by similarity score descending
    similar.sort(key=lambda x: x[1], reverse=True)
    return similar


def find_best_match(search_name: str, threshold: float = 0.8) -> Optional[Tuple[dict, float]]:
    """
    Find the best matching member
    
    :return: (member_dict, score) or None if no match above threshold
    """
    matches = find_similar_members(search_name, threshold)
    return matches[0] if matches else None


def autocomplete_members(partial_name: str, limit: int = 10) -> List[dict]:
    """
    Get autocomplete suggestions for member name
    
    :param partial_name: Partial name to search
    :param limit: Maximum results to return
    :return: List of member dicts
    """
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


def check_duplicate_before_create(name: str, nrp: str = None) -> dict:
    """
    Check for potential duplicates before creating a new member
    
    :return: Dict with 'has_duplicate', 'exact_match', 'similar_matches'
    """
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
    similar = find_similar_members(name, threshold=0.8)
    if similar:
        result['has_duplicate'] = True
        result['similar_matches'] = [
            {'member': m, 'similarity': f"{s*100:.0f}%"} 
            for m, s in similar[:5]  # Top 5 matches
        ]
    
    return result
