# transcriptPhorge.py – YouTube Transcript Downloader with Webshare Proxy

A simple, reliable Python script to download English transcripts from YouTube playlists or single videos and save them as clean, paragraph-grouped Markdown files. Be aware that the final transcript will only be as good as the original automated YouTube transcript.

- Bypasses YouTube IP blocks using Webshare rotating residential proxies
- Saves each video as a formatted .md file with title, YouTube link, and readable transcript
- Includes automatic run-on paragraph detection and a final report
- Supports both playlist and single-video modes
- Prompts for Webshare credentials (no hard-coded secrets)
- 60-second delay between videos (skipped after the last one)
- Skips already-existing files to prevent overwriting good transcripts
- Continues asking for more URLs until you quit

Features
- Playlist or single-video fetching
- Run-on text detection & report at the end (flags files with very long unbroken paragraphs)
- Retries on transient proxy errors
- No unnecessary pause after the final video
- --single command-line flag for single-video mode
- Safe credential handling (prompted once per run)

Requirements
- Python 3.8+
- Install dependencies:
`pip install youtube-transcript-api yt-dlp`

Setup – `Webshare Rotating Residential` proxies (Required)
YouTube aggressively blocks repeated caption requests, even from residential IPs. This script uses Webshare rotating residential proxies — the method recommended by the `youtube-transcript-api` maintainer.

Steps to set up Webshare
1. Go to `https://www.webshare.io`
2. Sign up (free tier gives 10 proxies / 1 GB trial — enough for testing)
3. Select `Rotating Residential` proxies (important: not datacenter or static residential)
4. Upgrade to a paid plan if needed
   - Rotating Residential Proxy w/ 1 GB: ~$3.50/GB (as of Feb 2026)
   - Bandwidth usage for transcripts is tiny (<1 MB for 10–20 videos)
5. After activation:
   - Go to Dashboard → Proxy List or Proxy Settings
   - Locate your Proxy Username and Proxy Password
   - These are what the script prompts for when you run it

Key notes about Webshare:
- Always use Residential rotating proxies — datacenter/static ones get blocked quickly
- You can cancel anytime — no long-term commitment
- A free trial is usually sufficient for one playlist or a few videos

How to Use

1. Clone or download the repo
git clone `https://github.com/yourusername/transcriptPhorge.git`
`cd transcriptPhorge`

2. Install dependencies
`pip install youtube-transcript-api yt-dlp`

3. Run the script

Playlist mode (default – fetches entire playlists):
`python transcriptPhorge.py`

Single-video mode (fetch one video at a time):
`python transcriptPhorge.py --single`

What happens when you run it
1. Prompts for your Webshare username and password (only once per run)
2. Asks for a playlist URL (or video URL in --single mode)
3. Processes each video:
   - Fetches transcript via Webshare proxy
   - Saves as numbered Markdown file in transcripts/ folder
   - Pauses 60 seconds between videos (skipped after last one)
4. After finishing:
   - Shows a Run-on Report if any files have very long, unbroken paragraphs
   - Asks if you want to process another playlist/video

Press Enter (leave input empty) to quit when done.

Example output filenames
01 - Lecture #1_ Introduction — Brandon Sanderson on Writing Science Fiction and Fantasy.md
...
14 - Lecture #13_ Publishing Part Two — Brandon Sanderson on Writing Science Fiction and Fantasy.md

Example Run-on Report
RUN-ON REPORT (long paragraphs detected)
==================================================
• 12 - Lecture #11_ Character Q&A — Brandon Sanderson on Writing Science Fiction and Fantasy.md  (longest paragraph: 1852 chars)
• 13 - Lecture #12_ Publishing Part One — Brandon Sanderson on Writing Science Fiction and Fantasy.md  (longest paragraph: 2140 chars)

Suggestion: Re-fetch these individually or manually break long paragraphs.

Customization
- Change `RUN_ON_THRESHOLD = 1200` (top of script) to adjust run-on detection sensitivity
- Modify `time.sleep(60)` to change delay between videos
- Remove `filter_ip_locations=["us"]` for global IP rotation (may be slower)
- Add more retries or logging as needed

Limitations & Notes
- Only fetches English captions (en)
- Requires YouTube captions (auto or manual)
- Webshare residential proxy is essential — free proxies, Tor, or VPNs usually get blocked
- Auto-captions may contain typos, filler words ("um", "uh"), or long run-on sections (especially in Q&A/monologue videos)

---

**License**

Licensed under the GNU General Public License v3.0 (GPL-3.0). This means you can freely use, modify, and distribute this software, provided that:

- You disclose the source code of your modifications
- You license your modifications under the same GPL-3.0 license
- You preserve the original copyright notices and disclaimers
- See the LICENSE file for the complete text of the GPL-3.0 license.