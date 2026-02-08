using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SQLite;
using KoperasiBrimob.Helpers;
using KoperasiBrimob.Models;

namespace KoperasiBrimob.Services
{
    public class LoanService
    {
        public Dictionary<string, object> SimulateLoan(double amount, double interestRate, int durationMonths)
        {
            if (amount <= 0 || durationMonths <= 0)
                return new Dictionary<string, object> { { "success", false }, { "message", "Invalid input" } };

            double interestAmount = amount * (interestRate / 100.0);
            double totalAmount = amount + interestAmount;
            double monthlyPayment = totalAmount / durationMonths;

            var breakdown = new List<Dictionary<string, object>>();
            double remaining = totalAmount;

            for (int i = 1; i <= durationMonths; i++)
            {
                remaining -= monthlyPayment;
                if (remaining < 0) remaining = 0;
                breakdown.Add(new Dictionary<string, object>
                {
                    { "month", i },
                    { "payment", monthlyPayment },
                    { "remaining", remaining },
                    { "progress", ((double)i / durationMonths) * 100 }
                });
            }

            return new Dictionary<string, object>
            {
                { "success", true },
                { "principal", amount },
                { "interest_rate", interestRate },
                { "interest_amount", interestAmount },
                { "total_amount", totalAmount },
                { "duration_months", durationMonths },
                { "monthly_payment", monthlyPayment },
                { "breakdown", breakdown }
            };
        }

