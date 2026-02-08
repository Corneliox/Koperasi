using System;
using System.Windows.Forms;
using KoperasiBrimob.Services;

namespace KoperasiBrimob.Forms
{
    public partial class LoginForm : Form
    {
        private AuthService _authService;

        public LoginForm()
        {
            InitializeComponent();
            _authService = new AuthService();
            this.AcceptButton = btnLogin;
        }

        private void btnLogin_Click(object sender, EventArgs e)
        {
            if (_authService.Login(txtUsername.Text, txtPassword.Text))
            {
                this.Hide();
                new MainForm().ShowDialog();
                this.Close();
            }
            else
            {
                MessageBox.Show("Login Failed", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}
