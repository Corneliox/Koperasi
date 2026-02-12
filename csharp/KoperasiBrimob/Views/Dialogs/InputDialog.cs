using System;
using System.Drawing;
using System.Windows.Forms;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;

namespace KoperasiBrimob.Views.Dialogs
{
    public class InputDialog : BaseDialog
    {
        public string InputValue { get { return txtInput.Text; } }
        private DarkTextBox txtInput;

        public InputDialog(string title, string prompt) : base(title, 400, 200)
        {
            pnlContent.Controls.Add(new DarkLabel { Text = prompt, Location = new Point(20, 20) });
            txtInput = new DarkTextBox { Location = new Point(20, 50), Size = new Size(340, 30) };
            pnlContent.Controls.Add(txtInput);

            var btnOk = new DarkButton { Text = "OK", Location = new Point(20, 100), Size = new Size(100, 35), BackColor = ThemeColor.Success };
            btnOk.Click += (s, e) => { this.DialogResult = DialogResult.OK; this.Close(); };
            pnlContent.Controls.Add(btnOk);
        }
    }
}
