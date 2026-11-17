#!/usr/bin/env python3
"""Render the GTA VI countdown as a video stream for VLC (e.g. VLC on Apple TV).

The video starts at local midnight of --start, so the playback position equals
the time of day: at 3:15 PM, scrub to 15:15 and the countdown is correct.
Everything is relative to local midnight on release day (same as the website),
so the same files work in any time zone.

Output is HLS (an .m3u8 playlist + 10-minute .ts segments) so it can be hosted
on GitHub Pages (100 MB per-file limit) and seeked as one long video in VLC.
A second playlist per extra day is written that starts at that day's midnight
and reuses the same segments.

Usage:
  python3 make_video.py --mode oled --start 2026-11-17 --out ../tv
Needs: ffmpeg with libx264 + drawtext, and the Inter font.
"""
import argparse, datetime, os, subprocess, tempfile

RELEASE = datetime.datetime(2026, 11, 19)
FONTS = "/usr/share/fonts/opentype/inter/"
SEG = 600  # seconds per HLS segment

ap = argparse.ArgumentParser()
ap.add_argument("--mode", choices=["oled", "normal"], default="oled")
ap.add_argument("--start", default="2026-11-17", help="local day the video starts (midnight)")
ap.add_argument("--tail", type=float, default=3, help="hours of 'It's here' after release")
ap.add_argument("--height", type=int, default=720)
ap.add_argument("--crf", default="31")
ap.add_argument("--bg", help="background image (normal mode)")
ap.add_argument("--hours", type=float, help="override total length (for testing)")
ap.add_argument("--out", required=True)
a = ap.parse_args()

start = datetime.datetime.fromisoformat(a.start)
S0 = int((RELEASE - start).total_seconds())          # seconds remaining at t=0
dur = int(a.hours * 3600) if a.hours else S0 + int(a.tail * 3600)
H = a.height; W = H * 16 // 9; k = H / 1080             # layout designed at 1080p
oled = a.mode == "oled"
px = lambda v: round(v * k)

# Burn-in protection: the whole layout glides along a slow Lissajous path
# (never the same pixels for long). It moves in small steps every 4 s, which
# keeps the files small. OLED mode also "breathes" brightness over ~5 minutes.
step = "trunc(t/4)*4"
if oled:
    X = f"({px(170)}*sin({step}/97))"; Y = f"({px(200)}*sin({step}/131+1))"
    color, muted = "0xb8b8b8", "0x5a5a5a"
    alpha = "'0.70*(0.92+0.08*sin(trunc(t/20)*20/47.7))'"
else:
    X = f"({px(40)}*sin({step}/193))"; Y = f"({px(25)}*sin({step}/251+1))"
    color, muted, alpha = "white", "0xeeeeee", "1"

R = f"max(0\\,{S0}-t)"
pad2 = lambda e: f"%{{eif\\:{e}\\:d\\:2}}"
fields = [("DAYS", f"%{{eif\\:trunc({R}/86400)\\:d}}"),
          ("HOURS", pad2(f"mod(trunc({R}/3600)\\,24)")),
          ("MINUTES", pad2(f"mod(trunc({R}/60)\\,60)")),
          ("SECONDS", pad2(f"mod({R}\\,60)"))]

def text(txt, font, size, cx, y, col, enable=None, extra=""):
    s = (f"drawtext=fontfile={FONTS}{font}:text='{txt}':fontsize={px(size)}:fontcolor={col}"
         f":alpha={alpha}:x='{px(cx)}-text_w/2+{X}':y='{px(y)}+{Y}'")
    if enable: s += f":enable='{enable}'"
    return s + extra

before, after = f"lt(t\\,{S0})", f"gte(t\\,{S0})"
big = "Inter-Thin.otf" if oled else "Inter-Light.otf"
glow = "" if oled else ":shadowcolor=0x3c0050@0.6:shadowx=0:shadowy=4"
f = [text("G R A N D   T H E F T   A U T O   V I", "Inter-Light.otf" if oled else "Inter-Bold.otf",
          40, 960, 295, muted)]
for i, (label, expr) in enumerate(fields):
    cx = 960 + (i - 1.5) * 380
    f.append(text(expr, big, 250, cx, 380, color, before, glow))
    f.append(text(" ".join(label), "Inter-Light.otf", 26, cx, 680, muted, before))
f.append(text("It’s here.", big, 200, 960, 430, color, after, glow))
f.append(text("T H U R S D A Y ,   N O V E M B E R   1 9 ,   2 0 2 6", "Inter-Light.otf",
              26, 960, 760, muted))

if oled:
    src = ["-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r=1:d={dur}"]
    graph = "[0:v]" + ",".join(f) + "[v]"
else:
    src = ["-loop", "1", "-framerate", "1", "-t", str(dur), "-i", a.bg]
    graph = f"[0:v]scale={W}:{H}," + ",".join(f) + "[v]"

os.makedirs(a.out, exist_ok=True)
name = a.mode
with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
    fh.write(graph); script = fh.name
full = os.path.join(a.out, f"{name}-{a.start}.m3u8")
subprocess.run([
    "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats", *src,
    "-filter_complex_script", script, "-map", "[v]",
    "-c:v", "libx264", "-preset", "medium", "-crf", a.crf, "-tune", "stillimage",
    "-g", "60", "-force_key_frames", f"expr:gte(t,n_forced*{SEG})",
    "-pix_fmt", "yuv420p", "-r", "1",
    "-f", "hls", "-hls_time", str(SEG), "-hls_playlist_type", "vod",
    "-hls_segment_filename", os.path.join(a.out, f"{name}_%03d.ts"), full], check=True)
os.unlink(script)

# Extra playlists that start at each later midnight (same segments, no copies).
lines = open(full).read().splitlines()
header = [l for l in lines if l.startswith("#EXT") and not l.startswith(("#EXTINF", "#EXT-X-ENDLIST"))]
segs = [(lines[i], lines[i + 1]) for i, l in enumerate(lines) if l.startswith("#EXTINF")]
day = 1
while day * 86400 < dur:
    d = (start + datetime.timedelta(days=day)).date().isoformat()
    skip = day * 86400 // SEG
    body = [x for pair in segs[skip:] for x in pair]
    hdr = [f"#EXT-X-MEDIA-SEQUENCE:{skip}" if h.startswith("#EXT-X-MEDIA-SEQUENCE") else h for h in header]
    open(os.path.join(a.out, f"{name}-{d}.m3u8"), "w").write("\n".join(hdr + body + ["#EXT-X-ENDLIST", ""]))
    day += 1
print("wrote", a.out)
