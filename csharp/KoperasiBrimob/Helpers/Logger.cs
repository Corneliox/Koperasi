using System;
using System.Data.SQLite;

namespace KoperasiBrimob.Helpers
{
    public static class Logger
    {
        public static string CurrentUser = "admin";

        public static void Log(string actionType, string details, string user = null)
        {
            try
            {
                using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
                {
                    conn.Open();
                    using (var cmd = conn.CreateCommand())
                    {
                        cmd.CommandText = "INSERT INTO activity_logs (user, action_type, details) VALUES (@u, @a, @d)";
                        cmd.Parameters.AddWithValue("@u", user ?? CurrentUser);
                        cmd.Parameters.AddWithValue("@a", actionType);
                        cmd.Parameters.AddWithValue("@d", details);
                        cmd.ExecuteNonQuery();
                    }
                }
            }
            catch (Exception)
            {
                // Fail silently for logs to avoid crashing app
            }
        }
    }
}
