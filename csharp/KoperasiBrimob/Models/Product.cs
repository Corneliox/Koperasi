using System;

namespace KoperasiBrimob.Models
{
    public class Product
    {
        public long Id { get; set; }
        public string Name { get; set; }
        public string CategoryType { get; set; }
        public int Stock { get; set; }
        public double BuyPrice { get; set; }
        public double SellPrice { get; set; }
        public string Status { get; set; } // Koperasi / Konsinyasi
        public string Description { get; set; }
        public DateTime UpdatedAt { get; set; }
    }
}
