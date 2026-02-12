using System;
using System.Drawing;
using System.Windows.Forms;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;

namespace KoperasiBrimob.Views
{
    public class CategorySelectForm : Form
    {
        public CategorySelectForm()
        {
            InitializeComponent();
        }

        private void InitializeComponent()
        {
            this.Size = new Size(800, 500);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.BackColor = ThemeColor.Background;
            this.Text = "Pilih Kategori - Koperasi Brimob";
            this.Icon = new Icon("icon.ico");

            var lblTitle = new HeaderLabel();
            lblTitle.Text = "PILIH UNIT LAYANAN";
            lblTitle.Location = new Point(280, 50);
            this.Controls.Add(lblTitle);

            // Sembako Card
            var btnSembako = CreateCard("🛒 SEMBAKO", "Kebutuhan Pokok & Pangan", 100, 120, ThemeColor.Success);
            btnSembako.Click += (s, e) => LaunchMain("SEMBAKO");
            this.Controls.Add(btnSembako);

            // Taktikal Card
            var btnTaktikal = CreateCard("🎯 TAKTIKAL", "Perlengkapan & Atribut", 450, 120, ThemeColor.Accent);
            btnTaktikal.Click += (s, e) => LaunchMain("TAKTIKAL");
            this.Controls.Add(btnTaktikal);

            // Admin Link
            var btnAdmin = new DarkButton { Text = "Manajemen Anggota & Pinjaman", Location = new Point(250, 380), Size = new Size(300, 40) };
            btnAdmin.Click += (s, e) => LaunchMain("ADMIN");
            this.Controls.Add(btnAdmin);
        }

        private Button CreateCard(string title, string desc, int x, int y, Color color)
        {
            var btn = new Button();
            btn.Size = new Size(250, 220);
            btn.Location = new Point(x, y);
            btn.FlatStyle = FlatStyle.Flat;
            btn.FlatAppearance.BorderSize = 2;
            btn.FlatAppearance.BorderColor = color;
            btn.BackColor = ThemeColor.Surface;
            btn.ForeColor = ThemeColor.Text;
            btn.Cursor = Cursors.Hand;
            btn.Font = new Font("Segoe UI", 14F, FontStyle.Bold);
            btn.Text = title + "\n\n" + desc;
            return btn;
        }

        private void LaunchMain(string context)
        {
            this.Hide();
            var main = new MainForm(context);
            // Jangan bind FormClosed ke this.Close() jika kita ingin kembali ke sini
            main.Show();
        }
    }
}
