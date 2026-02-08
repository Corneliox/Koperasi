using System;
using System.Data.SQLite;
using KoperasiBrimob.Helpers;

namespace KoperasiBrimob.Services
{
    public class AuthService
    {
        public bool Login(string username, string password)
        {
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                using (var cmd = conn.CreateCommand())
                {
                    cmd.CommandText = "SELECT COUNT(*) FROM users WHERE username = @u AND password = @p";
                    cmd.Parameters.AddWithValue("@u", username);
                    cmd.Parameters.AddWithValue("@p", password); // Plaintext as per legacy code
                    long count = (long)cmd.ExecuteScalar();
                    if (count > 0)
                    {
                        Logger.CurrentUser = username;
                        Logger.Log("SYSTEM", "User Login Success");
                        return true;
                    }
                }
            }
            Logger.Log("SECURITY", "Failed Login Attempt: " + username);
            return false;
        }
    }
}
