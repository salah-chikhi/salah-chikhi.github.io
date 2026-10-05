"""Generate the research figures and inject them into index.html at <!--FIG:name--> markers.

Usage, from the repository root:  python tools/build_figures.py index.html
"""
import math, re, random, sys

def f(x): return f"{x:.1f}".rstrip("0").rstrip(".")
def pts(seq): return " ".join(f"{f(x)},{f(y)}" for x, y in seq)
def sup(t): return f'<tspan baseline-shift="super" font-size="70%">{t}</tspan>'
def sub(t): return f'<tspan baseline-shift="sub" font-size="70%">{t}</tspan>'

def svg(name, title, desc, body, h=300, w=520):
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-labelledby="{name}-t {name}-d">'
            f'<title id="{name}-t">{title}</title><desc id="{name}-d">{desc}</desc>{body}</svg>')

def A(kind, d=0):
    """animation hook: kind in draw/fade/pop/growx/growy, d = delay in seconds"""
    return f' data-a="{kind}" style="--d:{d:.2f}s"' + (' pathLength="1"' if kind == "draw" else "")

def arrowhead(x, y):
    return f'<path class="d-arrowhead" d="M{x-10} {y-6} L{x} {y} L{x-10} {y+6} Z"/>'

# ---------------------------------------------------------------- 1. s-composability
def fig_opt():
    n = 5
    lo, hi = 1.0, 2.0
    for _ in range(80):
        m = (lo + hi) / 2
        if 1 / (1 + n * m) - (m - 1) ** n > 0: lo = m
        else: hi = m
    h = lo; eta = 1 / (1 + n * h)
    X0, X1, Y0, Y1 = 56, 500, 236, 20
    a0, a1, ymax = 0.6, 2.0, 0.26
    X = lambda a: X0 + (a - a0) / (a1 - a0) * (X1 - X0)
    Y = lambda v: Y0 - min(v, ymax) / ymax * (Y0 - Y1)
    grid = [a0 + i * (a1 - a0) / 400 for i in range(401)]
    dec = [(X(a), Y(1 / (1 + n * a))) for a in grid]
    ris = [(X(a), Y(abs(1 - a) ** n)) for a in grid if abs(1 - a) ** n <= ymax]
    bnd = [(X(a), Y(max(1 / (1 + n * a), abs(1 - a) ** n))) for a in grid if max(1 / (1 + n * a), abs(1 - a) ** n) <= ymax]
    b = [f'<path class="d-axis" d="M{X0} {Y1} V{Y0} H{X1}"/>']
    for a in (0.6, 1.0, 1.4, 1.8):
        b.append(tex(f"${a:g}$", X(a), Y0 + 18, 13, anchor="middle", cls="t-soft"))
    for v in (0.1, 0.2):
        b.append(tex(f"${v:g}$", X0 - 8, Y(v) + 4, 13, anchor="end", cls="t-soft"))
    b.append(f'<polyline class="c-band"{A("fade", 1.1)} points="{pts(bnd)}"/>')
    b.append(f'<polyline class="c-accent c-mid"{A("draw", 0)} points="{pts(dec)}"/>')
    b.append(f'<polyline class="c-warm c-mid"{A("draw", 0.35)} points="{pts(ris)}"/>')
    hx, hy = X(h), Y(eta)
    b.append(f'<line class="d-guide"{A("fade", 1.4)} x1="{f(hx)}" y1="{f(hy)}" x2="{f(hx)}" y2="{Y0}"/>')
    b.append(f'<line class="d-guide"{A("fade", 1.4)} x1="{X0}" y1="{f(hy)}" x2="{f(hx)}" y2="{f(hy)}"/>')
    b.append(f'<circle class="d-star"{A("pop", 1.3)} cx="{f(hx)}" cy="{f(hy)}" r="6"/>')
    b.append(tex(r"$1/(1+n\alpha)$", X(0.84), Y(0.125), 18, cls="t-accent", extra=A("fade", 0.6)))
    b.append(tex(r"$|1-\alpha|^{n}$", X(1.86), Y(0.215), 18, anchor="end", cls="t-warm", extra=A("fade", 0.9)))
    b.append(tex(r"$h_5$", hx, Y0 + 19, 16, anchor="middle", extra=A("fade", 1.6)))
    b.append(tex(r"$\eta_5$", X0 + 8, hy - 8, 16, extra=A("fade", 1.6)))
    b.append(tex(r"$\alpha$", X1, Y0 + 40, 17, anchor="end"))
    b.append(tex(r"$n=5$", X1, Y1 + 14, 15, anchor="end", cls="t-soft"))
    return svg("f-opt", "The optimal constant stepsize sits where two worst cases meet",
               f"For n = 5 steps of gradient descent the worst-case final gradient is at least the larger of 1/(1+5α) and |1−α|^5. The two branches cross at α = h5 ≈ {h:.4f}, where the value is η5 ≈ {eta:.4f}; the paper proves this value is attained and that h5 is the unique optimal constant stepsize.",
               "".join(b), h=290)

