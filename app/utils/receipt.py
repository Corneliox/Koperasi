"""
Receipt/Invoice Generator for POS Transactions
Supports both PDF and text-based thermal receipt format
"""
import os
from datetime import datetime
from fpdf import FPDF


def generate_receipt(sale_data: dict, output_dir: str = None) -> str:
    """
    Generate receipt/invoice for a sale transaction safely
    
    :param sale_data: Dict containing transaction details
    :param output_dir: Output directory
    :return: Path to generated receipt
    """
    if not sale_data:
        return ""

    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "Koperasi_Struk")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate receipt number with microseconds to avoid collision
    receipt_no = datetime.now().strftime("%Y%m%d%H%M%S%f")[:17]
    
    # Create PDF receipt
    pdf = ReceiptPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, 'KOPERASI SIMPAN PINJAM', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, 'Struk Penjualan', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    # Line separator
    pdf.set_draw_color(100, 100, 100)
    pdf.line(10, pdf.get_y(), 90, pdf.get_y())
    pdf.ln(3)
    
    # Receipt info
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 5, f'No. Struk: {receipt_no}', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f'Tanggal: {datetime.now().strftime("%d/%m/%Y %H:%M")}', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f'Kategori: {sale_data.get("category", "SEMBAKO")}', new_x="LMARGIN", new_y="NEXT")
    
    if sale_data.get('member_name'):
        pdf.cell(0, 5, f'Pembeli: {sale_data["member_name"]}', new_x="LMARGIN", new_y="NEXT")
        if sale_data.get('member_nrp'):
            pdf.cell(0, 5, f'NRP: {sale_data["member_nrp"]}', new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(3)
    pdf.line(10, pdf.get_y(), 90, pdf.get_y())
    pdf.ln(3)
    
    # Item details
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(50, 5, 'Item', border=0)
    pdf.cell(15, 5, 'Qty', border=0, align='C')
    pdf.cell(25, 5, 'Harga', border=0, align='R')
    pdf.ln()
    
    pdf.set_font('Helvetica', '', 9)
    
    items_list = sale_data.get('items', [])
    if not items_list and sale_data.get('item_name'):
        items_list = [{
            'name': sale_data.get('item_name', '-'),
            'qty': sale_data.get('qty', 0),
            'price': sale_data.get('unit_price', 0),
            'total': sale_data.get('total', 0)
        }]
    
    grand_total = 0.0
    for it in items_list:
        item_name = str(it.get('name', '-'))
        if len(item_name) > 25:
            item_name = item_name[:25] + '...'
        
        try:
            qty_val = float(it.get('qty') or 0)
            price_val = float(it.get('price') or it.get('unit_price') or 0)
            total_val = float(it.get('total') or (qty_val * price_val))
        except (ValueError, TypeError):
            qty_val = 0.0
            price_val = 0.0
            total_val = 0.0
            
        grand_total += total_val
        
        pdf.cell(50, 5, item_name, border=0)
        pdf.cell(15, 5, f"{qty_val:.0f}", border=0, align='C')
        pdf.cell(25, 5, f"Rp {price_val:,.0f}", border=0, align='R')
        pdf.ln()
    
    # Override grand_total if explicitly given and valid
    if sale_data.get('grand_total') is not None or sale_data.get('total') is not None:
        try:
            specified_total = float(sale_data.get('grand_total') or sale_data.get('total') or 0)
            if specified_total > 0:
                grand_total = specified_total
        except (ValueError, TypeError):
            pass

    pdf.ln(3)
    pdf.line(10, pdf.get_y(), 90, pdf.get_y())
    pdf.ln(3)
    
    # Total
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(50, 6, 'TOTAL:', border=0)
    pdf.cell(40, 6, f"Rp {grand_total:,.0f}", border=0, align='R')
    pdf.ln(8)
    
    # Footer
    pdf.set_font('Helvetica', 'I', 8)
    pdf.cell(0, 5, 'Terima kasih atas kunjungan Anda', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, 'Barang yang sudah dibeli tidak dapat dikembalikan', align='C', new_x="LMARGIN", new_y="NEXT")
    
    # Save PDF
    filename = f"Struk_{receipt_no}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    
    return filepath


def generate_thermal_receipt(sale_data: dict, output_dir: str = None) -> str:
    """
    Generate thermal printer compatible text receipt safely
    Standard 58mm/80mm thermal paper format
    """
    if not sale_data:
        return ""

    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "Koperasi_Struk")
    
    os.makedirs(output_dir, exist_ok=True)
    
    receipt_no = datetime.now().strftime("%Y%m%d%H%M%S%f")[:17]
    
    # Build receipt text (32 char width for 58mm paper)
    lines = []
    lines.append("=" * 32)
    lines.append("   KOPERASI SIMPAN PINJAM")
    lines.append("      Struk Penjualan")
    lines.append("=" * 32)
    lines.append(f"No: {receipt_no}")
    lines.append(f"Tgl: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    lines.append(f"Kat: {sale_data.get('category', 'SEMBAKO')}")
    
    if sale_data.get('member_name'):
        lines.append(f"Pembeli: {str(sale_data['member_name'])[:20]}")
    
    lines.append("-" * 32)
    
    # Items
    items_list = sale_data.get('items', [])
    if not items_list and sale_data.get('item_name'):
        items_list = [{
            'name': sale_data.get('item_name', '-'),
            'qty': sale_data.get('qty', 0),
            'price': sale_data.get('unit_price', 0),
            'total': sale_data.get('total', 0)
        }]
    
    grand_total = 0.0
    for it in items_list:
        item_name = str(it.get('name', '-'))[:25]
        try:
            qty_val = float(it.get('qty') or 0)
            price_val = float(it.get('price') or it.get('unit_price') or 0)
            total_val = float(it.get('total') or (qty_val * price_val))
        except (ValueError, TypeError):
            qty_val = 0.0
            price_val = 0.0
            total_val = 0.0
            
        grand_total += total_val
        lines.append(item_name)
        lines.append(f"  {qty_val:.0f} x Rp {price_val:,.0f}")
    
    if sale_data.get('grand_total') is not None or sale_data.get('total') is not None:
        try:
            specified_total = float(sale_data.get('grand_total') or sale_data.get('total') or 0)
            if specified_total > 0:
                grand_total = specified_total
        except (ValueError, TypeError):
            pass

    lines.append("-" * 32)
    lines.append(f"TOTAL: Rp {grand_total:,.0f}".rjust(32))
    lines.append("=" * 32)
    lines.append("   Terima kasih")
    lines.append("")
    
    # Save text file
    filename = f"Struk_{receipt_no}.txt"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return filepath


def generate_invoice(transaction_list: list, member_info: dict = None,
                     output_dir: str = None) -> str:
    """
    Generate invoice for multiple items (bulk purchase) safely
    
    :param transaction_list: List of transactions
    :param member_info: Optional member info dict
    :param output_dir: Output directory
    :return: Path to PDF invoice
    """
    if not transaction_list:
        return ""

    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "Koperasi_Invoice")
    
    os.makedirs(output_dir, exist_ok=True)
    
    invoice_no = datetime.now().strftime("INV%Y%m%d%H%M%S%f")[:20]
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Header
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 12, 'INVOICE', align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, 'KOPERASI SIMPAN PINJAM', align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Invoice info
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(100, 6, f'No. Invoice: {invoice_no}')
    pdf.cell(0, 6, f'Tanggal: {datetime.now().strftime("%d/%m/%Y")}', align='R')
    pdf.ln()
    
    # Member info
    if member_info:
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 6, 'Kepada:', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 11)
        pdf.cell(0, 6, f'{member_info.get("name", "-")}', new_x="LMARGIN", new_y="NEXT")
        if member_info.get('nrp'):
            pdf.cell(0, 6, f'NRP: {member_info["nrp"]}', new_x="LMARGIN", new_y="NEXT")
        if member_info.get('unit'):
            pdf.cell(0, 6, f'Unit: {member_info["unit"]}', new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(10)
    
    # Table header
    pdf.set_fill_color(43, 87, 154)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 10)
    
    pdf.cell(10, 8, 'No', border=1, align='C', fill=True)
    pdf.cell(70, 8, 'Nama Barang', border=1, align='C', fill=True)
    pdf.cell(25, 8, 'Qty', border=1, align='C', fill=True)
    pdf.cell(35, 8, 'Harga', border=1, align='C', fill=True)
    pdf.cell(40, 8, 'Subtotal', border=1, align='C', fill=True)
    pdf.ln()
    
    # Table data
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Helvetica', '', 10)
    
    total = 0.0
    for idx, trans in enumerate(transaction_list):
        try:
            qty_val = float(trans.get('qty') or 0)
            unit_price_val = float(trans.get('unit_price') or 0)
        except (ValueError, TypeError):
            qty_val = 0.0
            unit_price_val = 0.0
            
        subtotal = qty_val * unit_price_val
        total += subtotal
        
        pdf.cell(10, 7, str(idx + 1), border=1, align='C')
        pdf.cell(70, 7, str(trans.get('item_name', '-'))[:35], border=1)
        pdf.cell(25, 7, f"{qty_val:.0f}", border=1, align='C')
        pdf.cell(35, 7, f"Rp {unit_price_val:,.0f}", border=1, align='R')
        pdf.cell(40, 7, f"Rp {subtotal:,.0f}", border=1, align='R')
        pdf.ln()
    
    # Total
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(140, 10, 'TOTAL:', border=0, align='R')
    pdf.cell(40, 10, f"Rp {total:,.0f}", border=1, align='R')
    pdf.ln(15)
    
    # Footer
    pdf.set_font('Helvetica', 'I', 9)
    pdf.cell(0, 6, 'Terima kasih atas kepercayaan Anda kepada Koperasi', align='C')
    
    # Save
    filename = f"{invoice_no}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    
    return filepath


class ReceiptPDF(FPDF):
    """Custom PDF class for receipts - 100mm x variable height"""
    
    def __init__(self):
        # Receipt paper is typically 58mm or 80mm wide
        # We'll use A7-ish size for PDF representation
        super().__init__(format=(100, 150))  # 100mm width
        self.set_auto_page_break(auto=True, margin=10)
        self.set_margins(10, 10, 10)
