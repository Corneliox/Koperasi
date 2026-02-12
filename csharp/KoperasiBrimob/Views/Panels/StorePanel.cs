using System;
using System.Drawing;
using System.Windows.Forms;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Views.Controls;
using KoperasiBrimob.Services;
using KoperasiBrimob.Models;

namespace KoperasiBrimob.Views.Panels
{
    public class StorePanel : UserControl
    {
        private string _category;
        private WarehouseService _service;
        private DataGridView grid;
        private DarkTextBox txtSearch;

        public StorePanel(string category)
        {
            _category = category;
            _service = new WarehouseService(category);
            this.Dock = DockStyle.Fill;
            this.BackColor = ThemeColor.Background;
            InitializeComponent();
            LoadData();
        }

        private void InitializeComponent()
        {
            // Header
            var lblTitle = new HeaderLabel();
            lblTitle.Text = _category + " Inventory";
            lblTitle.Location = new Point(20, 20);
            this.Controls.Add(lblTitle);

            // Flow Layout for Controls
            var flowControls = new FlowLayoutPanel();
            flowControls.Location = new Point(20, 60);
            flowControls.Size = new Size(1000, 50);
            flowControls.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            flowControls.AutoSize = true;
            this.Controls.Add(flowControls);

            // Search
            txtSearch = new DarkTextBox();
            txtSearch.Size = new Size(200, 30);
            txtSearch.TextChanged += (s, e) => LoadData();
            flowControls.Controls.Add(txtSearch);

            // Buttons...
            var btnAdd = new DarkButton { Text = "Add Item", BackColor = ThemeColor.Success, Size = new Size(100, 35) };
            btnAdd.Click += (s, e) => 
            {
                using (var dlg = new Dialogs.AddItemDialog())
                {
                    if (dlg.ShowDialog() == DialogResult.OK)
                    {
                        _service.AddItem(dlg.NewProduct);
                        LoadData();
                    }
                }
            };
            flowControls.Controls.Add(btnAdd);

            var btnSell = new DarkButton { Text = "Sell", BackColor = ThemeColor.Primary, Size = new Size(80, 35) };
            btnSell.Click += (s, e) => 
            {
                if (grid.SelectedRows.Count == 0) { MessageBox.Show("Select an item first"); return; }
                var item = (Product)grid.SelectedRows[0].DataBoundItem;
                
                using (var dlg = new Dialogs.TransactionDialog(item))
                {
                    if (dlg.ShowDialog() == DialogResult.OK)
                    {
                        _service.SellItem(item.Id, dlg.Quantity, item.SellPrice, dlg.PaymentMethod);
                        LoadData();
                    }
                }
            };
            flowControls.Controls.Add(btnSell);

            var btnEdit = new DarkButton { Text = "Edit", BackColor = ThemeColor.Warning, Size = new Size(80, 35) };
            btnEdit.Click += (s, e) => 
            {
                if (grid.SelectedRows.Count == 0) return;
                var item = (Product)grid.SelectedRows[0].DataBoundItem;
                using (var dlg = new Dialogs.AddItemDialog(item))
                {
                    if (dlg.ShowDialog() == DialogResult.OK)
                    {
                        _service.UpdateItem(dlg.NewProduct);
                        LoadData();
                    }
                }
            };
            flowControls.Controls.Add(btnEdit);

            var btnExport = new DarkButton { Text = "Export Excel", BackColor = Color.DarkOliveGreen, Size = new Size(100, 35) };
            btnExport.Click += (s, e) => 
            {
                var dt = (System.Collections.Generic.List<Product>)grid.DataSource;
                var ds = new DataService();
                var sfd = new SaveFileDialog { Filter = "Excel CSV (*.csv)|*.csv" };
                if(sfd.ShowDialog() == DialogResult.OK)
                {
                    var dataTable = new System.Data.DataTable();
                    dataTable.Columns.Add("Name"); dataTable.Columns.Add("Stock"); dataTable.Columns.Add("Price");
                    foreach(var p in dt) dataTable.Rows.Add(p.Name, p.Stock, p.SellPrice);
                    ds.ExportToCsv(dataTable, sfd.FileName);
                    MessageBox.Show("Exported successfully");
                }
            };
            flowControls.Controls.Add(btnExport);

            // Import Button
            var btnImport = new DarkButton { Text = "Import CSV", BackColor = Color.Teal, Size = new Size(100, 35) };
            btnImport.Click += (s, e) =>
            {
                var ofd = new OpenFileDialog { Filter = "CSV Files (*.csv)|*.csv" };
                if (ofd.ShowDialog() == DialogResult.OK)
                {
                    var data = new DataService().ImportStockFromCsv(ofd.FileName);
                    if (data.Count > 0)
                    {
                        _service.ImportItems(data);
                        LoadData();
                    }
                    else MessageBox.Show("No valid data found in CSV");
                }
            };
            flowControls.Controls.Add(btnImport);

            // Grid Layout Fix: Use Container with Padding
            var gridContainer = new Panel();
            gridContainer.Location = new Point(20, 120);
            gridContainer.Size = new Size(this.Width - 60, this.Height - 140); // Initial size
            gridContainer.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right | AnchorStyles.Bottom;
            // 2.5% Right Margin -> Padding Right
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
            grid.DataSource = _service.GetAllItems(txtSearch.Text);
        }
    }
}
