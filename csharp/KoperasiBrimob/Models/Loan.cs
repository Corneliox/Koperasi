using System;

namespace KoperasiBrimob.Models
{
    public class Loan
    {
        public long Id { get; set; }
        public long MemberId { get; set; }
        public string MemberName { get; set; } // Joined
        public string MemberNrp { get; set; }  // Joined
        public double Principal { get; set; }
        public double InterestRate { get; set; }
        public int DurationMonths { get; set; }
        public double TotalAmount { get; set; }
        public double MonthlyPayment { get; set; }
        public double PaidAmount { get; set; }
        public string Status { get; set; }
        public DateTime DueDate { get; set; }
        public string Notes { get; set; }
        public DateTime CreatedAt { get; set; }
    }

    public class LoanPayment
    {
        public long Id { get; set; }
        public long LoanId { get; set; }
        public double Amount { get; set; }
        public string PaymentMethod { get; set; }
        public DateTime PaymentDate { get; set; }
        public string Notes { get; set; }
    }
}
