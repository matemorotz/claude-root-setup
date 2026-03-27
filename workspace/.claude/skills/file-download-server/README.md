# File Download Server Skill

Minimal HTTP server that forces correct file extensions on mobile downloads.

## Problem

Mobile browsers download files as `.bin` when `Content-Disposition` header is missing.

## Solution

Python HTTP server with proper headers:
```http
Content-Disposition: attachment; filename="document.pdf"
Content-Type: application/pdf
```

## Files

- `SKILL.md` - Complete workflow (134 lines)
- `download_server.py` - Ready-to-use server
- `README.md` - This file

## Quick Use

```bash
cp download_server.py /your/directory/
# Edit SERVE_DIR in file
python3 download_server.py
```

That's it. Files download with correct extensions on all devices.