# ---------------------------------------------------------------- LaTeX-style labels
# Math is set in Computer Modern by matplotlib's mathtext and embedded as SVG paths, so it reads like
# LaTeX and still follows the theme through CSS (class "tex").
import matplotlib
matplotlib.rcParams["mathtext.fontset"] = "cm"
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as MplPath

def tex(s, x, y, size=16, anchor="start", cls="", extra=""):
    """Render the mathtext string s with its baseline at (x, y)."""
    tp = TextPath((0, 0), s, size=size, prop=FontProperties(family="serif"))
    bb = tp.get_extents()
    dx = {"start": -bb.x0, "middle": -(bb.x0 + bb.x1) / 2, "end": -bb.x1}[anchor]
    g = lambda u, v: f"{u + dx:.2f} {-v:.2f}"
    d = []
    for verts, code in tp.iter_segments(curves=True, simplify=False):
        p = [g(verts[k], verts[k + 1]) for k in range(0, len(verts), 2)]
        if code == MplPath.MOVETO: d.append("M" + p[0])
        elif code == MplPath.LINETO: d.append("L" + p[0])
        elif code == MplPath.CURVE3: d.append("Q" + " ".join(p))
        elif code == MplPath.CURVE4: d.append("C" + " ".join(p))
        elif code == MplPath.CLOSEPOLY: d.append("Z")
    return f'<path class="tex {cls}"{extra} transform="translate({x:.1f} {y:.1f})" d="{"".join(d)}"/>'


