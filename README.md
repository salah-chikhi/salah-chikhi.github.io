# salah-chikhi.github.io

Personal academic website of Salah Chikhi, served by GitHub Pages at
<https://salah-chikhi.github.io/>.

Plain static HTML and CSS, no build step:

- `index.html`, `publications.html`, `teaching.html`, `misc.html`: the four pages.
- `site.css`: all styles, light and dark themes.
- `theme.js`: the light/dark toggle in the menu; without a saved choice the site follows the system setting.
- `images/`: portrait, banner, book covers, paper first pages, Levine figures.
- `notes/`: course notes linked from the Teaching page.
- `Salah_Chikhi_CV.pdf`: the CV linked from the menu.

The research figures on the home page are generated SVG. To change one, edit
`tools/build_figures.py` and run, from the repository root:

```bash
python tools/build_figures.py index.html
```

It rewrites the figures between the `<!--FIG:name-->` and `<!--/FIG-->` markers.
Math labels are typeset in Computer Modern by matplotlib (`pip install matplotlib`) and
embedded as SVG paths, so they look like LaTeX and still follow the light/dark theme.

The selected readings and favorite papers on `misc.html` are the `BOOKS` and
`PAPERS` lists in the script at the bottom of that page.

Banner photo: Rabah Boualia, CC BY-SA 4.0, via Wikimedia Commons.
