using System;
using System.Drawing;
using System.Windows.Forms;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;
using KoperasiBrimob.Models;

namespace KoperasiBrimob.Views.Dialogs
{
    public class AddItemDialog : BaseDialog
    {
        public Product NewProduct { get; private set; }
        private DarkTextBox txtName, txtStock, txtBuy, txtSell;
        private ComboBox cmbStatus;
        private Product _existing;

        public AddItemDialog(Product existing = null) : base(existing == null ? "Add New Item" : "Edit Item", 400, 450)
        {
            _existing = existing;
            InitializeForm();
        }

        private void InitializeForm()
        {
            int y = 20;

            // Name
            pnlContent.Controls.Add(new DarkLabel { Text = "Item Name:", Location = new Point(20, y) });
            txtName = new DarkTextBox { Location = new Point(20, y + 25), Size = new Size(340, 30), Text = _existing != null ? _existing.Name : "" };
            pnlContent.Controls.Add(txtName);
            y += 65;

            // Stock
            pnlContent.Controls.Add(new DarkLabel { Text = "Stock:", Location = new Point(20, y) });
            txtStock = new DarkTextBox { Location = new Point(20, y + 25), Size = new Size(150, 30), Text = _existing != null ? _existing.Stock.ToString() : "0" };
            pnlContent.Controls.Add(txtStock);
            y += 65;

            // Buy Price
            pnlContent.Controls.Add(new DarkLabel { Text = "Buy Price (Rp):", Location = new Point(20, y) });
            txtBuy = new DarkTextBox { Location = new Point(20, y + 25), Size = new Size(150, 30), Text = _existing != null ? _existing.BuyPrice.ToString() : "0" };
            pnlContent.Controls.Add(txtBuy);

            // Sell Price
            pnlContent.Controls.Add(new DarkLabel { Text = "Sell Price (Rp):", Location = new Point(190, y) });
            txtSell = new DarkTextBox { Location = new Point(190, y + 25), Size = new Size(170, 30), Text = _existing != null ? _existing.SellPrice.ToString() : "0" };
            pnlContent.Controls.Add(txtSell);
            y += 65;

            // Status
            pnlContent.Controls.Add(new DarkLabel { Text = "Status:", Location = new Point(20, y) });
            cmbStatus = new ComboBox { Location = new Point(20, y + 25), Size = new Size(150, 30), FlatStyle = FlatStyle.Flat };
            cmbStatus.Items.AddRange(new object[] { "Koperasi", "Konsinyasi" });
            cmbStatus.SelectedIndex = _existing != null && _existing.Status == "Konsinyasi" ? 1 : 0;
            pnlContent.Controls.Add(cmbStatus);
            y += 70;

            // Save Button
            var btnSave = new DarkButton { Text = "SAVE", Location = new Point(20, y), Size = new Size(340, 40), BackColor = ThemeColor.Success };
            btnSave.Click += BtnSave_Click;
            pnlContent.Controls.Add(btnSave);
        }

        private void BtnSave_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(txtName.Text)) { MessageBox.Show("Name required"); return; }

            try
            {
                NewProduct = new Product
                {
                    Id = _existing != null ? _existing.Id : 0,
                    Name = txtName.Text,
                    Stock = int.Parse(txtStock.Text),
                    BuyPrice = double.Parse(txtBuy.Text),
                    SellPrice = double.Parse(txtSell.Text),
                    Status = cmbStatus.SelectedItem.ToString(),
                    Description = _existing != null ? _existing.Description : ""
                };
                this.DialogResult = DialogResult.OK;
                this.Close();
            }
            catch
            {
                MessageBox.Show("Invalid number format");
            }
        }
    }
}