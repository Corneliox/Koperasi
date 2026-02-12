using System;
using System.Drawing;
using System.Windows.Forms;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;
using KoperasiBrimob.Services;
using KoperasiBrimob.Views.Dialogs;
using KoperasiBrimob.Models;

namespace KoperasiBrimob.Views.Panels
{
    public class LoanPanel : UserControl
    {
        private LoanService _service;
        private DataGridView grid;

        public LoanPanel()
        {
            _service = new LoanService();
            this.Dock = DockStyle.Fill;
            this.BackColor = ThemeColor.Background;
            InitializeComponent();
            LoadData();
        }

        private void InitializeComponent()
        {
            var lblTitle = new HeaderLabel();
            lblTitle.Text = "Loan Management";
            lblTitle.Location = new Point(20, 20);
            this.Controls.Add(lblTitle);

            var flowControls = new FlowLayoutPanel();
            flowControls.Location = new Point(20, 60);
            flowControls.Size = new Size(1000, 50);
            flowControls.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            flowControls.AutoSize = true;
            this.Controls.Add(flowControls);

            var btnCreate = new DarkButton { Text = "+ New Loan", BackColor = ThemeColor.Success, Size = new Size(120, 35) };
            btnCreate.Click += BtnCreate_Click;
            flowControls.Controls.Add(btnCreate);

            var btnPay = new DarkButton { Text = "Pay", BackColor = ThemeColor.Primary, Size = new Size(80, 35) };
            btnPay.Click += BtnPay_Click;
            flowControls.Controls.Add(btnPay);

            var btnMacet = new DarkButton { Text = "Mark Bad", BackColor = ThemeColor.Danger, Size = new Size(100, 35) };
            btnMacet.Click += BtnMacet_Click;
            flowControls.Controls.Add(btnMacet);

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
            grid.ColumnHeadersHeight = 35;
            grid.RowTemplate.Height = 30;
            grid.AllowUserToAddRows = false;
            grid.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            grid.MultiSelect = false;
            grid.CellFormatting += Grid_CellFormatting;
            grid.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill;
            grid.ScrollBars = ScrollBars.Both;
            
            grid.EnableHeadersVisualStyles = false;
            grid.ColumnHeadersDefaultCellStyle.BackColor = ThemeColor.Primary;
            grid.ColumnHeadersDefaultCellStyle.ForeColor = ThemeColor.Text;
            grid.DefaultCellStyle.BackColor = ThemeColor.Surface;
            grid.DefaultCellStyle.ForeColor = ThemeColor.Text;
            grid.DefaultCellStyle.SelectionBackColor = ThemeColor.Accent;
            
            gridContainer.Controls.Add(grid);
        }

        private void Grid_CellFormatting(object sender, DataGridViewCellFormattingEventArgs e)
        {
            if (grid.Columns[e.ColumnIndex].Name == "Status")
            {
                if (e.Value != null)
                {
                    string status = e.Value.ToString();
                    if (status == "Lunas") e.CellStyle.ForeColor = ThemeColor.Success;
                    else if (status == "Macet") e.CellStyle.ForeColor = ThemeColor.Danger;
                }
            }
            // Due Date Check (Assuming DueDate column exists)
            // if (grid.Columns[e.ColumnIndex].Name == "DueDate" ... compare with DateTime.Now)
        }

        private void LoadData()
        {
            grid.DataSource = _service.GetAllLoans();
        }

        private void BtnCreate_Click(object sender, EventArgs e)
        {
            string input = Microsoft.VisualBasic.Interaction.InputBox("Enter Member ID:", "Select Member", "1");
            long memberId;
            if (long.TryParse(input, out memberId))
            {
                using (var dlg = new LoanDialog())
                {
                    if (dlg.ShowDialog() == DialogResult.OK)
                    {
                        var res = _service.CreateLoan(memberId, dlg.Amount, dlg.Rate, dlg.Duration, dlg.Notes);
                        MessageBox.Show(res["message"].ToString());
                        LoadData();
                    }
                }
            }
        }

        private void BtnPay_Click(object sender, EventArgs e)
        {
            if (grid.SelectedRows.Count == 0) return;
            long loanId = (long)grid.SelectedRows[0].Cells["Id"].Value;
            
            string amountStr = Microsoft.VisualBasic.Interaction.InputBox("Enter Payment Amount:", "Payment", "0");
            double amount;
            if (double.TryParse(amountStr, out amount))
            {
                 var res = _service.RecordPayment(loanId, amount, "Tunai", "Manual Payment");
                 MessageBox.Show(res["message"].ToString());
                 LoadData();
            }
        }

        private void BtnMacet_Click(object sender, EventArgs e)
        {
            if (grid.SelectedRows.Count == 0) return;
            long loanId = (long)grid.SelectedRows[0].Cells["Id"].Value;
            if (MessageBox.Show("Mark as Bad Debt?", "Confirm", MessageBoxButtons.YesNo) == DialogResult.Yes)
            {
                _service.MarkBadDebt(loanId);
                LoadData();
            }
        }
    }
}