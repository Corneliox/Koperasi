using System;
using System.Drawing;
using System.Windows.Forms;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;
using KoperasiBrimob.Services;

namespace KoperasiBrimob.Views.Panels
{
    public class FinancialPanel : UserControl
    {
        private FinancialService _service;
        private string _category;
        private FlowLayoutPanel flowLayout;

        public FinancialPanel(string category)
        {
            _service = new FinancialService();
            _category = category;
            this.Dock = DockStyle.Fill;
            this.BackColor = ThemeColor.Background;
            InitializeComponent();
            LoadData();
        }

        private void InitializeComponent()
        {
            var lblTitle = new HeaderLabel();
            lblTitle.Text = _category + " Financial Report";
            lblTitle.Location = new Point(20, 20);
            this.Controls.Add(lblTitle);

            flowLayout = new FlowLayoutPanel();
            flowLayout.Location = new Point(20, 70);
            flowLayout.Size = new Size(1000, 500);
            flowLayout.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right | AnchorStyles.Bottom;
            flowLayout.AutoScroll = true;
            this.Controls.Add(flowLayout);
        }

        private void LoadData()
        {
            var stats = _service.GetSummary(_category);
            flowLayout.Controls.Clear();

            AddStatCard("Total Sales (Revenue)", "Rp " + stats["TotalSales"].ToString("N0"), ThemeColor.Success);
            AddStatCard("Calculated Assets", "Rp " + stats["Assets"].ToString("N0"), ThemeColor.Accent);
            AddStatCard("Current Stock Value", "Rp " + stats["StockValue"].ToString("N0"), ThemeColor.Warning);
        }

        private void AddStatCard(string title, string value, Color accentColor)
        {
            Panel card = new Panel();
            card.Size = new Size(300, 150);
            card.BackColor = ThemeColor.Surface;
            card.Margin = new Padding(10);
            
            Panel stripe = new Panel { Size = new Size(5, 150), Dock = DockStyle.Left, BackColor = accentColor };
            card.Controls.Add(stripe);

            Label lblT = new Label { Text = title, ForeColor = ThemeColor.TextDim, Font = ThemeColor.SmallFont, Location = new Point(20, 30), AutoSize = true };
            card.Controls.Add(lblT);

            Label lblV = new Label { Text = value, ForeColor = ThemeColor.Text, Font = new Font("Segoe UI", 18F, FontStyle.Bold), Location = new Point(20, 65), AutoSize = true };
            card.Controls.Add(lblV);

            flowLayout.Controls.Add(card);
        }
    }
}
