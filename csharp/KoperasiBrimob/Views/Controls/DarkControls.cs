using System;
using System.Drawing;
using System.Windows.Forms;
using KoperasiBrimob.Infrastructure;

namespace KoperasiBrimob.Views.Controls
{
    public class DarkButton : Button
    {
        public DarkButton()
        {
            this.FlatStyle = FlatStyle.Flat;
            this.FlatAppearance.BorderSize = 0;
            this.BackColor = ThemeColor.Primary;
            this.ForeColor = ThemeColor.Text;
            this.Font = ThemeColor.PrimaryFont;
            this.Cursor = Cursors.Hand;
            this.Size = new Size(120, 35);
        }

        protected override void OnPaint(PaintEventArgs pevent)
        {
            base.OnPaint(pevent);
            // Add custom painting if needed, simpler is better for C# 4.0/Win7 performance
        }
    }

    public class DarkPanel : Panel
    {
        public DarkPanel()
        {
            this.BackColor = ThemeColor.Surface;
            this.ForeColor = ThemeColor.Text;
        }
    }

    public class DarkLabel : Label
    {
        public DarkLabel()
        {
            this.ForeColor = ThemeColor.Text;
            this.BackColor = Color.Transparent;
            this.Font = ThemeColor.PrimaryFont;
        }
    }

    public class HeaderLabel : Label
    {
        public HeaderLabel()
        {
            this.ForeColor = ThemeColor.Accent;
            this.BackColor = Color.Transparent;
            this.Font = ThemeColor.HeaderFont;
            this.AutoSize = true;
        }
    }

    public class DarkTextBox : TextBox
    {
        public DarkTextBox()
        {
            this.BackColor = Color.FromArgb(40, 40, 50);
            this.ForeColor = ThemeColor.Text;
            this.BorderStyle = BorderStyle.FixedSingle;
            this.Font = ThemeColor.PrimaryFont;
        }
    }
}
