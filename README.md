# GTA VI Countdown

A single-page countdown to the GTA VI release (Nov 19, 2026), built to sit on a TV.

Open `index.html` in a browser (or host it with GitHub Pages).

## Modes
- **OLED (default):** pure black background, dimmed grey thin text, and burn-in protection:
  the whole display slowly drifts around the screen, brightness gently "breathes",
  and the controls and cursor hide after 4 seconds of no input.
- **Normal:** colorful sunset theme for LCD/LED screens.

## Controls
`M` mode · `F` fullscreen · `S` show/hide seconds · `↑`/`↓` brightness.
Settings are remembered in the browser. The page also asks the browser to keep the screen awake.

URL options: `?mode=normal` or `?mode=oled`, and `?date=2026-11-19T00:00:00` to change the target.
