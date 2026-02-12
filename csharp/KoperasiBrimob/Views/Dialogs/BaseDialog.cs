using System;
using System.Drawing;
using System.Windows.Forms;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;

namespace KoperasiBrimob.Views.Dialogs
{
    public class BaseDialog : Form
    {
        protected Panel pnlHeader;
        protected HeaderLabel lblTitle;
        protected DarkButton btnClose;
        protected Panel pnlContent;

        public BaseDialog(string title, int width = 500, int height = 400)
        {
            this.FormBorderStyle = FormBorderStyle.None;
            this.StartPosition = FormStartPosition.CenterParent;
            this.Size = new Size(width, height);
            this.BackColor = ThemeColor.Surface;
            this.Padding = new Padding(1); // Border effect

            // Header
            pnlHeader = new Panel();
            pnlHeader.Height = 50;
            pnlHeader.Dock = DockStyle.Top;
            pnlHeader.BackColor = ThemeColor.Background;
            pnlHeader.MouseDown += (s, e) => { if (e.Button == MouseButtons.Left) { ReleaseCapture(); SendMessage(Handle, 0xA1, 0x2, 0); } };
            this.Controls.Add(pnlHeader);

            lblTitle = new HeaderLabel();
            lblTitle.Text = title;
            lblTitle.Location = new Point(20, 13);
            pnlHeader.Controls.Add(lblTitle);

            btnClose = new DarkButton();
            btnClose.Text = "X";
            btnClose.Size = new Size(40, 30);
            btnClose.Location = new Point(width - 50, 10);
            btnClose.BackColor = Color.Transparent;
            btnClose.Click += (s, e) => this.Close();
            pnlHeader.Controls.Add(btnClose);

            // Content
            pnlContent = new Panel();
            pnlContent.Dock = DockStyle.Fill;
            pnlContent.BackColor = ThemeColor.Background;
            pnlContent.Padding = new Padding(20);
            pnlContent.AutoScroll = true;
            this.Controls.Add(pnlContent);
        }

        // Drag window logic
        [System.Runtime.InteropServices.DllImport("user32.dll")]
        public static extern bool ReleaseCapture();
        [System.Runtime.InteropServices.DllImport("user32.dll")]
        public static extern int SendMessage(IntPtr hWnd, int Msg, int wParam, int lParam);

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            ControlPaint.DrawBorder(e.Graphics, this.ClientRectangle, ThemeColor.Primary, ButtonBorderStyle.Solid);
        }
    }
}
