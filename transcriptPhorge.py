import os
import re
import sys
import time
import argparse
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, IpBlocked
from youtube_transcript_api.proxies import WebshareProxyConfig
import yt_dlp

# ========================= CONFIG =========================
RUN_ON_THRESHOLD = 1200  # characters — raise/lower if needed
# =========================================================

def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', '_', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:200]

def build_markdown(title: str, url: str, fetched_transcript) -> str:
    md = f"# {title}\n\n"
    md += f"[🎥 Watch the video]({url})\n\n"
    md += "## Transcript\n\n"
    md += "_From YouTube captions (manual or auto-generated)_\n\n"

    current_paragraph = []
    paragraph_char_count = 0

    for snippet in fetched_transcript:
        text = snippet.text.strip()
        if not text:
            if current_paragraph:
                md += " ".join(current_paragraph) + "\n\n"
                current_paragraph = []
                paragraph_char_count = 0
            continue

        current_paragraph.append(text)
        paragraph_char_count += len(text) + 1

        if (text.endswith(('.', '!', '?', '"', '”', ':', ';', '—', '…')) or
            text.lower().endswith(('um', 'uh', 'so', 'well', 'but', 'and', 'then', 'okay', 'alright')) or
            paragraph_char_count > 400):
            if current_paragraph:
                md += " ".join(current_paragraph) + "\n\n"
                current_paragraph = []
                paragraph_char_count = 0

    if current_paragraph:
        md += " ".join(current_paragraph) + "\n\n"

    return md

def is_run_on_transcript(markdown: str) -> tuple[bool, int]:
    paragraphs = [p.strip() for p in markdown.split('\n\n') if p.strip()]
    if not paragraphs:
        return False, 0
    longest = max(len(p) for p in paragraphs)
    return longest > RUN_ON_THRESHOLD, longest

def get_playlist_videos(playlist_url: str):
    ydl_opts = {'extract_flat': True, 'quiet': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

    videos = []
    if 'entries' in info and info.get('entries'):
        for entry in info['entries']:
            if entry and entry.get('id'):
                videos.append({
                    'id': entry['id'],
                    'title': entry.get('title', f"Video {entry['id']}"),
                    'url': f"https://www.youtube.com/watch?v={entry['id']}"
                })
    else:
        videos.append({
            'id': info['id'],
            'title': info.get('title', 'Unknown Video'),
            'url': playlist_url
        })
    return videos

def _save_placeholder(filepath, title, url, message="No transcript available"):
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n[🎥 Watch the video]({url})\n\n## Transcript\n\n**{message}**")

def fetch_with_retry(ytt, vid_id, max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            return ytt.fetch(vid_id)
        except (IpBlocked, Exception) as e:
            print(f"   ⚠️ Issue (attempt {attempt+1}): {type(e).__name__}")
            if attempt < max_retries:
                time.sleep(120 + attempt * 60)
    raise Exception("Max retries exceeded")

def get_delay_seconds():
    print("\nChoose delay between videos (seconds):")
    print("  1) 15")
    print("  2) 30 (default)")
    print("  3) 60")
    print("  4) 90")
    print("  5) 120")
    choice = input("Enter number (1–5) or press Enter for 30: ").strip()

    delays = {1: 15, 2: 30, 3: 60, 4: 90, 5: 120}
    try:
        if choice == "":
            return 30
        num = int(choice)
        return delays.get(num, 30)
    except ValueError:
        print("Invalid choice — using 30 seconds.")
        return 30

def main():
    parser = argparse.ArgumentParser(description="YouTube Transcript Downloader with Run-on Report")
    parser.add_argument('--single', action='store_true', help="Run in single-video mode")
    args = parser.parse_args()

    print("YouTube Transcript Downloader with Run-on Report\n")

    username = input("Webshare username: ").strip()
    password = input("Webshare password: ").strip()
    if not username or not password:
        print("Credentials required.")
        sys.exit(1)

    ytt = YouTubeTranscriptApi(
        proxy_config=WebshareProxyConfig(
            proxy_username=username,
            proxy_password=password,
            filter_ip_locations=["us"]
        )
    )

    delay_seconds = get_delay_seconds()
    print(f"Using {delay_seconds}-second delay between videos.\n")

    output_folder = "transcripts"
    os.makedirs(output_folder, exist_ok=True)

    run_on_report = []

    while True:
        if args.single:
            url = input("\nEnter video URL (or Enter to quit): ").strip()
            if not url:
                break
            vid_id = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1]
            videos = [{'id': vid_id, 'title': "Single Video", 'url': url}]
            start_i = 1
        else:
            playlist_url = input("\nEnter playlist URL (or Enter to quit): ").strip()
            if not playlist_url:
                break
            print("\nFetching playlist...")
            videos = get_playlist_videos(playlist_url)
            print(f"Found {len(videos)} video(s).\n")
            start_i = 1

        for i, video in enumerate(videos, start_i):
            vid_id = video['id']
            title = video['title']
            url = video['url']

            print(f"[{i}/{len(videos)}] Processing: {title}")

            safe_title = sanitize_filename(title)
            filename = f"{i:02d} - {safe_title}.md" if not args.single else f"single_{vid_id}.md"
            filepath = os.path.join(output_folder, filename)

            if os.path.exists(filepath):
                print(f"   Skipping (already exists)")
                continue

            try:
                fetched = fetch_with_retry(ytt, vid_id)
                markdown = build_markdown(title, url, fetched)

                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(markdown)

                is_bad, longest = is_run_on_transcript(markdown)
                print(f"   ✅ Saved: {filename}" + ("  ⚠️ LONG PARAGRAPH" if is_bad else ""))
                if is_bad:
                    run_on_report.append((filename, longest))

            except (NoTranscriptFound, TranscriptsDisabled):
                print("   ⚠️ No captions")
                _save_placeholder(filepath, title, url)
            except Exception as e:
                print(f"   ❌ Error: {e}")
                _save_placeholder(filepath, title, url, f"Error: {e}")

            if i < len(videos):
                print(f"   Pausing {delay_seconds} seconds before next video...")
                time.sleep(delay_seconds)

        again = input("\nProcess another? (y/n): ").strip().lower()
        if again != 'y':
            break

    if run_on_report:
        print("\n" + "="*60)
        print("RUN-ON REPORT (long paragraphs detected)")
        print("="*60)
        for filename, length in run_on_report:
            print(f"• {filename}  (longest paragraph: {length} chars)")
        print("\nSuggestion: Re-fetch these individually or manually break long paragraphs.")
    else:
        print("\n✅ No run-on transcripts detected.")
    print("="*60)

if __name__ == "__main__":
    main()