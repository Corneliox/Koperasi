using System;
using System.Drawing;
using System.Windows.Forms;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;
using KoperasiBrimob.Data;
using System.Data.SQLite;

namespace KoperasiBrimob.Views.Panels
{
    public class DashboardPanel : UserControl
    {
        private FlowLayoutPanel flowLayout;

        public DashboardPanel()
        {
            this.Dock = DockStyle.Fill;
            this.BackColor = ThemeColor.Background;
            InitializeComponent();
            LoadStats();
        }

        private void InitializeComponent()
        {
            var lblTitle = new HeaderLabel { Text = "Dashboard Overview", Location = new Point(20, 20) };
            this.Controls.Add(lblTitle);

            flowLayout = new FlowLayoutPanel { Location = new Point(20, 70), Size = new Size(1200, 600), Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right | AnchorStyles.Bottom, AutoScroll = true };
            this.Controls.Add(flowLayout);
        }

        private void LoadStats()
        {
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                flowLayout.Controls.Clear();

                // Total Members
                long members = 0;
                using (var cmd = new SQLiteCommand("SELECT COUNT(*) FROM members", conn)) members = (long)cmd.ExecuteScalar();
                AddStatCard("Total Members", members.ToString(), ThemeColor.Primary);

                // Total Loans
                double loans = 0;
                using (var cmd = new SQLiteCommand("SELECT SUM(total_amount - paid_amount) FROM loans WHERE status='Aktif'", conn))
                {
                    var res = cmd.ExecuteScalar();
                    loans = res != DBNull.Value ? Convert.ToDouble(res) : 0;
                }
                AddStatCard("Active Loans", "Rp " + loans.ToString("N0"), ThemeColor.Warning);

                // Sembako Stats
                long sembakoCount = 0;
                using (var cmd = new SQLiteCommand("SELECT COUNT(*) FROM warehouse WHERE category_type='SEMBAKO'", conn)) sembakoCount = (long)cmd.ExecuteScalar();
                AddStatCard("Sembako Items", sembakoCount.ToString(), ThemeColor.Success);

                // Taktikal Stats
                long taktikalCount = 0;
                using (var cmd = new SQLiteCommand("SELECT COUNT(*) FROM warehouse WHERE category_type='TAKTIKAL'", conn)) taktikalCount = (long)cmd.ExecuteScalar();
                AddStatCard("Taktikal Items", taktikalCount.ToString(), ThemeColor.Accent);
            }
        }

        private void AddStatCard(string title, string value, Color color)
        {
            Panel card = new Panel { Size = new Size(250, 130), BackColor = ThemeColor.Surface, Margin = new Padding(10) };
            Panel stripe = new Panel { Size = new Size(5, 130), Dock = DockStyle.Left, BackColor = color };
            card.Controls.Add(stripe);
            card.Controls.Add(new Label { Text = title, ForeColor = ThemeColor.TextDim, Font = ThemeColor.SmallFont, Location = new Point(20, 25), AutoSize = true });
            card.Controls.Add(new Label { Text = value, ForeColor = ThemeColor.Text, Font = new Font("Segoe UI", 16F, FontStyle.Bold), Location = new Point(20, 55), AutoSize = true });
            flowLayout.Controls.Add(card);
        }
    }
}