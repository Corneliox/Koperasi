using System;

namespace KoperasiBrimob.Models
{
    public class Transaction
    {
        public long Id { get; set; }
        public long ItemId { get; set; }
        public string ItemName { get; set; } // Joined
        public long? MemberId { get; set; }
        public int Qty { get; set; }
        public double UnitPrice { get; set; }
        public double TotalPrice { get; set; }
        public DateTime Date { get; set; }
        public string CategoryType { get; set; }
        public string PaymentMethod { get; set; }
    }
}
