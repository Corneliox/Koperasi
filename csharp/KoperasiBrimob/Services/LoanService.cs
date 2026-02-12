using System;
using System.Collections.Generic;
using System.Data.SQLite;
using KoperasiBrimob.Data;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Models;

namespace KoperasiBrimob.Services
{
    public class LoanService
    {
        public Dictionary<string, object> Simulate(double amount, double rate, int months)
        {
            double interest = amount * (rate / 100.0);
            double total = amount + interest;
            double monthly = total / months;

            var schedule = new List<string>();
            double remaining = total;
            for (int i = 1; i <= months; i++)
            {
                remaining -= monthly;
                if (remaining < 0) remaining = 0;
                schedule.Add(string.Format("Month {0}: Pay {1:N0}, Remaining {2:N0}", i, monthly, remaining));
            }

            var result = new Dictionary<string, object>();
            result["Total"] = total;
            result["Monthly"] = monthly;
            result["Schedule"] = schedule;
            return result;
        }

        public List<Loan> GetAllLoans(string statusFilter = null)
        {
            var loans = new List<Loan>();
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                string sql = "SELECT l.*, m.name as member_name, m.nrp as member_nrp FROM loans l JOIN members m ON l.member_id = m.id";
                
                if (!string.IsNullOrEmpty(statusFilter) && statusFilter != "All")
                {
                    sql += " WHERE l.status = @s";
                }
                
                sql += " ORDER BY l.created_at DESC";

                using (var cmd = new SQLiteCommand(sql, conn))
                {
                    if (!string.IsNullOrEmpty(statusFilter) && statusFilter != "All")
                        cmd.Parameters.AddWithValue("@s", statusFilter);

                    using (var reader = cmd.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            loans.Add(new Loan
                            {
                                Id = Convert.ToInt64(reader["id"]),
                                MemberId = Convert.ToInt64(reader["member_id"]),
                                MemberName = reader["member_name"].ToString(),
                                MemberNrp = reader["member_nrp"].ToString(),
                                Principal = Convert.ToDouble(reader["principal"]),
                                TotalAmount = Convert.ToDouble(reader["total_amount"]),
                                PaidAmount = Convert.ToDouble(reader["paid_amount"]),
                                Status = reader["status"].ToString(),
                                DueDate = Convert.ToDateTime(reader["due_date"]),
                                CreatedAt = Convert.ToDateTime(reader["created_at"])
                            });
                        }
                    }
                }
            }
            return loans;
        }

        public Dictionary<string, object> CreateLoan(long memberId, double amount, double rate, int duration, string notes)
        {
            var sim = Simulate(amount, rate, duration);
            double total = (double)sim["Total"];
            double monthly = (double)sim["Monthly"];

            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                using (var cmd = new SQLiteCommand("INSERT INTO loans (member_id, principal, interest_rate, duration_months, total_amount, monthly_payment, due_date, notes, paid_amount, status) VALUES (@mid, @p, @ir, @dm, @tot, @mp, @dd, @n, 0, 'Aktif')", conn))
                {
                    cmd.Parameters.AddWithValue("@mid", memberId);
                    cmd.Parameters.AddWithValue("@p", amount);
                    cmd.Parameters.AddWithValue("@ir", rate);
                    cmd.Parameters.AddWithValue("@dm", duration);
                    cmd.Parameters.AddWithValue("@tot", total);
                    cmd.Parameters.AddWithValue("@mp", monthly);
                    cmd.Parameters.AddWithValue("@dd", DateTime.Now.AddMonths(duration));
                    cmd.Parameters.AddWithValue("@n", notes);
                    cmd.ExecuteNonQuery();
                }
            }
            Logger.Log("LOAN", string.Format("Created Loan: {0:N0}", total));
            var res = new Dictionary<string, object>();
            res["success"] = true;
            res["message"] = "Loan Created";
            return res;
        }

        public Dictionary<string, object> RecordPayment(long loanId, double amount, string method, string notes)
        {
             using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                // Check Status
                string status = "Aktif";
                using (var cmd = new SQLiteCommand("SELECT total_amount, paid_amount FROM loans WHERE id=@id", conn))
                {
                    cmd.Parameters.AddWithValue("@id", loanId);
                    using (var r = cmd.ExecuteReader())
                    {
                        if(r.Read())
                        {
                            double total = Convert.ToDouble(r["total_amount"]);
                            double paid = Convert.ToDouble(r["paid_amount"]);
                            if (paid + amount >= total) status = "Lunas";
                        }
                    }
                }

                // Update Loan
                using (var cmd = new SQLiteCommand("UPDATE loans SET paid_amount = paid_amount + @a, status = @s WHERE id=@id", conn))
                {
                    cmd.Parameters.AddWithValue("@a", amount);
                    cmd.Parameters.AddWithValue("@s", status);
                    cmd.Parameters.AddWithValue("@id", loanId);
                    cmd.ExecuteNonQuery();
                }
                // Record Payment
                using (var cmd = new SQLiteCommand("INSERT INTO loan_payments (loan_id, amount, payment_method, notes) VALUES (@lid, @a, @pm, @n)", conn))
                {
                    cmd.Parameters.AddWithValue("@lid", loanId);
                    cmd.Parameters.AddWithValue("@a", amount);
                    cmd.Parameters.AddWithValue("@pm", method);
                    cmd.Parameters.AddWithValue("@n", notes);
                    cmd.ExecuteNonQuery();
                }
            }
            Logger.Log("LOAN", string.Format("Payment ID {0}: {1:N0}", loanId, amount));
            var res = new Dictionary<string, object>();
            res["success"] = true;
            res["message"] = "Payment Recorded";
            return res;
        }

        public void MarkBadDebt(long loanId)
        {
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                using (var cmd = new SQLiteCommand("UPDATE loans SET status = 'Macet' WHERE id=@id", conn))
                {
                    cmd.Parameters.AddWithValue("@id", loanId);
                    cmd.ExecuteNonQuery();
                }
            }
            Logger.Log("LOAN", "Marked Loan " + loanId + " as Bad Debt", "WARNING");
        }
    }
}