"""
Financial Balance Sheet (Neraca Keuangan) Module
Generates financial reports with export to Excel and PDF
"""
import os
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd
from fpdf import FPDF
from app.database.connection import get_connection


class FinancialReportManager:
    """Manager for generating financial reports"""
    
    def __init__(self, category_context: str = None):
        """
        Initialize financial report manager
        :param category_context: Filter by category, or None for all
        """
        self.category_context = category_context
    
    def get_balance_sheet(self, start_date: str = None, end_date: str = None) -> dict:
        """
        Generate balance sheet data
        
        :param start_date: Start date (YYYY-MM-DD)
        :param end_date: End date (YYYY-MM-DD)
        :return: Balance sheet dict
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Default to current month
            if not start_date:
                today = datetime.now()
                start_date = today.replace(day=1).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # Build category filter
            cat_filter = ""
            cat_params = []
            if self.category_context:
                cat_filter = "AND category_type = ?"
                cat_params = [self.category_context]
            
            # === ASSETS (AKTIVA) ===
            
            # 1. Inventory Value (Nilai Persediaan)
            cursor.execute(f"""
                SELECT COALESCE(SUM(stock * buy_price), 0) as value
                FROM warehouse
                WHERE 1=1 {cat_filter.replace('category_type', 'category_type')}
            """, cat_params)
            inventory_value = cursor.fetchone()['value']
            
            # 2. Total Items Count
            cursor.execute(f"""
                SELECT COUNT(*), COALESCE(SUM(stock), 0) as total_stock
                FROM warehouse
                WHERE 1=1 {cat_filter}
            """, cat_params)
            row = cursor.fetchone()
            total_items = row[0]
            total_stock = row['total_stock']
            
            # 3. Outstanding Loans (Piutang)
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount - paid_amount), 0) as outstanding
                FROM loans
                WHERE status = 'Aktif'
            """)
            outstanding_loans = cursor.fetchone()['outstanding']
            
            # 4. Bad Debts (Piutang Macet)
            cursor.execute("""
                SELECT COALESCE(SUM(total_amount - paid_amount), 0) as bad_debt
                FROM loans
                WHERE status = 'Macet'
            """)
            bad_debts = cursor.fetchone()['bad_debt']
            
            # === INCOME (PENDAPATAN) ===
            
            # 5. Sales Revenue (Pendapatan Penjualan)
            if self.category_context:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as count,
                        COALESCE(SUM(total_price), 0) as revenue,
                        COALESCE(SUM(qty), 0) as items_sold
                    FROM transactions
                    WHERE DATE(date) BETWEEN ? AND ? AND category_type = ?
                """, [start_date, end_date, self.category_context])
            else:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as count,
                        COALESCE(SUM(total_price), 0) as revenue,
                        COALESCE(SUM(qty), 0) as items_sold
                    FROM transactions
                    WHERE DATE(date) BETWEEN ? AND ?
                """, [start_date, end_date])
            sales_row = cursor.fetchone()
            sales_count = sales_row['count']
            sales_revenue = sales_row['revenue']
            items_sold = sales_row['items_sold']
            
            # 6. Calculate COGS (Harga Pokok Penjualan)
            if self.category_context:
                cursor.execute("""
                    SELECT COALESCE(SUM(t.qty * w.buy_price), 0) as cogs
                    FROM transactions t
                    JOIN warehouse w ON t.item_id = w.id
                    WHERE DATE(t.date) BETWEEN ? AND ? AND t.category_type = ?
                """, [start_date, end_date, self.category_context])
            else:
                cursor.execute("""
                    SELECT COALESCE(SUM(t.qty * w.buy_price), 0) as cogs
                    FROM transactions t
                    JOIN warehouse w ON t.item_id = w.id
                    WHERE DATE(t.date) BETWEEN ? AND ?
                """, [start_date, end_date])
            cogs = cursor.fetchone()['cogs']
            
            # 7. Gross Profit (Laba Kotor)
            gross_profit = sales_revenue - cogs
            
            # 8. Loan Interest Received (Pendapatan Bunga Pinjaman)
            cursor.execute("""
                SELECT COALESCE(SUM(
                    CASE WHEN l.total_amount > 0 AND l.total_amount > l.principal 
                         THEN lp.amount * ((l.total_amount - l.principal) * 1.0 / l.total_amount)
                         ELSE 0 
                    END
                ), 0) as interest,
                COALESCE(SUM(lp.amount), 0) as total_payments
                FROM loan_payments lp
                JOIN loans l ON lp.loan_id = l.id
                WHERE DATE(lp.payment_date) BETWEEN ? AND ?
            """, [start_date, end_date])
            row_lp = cursor.fetchone()
            loan_interest_received = row_lp['interest'] if row_lp else 0
            loan_payments_total = row_lp['total_payments'] if row_lp else 0
            
            # === MUTATIONS SUMMARY ===
            
            # 9. Stock Mutations
            if self.category_context:
                cursor.execute("""
                    SELECT wm.type, COALESCE(SUM(wm.qty), 0) as total
                    FROM warehouse_mutation wm
                    JOIN warehouse w ON wm.item_id = w.id
                    WHERE DATE(wm.date) BETWEEN ? AND ? AND w.category_type = ?
                    GROUP BY wm.type
                """, [start_date, end_date, self.category_context])
            else:
                cursor.execute("""
                    SELECT type, COALESCE(SUM(qty), 0) as total
                    FROM warehouse_mutation
                    WHERE DATE(date) BETWEEN ? AND ?
                    GROUP BY type
                """, [start_date, end_date])
            
            mutations = {row['type']: row['total'] for row in cursor.fetchall()}
        finally:
            conn.close()
        
        # Calculate totals
        total_assets = inventory_value + outstanding_loans
        total_income = sales_revenue + loan_interest_received
        net_income = gross_profit + loan_interest_received
        
        return {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'category': self.category_context or 'Semua Kategori'
            },
            'assets': {
                'inventory_value': inventory_value,
                'total_items': total_items,
                'total_stock': total_stock,
                'outstanding_loans': outstanding_loans,
                'bad_debts': bad_debts,
                'total_assets': total_assets
            },
            'income': {
                'sales_revenue': sales_revenue,
                'sales_count': sales_count,
                'items_sold': items_sold,
                'cogs': cogs,
                'gross_profit': gross_profit,
                'loan_interest': loan_interest_received,
                'total_income': total_income,
                'net_income': net_income
            },
            'mutations': {
                'stock_in': mutations.get('IN', 0),
                'stock_out': mutations.get('OUT', 0),
                'returns': mutations.get('RETURN', 0),
                'corrections': mutations.get('CORRECTION', 0)
            },
            'generated_at': datetime.now().isoformat()
        }
    
    def get_profit_loss_statement(self, start_date: str = None, end_date: str = None) -> dict:
        """Generate profit/loss statement"""
        balance = self.get_balance_sheet(start_date, end_date)
        
        return {
            'period': balance['period'],
            'revenue': {
                'sales': balance['income']['sales_revenue'],
                'loan_interest': balance['income']['loan_interest'],
                'total_revenue': balance['income']['total_income']
            },
            'expenses': {
                'cogs': balance['income']['cogs'],
                'total_expenses': balance['income']['cogs']  # Add more expense categories as needed
            },
            'profit': {
                'gross_profit': balance['income']['gross_profit'],
                'net_profit': balance['income']['net_income']
            }
        }


