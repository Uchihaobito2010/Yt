from http.server import BaseHTTPRequestHandler
import json
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse query parameters
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        # Check if accessing root path
        if self.path == '/' or self.path == '/api':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": 1,
                "message": "YouTube Download API",
                "endpoint": "/api?link=YOUTUBE_URL",
                "example": "/api?link=https://youtube.com/watch?v=dQw4w9WgXcQ",
                "credits": "Developed by @Aotpy"
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        link = query_params.get('link', [None])[0]
        
        if not link:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": 0,
                "error": "Missing link parameter",
                "message": "Error occurred! Contact developer - @Aotpy",
                "usage": "Use /api?link=YOUTUBE_URL"
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        try:
            payload = {
                "url": "/media/parse",
                "data": {
                    "origin": "source",
                    "link": link
                },
                "token": ""
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android)",
                "Accept": "*/*",
                "Content-Type": "application/json",
                "Origin": "https://vidssave.com",
                "Referer": "https://vidssave.com/yt"
            }
            
            session = requests.Session()
            session.get("https://vidssave.com/yt", headers=headers)
            res = session.post(
                "https://vidssave.com/api/proxy",
                headers=headers,
                json=payload,
                timeout=20
            )
            
            data = res.json()
            
            if data.get("status") != 1:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": 0,
                    "error": "Invalid response from source",
                    "message": "Error occurred! Contact developer - @Aotpy"
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            info = data["data"]
            out = []
            thumb = info.get("thumbnail")
            
            for rsc in info.get("resources", []):
                if rsc.get("download_mode") == "check_download":
                    out.append({
                        "quality": rsc.get("quality"),
                        "format": rsc.get("format"),
                        "size": rsc.get("size"),
                        "download": rsc.get("download_url")
                    })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": 1,
                "response": {
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "thumbnail": thumb,
                    "data": out
                },
                "credits": "Developed by @Aotpy"
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": 0,
                "error": str(e),
                "message": "Error occurred! Contact developer - @Aotpy"
            }
            self.wfile.write(json.dumps(response).encode())
