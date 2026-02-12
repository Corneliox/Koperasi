using System;
using System.Drawing;
using System.Windows.Forms;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Services;
using KoperasiBrimob.Views.Controls;

namespace KoperasiBrimob.Views
{
    public class LoginForm : Form
    {
        private DarkTextBox txtUsername;
        private DarkTextBox txtPassword;
        private DarkButton btnLogin;
        private HeaderLabel lblTitle;
        private DarkLabel lblUser, lblPass;
        private AuthService _authService;

        public LoginForm()
        {
            _authService = new AuthService();
            InitializeComponent();
        }

        private void InitializeComponent()
        {
            this.Size = new Size(350, 300);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.BackColor = ThemeColor.Background;
            this.Text = "Login - Koperasi Brimob";
            this.Icon = new Icon("icon.ico");

            lblTitle = new HeaderLabel();
            lblTitle.Text = "Koperasi Brimob";
            lblTitle.Location = new Point(85, 30);
            this.Controls.Add(lblTitle);

            lblUser = new DarkLabel();
            lblUser.Text = "Username";
            lblUser.Location = new Point(50, 80);
            this.Controls.Add(lblUser);

            txtUsername = new DarkTextBox();
            txtUsername.Location = new Point(50, 105);
            txtUsername.Size = new Size(240, 30);
            this.Controls.Add(txtUsername);

            lblPass = new DarkLabel();
            lblPass.Text = "Password";
            lblPass.Location = new Point(50, 145);
            this.Controls.Add(lblPass);

            txtPassword = new DarkTextBox();
            txtPassword.Location = new Point(50, 170);
            txtPassword.Size = new Size(240, 30);
            txtPassword.PasswordChar = '*';
            this.Controls.Add(txtPassword);

            btnLogin = new DarkButton();
            btnLogin.Text = "LOGIN";
            btnLogin.Location = new Point(50, 220);
            btnLogin.Size = new Size(240, 40);
            btnLogin.Click += new EventHandler(btnLogin_Click);
            this.Controls.Add(btnLogin);

            this.AcceptButton = btnLogin;
        }

        private void btnLogin_Click(object sender, EventArgs e)
        {
            if (_authService.Login(txtUsername.Text, txtPassword.Text))
            {
                this.Hide();
                var select = new CategorySelectForm();
                select.FormClosed += (s, args) => this.Close();
                select.Show();
            }
            else
            {
                MessageBox.Show("Login Failed", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}
