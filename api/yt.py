from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

OWNER = "@Aotpy"
CONTACT = "https://t.me/Aotpy"

def shorten_url(url):
    if not url:
        return url
    try:
        r = requests.post(
            "https://freelyshrink.com/shorten.php",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={"long_url": url},
            timeout=10
        )

        if "code=" in r.url:
            code = r.url.split("code=")[1].split("&")[0]
            return f"https://hosturl.link/{code}"

        m = re.search(r'code=([a-zA-Z0-9]+)', r.text)
        if m:
            return f"https://hosturl.link/{m.group(1)}"

    except:
        pass

    return url


@app.route("/api/yt", methods=["GET"])
def yt_api():
    link = request.args.get("link")

    if not link:
        return jsonify({
            "status": 0,
            "error": "Missing 'link' parameter",
            "contact": CONTACT
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
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Origin": "https://vidssave.com",
        "Referer": "https://vidssave.com/yt"
    }

    try:
        session = requests.Session()
        session.get("https://vidssave.com/yt", headers=headers)

        r = session.post(
            "https://vidssave.com/api/proxy",
            headers=headers,
            json=payload,
            timeout=20
        )

        data = r.json()

        if data.get("status") != 1:
            return jsonify({
                "status": 0,
                "error": "Failed to fetch video data",
                "contact": CONTACT
            }), 500

        info = data["data"]
        results = []

        for res in info.get("resources", []):
            if res.get("download_mode") == "check_download":
                results.append({
                    "quality": res.get("quality"),
                    "format": res.get("format"),
                    "size": res.get("size"),
                    "download": shorten_url(res.get("download_url"))
                })

        return jsonify({
            "status": 1,
            "owner": OWNER,
            "response": {
                "title": info.get("title"),
                "duration": info.get("duration"),
                "thumbnail": shorten_url(info.get("thumbnail")),
                "downloads": results
            }
        })

    except requests.exceptions.Timeout:
        return jsonify({
            "status": 0,
            "error": "Source timeout",
            "contact": CONTACT
        }), 504

    except Exception as e:
        return jsonify({
            "status": 0,
            "error": str(e),
            "contact": CONTACT
        }), 500


app = app
