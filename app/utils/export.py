"""
Export Utilities - Excel and PDF Export Functions
"""
import os
from datetime import datetime
import pandas as pd
from fpdf import FPDF


def export_to_excel(data: list, columns: dict, filename: str, 
                    sheet_name: str = "Data", output_dir: str = None) -> str:
    """
    Export data to Excel file
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
    for row in data:
        df_row = {}
        for key, header in columns.items():
            df_row[header] = row.get(key, "")
        df_data.append(df_row)
    
    df = pd.DataFrame(df_data)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{filename}_{timestamp}.xlsx"
    filepath = os.path.join(output_dir, full_filename)
    
    # Export with formatting
    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Header format
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#2B579A',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        # Cell format
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'vcenter'
        })
        
        # Number format
        number_format = workbook.add_format({
            'border': 1,
            'num_format': '#,##0',
            'align': 'right'
        })
        
        # Apply header format
        for col_num, header in enumerate(df.columns):
            worksheet.write(0, col_num, header, header_format)
            worksheet.set_column(col_num, col_num, 20)
        
        # Freeze header row
        worksheet.freeze_panes(1, 0)
    
    return filepath


def export_transactions_excel(transactions: list, filename: str = "Laporan_Transaksi",
                              output_dir: str = None) -> str:
    """Export transactions to Excel"""
    columns = {
        'date': 'Tanggal',
        'item_name': 'Nama Barang',
        'qty': 'Jumlah',
        'unit_price': 'Harga Satuan',
        'total_price': 'Total',
        'member_name': 'Pembeli',
        'member_nrp': 'NRP',
        'payment_method': 'Metode Bayar'
    }
    return export_to_excel(transactions, columns, filename, "Transaksi", output_dir)


def export_inventory_excel(items: list, filename: str = "Laporan_Inventaris",
                           output_dir: str = None) -> str:
    """Export inventory to Excel with full headers and calculations"""
    processed_items = []
    for item in items:
        processed = dict(item)
        processed['laba'] = item['sell_price'] - item['buy_price']
        processed['status_aktif'] = "Ya" if item.get('is_active', 1) else "Tidak"
        processed['harga_aset'] = item['sell_price'] * item['stock']
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
    
    def __init__(self, title: str = "Laporan Koperasi Brimob"):
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
        """Add a table to the PDF"""
        if col_widths is None:
            col_widths = [self.epw / len(headers)] * len(headers)
        
        # Header
        self.set_font('Helvetica', 'B', 10)
        self.set_fill_color(43, 87, 154)
        self.set_text_color(255, 255, 255)
        
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 8, header, border=1, align='C', fill=True)
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
    """Export transactions to PDF"""
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "Koperasi_Export")
    
    os.makedirs(output_dir, exist_ok=True)
    
    pdf = PDFReport(title)
    pdf.alias_nb_pages()
    pdf.add_page()
    
    headers = ['Tanggal', 'Barang', 'Qty', 'Total', 'Pembeli']
    col_widths = [35, 55, 20, 35, 45]
    
    data = []
    for t in transactions:
        date_str = t.get('date', '')[:10] if t.get('date') else ''
        data.append([
            date_str,
            str(t.get('item_name', ''))[:25],
            str(t.get('qty', '')),
            f"Rp {t.get('total_price', 0):,.0f}",
            str(t.get('member_name', '-'))[:20]
        ])
    
    pdf.add_table(headers, data, col_widths)
    
    # Summary
    total = sum(t.get('total_price', 0) for t in transactions)
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
    """Export inventory to PDF with new columns"""
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
    total_asset_value = 0
    for item in items:
        laba = item['sell_price'] - item['buy_price']
        aset = item['sell_price'] * item['stock']
        total_asset_value += aset
        
        data.append([
            str(item.get('id', '')),
            str(item.get('item_code', '-'))[:10],
            str(item.get('name', ''))[:20],
            str(item.get('stock', '')),
            f"{item.get('buy_price', 0):,.0f}",
            f"{item.get('sell_price', 0):,.0f}",
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
