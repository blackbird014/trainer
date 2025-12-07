#!/usr/bin/env python3
"""
Simple web server to display HTML stored in MongoDB.
Retrieves HTML from data-store and serves it via a web browser.
"""

import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
import threading
import time

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from data_store import create_store
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure data-store is installed:")
    print("  pip install -e ../data-store")
    sys.exit(1)


class HTMLViewerHandler(BaseHTTPRequestHandler):
    """HTTP handler that serves HTML from MongoDB."""
    
    store = None  # Will be set before creating server
    
    def do_GET(self):
        """Handle GET requests."""
        if not self.store:
            self.send_error(500, "Store not initialized")
            return
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/' or self.path == '/index.html':
            # List all HTML documents
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Query for formatted outputs
            result = self.store.query({'source': 'format_converter'})
            
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>HTML Documents from MongoDB</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
                    h1 { color: #333; }
                    .doc-list { list-style: none; padding: 0; }
                    .doc-item { background: #f9f9f9; margin: 10px 0; padding: 15px; border-radius: 4px; border-left: 4px solid #3498db; }
                    .doc-item a { color: #3498db; text-decoration: none; font-weight: bold; }
                    .doc-item a:hover { text-decoration: underline; }
                    .meta { color: #666; font-size: 0.9em; margin-top: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>📄 HTML Documents from MongoDB</h1>
                    <ul class="doc-list">
            """
            
            if result.items:
                for i, item in enumerate(result.items):
                    key = item.key
                    stored_at = item.stored_at.strftime('%Y-%m-%d %H:%M:%S')
                    format_type = item.metadata.get('format', 'unknown')
                    original_key = item.metadata.get('original_data_key', 'N/A')
                    
                    html_content += f"""
                        <li class="doc-item">
                            <a href="/html/{i}">{key}</a>
                            <div class="meta">
                                Format: {format_type} | 
                                Stored: {stored_at} | 
                                Original: {original_key}
                            </div>
                        </li>
                    """
            else:
                html_content += "<li class='doc-item'>No HTML documents found in MongoDB.</li>"
            
            html_content += """
                    </ul>
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html_content.encode('utf-8'))
        
        elif self.path.startswith('/html/'):
            # Serve specific HTML document
            try:
                doc_index = int(self.path.split('/html/')[1])
                result = self.store.query({'source': 'format_converter'})
                
                if doc_index < len(result.items):
                    item = result.items[doc_index]
                    html_content = item.data.get('html', '')
                    
                    if html_content:
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(html_content.encode('utf-8'))
                    else:
                        self.send_error(404, "HTML content not found")
                else:
                    self.send_error(404, "Document not found")
            except (ValueError, IndexError):
                self.send_error(400, "Invalid document index")
        
        else:
            self.send_error(404, "Not found")
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass




def main():
    """Main entry point."""
    print("=" * 80)
    print("🌐 HTML Viewer from MongoDB")
    print("=" * 80)
    print()
    
    # Initialize data store
    print("Step 1: Connecting to MongoDB...")
    try:
        store = create_store(
            "mongodb",
            connection_string="mongodb://localhost:27017",
            database="trainer_data"
        )
        print("✓ Connected to MongoDB")
    except Exception as e:
        print(f"✗ Error connecting to MongoDB: {e}")
        print("   Make sure MongoDB is running:")
        print("   docker start mongodb")
        sys.exit(1)
    
    # Check for HTML documents
    print("\nStep 2: Checking for HTML documents...")
    result = store.query({'source': 'format_converter'})
    if not result.items:
        print("⚠ No HTML documents found in MongoDB.")
        print("   Run the integration example first:")
        print("   cd ../format-converter && python3 examples/integration_all_modules.py")
        sys.exit(1)
    
    print(f"✓ Found {result.total} HTML document(s)")
    for item in result.items:
        print(f"   - {item.key}")
    
    # Start web server
    print("\nStep 3: Starting web server...")
    port = 8888
    HTMLViewerHandler.store = store  # Set store on handler class
    httpd = HTTPServer(('localhost', port), HTMLViewerHandler)
    
    url = f"http://localhost:{port}"
    print(f"✓ Server running on {url}")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(1)
        print(f"\n🌐 Opening browser at {url}...")
        webbrowser.open(url)
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("\n" + "=" * 80)
    print("Server is running. Press Ctrl+C to stop.")
    print("=" * 80)
    print()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down server...")
        httpd.shutdown()
        print("✓ Server stopped")


if __name__ == "__main__":
    main()

