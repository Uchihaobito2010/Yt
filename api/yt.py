from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": 1,
        "message": "YouTube Download API",
        "endpoint": "/api/yt?link=YOUTUBE_URL",
        "credits": "Developed by @Aotpy"
    })

@app.route("/api/yt", methods=["GET"])
def api():
    link = request.args.get("link")

    if not link:
        return jsonify({
            "status": 0,
            "error": "Missing link parameter",
            "message": "Error occurred! Contact developer - @Aotpy",
            "usage": "/api/yt?link=https://youtube.com/watch?v=VIDEO_ID"
        }), 400

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

    try:
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
            return jsonify({
                "status": 0,
                "error": "Invalid response from source",
                "message": "Error occurred! Contact developer - @Aotpy"
            }), 500

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

        return jsonify({
            "status": 1,
            "response": {
                "title": info.get("title"),
                "duration": info.get("duration"),
                "thumbnail": thumb,
                "data": out
            },
            "credits": "Developed by @Aotpy"
        })

    except requests.exceptions.Timeout:
        return jsonify({
            "status": 0,
            "error": "Request timeout",
            "message": "Error occurred! Contact developer - @Aotpy"
        }), 500
    except Exception as e:
        return jsonify({
            "status": 0,
            "error": str(e),
            "message": "Error occurred! Contact developer - @Aotpy"
        }), 500

# Vercel 需要这个
if __name__ == "__main__":
    app.run()
