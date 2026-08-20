"""
Export Utilities - Excel and PDF Export Functions
"""
import os
from datetime import datetime
import pandas as pd
from fpdf import FPDF


def get_excel_col_letter(col_idx: int) -> str:
    """Convert 0-indexed column integer to Excel column letter (0->A, 25->Z, 26->AA)"""
    result = ""
    col_idx += 1
    while col_idx > 0:
        col_idx, remainder = divmod(col_idx - 1, 26)
        result = chr(65 + remainder) + result
    return result


def export_to_excel(data: list, columns: dict, filename: str, 
                    sheet_name: str = "Data", output_dir: str = None) -> str:
    """
    Export data to Excel file safely
    :param data: List of dictionaries
    :param columns: Dict mapping data keys to column headers
    :param filename: Output filename (without extension)
    :param sheet_name: Excel sheet name
    :param output_dir: Output directory (default: user's Documents)
    :return: Full path to created file
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "Koperasi_Export")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Create DataFrame with selected columns
    df_data = []
    if data:
        for row in data:
            df_row = {}
            for key, header in columns.items():
                df_row[header] = row.get(key, "")
            df_data.append(df_row)
        df = pd.DataFrame(df_data)
    else:
        # Create empty DataFrame with proper column headers
        df = pd.DataFrame(columns=list(columns.values()))
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{filename}_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, full_filename)
    
    # Export with formatting
    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        last_row = max(1, len(df) + 1)
        
        # Header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#2B579A',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # Total format
        total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#E2EFDA',
            'border': 1,
            'num_format': '#,##0',
            'align': 'right'
        })
        
        # Apply header format
        for col_num, header in enumerate(df.columns):
            worksheet.write(0, col_num, header, header_format)
            worksheet.set_column(col_num, col_num, 20)
            
            # Add TOTAL row at the end if it's a numeric column and we have data
            if len(df) > 0:
                col_name = df.columns[col_num]
                col_letter = get_excel_col_letter(col_num)
                if col_num == 0:
                    worksheet.write(last_row, col_num, "TOTAL", total_format)
                elif col_name in ['Jumlah', 'Total', 'Profit', 'Laba', 'Harga aset']:
                    sum_formula = f"=SUM({col_letter}2:{col_letter}{last_row})"
                    worksheet.write_formula(last_row, col_num, sum_formula, total_format)
                else:
                    worksheet.write(last_row, col_num, "", total_format)
        
        # Freeze header row
        worksheet.freeze_panes(1, 0)
    
    return filepath


def export_transactions_excel(transactions: list, filename: str = "Laporan_Transaksi",
                              output_dir: str = None) -> str:
    """Export transactions to Excel with ID, Nama, Tanggal order and Profit"""
    processed = []
    for t in (transactions or []):
        row = dict(t)
        try:
            unit_price = float(t.get('unit_price') or 0)
            qty = float(t.get('qty') or 0)
        except (ValueError, TypeError):
            unit_price = 0.0
            qty = 0.0
            
        estimated_buy = unit_price * 0.85
        row['profit'] = (unit_price - estimated_buy) * qty
        processed.append(row)

    columns = {
        'id': 'ID',
        'member_name': 'Nama',
        'date': 'Tanggal',
        'item_name': 'Nama Barang',
        'qty': 'Jumlah',
        'unit_price': 'Harga Satuan',
        'total_price': 'Total',
        'profit': 'Profit',
        'payment_method': 'Metode Bayar'
    }
    return export_to_excel(processed, columns, filename, "Transaksi", output_dir)


def export_inventory_excel(items: list, filename: str = "Laporan_Inventaris",
                           output_dir: str = None) -> str:
    """Export inventory to Excel with full headers and calculations"""
    processed_items = []
    for item in (items or []):
        processed = dict(item)
        try:
            sell_price = float(item.get('sell_price') or 0)
            buy_price = float(item.get('buy_price') or 0)
            stock = float(item.get('stock') or 0)
        except (ValueError, TypeError):
            sell_price = 0.0
            buy_price = 0.0
            stock = 0.0
            
        processed['laba'] = sell_price - buy_price
        processed['status_aktif'] = "Ya" if item.get('is_active', 1) else "Tidak"
        processed['harga_aset'] = sell_price * stock
        processed_items.append(processed)

    columns = {
        'id': 'ID',
        'item_code': 'Kodebrg',
        'name': 'Nama Barang',
        'stock': 'Stok',
        'buy_price': 'Harga Pokok',
        'sell_price': 'Harga Jual',
        'laba': 'Laba',
        'status': 'Status Barang',
        'status_aktif': 'Status Aktif',
        'harga_aset': 'Harga aset'
    }
    return export_to_excel(processed_items, columns, filename, "Inventaris", output_dir)


def export_mutations_excel(mutations: list, filename: str = "Laporan_Mutasi",
                           output_dir: str = None) -> str:
    """Export mutations to Excel"""
    columns = {
        'date': 'Tanggal',
        'item_name': 'Nama Barang',
        'type': 'Tipe',
        'qty': 'Jumlah',
        'description': 'Keterangan'
    }
    return export_to_excel(mutations, columns, filename, "Mutasi", output_dir)


class PDFReport(FPDF):
    """Custom PDF class for reports"""
    
    def __init__(self, title: str = "Laporan Koperasi"):
        super().__init__()
        self.title = title
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font('Helvetica', 'B', 16)
        self.cell(0, 10, self.title, align='C', new_x="LMARGIN", new_y="NEXT")
        self.set_font('Helvetica', '', 10)
        self.cell(0, 5, f"Dicetak: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                  align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Halaman {self.page_no()}/{{nb}}', align='C')
    
    def add_table(self, headers: list, data: list, col_widths: list = None):
        """Add a table to the PDF safely"""
        if not headers:
            return
            
        if col_widths is None:
            col_widths = [self.epw / len(headers)] * len(headers)
        
        # Header
        self.set_font('Helvetica', 'B', 10)
        self.set_fill_color(43, 87, 154)
        self.set_text_color(255, 255, 255)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, str(header), border=1, align='C', fill=True)
        self.ln()
        
        # Data rows
        self.set_font('Helvetica', '', 9)
        self.set_text_color(0, 0, 0)
        fill = False
        
        for row in data:
            if fill:
                self.set_fill_color(240, 240, 240)
            else:
                self.set_fill_color(255, 255, 255)
            
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 7, str(cell)[:30], border=1, align='L', fill=True)
            self.ln()
            fill = not fill


def export_transactions_pdf(transactions: list, title: str = "Laporan Transaksi",
                            filename: str = "Laporan_Transaksi",
                            output_dir: str = None) -> str:
    """Export transactions to PDF with safe numeric conversions"""
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "Koperasi_Export")
    
    os.makedirs(output_dir, exist_ok=True)
    
    pdf = PDFReport(title)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    headers = ['Tanggal', 'Barang', 'Qty', 'Total', 'Pembeli']
    col_widths = [35, 55, 20, 35, 45]
    
    data = []
    total = 0.0
    for t in (transactions or []):
        date_str = str(t.get('date', ''))[:10] if t.get('date') else ''
        try:
            total_price = float(t.get('total_price') or 0)
        except (ValueError, TypeError):
            total_price = 0.0
        total += total_price
        
        data.append([
            date_str,
            str(t.get('item_name', ''))[:25],
            str(t.get('qty', '')),
            f"Rp {total_price:,.0f}",
            str(t.get('member_name', '-'))[:20]
        ])
    
    pdf.add_table(headers, data, col_widths)
    
    # Summary
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 10, f"Total: Rp {total:,.0f}", align='R')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{filename}_{timestamp}.pdf"
    filepath = os.path.join(output_dir, full_filename)
    
    pdf.output(filepath)
    return filepath


def export_inventory_pdf(items: list, category: str, filename: str = "Laporan_Inventaris",
                         output_dir: str = None) -> str:
    """Export inventory to PDF with safe float calculations and formatting"""
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "Koperasi_Export")
    
    os.makedirs(output_dir, exist_ok=True)
    
    pdf = PDFReport(f"Laporan Inventaris - {category}")
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Headers matching the request
    headers = ['ID', 'Kode', 'Nama Barang', 'Stok', 'Pokok', 'Jual', 'Laba', 'Aset']
    col_widths = [10, 20, 45, 15, 25, 25, 25, 25] # Total should be ~190 for A4
    
    data = []
    total_asset_value = 0.0
    for item in (items or []):
        try:
            sell_price = float(item.get('sell_price') or 0)
            buy_price = float(item.get('buy_price') or 0)
            stock = float(item.get('stock') or 0)
        except (ValueError, TypeError):
            sell_price = 0.0
            buy_price = 0.0
            stock = 0.0
            
        laba = sell_price - buy_price
        aset = sell_price * stock
        total_asset_value += aset
        
        stock_str = f"{int(stock)}" if stock.is_integer() else f"{stock:,.1f}"
        
        data.append([
            str(item.get('id', '')),
            str(item.get('item_code', '-'))[:10],
            str(item.get('name', ''))[:20],
            stock_str,
            f"{buy_price:,.0f}",
            f"{sell_price:,.0f}",
            f"{laba:,.0f}",
            f"{aset:,.0f}"
        ])
    
    pdf.add_table(headers, data, col_widths)
    
    # Summary
    pdf.ln(10)
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 10, f"Total Nilai Aset (Harga Jual): Rp {total_asset_value:,.0f}", align='R')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{filename}_{timestamp}.pdf"
    filepath = os.path.join(output_dir, full_filename)
    
    pdf.output(filepath)
    return filepath
