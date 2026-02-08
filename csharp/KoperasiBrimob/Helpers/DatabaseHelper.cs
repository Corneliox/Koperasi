using System;
using System.Data.SQLite;
using System.IO;
using System.Data;

namespace KoperasiBrimob.Helpers
{
    public static class DatabaseHelper
    {
        private static string DbPath = "koperasi_brimob.db";
        public static string ConnectionString { get { return "Data Source=" + DbPath + ";Version=3;Foreign Keys=True;"; } }

        public static void InitializeDatabase()
        {
            if (!File.Exists(DbPath))
            {
                SQLiteConnection.CreateFile(DbPath);
            }

            using (var conn = new SQLiteConnection(ConnectionString))
            {
                conn.Open();
                using (var cmd = conn.CreateCommand())
                {
                    // Users
                    cmd.CommandText = @"
                        CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            role TEXT DEFAULT 'admin',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );";
                    cmd.ExecuteNonQuery();

                    // Warehouse
                    cmd.CommandText = @"
                        CREATE TABLE IF NOT EXISTS warehouse (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            category_type TEXT NOT NULL CHECK(category_type IN ('SEMBAKO', 'TAKTIKAL')),
                            stock INTEGER DEFAULT 0,
                            buy_price REAL DEFAULT 0,
                            sell_price REAL DEFAULT 0,
                            status TEXT DEFAULT 'Koperasi' CHECK(status IN ('Koperasi', 'Konsinyasi')),
                            description TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );";
                    cmd.ExecuteNonQuery();

                    // Mutation
                    cmd.CommandText = @"
                        CREATE TABLE IF NOT EXISTS warehouse_mutation (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            item_id INTEGER NOT NULL,
                            type TEXT NOT NULL CHECK(type IN ('IN', 'OUT', 'RETURN', 'CORRECTION')),
                            qty INTEGER NOT NULL,
                            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            description TEXT,
                            FOREIGN KEY (item_id) REFERENCES warehouse(id) ON DELETE CASCADE
                        );";
                    cmd.ExecuteNonQuery();

                    // Members
                    cmd.CommandText = @"
                        CREATE TABLE IF NOT EXISTS members (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            rank TEXT,
                            unit TEXT,
                            nrp TEXT UNIQUE,
                            phone TEXT,
                            address TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );";
                    cmd.ExecuteNonQuery();

                    // Transactions
                    cmd.CommandText = @"
                        CREATE TABLE IF NOT EXISTS transactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            item_id INTEGER NOT NULL,
                            member_id INTEGER,
                            qty INTEGER NOT NULL,
                            unit_price REAL NOT NULL,
                            total_price REAL NOT NULL,
                            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            category_type TEXT NOT NULL,
                            payment_method TEXT DEFAULT 'Tunai',
                            FOREIGN KEY (item_id) REFERENCES warehouse(id) ON DELETE SET NULL,
                            FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE SET NULL
                        );";
                    cmd.ExecuteNonQuery();

                    // Loans
                    cmd.CommandText = @"
                        CREATE TABLE IF NOT EXISTS loans (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            member_id INTEGER NOT NULL,
                            principal REAL NOT NULL,
                            interest_rate REAL DEFAULT 0,
                            duration_months INTEGER DEFAULT 12,
                            total_amount REAL NOT NULL,
                            monthly_payment REAL DEFAULT 0,
                            paid_amount REAL DEFAULT 0,
                            status TEXT DEFAULT 'Aktif' CHECK(status IN ('Aktif', 'Lunas', 'Macet')),
                            due_date DATE,
                            notes TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
                        );";
                    cmd.ExecuteNonQuery();

                    // Loan Payments
                    cmd.CommandText = @"
                        CREATE TABLE IF NOT EXISTS loan_payments (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            loan_id INTEGER NOT NULL,
                            amount REAL NOT NULL,
                            payment_method TEXT DEFAULT 'Tunai',
                            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            notes TEXT,
                            FOREIGN KEY (loan_id) REFERENCES loans(id) ON DELETE CASCADE
                        );";
                    cmd.ExecuteNonQuery();

                    // Audit Logs
                    cmd.CommandText = @"
                        CREATE TABLE IF NOT EXISTS activity_logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user TEXT,
                            action_type TEXT NOT NULL,
                            details TEXT,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );";
                    cmd.ExecuteNonQuery();

                    // Default Admin
                    cmd.CommandText = "SELECT COUNT(*) FROM users WHERE username = 'admin'";
                    long count = (long)cmd.ExecuteScalar();
                    if (count == 0)
                    {
                        cmd.CommandText = "INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')";
                        cmd.ExecuteNonQuery();
                    }
                }
            }
        }
    }
}
