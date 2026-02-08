using System;
using System.Collections.Generic;
using System.Data.SQLite;
using KoperasiBrimob.Helpers;
using KoperasiBrimob.Models;

namespace KoperasiBrimob.Services
{
    public class WarehouseService
    {
        private string _categoryContext;

        public WarehouseService(string categoryContext)
        {
            _categoryContext = categoryContext; // SEMBAKO or TAKTIKAL
        }

        public List<Product> GetAllItems(string search = null)
        {
            var list = new List<Product>();
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                string sql = "SELECT * FROM warehouse WHERE category_type = @c";
                if (!string.IsNullOrEmpty(search)) sql += " AND name LIKE @s";
                sql += " ORDER BY name";

                using (var cmd = new SQLiteCommand(sql, conn))
                {
                    cmd.Parameters.AddWithValue("@c", _categoryContext);
                    if (!string.IsNullOrEmpty(search)) cmd.Parameters.AddWithValue("@s", "%" + search + "%");

                    using (var reader = cmd.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            list.Add(new Product
                            {
                                Id = Convert.ToInt64(reader["id"]),
                                Name = reader["name"].ToString(),
                                CategoryType = reader["category_type"].ToString(),
                                Stock = Convert.ToInt32(reader["stock"]),
                                BuyPrice = Convert.ToDouble(reader["buy_price"]),
                                SellPrice = Convert.ToDouble(reader["sell_price"]),
                                Status = reader["status"].ToString(),
                                Description = reader["description"].ToString()
                            });
                        }
                    }
                }
            }
            return list;
        }

        public void AddItem(Product p)
        {
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                using (var trans = conn.BeginTransaction())
                {
                    using (var cmd = new SQLiteCommand(conn))
                    {
                        cmd.CommandText = @"INSERT INTO warehouse (name, category_type, stock, buy_price, sell_price, status, description) 
                                          VALUES (@n, @c, @s, @bp, @sp, @st, @d)";
                        cmd.Parameters.AddWithValue("@n", p.Name);
                        cmd.Parameters.AddWithValue("@c", _categoryContext);
                        cmd.Parameters.AddWithValue("@s", p.Stock);
                        cmd.Parameters.AddWithValue("@bp", p.BuyPrice);
                        cmd.Parameters.AddWithValue("@sp", p.SellPrice);
                        cmd.Parameters.AddWithValue("@st", p.Status);
                        cmd.Parameters.AddWithValue("@d", p.Description);
                        cmd.ExecuteNonQuery();
                        
                        long itemId = conn.LastInsertRowId;

                        if (p.Stock > 0)
                        {
                            using (var mutCmd = new SQLiteCommand("INSERT INTO warehouse_mutation (item_id, type, qty, description) VALUES (@id, 'IN', @q, @desc)", conn))
                            {
                                mutCmd.Parameters.AddWithValue("@id", itemId);
                                mutCmd.Parameters.AddWithValue("@q", p.Stock);
                                mutCmd.Parameters.AddWithValue("@desc", "Initial Stock: " + p.Name);
                                mutCmd.ExecuteNonQuery();
                            }
                        }
                    }
                    trans.Commit();
                }
            }
            Logger.Log("INVENTORY", string.Format("Added Item {0}: {1}, Stock: {2}", _categoryContext, p.Name, p.Stock));
        }

        public Dictionary<string, object> SellItem(long itemId, int qty, long? memberId, string paymentMethod)
        {
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                
                Product item = null;
                using (var cmd = new SQLiteCommand("SELECT * FROM warehouse WHERE id=@id", conn))
                {
                    cmd.Parameters.AddWithValue("@id", itemId);
                    using (var r = cmd.ExecuteReader())
                    {
                        if(r.Read()) item = new Product { 
                            Id = Convert.ToInt64(r["id"]), 
                            Stock = Convert.ToInt32(r["stock"]), 
                            SellPrice = Convert.ToDouble(r["sell_price"]),
                            Name = r["name"].ToString()
                        };
                    }
                }

                if (item == null) return new Dictionary<string, object> { { "success", false }, { "message", "Item not found" } };
                if (item.Stock < qty) return new Dictionary<string, object> { { "success", false }, { "message", string.Format("Not enough stock. Available: {0}", item.Stock) } };

                int newStock = item.Stock - qty;
                double total = item.SellPrice * qty;

                using (var trans = conn.BeginTransaction())
                {
                    // Update Stock
                    using (var cmd = new SQLiteCommand("UPDATE warehouse SET stock=@s, updated_at=CURRENT_TIMESTAMP WHERE id=@id", conn))
                    {
                        cmd.Parameters.AddWithValue("@s", newStock);
                        cmd.Parameters.AddWithValue("@id", itemId);
                        cmd.ExecuteNonQuery();
                    }

                    // Mutation OUT
                    using (var cmd = new SQLiteCommand("INSERT INTO warehouse_mutation (item_id, type, qty, description) VALUES (@id, 'OUT', @q, @d)", conn))
                    {
                        cmd.Parameters.AddWithValue("@id", itemId);
                        cmd.Parameters.AddWithValue("@q", qty);
                        cmd.Parameters.AddWithValue("@d", "Sale: " + qty + " unit");
                        cmd.ExecuteNonQuery();
                    }

                    // Transaction
                    using (var cmd = new SQLiteCommand(conn))
                    {
                        cmd.CommandText = @"INSERT INTO transactions (item_id, member_id, qty, unit_price, total_price, category_type, payment_method) 
                                          VALUES (@id, @mid, @q, @up, @tot, @cat, @pm)";
                        cmd.Parameters.AddWithValue("@id", itemId);
                        cmd.Parameters.AddWithValue("@mid", memberId.HasValue ? (object)memberId.Value : DBNull.Value);
                        cmd.Parameters.AddWithValue("@q", qty);
                        cmd.Parameters.AddWithValue("@up", item.SellPrice);
                        cmd.Parameters.AddWithValue("@tot", total);
                        cmd.Parameters.AddWithValue("@cat", _categoryContext);
                        cmd.Parameters.AddWithValue("@pm", paymentMethod);
                        cmd.ExecuteNonQuery();
                    }

                    trans.Commit();
                }

                Logger.Log("TRANSACTION", string.Format("Sold {0} x{1} = {2:N0} ({3})", item.Name, qty, total, paymentMethod));
                return new Dictionary<string, object> { { "success", true }, { "message", "Sale Successful" }, { "total", total } };
            }
        }

        public Dictionary<string, object> ReturBarang(long itemId, int qty, string reason)
        {
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                Product item = null;
                using (var cmd = new SQLiteCommand("SELECT * FROM warehouse WHERE id=@id", conn))
                {
                    cmd.Parameters.AddWithValue("@id", itemId);
                    using (var r = cmd.ExecuteReader())
                    {
                        if(r.Read()) item = new Product { Id = Convert.ToInt64(r["id"]), Stock = Convert.ToInt32(r["stock"]), Name = r["name"].ToString() };
                    }
                }

                if (item == null) return new Dictionary<string, object> { { "success", false }, { "message", "Item not found" } };
                if (item.Stock < qty) return new Dictionary<string, object> { { "success", false }, { "message", "Not enough stock to return" } };

                int newStock = item.Stock - qty;

                using (var trans = conn.BeginTransaction())
                {
                    using (var cmd = new SQLiteCommand("UPDATE warehouse SET stock=@s WHERE id=@id", conn))
                    {
                        cmd.Parameters.AddWithValue("@s", newStock);
                        cmd.Parameters.AddWithValue("@id", itemId);
                        cmd.ExecuteNonQuery();
                    }

                    using (var cmd = new SQLiteCommand("INSERT INTO warehouse_mutation (item_id, type, qty, description) VALUES (@id, 'RETURN', @q, @d)", conn))
                    {
                        cmd.Parameters.AddWithValue("@id", itemId);
                        cmd.Parameters.AddWithValue("@q", qty);
                        cmd.Parameters.AddWithValue("@d", "Return: " + reason);
                        cmd.ExecuteNonQuery();
                    }
                    trans.Commit();
                }

                Logger.Log("INVENTORY", string.Format("Returned {0} x{1}. Reason: {2}", item.Name, qty, reason), "WARNING");
                return new Dictionary<string, object> { { "success", true }, { "message", "Return Recorded" } };
            }
        }
    }
}