def export_balance_sheet_excel(balance_data: dict, output_dir: str = None) -> str:
    """
    Export balance sheet to Excel
    
    :param balance_data: Balance sheet dict from get_balance_sheet()
    :param output_dir: Output directory
    :return: Path to Excel file
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "Koperasi_Export")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare data for Excel
    assets_data = [
        ['AKTIVA (ASSETS)', ''],
        ['Nilai Persediaan Barang', balance_data['assets']['inventory_value']],
        ['Jumlah Jenis Barang', balance_data['assets']['total_items']],
        ['Total Unit Stok', balance_data['assets']['total_stock']],
        ['Piutang Pinjaman Aktif', balance_data['assets']['outstanding_loans']],
        ['Piutang Macet', balance_data['assets']['bad_debts']],
        ['TOTAL AKTIVA', balance_data['assets']['total_assets']],
    ]
    
    income_data = [
        ['', ''],
        ['PENDAPATAN (INCOME)', ''],
        ['Pendapatan Penjualan', balance_data['income']['sales_revenue']],
        ['Jumlah Transaksi', balance_data['income']['sales_count']],
        ['Unit Terjual', balance_data['income']['items_sold']],
        ['Harga Pokok Penjualan (HPP)', balance_data['income']['cogs']],
        ['Laba Kotor', balance_data['income']['gross_profit']],
        ['Pendapatan Bunga Pinjaman', balance_data['income']['loan_interest']],
        ['LABA BERSIH', balance_data['income']['net_income']],
    ]
    
    mutation_data = [
        ['', ''],
        ['MUTASI STOK', ''],
        ['Barang Masuk (IN)', balance_data['mutations']['stock_in']],
        ['Barang Keluar (OUT)', balance_data['mutations']['stock_out']],
        ['Retur', balance_data['mutations']['returns']],
        ['Koreksi', balance_data['mutations']['corrections']],
    ]
    
    all_data = assets_data + income_data + mutation_data
    df = pd.DataFrame(all_data, columns=['Keterangan', 'Nilai'])
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    category = balance_data['period']['category'].replace(' ', '_')
    filename = f"Neraca_Keuangan_{category}_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, filename)
    
    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Neraca', index=False, startrow=4)
        
        workbook = writer.book
        worksheet = writer.sheets['Neraca']
        
        # Title
        title_format = workbook.add_format({
            'bold': True, 'font_size': 16, 'align': 'center'
        })
        worksheet.merge_range('A1:B1', 'NERACA KEUANGAN', title_format)
        worksheet.merge_range('A2:B2', 'KOPERASI SIMPAN PINJAM', title_format)
        
        # Period info
        period_format = workbook.add_format({'font_size': 11, 'align': 'center'})
        period_text = f"Periode: {balance_data['period']['start_date']} s/d {balance_data['period']['end_date']}"
        worksheet.merge_range('A3:B3', period_text, period_format)
        worksheet.merge_range('A4:B4', f"Kategori: {balance_data['period']['category']}", period_format)
        
        # Header format
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#2B579A', 'font_color': 'white',
            'border': 1, 'align': 'center'
        })
        
        # Section header format
        section_format = workbook.add_format({
            'bold': True, 'bg_color': '#4472C4', 'font_color': 'white'
        })
        
        # Number format
        number_format = workbook.add_format({
            'num_format': '#,##0', 'border': 1
        })
        
        # Total format
        total_format = workbook.add_format({
            'bold': True, 'num_format': '#,##0', 'border': 1,
            'bg_color': '#E2EFDA'
        })
        
        # Apply formats
        worksheet.write('A5', 'Keterangan', header_format)
        worksheet.write('B5', 'Nilai (Rp)', header_format)
        
        worksheet.set_column('A:A', 35)
        worksheet.set_column('B:B', 20)
    
    return filepath


def export_balance_sheet_pdf(balance_data: dict, output_dir: str = None) -> str:
    """
    Export balance sheet to PDF
    
    :param balance_data: Balance sheet dict
    :param output_dir: Output directory
    :return: Path to PDF file
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "Koperasi_Export")
    
    os.makedirs(output_dir, exist_ok=True)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 10, 'NERACA KEUANGAN', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, 'KOPERASI SIMPAN PINJAM', align='C', new_x="LMARGIN", new_y="NEXT")
    
    # Period
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 6, f"Periode: {balance_data['period']['start_date']} s/d {balance_data['period']['end_date']}", 
             align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Kategori: {balance_data['period']['category']}", 
             align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    # Helper function for section
    def add_section(title, items):
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_fill_color(68, 114, 196)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 8, title, fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        
        pdf.set_font('Helvetica', '', 10)
        for label, value in items:
            is_total = 'TOTAL' in label or 'LABA' in label
            if is_total:
                pdf.set_font('Helvetica', 'B', 10)
                pdf.set_fill_color(226, 239, 218)
            else:
                pdf.set_font('Helvetica', '', 10)
                pdf.set_fill_color(255, 255, 255)
            
            pdf.cell(120, 7, label, border=1, fill=is_total)
            
            if isinstance(value, (int, float)):
                pdf.cell(60, 7, f"Rp {value:,.0f}", border=1, align='R', fill=is_total)
            else:
                pdf.cell(60, 7, str(value), border=1, align='R', fill=is_total)
            pdf.ln()
        
        pdf.ln(5)
    
    # Assets section
    add_section('AKTIVA (ASSETS)', [
        ('Nilai Persediaan Barang', balance_data['assets']['inventory_value']),
        ('Jumlah Jenis Barang', balance_data['assets']['total_items']),
        ('Total Unit Stok', balance_data['assets']['total_stock']),
        ('Piutang Pinjaman Aktif', balance_data['assets']['outstanding_loans']),
        ('Piutang Macet', balance_data['assets']['bad_debts']),
        ('TOTAL AKTIVA', balance_data['assets']['total_assets']),
    ])
    
    # Income section
    add_section('PENDAPATAN (INCOME)', [
        ('Pendapatan Penjualan', balance_data['income']['sales_revenue']),
        ('Jumlah Transaksi', balance_data['income']['sales_count']),
        ('Unit Terjual', balance_data['income']['items_sold']),
        ('Harga Pokok Penjualan (HPP)', balance_data['income']['cogs']),
        ('Laba Kotor', balance_data['income']['gross_profit']),
        ('Pendapatan Bunga Pinjaman', balance_data['income']['loan_interest']),
        ('LABA BERSIH', balance_data['income']['net_income']),
    ])
    
    # Mutations section
    add_section('MUTASI STOK', [
        ('Barang Masuk (IN)', balance_data['mutations']['stock_in']),
        ('Barang Keluar (OUT)', balance_data['mutations']['stock_out']),
        ('Retur', balance_data['mutations']['returns']),
        ('Koreksi', balance_data['mutations']['corrections']),
    ])
    
    # Footer
    pdf.set_font('Helvetica', 'I', 9)
    pdf.cell(0, 10, f"Dicetak: {datetime.now().strftime('%d/%m/%Y %H:%M')}", align='R')
    
    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    category = balance_data['period']['category'].replace(' ', '_')
    filename = f"Neraca_Keuangan_{category}_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)
    
    pdf.output(filepath)
    return filepath
