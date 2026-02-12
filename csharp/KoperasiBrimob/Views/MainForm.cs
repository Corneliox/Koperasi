using System;
using System.Drawing;
using System.Windows.Forms;
using System.Collections.Generic;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;
using KoperasiBrimob.Views.Panels;

namespace KoperasiBrimob.Views
{
    public class MainForm : Form
    {
        private string _context; // SEMBAKO, TAKTIKAL, or ADMIN
        private TableLayoutPanel mainLayout;
        private Panel sidebar;
        private Panel contentArea;
        private HeaderLabel lblAdmin;
        private int adminClickCount = 0;
        private Timer adminResetTimer;

        public MainForm(string context)
        {
            _context = context;
            InitializeComponent();
            SetupSidebar();
            LoadPanel("Dashboard");
        }

        private void InitializeComponent()
        {
            this.Size = new Size(1280, 720);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.Text = "Koperasi Brimob Manager - " + _context;
            this.Icon = new Icon("icon.ico");
            this.BackColor = ThemeColor.Background;

            mainLayout = new TableLayoutPanel { Dock = DockStyle.Fill, ColumnCount = 2 };
            mainLayout.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 220F));
            mainLayout.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100F));
            this.Controls.Add(mainLayout);

            sidebar = new Panel { Dock = DockStyle.Fill, BackColor = ThemeColor.Surface };
            mainLayout.Controls.Add(sidebar, 0, 0);

            lblAdmin = new HeaderLabel { Text = "🛡️ " + _context, Location = new Point(20, 20), Cursor = Cursors.Hand };
            lblAdmin.MouseDown += LblAdmin_MouseDown;
            sidebar.Controls.Add(lblAdmin);

            contentArea = new Panel { Dock = DockStyle.Fill, BackColor = ThemeColor.Background };
            mainLayout.Controls.Add(contentArea, 1, 0);

            adminResetTimer = new Timer { Interval = 2000 };
            adminResetTimer.Tick += (s, e) => { adminClickCount = 0; adminResetTimer.Stop(); };
        }

        private void SetupSidebar()
        {
            List<string> buttons = new List<string>();
            buttons.Add("Dashboard");

            if (_context == "ADMIN")
            {
                buttons.Add("Anggota");
                buttons.Add("Pinjaman");
            }
            else
            {
                buttons.Add("Stok Barang");
                buttons.Add("Riwayat Transaksi");
                buttons.Add("Laporan Keuangan");
            }

            buttons.Add("Switch Category");

            int y = 80;
            foreach (var btnText in buttons)
            {
                var btn = new DarkButton
                {
                    Text = btnText,
                    Size = new Size(180, 45),
                    Location = new Point(20, y),
                    TextAlign = ContentAlignment.MiddleLeft
                };
                btn.Click += (s, e) => {
                    if (btnText == "Switch Category") { 
                        foreach(Form f in Application.OpenForms) {
                            if(f is CategorySelectForm) {
                                f.Show();
                                break;
                            }
                        }
                        this.Close(); 
                    }
                    else LoadPanel(btnText);
                };
                sidebar.Controls.Add(btn);
                y += 55;
            }
        }

        private void LoadPanel(string name)
        {
            contentArea.Controls.Clear();
            Control p = null;

            if (name == "Dashboard") p = new DashboardPanel();
            else if (name == "Stok Barang") p = new StorePanel(_context);
            else if (name == "Riwayat Transaksi") p = new TransactionHistoryPanel(_context);
            else if (name == "Laporan Keuangan") p = new FinancialPanel(_context);
            else if (name == "Anggota") p = new MemberPanel();
            else if (name == "Pinjaman") p = new LoanPanel();

            if (p != null)
            {
                p.Dock = DockStyle.Fill;
                contentArea.Controls.Add(p);
            }
        }

        private void LblAdmin_MouseDown(object sender, MouseEventArgs e)
        {
            if (Control.ModifierKeys == Keys.Control)
            {
                adminClickCount++;
                adminResetTimer.Stop(); adminResetTimer.Start();
                if (adminClickCount >= 5)
                {
                    adminClickCount = 0; adminResetTimer.Stop();
                    new Dialogs.DangerResetDialog().ShowDialog();
                }
            }
        }
    }
}