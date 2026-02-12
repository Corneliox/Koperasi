using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Text;
using System.Windows.Forms;
using KoperasiBrimob.Data;

namespace KoperasiBrimob.Services
{
    public class DataService
    {
        // 1. Export DataTable to CSV (Excel Compatible)
        public bool ExportToCsv(DataTable dt, string fileName)
        {
            try
            {
                StringBuilder sb = new StringBuilder();

                // Column Headers
                string[] columnNames = new string[dt.Columns.Count];
                for (int i = 0; i < dt.Columns.Count; i++)
                {
                    columnNames[i] = dt.Columns[i].ColumnName;
                }
                sb.AppendLine(string.Join(",", columnNames));

                // Rows
                foreach (DataRow row in dt.Rows)
                {
                    string[] fields = new string[dt.Columns.Count];
                    for (int i = 0; i < dt.Columns.Count; i++)
                    {
                        fields[i] = "\"" + row[i].ToString().Replace("\"", "\"\"") + "\"";
                    }
                    sb.AppendLine(string.Join(",", fields));
                }

                File.WriteAllText(fileName, sb.ToString(), Encoding.UTF8);
                return true;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Export Failed: " + ex.Message);
                return false;
            }
        }

        // 2. Database Backup (The "Export Database" feature)
        public bool BackupDatabase(string destPath)
        {
            try
            {
                string sourcePath = "koperasi_brimob.db";
                if (File.Exists(sourcePath))
                {
                    File.Copy(sourcePath, destPath, true);
                    return true;
                }
                return false;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Backup Failed: " + ex.Message);
                return false;
            }
        }

        // 3. Database Restore (The "Import Database" feature)
        public bool RestoreDatabase(string srcPath)
        {
            try
            {
                if (File.Exists(srcPath))
                {
                    File.Copy(srcPath, "koperasi_brimob.db", true);
                    return true;
                }
                return false;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Restore Failed: " + ex.Message);
                return false;
            }
        }

        // 4. Generate Simple HTML Report (For "PDF" printing)
        // User can open in browser and Save as PDF/Print
        public void ExportToHtml(DataTable dt, string title, string fileName)
        {
            StringBuilder sb = new StringBuilder();
            sb.AppendLine("<html><head><style>table { border-collapse: collapse; width: 100%; } th, td { border: 1px solid black; padding: 8px; text-align: left; } th { background-color: #f2f2f2; }</style></head><body>");
            sb.AppendLine("<h1>" + title + "</h1>");
            sb.AppendLine("<p>Generated on: " + DateTime.Now.ToString() + "</p>");
            sb.AppendLine("<table><thead><tr>");
            foreach (DataColumn col in dt.Columns) sb.AppendLine("<th>" + col.ColumnName + "</th>");
            sb.AppendLine("</tr></thead><tbody>");
            foreach (DataRow row in dt.Rows)
            {
                sb.AppendLine("<tr>");
                foreach (var item in row.ItemArray) sb.AppendLine("<td>" + item.ToString() + "</td>");
                sb.AppendLine("</tr>");
            }
            sb.AppendLine("</tbody></table></body></html>");
            File.WriteAllText(fileName, sb.ToString());
        }
        // 5. Import Stock from CSV
        public List<string[]> ImportStockFromCsv(string fileName)
        {
            var results = new List<string[]>();
            try
            {
                var lines = File.ReadAllLines(fileName);
                // Skip header if exists (simple check: first line contains "Name")
                int start = lines.Length > 0 && lines[0].ToLower().Contains("name") ? 1 : 0;

                for (int i = start; i < lines.Length; i++)
                {
                    if (string.IsNullOrWhiteSpace(lines[i])) continue;
                    
                    // Simple CSV split (handling quotes ideally, but basic split for now to match .NET 4 constraints without libs)
                    // For robust CSV, we assume standard comma separation
                    var parts = lines[i].Split(',');
                    if (parts.Length >= 2) // Need at least Name and Stock
                    {
                        // Clean quotes
                        for(int j=0; j<parts.Length; j++) parts[j] = parts[j].Trim().Trim('"');
                        results.Add(parts);
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Import Failed: " + ex.Message);
            }
            return results;
        }
    }
}
