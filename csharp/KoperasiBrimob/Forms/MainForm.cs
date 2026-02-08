using System;
using System.Windows.Forms;
using KoperasiBrimob.Services;
using KoperasiBrimob.Helpers;
using System.Collections.Generic;

namespace KoperasiBrimob.Forms
{
    public partial class MainForm : Form
    {
        private WarehouseService _sembakoService;
        private WarehouseService _taktikalService;
        private MemberService _memberService;
        private LoanService _loanService;
        
        // Easter Egg State
        private int _adminClickCount = 0;

        public MainForm()
        {
            InitializeComponent();
            _sembakoService = new WarehouseService("SEMBAKO");
            _taktikalService = new WarehouseService("TAKTIKAL");
            _memberService = new MemberService();
            _loanService = new LoanService();
            
            LoadData();
        }

        private void LoadData()
        {
            LoadSembako();
            LoadTaktikal();
            LoadMembers();
            LoadLoans();
        }

        private void LoadSembako()
        {
            dgvSembako.DataSource = _sembakoService.GetAllItems(txtSearchSembako.Text);
        }

        private void LoadTaktikal()
        {
            dgvTaktikal.DataSource = _taktikalService.GetAllItems(txtSearchTaktikal.Text);
        }

        private void LoadMembers()
        {
            dgvMembers.DataSource = _memberService.GetAllMembers(txtSearchMember.Text);
        }

        private void LoadLoans()
        {
            dgvLoans.DataSource = _loanService.GetAllLoans();
        }

        // --- Handlers ---

        private void HandleAddStock(string category)
        {
            // Simplified Input Dialog for prototype
            // In real app, create a custom Form
            MessageBox.Show(string.Format("Fitur Tambah Stok {0} akan membuka Form Dialog.\n(Implementasi detail ada di WarehouseService)", category), "Info");
            // Example:
            // var form = new AddItemForm(); 
            // if(form.ShowDialog() == OK) _service.AddItem(form.Product);
        }

        private void HandleSell(string category)
        {
             MessageBox.Show(string.Format("Fitur Penjualan {0} akan membuka Form Transaksi.\n(Logika Assets = SellPrice * Qty sudah di Service)", category), "Info");
        }

        private void HandleReturn(string category)
        {
             MessageBox.Show("Fitur Retur " + category + " mengurangi stok tanpa tercatat sebagai penjualan (Out).", "Info");
        }

        private void HandleAddMember()
        {
             MessageBox.Show("Fitur Tambah Anggota dengan Cek Duplikasi (Levenshtein) di Service.", "Info");
        }

        private void HandleNewLoan()
        {
             MessageBox.Show("Fitur Simulasi Pinjaman & Create Loan.", "Info");
        }

        private void HandlePayLoan()
        {
             MessageBox.Show("Fitur Bayar Cicilan (Cash/Transfer/QRIS).", "Info");
        }

        // --- Admin Easter Egg ---

        private void lblAdminIcon_MouseDown(object sender, MouseEventArgs e)
        {
            if (Control.ModifierKeys == Keys.Control)
            {
                _adminClickCount++;
                timerAdminReset.Stop();
                timerAdminReset.Start(); // Reset counter if no click within 2s

                if (_adminClickCount >= 5)
                {
                    _adminClickCount = 0;
                    timerAdminReset.Stop();
                    ShowAdminResetDialog();
                }
            }
        }

        private void timerAdminReset_Tick(object sender, EventArgs e)
        {
            _adminClickCount = 0;
            timerAdminReset.Stop();
        }

        private void ShowAdminResetDialog()
        {
            var result = MessageBox.Show(
                @"⚠️ DANGER ZONE ⚠️

Reset Database? This cannot be undone.", 
                "Admin Reset", 
                MessageBoxButtons.YesNo, 
                MessageBoxIcon.Warning);
            
            if (result == DialogResult.Yes)
            {
                // Call Reset Logic (Not fully implemented in C# side for safety in this snippet, 
                // but Logger allows logging this event)
                Logger.Log("SYSTEM", "Admin Reset Triggered", "ADMIN");
                MessageBox.Show("Reset functionality logged.", "Admin");
            }
        }
    }
}
