using System.Drawing;

namespace KoperasiBrimob.Infrastructure
{
    public static class ThemeColor
    {
        // CustomTkinter Dark Theme Palette
        public static readonly Color Background = Color.FromArgb(26, 26, 46);      // #1a1a2e
        public static readonly Color Surface = Color.FromArgb(22, 33, 62);         // #16213e
        public static readonly Color Primary = Color.FromArgb(15, 52, 96);         // #0f3460
        public static readonly Color Accent = Color.FromArgb(233, 69, 96);         // #e94560
        public static readonly Color Text = Color.FromArgb(240, 240, 240);       // #f0f0f0
        public static readonly Color TextDim = Color.FromArgb(160, 160, 160);      // #a0a0a0
        public static readonly Color Danger = Color.FromArgb(180, 40, 40);         // Red
        public static readonly Color Success = Color.FromArgb(40, 160, 80);        // Green
        public static readonly Color Warning = Color.FromArgb(255, 165, 0);        // Orange
        
        public static Font PrimaryFont = new Font("Segoe UI", 10F, FontStyle.Regular);
        public static Font HeaderFont = new Font("Segoe UI", 14F, FontStyle.Bold);
        public static Font SmallFont = new Font("Segoe UI", 8.5F, FontStyle.Regular);
    }
}
