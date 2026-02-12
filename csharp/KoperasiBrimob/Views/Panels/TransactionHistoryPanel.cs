using System;
using System.Data;
using System.Data.SQLite;
using System.Drawing;
using System.Windows.Forms;
using KoperasiBrimob.Data;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;
using KoperasiBrimob.Services;

namespace KoperasiBrimob.Views.Panels
{
    public class TransactionHistoryPanel : UserControl
    {
        private DataGridView grid;
        private string _category;

        public TransactionHistoryPanel(string category)
        {
            _category = category;
            this.Dock = DockStyle.Fill;
            this.BackColor = ThemeColor.Background;
            InitializeComponent();
            LoadData();
        }

        private void InitializeComponent()
        {
            var lblTitle = new HeaderLabel();
            lblTitle.Text = _category + " Transaction History";
            lblTitle.Location = new Point(20, 20);
            this.Controls.Add(lblTitle);

            var flow = new FlowLayoutPanel { Location = new Point(20, 60), Size = new Size(1000, 50), Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right };
            this.Controls.Add(flow);

            var btnExport = new DarkButton { Text = "Export Excel", BackColor = Color.DarkOliveGreen };
            btnExport.Click += (s, e) => {
                var sfd = new SaveFileDialog { Filter = "CSV|*.csv" };
                if(sfd.ShowDialog() == DialogResult.OK) {
                    new DataService().ExportToCsv((DataTable)grid.DataSource, sfd.FileName);
                    MessageBox.Show("Export complete");
                }
            };
            flow.Controls.Add(btnExport);

            // Grid Container with Margin
            var gridContainer = new Panel();
            gridContainer.Location = new Point(20, 120);
            gridContainer.Size = new Size(this.Width - 60, this.Height - 140);
            gridContainer.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right | AnchorStyles.Bottom;
            gridContainer.Padding = new Padding(0, 0, 40, 20);
            this.Controls.Add(gridContainer);

            grid = new DataGridView();
            grid.Dock = DockStyle.Fill;
            grid.BackgroundColor = ThemeColor.Surface;
            grid.BorderStyle = BorderStyle.None;
            grid.ReadOnly = true;
            grid.AllowUserToAddRows = false;
            grid.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            grid.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill;
            grid.ScrollBars = ScrollBars.Both;

            grid.EnableHeadersVisualStyles = false;
            grid.ColumnHeadersDefaultCellStyle.BackColor = ThemeColor.Primary;
            grid.ColumnHeadersDefaultCellStyle.ForeColor = ThemeColor.Text;
            grid.DefaultCellStyle.BackColor = ThemeColor.Surface;
            grid.DefaultCellStyle.ForeColor = ThemeColor.Text;

            gridContainer.Controls.Add(grid);
        }

        private void LoadData()
        {
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                string sql = "SELECT t.id, w.name as Item, t.qty, t.unit_price as Price, t.total_price as Total, t.payment_method as Method, t.date " +
                             "FROM transactions t JOIN warehouse w ON t.item_id = w.id " +
                             "WHERE t.category_type = @c ORDER BY t.date DESC";
                var da = new SQLiteDataAdapter(sql, conn);
                da.SelectCommand.Parameters.AddWithValue("@c", _category);
                var dt = new DataTable();
                da.Fill(dt);
                grid.DataSource = dt;
            }
        }
    }
}
