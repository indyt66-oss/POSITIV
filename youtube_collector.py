
import os
import json
import random
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
OUTPUT = Path("data/videos.json")

THEMES = {
    "Animaux": "animal rescue wildlife birds",
    "Espace": "NASA space astronomy discovery",
    "Solidarite": "kindness community helping people",
    "Sport": "inspiring sports achievements",
    "Savoir-faire": "craftsmanship amazing skills",
    "Architecture": "beautiful architecture cities",
    "Education": "inspiring education learning",
    "Innovation": "renewable energy inventions",
    "Art": "inspiring art music performance",
    "Nature": "beautiful forests mountains landscapes",
    "Cuisine": "traditional cooking agriculture",
    "Science": "positive science discoveries",
}

def search_youtube(query, max_results=15):
    params = urllib.parse.urlencode({
        "part": "snippet",
        "q": query,
        "type": "video",
        "videoEmbeddable": "true",
        "safeSearch": "strict",
        "maxResults": max_results,
        "order": "relevance",
        "key": API_KEY,
    })
    url = "https://www.googleapis.com/youtube/v3/search?" + params
    request = urllib.request.Request(
        url, headers={"User-Agent": "POSITIV/1.0"}
    )
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.load(response).get("items", [])

def main():
    if not API_KEY:
        raise RuntimeError("YOUTUBE_API_KEY manquante")

    existing = []
    if OUTPUT.exists():
        try:
            existing = json.loads(OUTPUT.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            existing = []

    videos = {
        item["id"]: item
        for item in existing
        if isinstance(item, dict) and item.get("id")
    }

    for theme, query in THEMES.items():
        try:
            results = search_youtube(query)
            added = 0
            for result in results:
                video_id = result.get("id", {}).get("videoId")
                snippet = result.get("snippet", {})
                if not video_id or video_id in videos:
                    continue
                videos[video_id] = {
                    "id": video_id,
                    "title": snippet.get("title", ""),
                    "theme": theme,
                    "source": "YouTube",
                    "channel": snippet.get("channelTitle", ""),
                    "published": snippet.get("publishedAt", ""),
                    "url": "https://www.youtube.com/watch?v=" + video_id,
                    "embed": "https://www.youtube-nocookie.com/embed/" + video_id,
                    "thumbnail": (
                        snippet.get("thumbnails", {})
                        .get("high", {})
                        .get("url", "")
                    ),
                    "collected": datetime.now(timezone.utc).isoformat(),
                    "rights": "YouTube embed - no redistribution",
                    "status": "pending_review",
                }
                added += 1
            print(f"{theme}: {added} nouvelles videos")
        except Exception as error:
            print(f"Erreur pour {theme}: {error}")

    items = list(videos.values())
    random.shuffle(items)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Total: {len(items)} videos candidates")

if __name__ == "__main__":
    main()
