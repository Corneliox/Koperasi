using System;
using System.Collections.Generic;
using System.Data.SQLite;
using KoperasiBrimob.Data;
using KoperasiBrimob.Models;

namespace KoperasiBrimob.Services
{
    public class FinancialService
    {
        public Dictionary<string, double> GetSummary(string category)
        {
            var stats = new Dictionary<string, double>();
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();

                // 1. Total Sales (Income)
                using (var cmd = new SQLiteCommand("SELECT SUM(total_price) FROM transactions WHERE category_type=@c", conn))
                {
                    cmd.Parameters.AddWithValue("@c", category);
                    var res = cmd.ExecuteScalar();
                    stats["TotalSales"] = res != DBNull.Value ? Convert.ToDouble(res) : 0;
                }

                // 2. Assets (Rule: Sell Price * Quantity Out)
                // We sum (unit_price * qty) from transactions which represents "Out"
                using (var cmd = new SQLiteCommand("SELECT SUM(qty * unit_price) FROM transactions WHERE category_type=@c", conn))
                {
                    cmd.Parameters.AddWithValue("@c", category);
                    var res = cmd.ExecuteScalar();
                    stats["Assets"] = res != DBNull.Value ? Convert.ToDouble(res) : 0;
                }

                // 3. Stock Value (Current Inventory Value)
                using (var cmd = new SQLiteCommand("SELECT SUM(stock * buy_price) FROM warehouse WHERE category_type=@c", conn))
                {
                    cmd.Parameters.AddWithValue("@c", category);
                    var res = cmd.ExecuteScalar();
                    stats["StockValue"] = res != DBNull.Value ? Convert.ToDouble(res) : 0;
                }
            }
            return stats;
        }
    }
}
