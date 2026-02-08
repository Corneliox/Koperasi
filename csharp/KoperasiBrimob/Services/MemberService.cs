using System;
using System.Collections.Generic;
using System.Data.SQLite;
using KoperasiBrimob.Helpers;
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
                    sql += " WHERE name LIKE @s OR nrp LIKE @s OR unit LIKE @s";
                sql += " ORDER BY name";

                using (var cmd = new SQLiteCommand(sql, conn))
                {
                    if (!string.IsNullOrEmpty(search))
                        cmd.Parameters.AddWithValue("@s", "%" + search + "%");

                    using (var reader = cmd.ExecuteReader())
                    {
                        while (reader.Read()) list.Add(MapMember(reader));
                    }
                }
            }
            return list;
        }

        public List<Dictionary<string, object>> FindSimilarMembers(string name, double threshold = 0.8)
        {
            var all = GetAllMembers();
            var similar = new List<Dictionary<string, object>>();

            foreach (var m in all)
            {
                double score = Levenshtein.Similarity(name, m.Name);
                if (score >= threshold)
                {
                    similar.Add(new Dictionary<string, object>
                    {
                        { "member", m },
                        { "score", score },
                        { "similarity", (score * 100).ToString("N0") + "%" }
                    });
                }
            }
            similar.Sort((a, b) => ((double)b["score"]).CompareTo((double)a["score"]));
            return similar;
        }

        public Dictionary<string, object> AddMember(Member m)
        {
            var check = CheckDuplicate(m.Name, m.Nrp);
            if ((bool)check["has_duplicate"] && !string.IsNullOrEmpty(m.Nrp))
            {
                 // Strictly block if NRP matches
                 if (check.ContainsKey("exact_match") && check["exact_match"] != null)
                    return new Dictionary<string, object> { { "success", false }, { "message", "NRP already exists" } };
            }

            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                using (var cmd = new SQLiteCommand("INSERT INTO members (name, rank, unit, nrp, phone, address) VALUES (@n, @r, @u, @nrp, @p, @a)", conn))
                {
                    cmd.Parameters.AddWithValue("@n", m.Name);
                    cmd.Parameters.AddWithValue("@r", m.Rank);
                    cmd.Parameters.AddWithValue("@u", m.Unit);
                    cmd.Parameters.AddWithValue("@nrp", m.Nrp);
                    cmd.Parameters.AddWithValue("@p", m.Phone);
                    cmd.Parameters.AddWithValue("@a", m.Address);
                    cmd.ExecuteNonQuery();
                }
            }
            Logger.Log("MEMBER", "Added Member: " + m.Name + " (" + m.Nrp + ")");
            return new Dictionary<string, object> { { "success", true }, { "message", "Member Added" } };
        }

        public Dictionary<string, object> CheckDuplicate(string name, string nrp)
        {
            var result = new Dictionary<string, object> { { "has_duplicate", false }, { "exact_match", null }, { "similar_matches", null } };
            
            using (var conn = new SQLiteConnection(DatabaseHelper.ConnectionString))
            {
                conn.Open();
                if (!string.IsNullOrEmpty(nrp))
                {
                    using (var cmd = new SQLiteCommand("SELECT * FROM members WHERE nrp=@nrp", conn))
                    {
                        cmd.Parameters.AddWithValue("@nrp", nrp);
                        using (var reader = cmd.ExecuteReader())
                        {
                            if (reader.Read())
                            {
                                result["has_duplicate"] = true;
                                result["exact_match"] = MapMember(reader);
                                return result;
                            }
                        }
                    }
                }
            }
            
            var similar = FindSimilarMembers(name);
            if (similar.Count > 0)
            {
                result["has_duplicate"] = true;
                result["similar_matches"] = similar;
            }

            return result;
        }

        private Member MapMember(SQLiteDataReader reader)
        {
            return new Member
            {
                Id = Convert.ToInt64(reader["id"]),
                Name = reader["name"].ToString(),
                Rank = reader["rank"].ToString(),
                Unit = reader["unit"].ToString(),
                Nrp = reader["nrp"].ToString(),
                Phone = reader["phone"].ToString(),
                Address = reader["address"].ToString(),
                CreatedAt = Convert.ToDateTime(reader["created_at"])
            };
        }
    }
}
