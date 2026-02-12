using System;
using System.Windows.Forms;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Data;
using KoperasiBrimob.Views; // For LoginForm

namespace KoperasiBrimob
{
    static class Program
    {
        [STAThread]
        static void Main()
        {
            // 1. Enable DPI Awareness for sharp text on Win7
            DpiAwareness.Enable();

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            
            // 2. Init DB
            try 
            {
                DatabaseHelper.InitializeDatabase();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Database Init Failed: " + ex.Message);
                return;
            }

            // 3. Launch Login (which will launch Main)
            Application.Run(new Views.LoginForm());
        }
    }
}