from math import cos, sin, pi, sqrt
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STEPS = 540
STRANDS = 56
PALETTES = {
    "light": {"paper": "#f6f4ee", "ink": "#264b47", "accent": "#bd5935"},
    "dark": {"paper": "#121a1c", "ink": "#a5c9bb", "accent": "#ed9b73"},
}


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def scale(v, amount):
    return tuple(x * amount for x in v)


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def unit(v):
    return scale(v, 1 / sqrt(sum(x * x for x in v)))


def centre(t):
    return ((2 + cos(3 * t)) * cos(2 * t), (2 + cos(3 * t)) * sin(2 * t), sin(3 * t))


def frame(t):
    tangent = unit(tuple(b - a for a, b in zip(centre(t - 0.0001), centre(t + 0.0001))))
    normal = unit(cross(tangent, (cos(2 * t), sin(2 * t), 0)))
    return normal, cross(tangent, normal)


def project(v):
    x, y, z = v
    y, z = y * cos(0.86) - z * sin(0.86), y * sin(0.86) + z * cos(0.86)
    x, z = x * cos(-0.24) + z * sin(-0.24), -x * sin(-0.24) + z * cos(-0.24)
    x, y = x * cos(-0.20) - y * sin(-0.20), x * sin(-0.20) + y * cos(-0.20)
    return 580 + x * 118, 240 - y * 65


def strand_path(index):
    angle = 2 * pi * index / STRANDS
    points = []
    for step in range(STEPS + 1):
        t = 2 * pi * step / STEPS
        normal, binormal = frame(t)
        offset = add(scale(normal, 0.43 * cos(angle)), scale(binormal, 0.43 * sin(angle)))
        points.append(project(add(centre(t), offset)))
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points) + "Z"


def render(palette, mobile, paths):
    viewbox = "160 0 880 480" if mobile else "0 0 1200 480"
    background = f'<rect x="0" y="-20" width="1200" height="540" fill="{palette["paper"]}"/>'
    strokes = []
    for index, path in enumerate(paths):
        accent = 10 <= index <= 21
        colour = palette["accent"] if accent else palette["ink"]
        opacity = "0.88" if accent else "0.58"
        strokes.append(f'<path d="{path}" stroke="{colour}" opacity="{opacity}"/>')
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" role="img" '
        'aria-labelledby="title desc">\n'
        '<title id="title">Continuity — a (2, 3) torus knot</title>\n'
        '<desc id="desc">Fifty-six fine strands trace a continuous mathematical knot in deep green and copper.</desc>\n'
        f'{background}\n'
        '<g fill="none" stroke-width="0.85" stroke-linejoin="round" stroke-linecap="round">\n'
        + "\n".join(strokes)
        + '\n</g>\n</svg>\n'
    )


if __name__ == "__main__":
    paths = [strand_path(index) for index in range(STRANDS)]
    destination = ROOT / "assets"
    destination.mkdir(exist_ok=True)
    for theme, palette in PALETTES.items():
        for mobile in (False, True):
            suffix = "-mobile" if mobile else ""
            output = destination / f"continuity-{theme}{suffix}.svg"
            output.write_text(render(palette, mobile, paths), encoding="utf-8", newline="\n")
            print(output.relative_to(ROOT))
