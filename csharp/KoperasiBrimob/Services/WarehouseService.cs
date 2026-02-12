using System;
using System.Collections.Generic;
using System.Data.SQLite;
using KoperasiBrimob.Data;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Models;

namespace KoperasiBrimob.Services
{
    public class WarehouseService
    {
        private string _categoryContext;

        public WarehouseService(string categoryContext)
        {
            _categoryContext = categoryContext;
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
                        cmd.CommandText = "INSERT INTO warehouse (name, category_type, stock, buy_price, sell_price, status, description) VALUES (@n, @c, @s, @bp, @sp, @st, @d)";
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

        public void UpdateItem(Product p)
        {
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                // Get old stock
                int oldStock = 0;
                using (var check = new SQLiteCommand("SELECT stock FROM warehouse WHERE id=@id", conn))
                {
                    check.Parameters.AddWithValue("@id", p.Id);
                    oldStock = Convert.ToInt32(check.ExecuteScalar());
                }

                using (var trans = conn.BeginTransaction())
                {
                    using (var cmd = new SQLiteCommand("UPDATE warehouse SET name=@n, buy_price=@bp, sell_price=@sp, status=@st, description=@d, stock=@s WHERE id=@id", conn))
                    {
                        cmd.Parameters.AddWithValue("@n", p.Name);
                        cmd.Parameters.AddWithValue("@bp", p.BuyPrice);
                        cmd.Parameters.AddWithValue("@sp", p.SellPrice);
                        cmd.Parameters.AddWithValue("@st", p.Status);
                        cmd.Parameters.AddWithValue("@d", p.Description);
                        cmd.Parameters.AddWithValue("@s", p.Stock);
                        cmd.Parameters.AddWithValue("@id", p.Id);
                        cmd.ExecuteNonQuery();
                    }

                    // Mutation if stock changed
                    int diff = p.Stock - oldStock;
                    if (diff != 0)
                    {
                        string type = diff > 0 ? "IN" : "OUT";
                        if (diff < 0) diff = -diff; // Abs
                        
                        using (var mut = new SQLiteCommand("INSERT INTO warehouse_mutation (item_id, type, qty, description) VALUES (@id, @t, @q, 'Manual Adjustment')", conn))
                        {
                            mut.Parameters.AddWithValue("@id", p.Id);
                            mut.Parameters.AddWithValue("@t", type);
                            mut.Parameters.AddWithValue("@q", diff);
                            mut.ExecuteNonQuery();
                        }
                    }
                    trans.Commit();
                }
            }
            Logger.Log("INVENTORY", "Updated Item " + p.Name);
        }

        public void AddStock(long itemId, int qty, string itemName)
        {
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                using (var trans = conn.BeginTransaction())
                {
                    using (var cmd = new SQLiteCommand("UPDATE warehouse SET stock = stock + @q, updated_at=CURRENT_TIMESTAMP WHERE id=@id", conn))
                    {
                        cmd.Parameters.AddWithValue("@q", qty);
                        cmd.Parameters.AddWithValue("@id", itemId);
                        cmd.ExecuteNonQuery();
                    }
                    using (var cmd = new SQLiteCommand("INSERT INTO warehouse_mutation (item_id, type, qty, description) VALUES (@id, 'IN', @q, @d)", conn))
                    {
                        cmd.Parameters.AddWithValue("@id", itemId);
                        cmd.Parameters.AddWithValue("@q", qty);
                        cmd.Parameters.AddWithValue("@d", "Restock: " + qty);
                        cmd.ExecuteNonQuery();
                    }
                    trans.Commit();
                }
            }
            Logger.Log("INVENTORY", string.Format("Added Stock {0}: {1} (+{2})", _categoryContext, itemName, qty));
        }

