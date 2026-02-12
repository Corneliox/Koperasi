using System;
using System.Runtime.InteropServices;

namespace KoperasiBrimob.Infrastructure
{
    public static class DpiAwareness
    {
        [DllImport("user32.dll")]
        private static extern bool SetProcessDPIAware();

        public static void Enable()
        {
            try
            {
                if (Environment.OSVersion.Version.Major >= 6)
                {
                    SetProcessDPIAware();
                }
            }
            catch 
            {
                // Fallback or ignore on very old systems
            }
        }
    }
}
