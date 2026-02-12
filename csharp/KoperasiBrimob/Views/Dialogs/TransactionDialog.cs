using System;
using System.Drawing;
using System.Windows.Forms;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;
using KoperasiBrimob.Models;

namespace KoperasiBrimob.Views.Dialogs
{
    public class TransactionDialog : BaseDialog
    {
        public int Quantity { get; private set; }
        public string PaymentMethod { get; private set; }
        
        private Product _product;
        private DarkTextBox txtQty;
        private ComboBox cmbPayment;
        private DarkLabel lblTotal;

        public TransactionDialog(Product product) : base("Sell Item: " + product.Name, 400, 350)
        {
            _product = product;
            InitializeForm();
        }

        private void InitializeForm()
        {
            int y = 20;

            // Info
            pnlContent.Controls.Add(new DarkLabel { Text = "Stock Available: " + _product.Stock, Location = new Point(20, y) });
            pnlContent.Controls.Add(new DarkLabel { Text = "Price: Rp " + _product.SellPrice.ToString("N0"), Location = new Point(200, y) });
            y += 40;

            // Qty
            pnlContent.Controls.Add(new DarkLabel { Text = "Quantity:", Location = new Point(20, y) });
            txtQty = new DarkTextBox { Location = new Point(20, y + 25), Size = new Size(340, 30), Text = "1" };
            txtQty.TextChanged += UpdateTotal;
            pnlContent.Controls.Add(txtQty);
            y += 65;

            // Payment
            pnlContent.Controls.Add(new DarkLabel { Text = "Payment Method:", Location = new Point(20, y) });
            cmbPayment = new ComboBox { Location = new Point(20, y + 25), Size = new Size(340, 30), FlatStyle = FlatStyle.Flat };
            cmbPayment.Items.AddRange(new object[] { "Tunai", "Transfer", "QRIS" });
            cmbPayment.SelectedIndex = 0;
            pnlContent.Controls.Add(cmbPayment);
            y += 65;

            // Total
            lblTotal = new DarkLabel { Text = "Total: Rp 0", Font = ThemeColor.HeaderFont, ForeColor = ThemeColor.Accent, Location = new Point(20, y) };
            pnlContent.Controls.Add(lblTotal);
            y += 50;

            // Confirm
            var btnConfirm = new DarkButton { Text = "CONFIRM SALE", Location = new Point(20, y), Size = new Size(340, 40), BackColor = ThemeColor.Success };
            btnConfirm.Click += BtnConfirm_Click;
            pnlContent.Controls.Add(btnConfirm);

            UpdateTotal(null, null);
        }

        private void UpdateTotal(object sender, EventArgs e)
        {
            int qty;
            if (int.TryParse(txtQty.Text, out qty))
            {
                double total = qty * _product.SellPrice;
                lblTotal.Text = "Total: Rp " + total.ToString("N0");
            }
        }

        private void BtnConfirm_Click(object sender, EventArgs e)
        {
            int qty;
            if (int.TryParse(txtQty.Text, out qty) && qty > 0)
            {
                if (qty > _product.Stock) { MessageBox.Show("Not enough stock!"); return; }
                
                Quantity = qty;
                PaymentMethod = cmbPayment.SelectedItem.ToString();
                this.DialogResult = DialogResult.OK;
                this.Close();
            }
            else
            {
                MessageBox.Show("Invalid Quantity");
            }
        }
    }
}