# ---------------------------------------------------------------- 2. Taylor / networked MDP
def fig_rl():
    """Left: a network where agent i and its kappa-neighborhood are kept and the rest is marginalized.
    Right: derivatives of Q_i decay exponentially with the graph distance d(beta) of the agents involved.
    Schematic: kappa = 1, rho = 0.45."""
    rnd = random.Random(11)
    b = []

    # --- jittered triangular lattice, so the graph looks irregular but stays planar
    s, rows, cols = 42.0, 7, 6
    hgt = s * math.sqrt(3) / 2
    ox, oy = 24.0, 30.0
    pos = {}
    for r in range(rows):
        for c in range(cols):
            x = ox + c * s + (s / 2 if r % 2 else 0)
            if x > 262: continue
            pos[(r, c)] = [x + rnd.uniform(-0.12, 0.12) * s, oy + r * hgt + rnd.uniform(-0.12, 0.12) * s]
    def lattice_nbrs(r, c):
        cand = [(r, c + 1), (r + 1, c - 1), (r + 1, c)] if r % 2 == 0 else [(r, c + 1), (r + 1, c), (r + 1, c + 1)]
        return [q for q in cand if q in pos]
    edges = [(p, q) for p in pos for q in lattice_nbrs(*p)]

    # agent i: the node nearest to the middle of the panel; its kappa = 1 neighborhood
    i = min(pos, key=lambda p: (pos[p][0] - 140) ** 2 + (pos[p][1] - 140) ** 2)
    adj = {p: set() for p in pos}
    for p, q in edges: adj[p].add(q); adj[q].add(p)
    hood = {i} | adj[i]
    # thin out the far edges for an irregular look (never inside the neighborhood, never isolating a node)
    kept = []
    deg = {p: len(adj[p]) for p in pos}
    for p, q in edges:
        if not (p in hood and q in hood) and rnd.random() < 0.3 and deg[p] > 3 and deg[q] > 3:
            deg[p] -= 1; deg[q] -= 1
            continue
        kept.append((p, q))
    cx, cy = pos[i]
    rad = max(math.dist(pos[i], pos[q]) for q in adj[i]) + 14
    for p in pos:                              # keep every outside node clearly outside the disk
        if p in hood: continue
        dd = math.dist(pos[i], pos[p])
        if dd < rad + 10:
            k = (rad + 10) / dd
            pos[p] = [cx + (pos[p][0] - cx) * k, cy + (pos[p][1] - cy) * k]
    lx, ly = cx + rad * 0.5, cy - rad - 7          # baseline of the N_i label
    gone = {p for p in pos if p not in hood and lx - 12 <= pos[p][0] <= lx + 44 and ly - 32 <= pos[p][1] <= ly + 10}
    for p in gone: del pos[p]
    kept = [(p, q) for p, q in kept if p in pos and q in pos]
    # hop distance from i, used only to stage the animation
    hop = {i: 0}; frontier = [i]
    kadj = {p: set() for p in pos}
    for p, q in kept: kadj[p].add(q); kadj[q].add(p)
    while frontier:
        nxt = []
        for p in frontier:
            for q in kadj[p]:
                if q not in hop: hop[q] = hop[p] + 1; nxt.append(q)
        frontier = nxt

    b.append(f'<circle class="g-hood"{A("fade", 0.45)} cx="{cx:.1f}" cy="{cy:.1f}" r="{rad:.1f}"/>')
    for p, q in kept:
        inside = p in hood and q in hood
        t = 0.06 * min(hop.get(p, 6), hop.get(q, 6))
        (x1, y1), (x2, y2) = pos[p], pos[q]
        b.append(f'<line class="{"g-edge-in" if inside else "g-edge"}"{A("fade", t)} x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
    for p, (x, y) in pos.items():
        cls, r = ("g-node-i", 10) if p == i else (("g-node-in", 8) if p in hood else ("g-node", 6.5))
        b.append(f'<circle class="{cls}"{A("pop", 0.06 * hop.get(p, 6))} cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>')
    b.append(tex(r"$i$", cx, cy + 25, 17, anchor="middle", cls="t-warm", extra=A("fade", 0.3)))
    b.append(tex(r"$\mathcal{N}_i^{\kappa}$", lx, ly, 19, cls="t-warm", extra=A("fade", 0.7)))
    b.append(tex(r"$\mathcal{N}_{-i}^{\kappa}$", 14, 296, 17, cls="t-soft", extra=A("fade", 0.9)))
    b.append(f'<path class="g-arrow"{A("fade", 0.9)} d="M46 283 L64 266"/><path class="g-arrowhead"{A("fade", 0.9)} d="M68 262 L59 265 L65 271 Z"/>')

    # --- right: derivative magnitude against graph distance
    X0, X1, base, top = 298, 508, 238, 54
    dmax, rho, K = 5, 0.45, 1
    X = lambda d: X0 + 14 + d * (X1 - X0 - 26) / dmax
    Y = lambda v: base - v * (base - top)
    b.append(f'<rect class="g-keep"{A("fade", 0.5)} x="{X0:.1f}" y="{top - 10}" width="{X(K + 0.5) - X0:.1f}" height="{base - top + 10}" rx="6"/>')
    b.append(f'<path class="d-axis" d="M{X0} {top - 12} V{base} H{X1}"/>')
    env = [(X(t / 25), Y(rho ** (t / 25))) for t in range(0, int((dmax + 0.3) * 25) + 1)]
    b.append(f'<polyline class="c-ink c-dash"{A("fade", 1.0)} points="{pts(env)}"/>')
    shades = {0: [1.0], 1: [0.95, 0.66, 0.42], 2: [0.9, 0.6, 0.38], 3: [0.95, 0.62, 0.35], 4: [0.9, 0.45], 5: [0.92, 0.4]}
    for d in range(dmax + 1):
        us = shades[d]
        for k, u in enumerate(us):
            dx = 0 if len(us) == 1 else (k - (len(us) - 1) / 2) * 0.24
            cls = "g-node-i" if d == 0 else ("d-node-near" if d <= K else "d-node")
            b.append(f'<circle class="{cls}"{A("pop", 0.5 + 0.1 * d + 0.03 * k)} cx="{X(d + dx):.1f}" cy="{Y(u * rho ** d):.1f}" r="{6 if d == 0 else 4.6}"/>')
        b.append(tex(f"${d}$", X(d), base + 17, 13, anchor="middle", cls="t-soft"))
    b.append(tex(r"$|\partial^{\beta} Q_i|$", X0 - 2, top - 20, 17))
    b.append(tex(r"$d(\beta)$", X1, base + 40, 16, anchor="end"))
    b.append(tex(r"$L_Q\,\rho^{d(\beta)}$", X(2.15), Y(rho ** 1.55) - 8, 16, extra=A("fade", 1.2)))
    b.append(tex(r"$d(\beta)\leq\kappa$", (X0 + X(K + 0.5)) / 2, base - 9, 13, anchor="middle", cls="t-warm", extra=A("fade", 0.6)))
    return svg("f-rl", "Derivatives of a local Q-function decay exponentially with graph distance",
               "Left: a network of agents; agent i and its neighborhood N_i^kappa are highlighted, and the other agents form N_-i^kappa, which is marginalized. "
               "Right: magnitudes of derivatives of Q_i plotted against the graph distance d(beta) from i to the farthest agent involved; "
               "they stay below the envelope L_Q rho to the power d(beta), which decays exponentially, and derivatives with d(beta) at most kappa are kept.",
               "".join(b), h=304)

# ---------------------------------------------------------------- 3. eps-sufficiency
def fig_data():
    b = []
    cx, cy, rx, ry, th = 120, 130, 94, 54, -24
    b.append(f'<ellipse class="d-ellipse"{A("fade", 0)} cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" transform="rotate({th} {cx} {cy})"/>')
    ang = math.radians(th)
    def inside(x, y):
        dx, dy = x - cx, y - cy
        u = dx * math.cos(-ang) - dy * math.sin(-ang)
        v = dx * math.sin(-ang) + dy * math.cos(-ang)
        return (u / rx) ** 2 + (v / ry) ** 2 <= 1
    lx = cx + 34
    ys = [y / 2 for y in range(0, 600) if inside(lx, y / 2)]
    ya, yb = min(ys), max(ys)
    b.append(f'<line class="d-guide" x1="{lx}" y1="20" x2="{lx}" y2="240"/>')
    b.append(f'<line class="d-fiber"{A("draw", 0.4)} x1="{lx}" y1="{f(ya)}" x2="{lx}" y2="{f(yb)}"/>')
    b.append(f'<circle class="d-star"{A("pop", 0.9)} cx="{lx}" cy="{f((ya+yb)/2)}" r="5.5"/>')
    b.append(f'<text class="d-math-i"{A("fade", 1.0)} x="{lx+10}" y="{f((ya+yb)/2+5)}">a{sub("y")}</text>')
    b.append(f'<text class="d-note" x="{lx+6}" y="32">Q{sup("T")}c = y</text>')
    b.append(f'<text class="d-note" x="{cx-34}" y="{cy+84}" text-anchor="middle">possible costs</text>')
    data = [(0, 1.9129), (1, .5501), (2, .5176), (4, .4301), (8, .2989), (16, .2150), (32, .1472), (64, 0.0)]
    X0, X1, Y0, Y1 = 278, 500, 226, 24
    w = (X1 - X0) / len(data)
    Y = lambda v: Y0 - min(v, 0.62) / 0.62 * (Y0 - Y1)
    thr = 0.32
    b.append(f'<path class="d-axis" d="M{X0} {Y1-4} V{Y0} H{X1}"/>')
    for i, (k, e) in enumerate(data):
        x = X0 + i * w + w * 0.18
        cls = "d-bar-warm" if e <= thr else "d-bar"
        hgt = max(Y0 - Y(e), 2)
        b.append(f'<rect class="{cls}"{A("growy", 1.1 + 0.09*i)} x="{f(x)}" y="{f(Y0-hgt)}" width="{f(w*0.64)}" height="{f(hgt)}"/>')
        b.append(f'<text class="d-tick" x="{f(x+w*0.32)}" y="{Y0+16}" text-anchor="middle">{k}</text>')
    b.append(f'<line class="d-thresh"{A("fade", 1.9)} x1="{X0}" y1="{f(Y(thr))}" x2="{X1}" y2="{f(Y(thr))}"/>')
    b.append(f'<text class="d-label d-warm"{A("fade", 1.9)} x="{X1}" y="{f(Y(thr)-8)}" text-anchor="end">ε</text>')
    b.append(f'<text class="d-note" x="{(X0+X1)//2}" y="{Y0+40}" text-anchor="middle">number of queries</text>')
    b.append(f'<text class="d-note" x="{X1}" y="{Y1+8}" text-anchor="end">certified regret</text>')
    b.append(f'<text class="d-tick" x="{f(X0+w*0.5)}" y="{Y1-10}" text-anchor="middle">1.91</text>')
    b.append(f'<path class="d-arrow" d="M226 130 H252"/>' + arrowhead(262, 130))
    return svg("f-data", "A spectral certificate of data sufficiency",
               "Left: an ellipsoid of possible costs; one linear query restricts the cost to a chord, the fiber, and the decision is taken at its center a_y. Right: on 8x8 digit binarization the certified regret falls from 1.91 with no query to 0.15 with 32 queries and 0 with all 64.",
               "".join(b), h=280)

# ---------------------------------------------------------------- 4. ASTP
def fig_sys():
    random.seed(7)
    b = ['<text class="d-label" x="40" y="22">Colocated</text>']
    def ragged(x0, x1, y0, lens, t0):
        out = []
        for r, L in enumerate(lens):
            y = y0 + r * 9
            out.append(f'<rect class="g-roll"{A("growx", t0 + 0.04*r)} x="{x0}" y="{y}" width="{f(L)}" height="6"/>')
            if x0 + L < x1:
                out.append(f'<rect class="g-bubble"{A("fade", t0 + 0.7)} x="{f(x0+L)}" y="{y}" width="{f(x1-x0-L)}" height="6"/>')
        return out
    b += ragged(40, 220, 34, [180, 62, 120, 40, 95, 150], 0)
    b.append(f'<rect class="g-train"{A("growx", 1.0)} x="224" y="34" width="58" height="51"/>')
    b += ragged(286, 470, 34, [70, 184, 110, 52, 140, 90], 1.4)
    b.append(f'<rect class="g-train"{A("growx", 2.4)} x="474" y="34" width="16" height="51"/>')
    b.append('<text class="d-label d-accent" x="40" y="128">ASP</text>')
    for u in range(3):
        y = 140 + u * 28
        x = 40 + u * 9
        while x < 300:
            L = min(random.choice([34, 46, 58, 70]), 300 - x)
            for r in range(2):
                b.append(f'<rect class="g-roll"{A("growx", 0.4 + (x-40)/260*1.6)} x="{f(x)}" y="{y + r*9}" width="{f(L-3+random.uniform(-2, 0))}" height="6"/>')
            x += L
        b.append(f'<path class="d-arrow-thin" d="M304 {y+8} L326 176"/>')
    b.append('<rect class="d-box" x="328" y="148" width="40" height="58" rx="2"/>')
    for s in range(4):
        b.append(f'<rect class="g-roll"{A("pop", 1.0 + 0.3*s)} x="334" y="{192 - s*12}" width="28" height="8"/>')
    b.append('<path class="d-arrow-thin" d="M370 176 H386"/>')
    for s in range(3):
        b.append(f'<rect class="g-train"{A("growx", 1.3 + 0.45*s)} x="{390 + s*34}" y="164" width="32" height="24"/>')
    b.append('<g transform="translate(40 244)">'
             '<rect class="g-roll" width="14" height="10"/><text class="d-note" x="20" y="9">rollout</text>'
             '<rect class="g-train" x="90" width="14" height="10"/><text class="d-note" x="110" y="9">training</text>'
             '<rect class="g-bubble" x="186" width="14" height="10"/><text class="d-note" x="206" y="9">idle</text>'
             '<rect class="d-box" x="252" y="-1" width="12" height="12"/><text class="d-note" x="270" y="9">bounded-lag queue</text></g>')
    return svg("f-sys", "Colocated pipeline versus ASP",
               "Top: in a colocated pipeline each rollout minibatch waits for its longest sequence, leaving idle time before training. Bottom: in ASP several generation units fill length-homogeneous minibatches that feed a bounded-lag queue, and the trainer runs back to back.",
               "".join(b), h=265)

# ---------------------------------------------------------------- 5. Levine hats (scenes)
def hat_scene(name, left, lsay, right, rsay, win):
    """left/right: hats from the head upward, 1 = black."""
    b = []
    cw, ch = 24, 19
    def player(cx, stack, say, side, looks, t0):
        o = []
        base = 176
        top = base - 6 * ch
        o.append(f'<line class="h-dots"{A("fade", t0 + 0.6)} x1="{cx}" y1="{top-6}" x2="{cx}" y2="{top-34}"/>'
                 f'<path class="h-tip"{A("fade", t0 + 0.6)} d="M{cx-5} {top-28} L{cx} {top-36} L{cx+5} {top-28}"/>')
        for k, hat in enumerate(stack):
            y = base - (k + 1) * ch
            o.append(f'<rect class="{"h-black" if hat else "h-white"}"{A("pop", t0 + 0.09*k)} x="{cx-cw/2}" y="{y}" width="{cw}" height="{ch}"/>')
            o.append(f'<path class="h-brim"{A("fade", t0 + 0.09*k)} d="M{cx-cw/2-9} {y+ch} H{cx+cw/2+9}"/>')
        y = base - say * ch
        o.append(f'<rect class="h-pick"{A("pop", 1.7)} x="{cx-cw/2-3}" y="{y-3}" width="{cw+6}" height="{ch+6}" rx="2"/>')
        o.append(f'<circle class="h-head" cx="{cx}" cy="{base+24}" r="24"/>')
        for ex in (-8, 8):
            o.append(f'<circle class="h-eye" cx="{cx+ex}" cy="{base+19}" r="4.5"/>'
                     f'<circle class="h-pupil" cx="{cx+ex+2.2*looks}" cy="{base+17}" r="2"/>')
        o.append(f'<ellipse class="h-mouth" cx="{cx}" cy="{base+34}" rx="4" ry="2.6"/>')
        bx = cx + side * 52
        o.append(f'<g{A("pop", 1.2 + t0)}>')
        o.append(f'<polygon class="h-bubble" points="{bx-side*14},{base+16} {bx-side*2},{base+20} {cx+side*19},{base+30}"/>')
        o.append(f'<ellipse class="h-bubble" cx="{bx}" cy="{base+8}" rx="23" ry="15"/>')
        o.append(f'<polygon class="h-bubble-fill" points="{bx-side*13},{base+15} {bx-side*3},{base+18} {cx+side*17},{base+28}"/>')
        o.append(f'<text class="h-say" x="{bx}" y="{base+14}" text-anchor="middle">{say}</text></g>')
        return o
    b += player(96, left, lsay, -1, 1, 0)
    b += player(244, right, rsay, 1, -1, 0.15)
    return svg(name, "A winning round" if win else "A losing round",
               ("Both players name a black hat on their own head." if win else
                "The second player names hat 1, which is white, so the team loses."),
               "".join(b), h=232, w=340)

def fig_hats():
    lose = hat_scene("f-hl", [1, 0, 0, 1, 0, 1], 4, [0, 1, 1, 0, 0, 1], 1, False)
    win = hat_scene("f-hw", [0, 0, 1, 1, 0, 1], 3, [0, 0, 0, 0, 1, 1], 5, True)
    return ('<div class="levine-grid">'
            f'<div class="levine-tile">{lose}<p>Lost: the second player names a white hat.</p></div>'
            f'<div class="levine-tile">{win}<p>Won: both players name a black hat.</p></div>'
            '<div class="levine-tile"><div class="mask-frame" data-a="fade" style="--d:0.3s"><div class="mask-tile" style="--mask:url(images/levine-s3.png)" role="img" aria-label="Winning region of the recursive strategy S3 in the unit square, a self-similar pattern of area 7/20"></div></div><p>Where 𝒮<sub>3</sub> wins in [0,1]², area 7/20.</p></div>'
            '<div class="levine-tile"><div class="mask-frame" data-a="fade" style="--d:0.6s"><div class="mask-tile" style="--mask:url(images/levine-strategy.png)" role="img" aria-label="Winning region of an arbitrary strategy, made of fans of thin bands"></div></div><p>The same picture for an arbitrary strategy.</p></div>'
            '</div>')

# ---------------------------------------------------------------- 6. complexity vs velocity
def fig_text():
    data = [(2.92, .0993), (5.14, .0379), (7.51, .0153), (10.37, .00857), (13.54, .00540), (17.64, .00039),
            (23.21, .00286), (34.75, .00199), (48.33, .00131), (64.09, .00097), (75.24, .00060), (125.0, .00052),
            (470.8, .00013), (3024, .00002)]
    X0, X1, Y0, Y1 = 66, 500, 232, 20
    cx0, cx1 = math.log10(2), math.log10(5000)
    vy0, vy1 = math.log10(3e-6), math.log10(0.2)
    X = lambda c: X0 + (math.log10(c) - cx0) / (cx1 - cx0) * (X1 - X0)
    Y = lambda v: Y0 - (math.log10(v) - vy0) / (vy1 - vy0) * (Y0 - Y1)
    b = [f'<path class="d-axis" d="M{X0} {Y1} V{Y0} H{X1}"/>']
    for c in (10, 100, 1000):
        b.append(f'<text class="d-tick" x="{f(X(c))}" y="{Y0+17}" text-anchor="middle">{c}</text>')
    for v, lab in ((1e-5, "10⁻⁵"), (1e-4, "10⁻⁴"), (1e-3, "10⁻³"), (1e-2, "10⁻²"), (1e-1, "10⁻¹")):
        b.append(f'<text class="d-tick" x="{X0-8}" y="{f(Y(v)+4)}" text-anchor="end">{lab}</text>')
        b.append(f'<line class="d-gridline" x1="{X0}" y1="{f(Y(v))}" x2="{X1}" y2="{f(Y(v))}"/>')
    fit = lambda c: math.exp(-1.953 - 1.225 * math.log(c))
    b.append(f'<line class="c-warm c-thin"{A("draw", 1.2)} x1="{f(X(2))}" y1="{f(Y(fit(2)))}" x2="{f(X(5000))}" y2="{f(Y(fit(5000)))}"/>')
    for j, (c, v) in enumerate(data):
        b.append(f'<circle class="d-dot-accent"{A("pop", 0.07*j)} cx="{f(X(c))}" cy="{f(Y(v))}" r="5"/>')
    for name, c, v, dx, dy, anc in (("industrials sector", 5.14, .0379, 10, 4, "start"),
                                    ("Mitsubishi Motors", 470.8, .00013, 10, -7, "start"),
                                    ("Comsys Holdings", 3024, .00002, -10, -9, "end")):
        b.append(f'<text class="d-tick"{A("fade", 1.5)} x="{f(X(c)+dx)}" y="{f(Y(v)+dy)}" text-anchor="{anc}">{name}</text>')
    b.append(f'<text class="d-note" x="{(X0+X1)//2}" y="{Y0+42}" text-anchor="middle">complexity</text>')
    b.append(f'<text class="d-note" x="16" y="{(Y0+Y1)//2}" transform="rotate(-90 16 {(Y0+Y1)//2})" text-anchor="middle">velocity</text>')
    b.append(f'<text class="d-key d-warm"{A("fade", 2.0)} x="{X1}" y="{Y1+12}" text-anchor="end" font-size="14">slope −1.23</text>')
    return svg("f-text", "Velocity falls with complexity",
               "Log-log scatter of publication velocity against complexity for 14 markers of the Construction cluster, with the fitted line of slope minus 1.225 and R squared 0.915. Simple markers such as 'industrials sector' are frequent; complex ones such as 'Comsys Holdings' are rare.",
               "".join(b), h=286)

FIGS = {"opt": fig_opt, "rl": fig_rl, "data": fig_data, "sys": fig_sys, "hats": fig_hats, "text": fig_text}

if __name__ == "__main__":
    path = sys.argv[1]
    html = open(path, encoding="utf-8").read()
    for k, fn in FIGS.items():
        html = re.sub(rf"<!--FIG:{k}-->.*?<!--/FIG-->|<!--FIG:{k}-->", lambda m, fn=fn, k=k: f"<!--FIG:{k}-->{fn()}<!--/FIG-->", html, flags=re.S)
    open(path, "w", encoding="utf-8", newline="\n").write(html)
    print("ok")
