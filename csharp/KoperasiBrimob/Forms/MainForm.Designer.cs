namespace KoperasiBrimob.Forms
{
    partial class MainForm
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null)) components.Dispose();
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.tabControl1 = new System.Windows.Forms.TabControl();
            this.tabDashboard = new System.Windows.Forms.TabPage();
            this.lblWelcome = new System.Windows.Forms.Label();
            this.tabSembako = new System.Windows.Forms.TabPage();
            this.dgvSembako = new System.Windows.Forms.DataGridView();
            this.panelSembakoOps = new System.Windows.Forms.Panel();
            this.btnAddSembako = new System.Windows.Forms.Button();
            this.btnSellSembako = new System.Windows.Forms.Button();
            this.btnReturnSembako = new System.Windows.Forms.Button();
            this.txtSearchSembako = new System.Windows.Forms.TextBox();
            this.tabTaktikal = new System.Windows.Forms.TabPage();
            this.dgvTaktikal = new System.Windows.Forms.DataGridView();
            this.panelTaktikalOps = new System.Windows.Forms.Panel();
            this.btnAddTaktikal = new System.Windows.Forms.Button();
            this.btnSellTaktikal = new System.Windows.Forms.Button();
            this.btnReturnTaktikal = new System.Windows.Forms.Button();
            this.txtSearchTaktikal = new System.Windows.Forms.TextBox();
            this.tabAnggota = new System.Windows.Forms.TabPage();
            this.dgvMembers = new System.Windows.Forms.DataGridView();
            this.panelMemberOps = new System.Windows.Forms.Panel();
            this.btnAddMember = new System.Windows.Forms.Button();
            this.txtSearchMember = new System.Windows.Forms.TextBox();
            this.tabPinjaman = new System.Windows.Forms.TabPage();
            this.dgvLoans = new System.Windows.Forms.DataGridView();
            this.panelLoanOps = new System.Windows.Forms.Panel();
            this.btnNewLoan = new System.Windows.Forms.Button();
            this.btnPayLoan = new System.Windows.Forms.Button();
            this.panelHeader = new System.Windows.Forms.Panel();
            this.lblAdminIcon = new System.Windows.Forms.Label();
            this.timerAdminReset = new System.Windows.Forms.Timer(this.components);

            this.tabControl1.SuspendLayout();
            this.tabDashboard.SuspendLayout();
            this.tabSembako.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvSembako)).BeginInit();
            this.panelSembakoOps.SuspendLayout();
            this.tabTaktikal.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvTaktikal)).BeginInit();
            this.panelTaktikalOps.SuspendLayout();
            this.tabAnggota.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvMembers)).BeginInit();
            this.panelMemberOps.SuspendLayout();
            this.tabPinjaman.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dgvLoans)).BeginInit();
            this.panelLoanOps.SuspendLayout();
            this.panelHeader.SuspendLayout();
            this.SuspendLayout();

            // Form
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1000, 600);
            this.Controls.Add(this.tabControl1);
            this.Controls.Add(this.panelHeader);
            this.Name = "MainForm";
            this.Text = "Koperasi Brimob Manager";
            
            // Header
            this.panelHeader.Controls.Add(this.lblAdminIcon);
            this.panelHeader.Dock = System.Windows.Forms.DockStyle.Top;
            this.panelHeader.Height = 50;
            this.panelHeader.BackColor = System.Drawing.Color.DarkSlateBlue;
            
            this.lblAdminIcon.Text = "🛡️ ADMIN";
            this.lblAdminIcon.ForeColor = System.Drawing.Color.White;
            this.lblAdminIcon.Font = new System.Drawing.Font("Arial", 12, System.Drawing.FontStyle.Bold);
            this.lblAdminIcon.Location = new System.Drawing.Point(900, 15);
            this.lblAdminIcon.AutoSize = true;
            this.lblAdminIcon.Cursor = System.Windows.Forms.Cursors.Hand;
            this.lblAdminIcon.MouseDown += new System.Windows.Forms.MouseEventHandler(this.lblAdminIcon_MouseDown);

            // TabControl
            this.tabControl1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.tabControl1.Controls.Add(this.tabDashboard);
            this.tabControl1.Controls.Add(this.tabSembako);
            this.tabControl1.Controls.Add(this.tabTaktikal);
            this.tabControl1.Controls.Add(this.tabAnggota);
            this.tabControl1.Controls.Add(this.tabPinjaman);

            // Dashboard
            this.tabDashboard.Controls.Add(this.lblWelcome);
            this.tabDashboard.Text = "Dashboard";
            this.lblWelcome.Text = "Selamat Datang di Sistem Koperasi Brimob";
            this.lblWelcome.Font = new System.Drawing.Font("Segoe UI", 20);
            this.lblWelcome.AutoSize = true;
            this.lblWelcome.Location = new System.Drawing.Point(50, 50);

            // Sembako
            this.tabSembako.Text = "Sembako";
            this.tabSembako.Controls.Add(this.dgvSembako);
            this.tabSembako.Controls.Add(this.panelSembakoOps);
            this.panelSembakoOps.Dock = System.Windows.Forms.DockStyle.Top;
            this.panelSembakoOps.Height = 50;
            this.panelSembakoOps.Controls.AddRange(new System.Windows.Forms.Control[] { this.txtSearchSembako, this.btnAddSembako, this.btnSellSembako, this.btnReturnSembako });
            this.dgvSembako.Dock = System.Windows.Forms.DockStyle.Fill;
            
            this.btnAddSembako.Text = "Tambah Stok"; this.btnAddSembako.Location = new System.Drawing.Point(10, 10); this.btnAddSembako.Width = 100;
            this.btnSellSembako.Text = "Penjualan"; this.btnSellSembako.Location = new System.Drawing.Point(120, 10); this.btnSellSembako.Width = 100;
            this.btnReturnSembako.Text = "Retur"; this.btnReturnSembako.Location = new System.Drawing.Point(230, 10); this.btnReturnSembako.Width = 100;
            this.txtSearchSembako.Location = new System.Drawing.Point(350, 12); this.txtSearchSembako.Width = 200;

            // Taktikal (Copy Sembako Layout)
            this.tabTaktikal.Text = "Taktikal";
            this.tabTaktikal.Controls.Add(this.dgvTaktikal);
            this.tabTaktikal.Controls.Add(this.panelTaktikalOps);
            this.panelTaktikalOps.Dock = System.Windows.Forms.DockStyle.Top;
            this.panelTaktikalOps.Height = 50;
            this.panelTaktikalOps.Controls.AddRange(new System.Windows.Forms.Control[] { this.txtSearchTaktikal, this.btnAddTaktikal, this.btnSellTaktikal, this.btnReturnTaktikal });
            this.dgvTaktikal.Dock = System.Windows.Forms.DockStyle.Fill;

            this.btnAddTaktikal.Text = "Tambah Stok"; this.btnAddTaktikal.Location = new System.Drawing.Point(10, 10); this.btnAddTaktikal.Width = 100;
            this.btnSellTaktikal.Text = "Penjualan"; this.btnSellTaktikal.Location = new System.Drawing.Point(120, 10); this.btnSellTaktikal.Width = 100;
            this.btnReturnTaktikal.Text = "Retur"; this.btnReturnTaktikal.Location = new System.Drawing.Point(230, 10); this.btnReturnTaktikal.Width = 100;
            this.txtSearchTaktikal.Location = new System.Drawing.Point(350, 12); this.txtSearchTaktikal.Width = 200;

            // Anggota
            this.tabAnggota.Text = "Keanggotaan";
            this.tabAnggota.Controls.Add(this.dgvMembers);
            this.tabAnggota.Controls.Add(this.panelMemberOps);
            this.panelMemberOps.Dock = System.Windows.Forms.DockStyle.Top;
            this.panelMemberOps.Height = 50;
            this.panelMemberOps.Controls.AddRange(new System.Windows.Forms.Control[] { this.txtSearchMember, this.btnAddMember });
            this.dgvMembers.Dock = System.Windows.Forms.DockStyle.Fill;
            this.btnAddMember.Text = "Tambah Anggota"; this.btnAddMember.Location = new System.Drawing.Point(10, 10); this.btnAddMember.Width = 120;
            this.txtSearchMember.Location = new System.Drawing.Point(150, 12); this.txtSearchMember.Width = 200;

            // Pinjaman
            this.tabPinjaman.Text = "Pinjaman";
            this.tabPinjaman.Controls.Add(this.dgvLoans);
            this.tabPinjaman.Controls.Add(this.panelLoanOps);
            this.panelLoanOps.Dock = System.Windows.Forms.DockStyle.Top;
            this.panelLoanOps.Height = 50;
            this.panelLoanOps.Controls.AddRange(new System.Windows.Forms.Control[] { this.btnNewLoan, this.btnPayLoan });
            this.dgvLoans.Dock = System.Windows.Forms.DockStyle.Fill;
            this.btnNewLoan.Text = "Buat Pinjaman"; this.btnNewLoan.Location = new System.Drawing.Point(10, 10); this.btnNewLoan.Width = 120;
            this.btnPayLoan.Text = "Bayar Angsuran"; this.btnPayLoan.Location = new System.Drawing.Point(140, 10); this.btnPayLoan.Width = 120;

            // Timer
            this.timerAdminReset.Interval = 2000;
            this.timerAdminReset.Tick += new System.EventHandler(this.timerAdminReset_Tick);

            // Events
            this.btnAddSembako.Click += (s, e) => HandleAddStock("SEMBAKO");
            this.btnSellSembako.Click += (s, e) => HandleSell("SEMBAKO");
            this.btnReturnSembako.Click += (s, e) => HandleReturn("SEMBAKO");
            this.txtSearchSembako.TextChanged += (s, e) => LoadSembako();

            this.btnAddTaktikal.Click += (s, e) => HandleAddStock("TAKTIKAL");
            this.btnSellTaktikal.Click += (s, e) => HandleSell("TAKTIKAL");
            this.btnReturnTaktikal.Click += (s, e) => HandleReturn("TAKTIKAL");
            this.txtSearchTaktikal.TextChanged += (s, e) => LoadTaktikal();

            this.btnAddMember.Click += (s, e) => HandleAddMember();
            this.txtSearchMember.TextChanged += (s, e) => LoadMembers();

            this.btnNewLoan.Click += (s, e) => HandleNewLoan();
            this.btnPayLoan.Click += (s, e) => HandlePayLoan();

            this.tabControl1.ResumeLayout(false);
            this.tabDashboard.ResumeLayout(false);
            this.tabDashboard.PerformLayout();
            this.tabSembako.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dgvSembako)).EndInit();
            this.panelSembakoOps.ResumeLayout(false);
            this.panelSembakoOps.PerformLayout();
            this.tabTaktikal.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dgvTaktikal)).EndInit();
            this.panelTaktikalOps.ResumeLayout(false);
            this.panelTaktikalOps.PerformLayout();
            this.tabAnggota.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dgvMembers)).EndInit();
            this.panelMemberOps.ResumeLayout(false);
            this.panelMemberOps.PerformLayout();
            this.tabPinjaman.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dgvLoans)).EndInit();
            this.panelLoanOps.ResumeLayout(false);
            this.panelHeader.ResumeLayout(false);
            this.panelHeader.PerformLayout();
            this.ResumeLayout(false);
        }

        private System.Windows.Forms.TabControl tabControl1;
        private System.Windows.Forms.TabPage tabDashboard, tabSembako, tabTaktikal, tabAnggota, tabPinjaman;
        private System.Windows.Forms.DataGridView dgvSembako, dgvTaktikal, dgvMembers, dgvLoans;
        private System.Windows.Forms.Panel panelSembakoOps, panelTaktikalOps, panelMemberOps, panelLoanOps, panelHeader;
        private System.Windows.Forms.Button btnAddSembako, btnSellSembako, btnReturnSembako;
        private System.Windows.Forms.Button btnAddTaktikal, btnSellTaktikal, btnReturnTaktikal;
        private System.Windows.Forms.Button btnAddMember, btnNewLoan, btnPayLoan;
        private System.Windows.Forms.TextBox txtSearchSembako, txtSearchTaktikal, txtSearchMember;
        private System.Windows.Forms.Label lblAdminIcon, lblWelcome;
        private System.Windows.Forms.Timer timerAdminReset;
    }
}
