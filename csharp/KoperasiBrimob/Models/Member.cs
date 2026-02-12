using System;

namespace KoperasiBrimob.Models
{
    public class Member
    {
        public long Id { get; set; }
        public string Name { get; set; }
        public string Rank { get; set; }
        public string Unit { get; set; }
        public string Nrp { get; set; }
        public string Phone { get; set; }
        public string Address { get; set; }
        public DateTime CreatedAt { get; set; }
    }
}