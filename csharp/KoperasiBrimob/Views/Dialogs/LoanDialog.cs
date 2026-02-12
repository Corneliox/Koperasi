using System;
using System.Drawing;
using System.Windows.Forms;
using System.Collections.Generic;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;
using KoperasiBrimob.Services;

namespace KoperasiBrimob.Views.Dialogs
{
    public class LoanDialog : BaseDialog
    {
        public double Amount { get; private set; }
        public double Rate { get; private set; }
        public int Duration { get; private set; }
        public string Notes { get; private set; }

        private DarkTextBox txtAmount, txtRate, txtDuration, txtNotes;
        private ListBox lstSchedule;
        private LoanService _service;

        public LoanDialog() : base("Create New Loan", 600, 500)
        {
            _service = new LoanService();
            InitializeForm();
        }

        private void InitializeForm()
        {
            int y = 20;

            // Inputs
            pnlContent.Controls.Add(new DarkLabel { Text = "Amount (Rp):", Location = new Point(20, y) });
            txtAmount = new DarkTextBox { Location = new Point(120, y - 3), Size = new Size(150, 30), Text = "1000000" };
            pnlContent.Controls.Add(txtAmount);
            
            pnlContent.Controls.Add(new DarkLabel { Text = "Rate (%):", Location = new Point(300, y) });
            txtRate = new DarkTextBox { Location = new Point(380, y - 3), Size = new Size(60, 30), Text = "2" };
            pnlContent.Controls.Add(txtRate);
            y += 40;

            pnlContent.Controls.Add(new DarkLabel { Text = "Duration (Mo):", Location = new Point(20, y) });
            txtDuration = new DarkTextBox { Location = new Point(120, y - 3), Size = new Size(60, 30), Text = "12" };
            pnlContent.Controls.Add(txtDuration);
            y += 40;

            var btnSimulate = new DarkButton { Text = "SIMULATE", Location = new Point(20, y), Size = new Size(540, 35), BackColor = ThemeColor.Warning };
            btnSimulate.Click += BtnSimulate_Click;
            pnlContent.Controls.Add(btnSimulate);
            y += 45;

            // Schedule
            pnlContent.Controls.Add(new DarkLabel { Text = "Repayment Schedule:", Location = new Point(20, y) });
            y += 25;
            lstSchedule = new ListBox { Location = new Point(20, y), Size = new Size(540, 150), BackColor = ThemeColor.Surface, ForeColor = ThemeColor.Text, BorderStyle = BorderStyle.FixedSingle };
            pnlContent.Controls.Add(lstSchedule);
            y += 160;

            // Notes
            pnlContent.Controls.Add(new DarkLabel { Text = "Notes:", Location = new Point(20, y) });
            txtNotes = new DarkTextBox { Location = new Point(80, y - 3), Size = new Size(480, 30) };
            pnlContent.Controls.Add(txtNotes);
            y += 40;

            // Create
            var btnCreate = new DarkButton { Text = "CREATE LOAN", Location = new Point(20, y), Size = new Size(540, 40), BackColor = ThemeColor.Success };
            btnCreate.Click += BtnCreate_Click;
            pnlContent.Controls.Add(btnCreate);
        }

        private void BtnSimulate_Click(object sender, EventArgs e)
        {
            try
            {
                double amt = double.Parse(txtAmount.Text);
                double rate = double.Parse(txtRate.Text);
                int dur = int.Parse(txtDuration.Text);

                var sim = _service.Simulate(amt, rate, dur);
                lstSchedule.Items.Clear();
                foreach (var s in (List<string>)sim["Schedule"])
                {
                    lstSchedule.Items.Add(s);
                }
            }
            catch { MessageBox.Show("Invalid Input"); }
        }

        private void BtnCreate_Click(object sender, EventArgs e)
        {
            try
            {
                if (lstSchedule.Items.Count == 0) { MessageBox.Show("Please Simulate first"); return; }
                
                Amount = double.Parse(txtAmount.Text);
                Rate = double.Parse(txtRate.Text);
                Duration = int.Parse(txtDuration.Text);
                Notes = txtNotes.Text;
                
                this.DialogResult = DialogResult.OK;
                this.Close();
            }
            catch { MessageBox.Show("Invalid Input"); }
        }
    }
}
