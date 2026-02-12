using System;
using System.Drawing;
using System.Windows.Forms;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;
using KoperasiBrimob.Data; // Direct DB access for logs
using System.Data.SQLite;
using System.Data;
using KoperasiBrimob.Services;

namespace KoperasiBrimob.Views.Panels
{
    public class AuditLogPanel : UserControl
    {
        private DataGridView grid;

        public AuditLogPanel()
        {
            this.Dock = DockStyle.Fill;
            this.BackColor = ThemeColor.Background;
            InitializeComponent();
            LoadData();
        }

        private void InitializeComponent()
        {
            var lblTitle = new HeaderLabel();
            lblTitle.Text = "System Admin & Audit Logs";
            lblTitle.Location = new Point(20, 20);
            this.Controls.Add(lblTitle);

            var flow = new FlowLayoutPanel { Location = new Point(20, 60), Size = new Size(1000, 50), Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right };
            this.Controls.Add(flow);

            var btnRefresh = new DarkButton { Text = "Refresh" };
            btnRefresh.Click += (s, e) => LoadData();
            flow.Controls.Add(btnRefresh);

            var btnBackup = new DarkButton { Text = "Backup Database", BackColor = ThemeColor.Primary };
            btnBackup.Click += (s, e) => {
                var sfd = new SaveFileDialog { Filter = "SQLite DB|*.db", FileName = "backup_koperasi.db" };
                if(sfd.ShowDialog() == DialogResult.OK) {
                    if(new DataService().BackupDatabase(sfd.FileName)) MessageBox.Show("Backup Success");
                }
            };
            flow.Controls.Add(btnBackup);

            var btnRestore = new DarkButton { Text = "Restore Database", BackColor = ThemeColor.Warning };
            btnRestore.Click += (s, e) => {
                var ofd = new OpenFileDialog { Filter = "SQLite DB|*.db" };
                if(ofd.ShowDialog() == DialogResult.OK) {
                    if(MessageBox.Show("Restore will overwrite current data. Continue?", "Confirm", MessageBoxButtons.YesNo) == DialogResult.Yes) {
                        if(new DataService().RestoreDatabase(ofd.FileName)) {
                            MessageBox.Show("Restore Success. App will restart.");
                            Application.Restart();
                        }
                    }
                }
            };
            flow.Controls.Add(btnRestore);

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
            grid.AllowUserToAddRows = false;
            grid.ReadOnly = true;
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
                var da = new SQLiteDataAdapter("SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT 100", conn);
                var dt = new DataTable();
                da.Fill(dt);
                grid.DataSource = dt;
            }
        }
    }
}
