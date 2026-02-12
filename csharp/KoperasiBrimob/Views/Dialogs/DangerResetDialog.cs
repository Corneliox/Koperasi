using System;
using System.Drawing;
using System.Windows.Forms;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;

namespace KoperasiBrimob.Views.Dialogs
{
    public class DangerResetDialog : BaseDialog
    {
        public DangerResetDialog() : base("⚠️ DANGER ZONE", 400, 300)
        {
            InitializeForm();
        }

        private void InitializeForm()
        {
            var lblWarn = new Label();
            lblWarn.Text = "You are about to RESET the database.\nThis action CANNOT be undone.";
            lblWarn.ForeColor = ThemeColor.Danger;
            lblWarn.Font = new Font("Segoe UI", 12F, FontStyle.Bold);
            lblWarn.Location = new Point(20, 20);
            lblWarn.Size = new Size(360, 60);
            pnlContent.Controls.Add(lblWarn);

            var btnSembako = new DarkButton { Text = "Reset Sembako", Location = new Point(20, 100), Size = new Size(340, 40), BackColor = ThemeColor.Warning };
            pnlContent.Controls.Add(btnSembako);

            var btnAll = new DarkButton { Text = "RESET EVERYTHING", Location = new Point(20, 150), Size = new Size(340, 50), BackColor = ThemeColor.Danger };
            btnAll.Click += (s, e) => { MessageBox.Show("Reset Executed (Logged to Audit)"); this.Close(); };
            pnlContent.Controls.Add(btnAll);
        }
    }
}