        public List<Loan> GetAllLoans(string statusFilter = null)
        {
            var loans = new List<Loan>();
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                string sql = @"SELECT l.*, m.name as member_name, m.nrp as member_nrp 
                               FROM loans l 
                               JOIN members m ON l.member_id = m.id";
                
                if (!string.IsNullOrEmpty(statusFilter))
                    sql += " WHERE l.status = @s";
                
                sql += " ORDER BY l.created_at DESC";

                using (var cmd = new SQLiteCommand(sql, conn))
                {
                    if (!string.IsNullOrEmpty(statusFilter))
                        cmd.Parameters.AddWithValue("@s", statusFilter);

                    using (var reader = cmd.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            loans.Add(MapLoan(reader));
                        }
                    }
                }
            }
            return loans;
        }

        public Dictionary<string, object> CreateLoan(long memberId, double amount, double interestRate, int duration, string notes)
        {
            var sim = SimulateLoan(amount, interestRate, duration);
            if (!(bool)sim["success"]) return sim;

            double totalAmount = (double)sim["total_amount"];
            double monthlyPayment = (double)sim["monthly_payment"];
            DateTime dueDate = DateTime.Now.AddDays(duration * 30);

            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                
                // Get Member Name
                string memberName = "";
                using (var cmdCheck = new SQLiteCommand("SELECT name FROM members WHERE id=@id", conn))
                {
                    cmdCheck.Parameters.AddWithValue("@id", memberId);
                    var res = cmdCheck.ExecuteScalar();
                    if (res == null) return new Dictionary<string, object> { { "success", false }, { "message", "Member not found" } };
                    memberName = res.ToString();
                }

                using (var cmd = new SQLiteCommand(conn))
                {
                    cmd.CommandText = @"INSERT INTO loans 
                        (member_id, principal, interest_rate, duration_months, total_amount, monthly_payment, due_date, notes, paid_amount, status)
                        VALUES (@mid, @p, @ir, @dm, @tot, @mp, @dd, @n, 0, 'Aktif')";
                    
                    cmd.Parameters.AddWithValue("@mid", memberId);
                    cmd.Parameters.AddWithValue("@p", amount);
                    cmd.Parameters.AddWithValue("@ir", interestRate);
                    cmd.Parameters.AddWithValue("@dm", duration);
                    cmd.Parameters.AddWithValue("@tot", totalAmount);
                    cmd.Parameters.AddWithValue("@mp", monthlyPayment);
                    cmd.Parameters.AddWithValue("@dd", dueDate);
                    cmd.Parameters.AddWithValue("@n", notes);
                    
                    cmd.ExecuteNonQuery();
                    long loanId = conn.LastInsertRowId;

                    Logger.Log("LOAN", string.Format("Created Loan for {0}: {1:N0} (Total: {2:N0})", memberName, amount, totalAmount));
                    
                    return new Dictionary<string, object>
                    {
                        { "success", true },
                        { "message", string.Format("Loan Created!\nTotal: {0:N0}\nMonthly: {1:N0}", totalAmount, monthlyPayment) },
                        { "loan_id", loanId }
                    };
                }
            }
        }

        public Dictionary<string, object> RecordPayment(long loanId, double amount, string method, string notes)
        {
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                
                // Get Loan
                Loan loan = null;
                using (var cmd = new SQLiteCommand("SELECT * FROM loans WHERE id=@id", conn))
                {
                    cmd.Parameters.AddWithValue("@id", loanId);
                    using (var reader = cmd.ExecuteReader())
                    {
                        if (reader.Read())
                        {
                            loan = new Loan
                            {
                                Id = Convert.ToInt64(reader["id"]),
                                TotalAmount = Convert.ToDouble(reader["total_amount"]),
                                PaidAmount = Convert.ToDouble(reader["paid_amount"]),
                                Status = reader["status"].ToString()
                            };
                        }
                    }
                }

                if (loan == null) return new Dictionary<string, object> { { "success", false }, { "message", "Loan not found" } };
                if (loan.Status == "Lunas") return new Dictionary<string, object> { { "success", false }, { "message", "Already Paid Off" } };

                double remaining = loan.TotalAmount - loan.PaidAmount;
                if (amount > remaining) return new Dictionary<string, object> { { "success", false }, { "message", string.Format("Amount exceeds remaining debt ({0:N0})", remaining) } };

                double newPaid = loan.PaidAmount + amount;
                string newStatus = (newPaid >= loan.TotalAmount) ? "Lunas" : "Aktif";

                using (var trans = conn.BeginTransaction())
                {
                    // Update Loan
                    using (var cmd = new SQLiteCommand("UPDATE loans SET paid_amount=@p, status=@s WHERE id=@id", conn))
                    {
                        cmd.Parameters.AddWithValue("@p", newPaid);
                        cmd.Parameters.AddWithValue("@s", newStatus);
                        cmd.Parameters.AddWithValue("@id", loanId);
                        cmd.ExecuteNonQuery();
                    }

                    // Record Payment
                    using (var cmd = new SQLiteCommand("INSERT INTO loan_payments (loan_id, amount, payment_method, notes) VALUES (@lid, @amt, @pm, @n)", conn))
                    {
                        cmd.Parameters.AddWithValue("@lid", loanId);
                        cmd.Parameters.AddWithValue("@amt", amount);
                        cmd.Parameters.AddWithValue("@pm", method);
                        cmd.Parameters.AddWithValue("@n", notes);
                        cmd.ExecuteNonQuery();
                    }

                    trans.Commit();
                }

                Logger.Log("LOAN", string.Format("Payment ID {0}: {1:N0} ({2})", loanId, amount, method));
                return new Dictionary<string, object> { { "success", true }, { "message", "Payment Recorded" } };
            }
        }

        private Loan MapLoan(SQLiteDataReader reader)
        {
            return new Loan
            {
                Id = Convert.ToInt64(reader["id"]),
                MemberId = Convert.ToInt64(reader["member_id"]),
                MemberName = reader["member_name"].ToString(),
                MemberNrp = reader["member_nrp"].ToString(),
                Principal = Convert.ToDouble(reader["principal"]),
                InterestRate = Convert.ToDouble(reader["interest_rate"]),
                DurationMonths = Convert.ToInt32(reader["duration_months"]),
                TotalAmount = Convert.ToDouble(reader["total_amount"]),
                MonthlyPayment = Convert.ToDouble(reader["monthly_payment"]),
                PaidAmount = Convert.ToDouble(reader["paid_amount"]),
                Status = reader["status"].ToString(),
                DueDate = Convert.ToDateTime(reader["due_date"]),
                CreatedAt = Convert.ToDateTime(reader["created_at"])
            };
        }
    }
}
