---
name: file-download-server
description: Set up HTTP server with Content-Disposition headers for correct file extensions on mobile downloads (prevents .bin downloads for .pdf, .md, etc.)
---

# File Download Server

Serves files with proper headers to ensure correct extensions on mobile downloads.

## Quick Setup

```bash
# 1. Create server script
cat > download_server.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import os
from urllib.parse import unquote

PORT = 8888
SERVE_DIR = '/path/to/files'  # Update this

class DownloadHandler(http.server.SimpleHTTPRequestHandler):
    MIME_TYPES = {
        '.pdf': 'application/pdf',
        '.md': 'text/markdown; charset=utf-8',
        '.txt': 'text/plain; charset=utf-8',
        '.zip': 'application/zip',
        '.json': 'application/json',
    }

    def end_headers(self):
        for ext, mime_type in self.MIME_TYPES.items():
            if self.path.endswith(ext):
                filename = os.path.basename(unquote(self.path))
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.send_header('Content-Type', mime_type)
                break
        super().end_headers()

os.chdir(SERVE_DIR)
with socketserver.TCPServer(("", PORT), DownloadHandler) as httpd:
    print(f"Serving from {os.getcwd()} on port {PORT}")
    httpd.serve_forever()
EOF

# 2. Configure
nano download_server.py  # Update SERVE_DIR

# 3. Open firewall
ufw allow 8888

# 4. Run
python3 download_server.py

# Or background:
nohup python3 download_server.py > /tmp/server.log 2>&1 &
```

## Verify

```bash
# Check running
netstat -tlnp | grep :8888

# Test headers
curl -I http://localhost:8888/file.pdf | grep Content-Disposition

# Should show:
# Content-Disposition: attachment; filename="file.pdf"
```

## Stop Server

```bash
pkill -f download_server.py
```

## Optional: Landing Page

Create `index.html` in serve directory:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Downloads</title>
    <style>
        body {
            font-family: -apple-system, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
        }
        a {
            display: block;
            padding: 18px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 12px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>File Downloads</h1>
        <a href="document.pdf" download>Download PDF</a>
    </div>
</body>
</html>
```

## How It Works

The `Content-Disposition: attachment; filename="file.pdf"` header forces browsers to download with the exact filename and extension, preventing mobile browsers from defaulting to `.bin`.

## References

- [MDN: Content-Disposition](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition)
- [Python http.server](https://docs.python.org/3/library/http.server.html)
