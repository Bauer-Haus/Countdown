# GTA VI Countdown

A single-page countdown to the GTA VI US/Canada release (Nov 19, 2026 at 12:00 AM Eastern),
built to sit on a TV. The website works in any time zone.

Open `index.html` in a browser (or host it with GitHub Pages).

## Modes
- **OLED (default):** pure black background, dimmed grey thin text, and burn-in protection:
  the whole display slowly drifts around the screen, brightness gently "breathes",
  and the controls and cursor hide after 4 seconds of no input.
- **Normal:** colorful sunset theme for LCD/LED screens.

## Controls
`M` mode · `F` fullscreen · `S` show/hide seconds · `↑`/`↓` brightness.
Settings are remembered in the browser. The page also asks the browser to keep the screen awake.

URL options: `?mode=normal` or `?mode=oled`, and `?date=2026-11-19T00:00:00-05:00` to change the target.

## Watch on Apple TV with VLC

The countdown is also available as a video stream (OLED style: black background,
dimmed text that slowly drifts and "breathes" to prevent burn-in).

1. Open **VLC** on the Apple TV → **Network** tab → **Open Network Stream**.
2. Enter one of these URLs:

   | Today is | URL |
   |---|---|
   | Tue Nov 17 | `https://raw.githubusercontent.com/Bauer-Haus/Countdown/claude/determined-fermi-13cwl1/tv/oled-2026-11-17.m3u8` |
   | Wed Nov 18 | `https://raw.githubusercontent.com/Bauer-Haus/Countdown/claude/determined-fermi-13cwl1/tv/oled-2026-11-18.m3u8` |

   (With GitHub Pages enabled you can use `https://bauer-haus.github.io/Countdown/tv/oled-2026-11-18.m3u8` instead.)
3. **Sync it:** each video starts at midnight, so the playback position is the time of day.
   If it's 7:42 PM, scrub to **19:42**. Get as close as you can, then it stays in sync.
   Once it starts it plays right through to release and shows "It's here." for 3 hours after.

**The video is made for US Central time** (release = 11:00 PM CT on Nov 18 = 12:00 AM ET on Nov 19),
because the playback position has to match your clock. For another time zone, re-render with
`--release` set to the release time on that clock.

To re-render (e.g. if the date changes, or for the colorful style), see `video/make_video.py`
(needs ffmpeg and the Inter font).
