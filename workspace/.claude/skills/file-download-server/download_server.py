#!/usr/bin/env python3
"""
Custom HTTP server with proper Content-Disposition headers
to force correct file extensions on mobile downloads

Usage:
    1. Update SERVE_DIR to your target directory
    2. Update PORT if needed (default: 8888)
    3. Run: python3 download_server.py
    4. Access: http://<server-ip>:8888/
"""

import http.server
import socketserver
import os
from urllib.parse import unquote

# Configuration
PORT = 8888
SERVE_DIR = '/root/Research'  # Change this to your directory

class DownloadHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom handler that adds Content-Disposition headers
    to force proper file extensions on mobile downloads
    """

    # File type mappings
    MIME_TYPES = {
        '.pdf': 'application/pdf',
        '.md': 'text/markdown; charset=utf-8',
        '.txt': 'text/plain; charset=utf-8',
        '.zip': 'application/zip',
        '.json': 'application/json',
        '.csv': 'text/csv; charset=utf-8',
        '.xml': 'application/xml',
        '.html': 'text/html; charset=utf-8',
    }

    def end_headers(self):
        """
        Add Content-Disposition header before sending response headers
        This forces browsers to download with correct filename
        """
        # Check if path matches any configured file type
        for ext, mime_type in self.MIME_TYPES.items():
            if self.path.endswith(ext):
                filename = os.path.basename(unquote(self.path))
                # Force download with exact filename
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.send_header('Content-Type', mime_type)
                break

        super().end_headers()

def main():
    """Start the download server"""
    # Change to serving directory
    os.chdir(SERVE_DIR)

    # Create server
    with socketserver.TCPServer(("", PORT), DownloadHandler) as httpd:
        print("=" * 50)
        print(f"File Download Server Started")
        print("=" * 50)
        print(f"Port: {PORT}")
        print(f"Serving from: {os.getcwd()}")
        print(f"Access at: http://<your-ip>:{PORT}/")
        print(f"Stop with: Ctrl+C")
        print("=" * 50)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()
