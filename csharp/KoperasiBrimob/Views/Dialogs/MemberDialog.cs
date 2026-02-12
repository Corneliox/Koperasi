using System;
using System.Drawing;
using System.Windows.Forms;
using System.Collections.Generic;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;
using KoperasiBrimob.Models;
using KoperasiBrimob.Services;

namespace KoperasiBrimob.Views.Dialogs
{
    public class MemberDialog : BaseDialog
    {
        public Member NewMember { get; private set; }
        private DarkTextBox txtName, txtNrp, txtRank, txtUnit, txtPhone, txtAddress;
        private MemberService _service;

        public MemberDialog() : base("Add New Member", 400, 550)
        {
            _service = new MemberService();
            InitializeForm();
        }

        private void InitializeForm()
        {
            int y = 10;

            AddInput("Name:", ref txtName, ref y);
            AddInput("NRP:", ref txtNrp, ref y);
            AddInput("Rank:", ref txtRank, ref y);
            AddInput("Unit:", ref txtUnit, ref y);
            AddInput("Phone:", ref txtPhone, ref y);
            AddInput("Address:", ref txtAddress, ref y);

            y += 10;
            var btnSave = new DarkButton { Text = "SAVE MEMBER", Location = new Point(20, y), Size = new Size(340, 40), BackColor = ThemeColor.Success };
            btnSave.Click += BtnSave_Click;
            pnlContent.Controls.Add(btnSave);
        }

        private void AddInput(string label, ref DarkTextBox box, ref int y)
        {
            pnlContent.Controls.Add(new DarkLabel { Text = label, Location = new Point(20, y) });
            box = new DarkTextBox { Location = new Point(20, y + 25), Size = new Size(340, 30) };
            pnlContent.Controls.Add(box);
            y += 60;
        }

        private void BtnSave_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(txtName.Text)) { MessageBox.Show("Name required"); return; }

            // Fuzzy Check
            var duplicates = _service.FindDuplicates(txtName.Text);
            if (duplicates.Count > 0)
            {
                string msg = "Potential duplicates found:\n" + string.Join("\n", duplicates.ToArray()) + "\n\nContinue anyway?";
                if (MessageBox.Show(msg, "Duplicate Warning", MessageBoxButtons.YesNo, MessageBoxIcon.Warning) == DialogResult.No)
                {
                    return;
                }
            }

            NewMember = new Member
            {
                Name = txtName.Text,
                Nrp = txtNrp.Text,
                Rank = txtRank.Text,
                Unit = txtUnit.Text,
                Phone = txtPhone.Text,
                Address = txtAddress.Text
            };
            this.DialogResult = DialogResult.OK;
            this.Close();
        }
    }
}
