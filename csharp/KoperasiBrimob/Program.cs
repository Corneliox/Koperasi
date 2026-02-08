using System;
using System.IO;
using System.Reflection;
using System.Windows.Forms;
using KoperasiBrimob.Forms;

namespace KoperasiBrimob
{
    static class Program
    {
        [STAThread]
        static void Main()
        {
            // Prepare for embedded resource loading (Basic setup)
            // In a real build, we would embed System.Data.SQLite.dll and SQLite.Interop.dll
            // and write them to a temp folder if not found.
            
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            
            // Ensure Database is Initialized
            try 
            {
                Helpers.DatabaseHelper.InitializeDatabase();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Database Initialization Failed: " + ex.Message, "Critical Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            Application.Run(new LoginForm());
        }
    }
}
