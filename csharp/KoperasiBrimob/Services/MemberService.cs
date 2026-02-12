using System;
using System.Collections.Generic;
using System.Data.SQLite;
using KoperasiBrimob.Data;
using KoperasiBrimob.Infrastructure;
using KoperasiBrimob.Models;

namespace KoperasiBrimob.Services
{
    public class MemberService
    {
        public List<Member> GetAllMembers(string search = null)
        {
            var list = new List<Member>();
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                string sql = "SELECT * FROM members";
                if (!string.IsNullOrEmpty(search))
                    sql += " WHERE name LIKE @s OR nrp LIKE @s";
                
                using (var cmd = new SQLiteCommand(sql, conn))
                {
                    if (!string.IsNullOrEmpty(search)) cmd.Parameters.AddWithValue("@s", "%" + search + "%");
                    using (var r = cmd.ExecuteReader())
                    {
                        while (r.Read())
                        {
                            list.Add(new Member
                            {
                                Id = Convert.ToInt64(r["id"]),
                                Name = r["name"].ToString(),
                                Nrp = r["nrp"].ToString(),
                                Rank = r["rank"].ToString(),
                                Unit = r["unit"].ToString(),
                                Phone = r["phone"].ToString(),
                                Address = r["address"].ToString()
                            });
                        }
                    }
                }
            }
            return list;
        }

        public List<string> FindDuplicates(string name, double threshold = 0.8)
        {
            var all = GetAllMembers();
            var duplicates = new List<string>();
            foreach (var m in all)
            {
                double score = Levenshtein.Similarity(name, m.Name);
                if (score >= threshold)
                {
                    duplicates.Add(string.Format("{0} ({1}) - {2:P0} Match", m.Name, m.Nrp, score));
                }
            }
            return duplicates;
        }

        public void AddMember(Member m)
        {
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                using (var cmd = new SQLiteCommand("INSERT INTO members (name, nrp, rank, unit, phone, address) VALUES (@n, @nrp, @r, @u, @p, @a)", conn))
                {
                    cmd.Parameters.AddWithValue("@n", m.Name);
                    cmd.Parameters.AddWithValue("@nrp", m.Nrp);
                    cmd.Parameters.AddWithValue("@r", m.Rank);
                    cmd.Parameters.AddWithValue("@u", m.Unit);
                    cmd.Parameters.AddWithValue("@p", m.Phone);
                    cmd.Parameters.AddWithValue("@a", m.Address);
                    cmd.ExecuteNonQuery();
                }
            }
            Logger.Log("MEMBER", "Added " + m.Name);
        }

        public void DeleteMember(long id)
        {
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                using (var cmd = new SQLiteCommand("DELETE FROM members WHERE id=@id", conn))
                {
                    cmd.Parameters.AddWithValue("@id", id);
                    cmd.ExecuteNonQuery();
                }
            }
            Logger.Log("MEMBER", "Deleted Member ID " + id);
        }
    }
}