        public void SellItem(long itemId, int qty, double sellPrice, string paymentMethod)
        {
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                using (var trans = conn.BeginTransaction())
                {
                    using (var cmd = new SQLiteCommand("UPDATE warehouse SET stock = stock - @q WHERE id=@id", conn))
                    {
                        cmd.Parameters.AddWithValue("@q", qty);
                        cmd.Parameters.AddWithValue("@id", itemId);
                        cmd.ExecuteNonQuery();
                    }
                    using (var cmd = new SQLiteCommand("INSERT INTO warehouse_mutation (item_id, type, qty, description) VALUES (@id, 'OUT', @q, 'Sale')", conn))
                    {
                        cmd.Parameters.AddWithValue("@id", itemId);
                        cmd.Parameters.AddWithValue("@q", qty);
                        cmd.ExecuteNonQuery();
                    }
                    using (var cmd = new SQLiteCommand("INSERT INTO transactions (item_id, qty, unit_price, total_price, category_type, payment_method) VALUES (@id, @q, @up, @tot, @cat, @pm)", conn))
                    {
                        cmd.Parameters.AddWithValue("@id", itemId);
                        cmd.Parameters.AddWithValue("@q", qty);
                        cmd.Parameters.AddWithValue("@up", sellPrice);
                        cmd.Parameters.AddWithValue("@tot", sellPrice * qty);
                        cmd.Parameters.AddWithValue("@cat", _categoryContext);
                        cmd.Parameters.AddWithValue("@pm", paymentMethod);
                        cmd.ExecuteNonQuery();
                    }
                    trans.Commit();
                }
            }
            Logger.Log("TRANSACTION", string.Format("Sold Item {0} x{1}", itemId, qty));
        }

        public void ReturnItem(long itemId, int qty, string reason)
        {
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                using (var trans = conn.BeginTransaction())
                {
                    using (var cmd = new SQLiteCommand("UPDATE warehouse SET stock = stock - @q WHERE id=@id", conn))
                    {
                        cmd.Parameters.AddWithValue("@q", qty);
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
            }
            Logger.Log("INVENTORY", string.Format("Returned Item {0} x{1}", itemId, qty));
        }
        public void ImportItems(List<string[]> items)
        {
            int added = 0;
            int updated = 0;

            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                using (var trans = conn.BeginTransaction())
                {
                    foreach (var item in items)
                    {
                        if (item.Length < 2) continue;
                        string name = item[0];
                        int stock = 0;
                        int.TryParse(item[1], out stock);
                        
                        double price = 0; // Optional price
                        if (item.Length > 2) double.TryParse(item[2], out price);

                        // Check existence
                        long existsId = 0;
                        using (var cmd = new SQLiteCommand("SELECT id FROM warehouse WHERE name=@n AND category_type=@c", conn))
                        {
                            cmd.Parameters.AddWithValue("@n", name);
                            cmd.Parameters.AddWithValue("@c", _categoryContext);
                            var res = cmd.ExecuteScalar();
                            if (res != null) existsId = Convert.ToInt64(res);
                        }

                        if (existsId > 0)
                        {
                            // Update Stock
                            using (var cmd = new SQLiteCommand("UPDATE warehouse SET stock = stock + @s WHERE id=@id", conn))
                            {
                                cmd.Parameters.AddWithValue("@s", stock);
                                cmd.Parameters.AddWithValue("@id", existsId);
                                cmd.ExecuteNonQuery();
                            }
                            // Log Mutation
                            using (var cmd = new SQLiteCommand("INSERT INTO warehouse_mutation (item_id, type, qty, description) VALUES (@id, 'IN', @q, 'Import CSV')", conn))
                            {
                                cmd.Parameters.AddWithValue("@id", existsId);
                                cmd.Parameters.AddWithValue("@q", stock);
                                cmd.ExecuteNonQuery();
                            }
                            updated++;
                        }
                        else
                        {
                            // Add New
                            using (var cmd = new SQLiteCommand("INSERT INTO warehouse (name, category_type, stock, buy_price, sell_price, status, description) VALUES (@n, @c, @s, @p, @p, 'Koperasi', 'Imported')", conn))
                            {
                                cmd.Parameters.AddWithValue("@n", name);
                                cmd.Parameters.AddWithValue("@c", _categoryContext);
                                cmd.Parameters.AddWithValue("@s", stock);
                                cmd.Parameters.AddWithValue("@p", price);
                                cmd.ExecuteNonQuery();
                                
                                long newId = conn.LastInsertRowId;
                                
                                // Log Mutation
                                using (var mut = new SQLiteCommand("INSERT INTO warehouse_mutation (item_id, type, qty, description) VALUES (@id, 'IN', @q, 'Initial Import')", conn))
                                {
                                    mut.Parameters.AddWithValue("@id", newId);
                                    mut.Parameters.AddWithValue("@q", stock);
                                    mut.ExecuteNonQuery();
                                }
                            }
                            added++;
                        }
                    }
                    trans.Commit();
                }
            }
            Logger.Log("IMPORT", string.Format("Imported {0}: {1} Added, {2} Updated", _categoryContext, added, updated));
            System.Windows.Forms.MessageBox.Show(string.Format("Import Success!\nAdded: {0}\nUpdated: {1}", added, updated));
        }
    }
}
