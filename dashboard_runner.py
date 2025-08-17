"""
Dashboard Runner Script
Sets up local HTTP server to run your ARR dashboard

Usage:
python dashboard_runner.py

This creates a local web server that serves your HTML dashboard
and allows it to read your CSV files properly.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def setup_dashboard():
    """
    Set up and run the ARR dashboard locally
    """
    print("🚀 Setting up Professional ARR Dashboard")
    print("=" * 50)
    
    # Check if required files exist
    required_files = [
        'cleaned_arr_data/arr_monthly_summary.csv',
        'cleaned_arr_data/arr_rollforward.csv', 
        'cleaned_arr_data/subscriptions_clean.csv'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("❌ Missing required data files:")
        for file in missing_files:
            print(f"   • {file}")
        print("\n💡 Please run the data engineering script first:")
        print("   python saas_data_engineering.py")
        return False
    
    print("✅ All data files found")
    
    # Check if HTML dashboard exists
    if not os.path.exists('arr_dashboard.html'):
        print("❌ Dashboard HTML file not found")
        print("💡 Please save the HTML code as 'arr_dashboard.html'")
        return False
    
    print("✅ Dashboard HTML file found")
    return True

def start_server(port=8000):
    """
    Start local HTTP server
    """
    try:
        # Change to current directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Create HTTP server with CORS headers
        class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            def end_headers(self):
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                super().end_headers()
        
        with socketserver.TCPServer(("", port), CORSHTTPRequestHandler) as httpd:
            print(f"🌐 Starting server at http://localhost:{port}")
            print(f"📊 Dashboard URL: http://localhost:{port}/arr_dashboard.html")
            print("\n🎯 Dashboard Features:")
            print("   • Interactive KPI cards with drill-down")
            print("   • Professional ARR waterfall chart")
            print("   • Real-time data from your CSV files")
            print("   • Customer segmentation analysis")
            print("   • Monthly performance trends")
            print("   • Export and sharing capabilities")
            
            print(f"\n🔗 Opening dashboard in browser...")
            
            # Open browser automatically
            webbrowser.open(f'http://localhost:{port}/arr_dashboard.html')
            
            print(f"\n⚡ Server running... Press Ctrl+C to stop")
            print(f"📁 Serving files from: {os.getcwd()}")
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print(f"\n🛑 Server stopped")
                
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {port} is already in use")
            print(f"💡 Try a different port: python dashboard_runner.py --port 8001")
        else:
            print(f"❌ Server error: {e}")

def main():
    """
    Main function
    """
    # Check for port argument
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number, using default 8000")
    
    # Setup validation
    if not setup_dashboard():
        print("\n🚨 Setup failed. Please fix the issues above and try again.")
        return
    
    # Start server
    start_server(port)

if __name__ == "__main__":
    main()

# Alternative: Simple one-liner server
"""
If the above script doesn't work, use this simple approach:

1. Open Terminal
2. Navigate to your project folder:
   cd /path/to/your/project

3. Start simple HTTP server:
   python3 -m http.server 8000

4. Open browser:
   http://localhost:8000/arr_dashboard.html

5. Your dashboard will load with real data!
"""
