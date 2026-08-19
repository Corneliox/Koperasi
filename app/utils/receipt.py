"""
Receipt/Invoice Generator for POS Transactions
Supports both PDF and text-based thermal receipt format
"""
import os
from datetime import datetime
from fpdf import FPDF


def generate_receipt(sale_data: dict, output_dir: str = None) -> str:
    """
    Generate receipt/invoice for a sale transaction
    
    :param sale_data: Dict containing:
        - item_name: Name of item sold
        - qty: Quantity sold
        - unit_price: Price per unit
        - total: Total amount
        - category: SEMBAKO or TAKTIKAL
        - member_name: (optional) Buyer name
        - member_nrp: (optional) Buyer NRP
    :param output_dir: Output directory
    :return: Path to generated receipt
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "Koperasi_Struk")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate receipt number
    receipt_no = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Create PDF receipt
    pdf = ReceiptPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, 'KOPERASI BRIMOB', align='C', new_x="LMARGIN", new_y="NEXT")
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
    
    grand_total = sale_data.get('grand_total', sale_data.get('total', 0))
    if not grand_total and items_list:
        grand_total = sum(it.get('total', it.get('qty', 0) * it.get('price', 0)) for it in items_list)
        
    for it in items_list:
        item_name = str(it.get('name', '-'))
        if len(item_name) > 25:
            item_name = item_name[:25] + '...'
        
        pdf.cell(50, 5, item_name, border=0)
        pdf.cell(15, 5, str(it.get('qty', 0)), border=0, align='C')
        pdf.cell(25, 5, f"Rp {it.get('price', 0):,.0f}", border=0, align='R')
        pdf.ln()
    
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
    Generate thermal printer compatible text receipt
    Standard 58mm/80mm thermal paper format
    
    :param sale_data: Same as generate_receipt
    :param output_dir: Output directory
    :return: Path to text file
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "Koperasi_Struk")
    
    os.makedirs(output_dir, exist_ok=True)
    
    receipt_no = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Build receipt text (32 char width for 58mm paper)
    lines = []
    lines.append("=" * 32)
    lines.append("     KOPERASI BRIMOB")
    lines.append("    Struk Penjualan")
    lines.append("=" * 32)
    lines.append(f"No: {receipt_no}")
    lines.append(f"Tgl: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    lines.append(f"Kat: {sale_data.get('category', 'SEMBAKO')}")
    
    if sale_data.get('member_name'):
        lines.append(f"Pembeli: {sale_data['member_name'][:20]}")
    
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
    
    grand_total = sale_data.get('grand_total', sale_data.get('total', 0))
    if not grand_total and items_list:
        grand_total = sum(it.get('total', it.get('qty', 0) * it.get('price', 0)) for it in items_list)
        
    for it in items_list:
        item_name = str(it.get('name', '-'))[:25]
        qty = it.get('qty', 0)
        unit_price = it.get('price', 0)
        lines.append(item_name)
        lines.append(f"  {qty} x Rp {unit_price:,.0f}")
    
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
    Generate invoice for multiple items (bulk purchase)
    
    :param transaction_list: List of transactions
    :param member_info: Optional member info dict
    :param output_dir: Output directory
    :return: Path to PDF invoice
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Documents", "Koperasi_Invoice")
    
    os.makedirs(output_dir, exist_ok=True)
    
    invoice_no = datetime.now().strftime("INV%Y%m%d%H%M%S")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Header
    pdf.set_font('Helvetica', 'B', 18)
    pdf.cell(0, 12, 'INVOICE', align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 8, 'KOPERASI BRIMOB', align='C', new_x="LMARGIN", new_y="NEXT")
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
    
    total = 0
    for idx, trans in enumerate(transaction_list):
        subtotal = trans.get('qty', 0) * trans.get('unit_price', 0)
        total += subtotal
        
        pdf.cell(10, 7, str(idx + 1), border=1, align='C')
        pdf.cell(70, 7, str(trans.get('item_name', '-'))[:35], border=1)
        pdf.cell(25, 7, str(trans.get('qty', 0)), border=1, align='C')
        pdf.cell(35, 7, f"Rp {trans.get('unit_price', 0):,.0f}", border=1, align='R')
        pdf.cell(40, 7, f"Rp {subtotal:,.0f}", border=1, align='R')
        pdf.ln()
    
    # Total
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(140, 10, 'TOTAL:', border=0, align='R')
    pdf.cell(40, 10, f"Rp {total:,.0f}", border=1, align='R')
    pdf.ln(15)
    
    # Footer
    pdf.set_font('Helvetica', 'I', 9)
    pdf.cell(0, 6, 'Terima kasih atas kepercayaan Anda kepada Koperasi Brimob', align='C')
    
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
