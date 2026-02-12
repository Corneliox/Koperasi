using System;
using System.Drawing;
using System.Windows.Forms;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;
using KoperasiBrimob.Services;
using KoperasiBrimob.Views.Dialogs;

namespace KoperasiBrimob.Views.Panels
{
    public class MemberPanel : UserControl
    {
        private MemberService _service;
        private DataGridView grid;
        private DarkTextBox txtSearch;

        public MemberPanel()
        {
            _service = new MemberService();
            this.Dock = DockStyle.Fill;
            this.BackColor = ThemeColor.Background;
            InitializeComponent();
            LoadData();
        }

        private void InitializeComponent()
        {
            var lblTitle = new HeaderLabel();
            lblTitle.Text = "Membership Management";
            lblTitle.Location = new Point(20, 20);
            this.Controls.Add(lblTitle);

            var flowControls = new FlowLayoutPanel();
            flowControls.Location = new Point(20, 60);
            flowControls.Size = new Size(1000, 50);
            flowControls.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            flowControls.AutoSize = true;
            this.Controls.Add(flowControls);

            txtSearch = new DarkTextBox();
            txtSearch.Size = new Size(250, 30);
            txtSearch.TextChanged += (s, e) => LoadData();
            flowControls.Controls.Add(txtSearch);

            var btnAdd = new DarkButton { Text = "+ Member", BackColor = ThemeColor.Success, Size = new Size(100, 35) };
            btnAdd.Click += BtnAdd_Click;
            flowControls.Controls.Add(btnAdd);

            var btnDelete = new DarkButton { Text = "Delete", BackColor = ThemeColor.Danger, Size = new Size(80, 35) };
            btnDelete.Click += BtnDelete_Click;
            flowControls.Controls.Add(btnDelete);

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

        private void LoadData()
        {
            grid.DataSource = _service.GetAllMembers(txtSearch.Text);
        }

        private void BtnAdd_Click(object sender, EventArgs e)
        {
            using (var dlg = new MemberDialog())
            {
                if (dlg.ShowDialog() == DialogResult.OK)
                {
                    _service.AddMember(dlg.NewMember);
                    LoadData();
                }
            }
        }

        private void BtnDelete_Click(object sender, EventArgs e)
        {
            if (grid.SelectedRows.Count == 0) return;
            long id = (long)grid.SelectedRows[0].Cells["Id"].Value;
            if (MessageBox.Show("Delete Member?", "Confirm", MessageBoxButtons.YesNo, MessageBoxIcon.Warning) == DialogResult.Yes)
            {
                _service.DeleteMember(id);
                LoadData();
            }
        }
    }
}