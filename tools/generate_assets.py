from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

BG = "#0b0f14"
GREEN = "#39ff14"
CYAN = "#00e5ff"
TEXT = "#c9d1d9"
DIM = "#6e7681"
BORDER = "#30363d"
FONT = "'JetBrains Mono','Fira Code','SF Mono',Menlo,Consolas,'Courier New',monospace"


def defs() -> str:
    return (
        '<defs>'
        '<filter id="glow" x="-20%" y="-60%" width="140%" height="220%">'
        '<feGaussianBlur stdDeviation="2.6" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
        '<rect width="4" height="1" fill="#ffffff" opacity="0.035"/></pattern>'
        f'<linearGradient id="line" x1="0" x2="1"><stop offset="0" stop-color="{GREEN}"/>'
        f'<stop offset="1" stop-color="{CYAN}"/></linearGradient>'
        '</defs>'
    )


def svg(w: int, h: int, body: str, title: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">'
        f'<title id="t">{escape(title)}</title>{defs()}{body}</svg>\n'
    )


def text(x, y, size, fill, content, extra="") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'fill="{fill}" {extra}>{escape(content)}</text>'
    )


def save(name: str, content: str) -> None:
    (OUT / name).write_text(content, encoding="utf-8")
    print("✔", name)


def panel(w: int, h: int, radius: int = 12) -> str:
    return (
        f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{radius}" fill="{BG}" '
        f'stroke="{GREEN}" stroke-opacity=".45"/>'
        f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{radius}" fill="url(#scan)"/>'
    )


def title_bar(w: int, label: str) -> str:
    return (
        f'<rect x="1" y="1" width="{w-2}" height="38" rx="12" fill="#111820"/>'
        f'<rect x="1" y="26" width="{w-2}" height="14" fill="#111820"/>'
        '<circle cx="24" cy="20" r="6" fill="#ff5f56"/>'
        '<circle cx="46" cy="20" r="6" fill="#ffbd2e"/>'
        '<circle cx="68" cy="20" r="6" fill="#27c93f"/>'
        + text(450, 25, 13, DIM, label, 'text-anchor="middle"')
    )


def typed(cid, x, y, size, segs, begin, per, bold=False, glow=False, pad=12):
    cw = size * 0.6
    n = sum(len(t) for t, _ in segs)
    vals = ";".join(f"{pad + i * cw:.1f}" for i in range(n)) + f";{pad * 2 + n * cw:.1f}"
    kt = ";".join(f"{i / n:.4f}" for i in range(n + 1))
    clip = (
        f'<clipPath id="{cid}"><rect x="{x - pad}" y="{y - size - 6}" width="{pad}" '
        f'height="{size * 1.8:.0f}"><animate attributeName="width" values="{vals}" '
        f'keyTimes="{kt}" calcMode="discrete" dur="{n * per:.2f}s" begin="{begin:.2f}s" '
        'fill="freeze"/></rect></clipPath>'
    )
    tsp = "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for t, c in segs)
    attrs = f'font-family="{FONT}" font-size="{size}" '
    attrs += 'font-weight="700" ' if bold else ""
    attrs += 'filter="url(#glow)" ' if glow else ""
    node = f'<text x="{x}" y="{y}" {attrs}clip-path="url(#{cid})" xml:space="preserve">{tsp}</text>'
    return clip, node, begin + n * per


def header():
    W, H = 900, 300
    prompt = [("andres@maldonado", GREEN), (":", DIM), ("~", CYAN)]
    lines = [
        ("c1", 40, 100, 20, prompt + [(" $ whoami", TEXT)], 0.4, 0.05, False, False),
        ("c2", 40, 154, 44, [("Andrés Maldonado", GREEN)], 2.0, 0.08, True, True),
        ("c3", 40, 194, 20, [("> ", DIM), ("Systems & Computer Engineer", CYAN)], 3.5, 0.03, False, False),
        ("c4", 40, 228, 20, [("> ", DIM), ("Backend · DevOps · Cloud · Cybersecurity", TEXT)], 4.8, 0.03, False, False),
    ]
    clips, nodes, end = "", "", 0
    for cid, x, y, size, segs, begin, per, bold, glow in lines:
        c, n, e = typed(cid, x, y, size, segs, begin, per, bold, glow)
        clips += c
        nodes += n
        end = max(end, e)
    t0 = end + 0.2
    prompt_txt = "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for t, c in prompt + [(" $ ", TEXT)])
    final = (
        f'<text x="40" y="270" font-family="{FONT}" font-size="20" opacity="0" xml:space="preserve">{prompt_txt}'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.01s" begin="{t0:.2f}s" fill="freeze"/></text>'
        f'<rect x="{40 + 21 * 12 + 2}" y="253" width="11" height="22" fill="{GREEN}" opacity="0">'
        f'<animate attributeName="opacity" values="1;0;1" dur="1s" begin="{t0:.2f}s" repeatCount="indefinite"/></rect>'
    )
    body = (
        f'<defs>{clips}</defs>'
        + panel(W, H)
        + title_bar(W, "andres@maldonado: ~")
        + nodes
        + final
    )
    save("header.svg", svg(W, H, body, "Andrés Maldonado, Systems & Computer Engineer: Backend, DevOps, Cloud and Cybersecurity"))


def about_card():
    W = 900
    rows = [
        ("name", "Andrés Maldonado"),
        ("role", "Systems & Computer Engineer"),
        ("focus", "Backend · DevOps · Cloud"),
        ("learning", "Applied cybersecurity: labs and a home SOC"),
        ("now", "Grownet: AWS architecture and secure CI/CD"),
        ("languages", "Spanish (native) · English B2"),
    ]
    y0, step = 112, 34
    H = y0 + step * len(rows) + 10
    body = panel(W, H) + title_bar(W, "~/about.sh")
    body += text(40, 82, 18, GREEN, "$", "font-weight=\"700\"") + text(62, 82, 18, TEXT, "cat about.txt")
    for i, (k, v) in enumerate(rows):
        y = y0 + i * step
        body += text(40, y, 17, CYAN, f"{k:<12}", 'xml:space="preserve"')
        body += text(190, y, 17, DIM, "=")
        body += text(214, y, 17, TEXT if i else GREEN, v, 'font-weight="700"' if i == 0 else "")
    save("about-card.svg", svg(W, H, body, "Summary: " + "; ".join(f"{k}: {v}" for k, v in rows)))


def banner(fname: str, title: str, cmd: str):
    W, H = 900, 60
    body = (
        panel(W, H, 10)
        + f'<rect x="22" y="26" width="8" height="8" fill="{GREEN}">'
        '<animate attributeName="opacity" values="1;0.2;1" dur="1.6s" repeatCount="indefinite"/></rect>'
        + text(46, 39, 24, GREEN, f"~/{title}", 'font-weight="700" filter="url(#glow)"')
        + text(872, 36, 14, DIM, f"// {cmd}", 'text-anchor="end"')
    )
    save(fname, svg(W, H, body, f"Section: {title}"))


def divider():
    W, H = 900, 24
    body = (
        f'<line x1="0" y1="12" x2="{W}" y2="12" stroke="url(#line)" stroke-width="2" opacity=".8"/>'
        f'<circle cy="12" r="4" fill="{GREEN}" filter="url(#glow)" cx="0">'
        f'<animate attributeName="cx" from="0" to="{W}" dur="6s" repeatCount="indefinite"/></circle>'
    )
    save("divider.svg", svg(W, H, body, "Divider"))


def chips(fname: str, title: str, items):
    CH, GAP, MAXW, CW = 36, 12, 860, 9.2
    rows, cur, curw = [], [], 0.0
    for label, color, primary in items:
        w = len(label) * CW + 52
        add = w if not cur else w + GAP
        if cur and curw + add > MAXW:
            rows.append((cur, curw))
            cur, curw, add = [], 0.0, w
        cur.append((label, color, primary, w))
        curw += add
    rows.append((cur, curw))

    W = 900
    H = len(rows) * (CH + GAP) + 4
    body = ""
    for r, (row, rw) in enumerate(rows):
        x = (W - rw) / 2
        y = 2 + r * (CH + GAP)
        for label, color, primary, w in row:
            body += f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{CH}" rx="18" fill="#0d1117"/>'
            if primary:
                body += (
                    f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{CH}" rx="18" fill="{color}" '
                    f'fill-opacity=".14" stroke="{color}" stroke-width="1.5" filter="url(#glow)"/>'
                )
            else:
                body += f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{CH}" rx="18" fill="none" stroke="{BORDER}" stroke-width="1.2"/>'
            body += f'<circle cx="{x + 20:.1f}" cy="{y + CH / 2}" r="5" fill="{color}"/>'
            body += text(f"{x + 34:.1f}", y + 23, 14, "#ffffff" if primary else TEXT, label,
                         'font-weight="700"' if primary else "")
            x += w + GAP
    save(fname, svg(W, H, body, f"{title}: " + ", ".join(i[0] for i in items)))


def button(fname: str, label: str, sub: str):
    W, H = 280, 56
    body = (
        f'<rect x="1.5" y="1.5" width="{W-3}" height="{H-3}" rx="28" fill="{BG}" stroke="{GREEN}" stroke-width="1.5"/>'
        + text(W / 2, 24, 15, GREEN, label, 'text-anchor="middle" font-weight="700"')
        + text(W / 2, 43, 12, TEXT, sub, 'text-anchor="middle"')
    )
    save(fname, svg(W, H, body, f"{label}: {sub}"))


if __name__ == "__main__":
    header()
    about_card()
    divider()

    banner("about-me.svg", "about-me", "whoami")
    banner("stack.svg", "stack", "docker ps")
    banner("experience.svg", "experience", "git log --oneline")
    banner("security.svg", "security", "nmap -sV localhost")
    banner("projects.svg", "projects", "ls ~/projects")
    banner("education.svg", "education", "cat roadmap.md")
    banner("stats.svg", "stats", "gh stats")
    banner("activity.svg", "activity", "git log --graph")
    banner("contact.svg", "contact", "ssh hello@andres")

    chips("stack-backend.svg", "Backend & web", [
        ("Java", "#f89820", True), ("Spring Boot", "#6db33f", True),
        ("TypeScript", "#3178c6", True), ("NestJS", "#e0234e", True),
        ("Node.js", "#5fa04e", True), ("Python", "#ffd43b", True),
        ("FastAPI", "#009688", False), ("Flask", "#cfd8dc", False),
        ("C# / .NET", "#9b4f96", False), ("PHP", "#777bb4", False),
        ("JavaScript", "#f7df1e", False), ("Next.js", "#ffffff", False),
    ])
    chips("stack-databases.svg", "Databases", [
        ("PostgreSQL", "#4169e1", True), ("Redis", "#dc382d", True),
        ("MySQL", "#4479a1", False), ("MongoDB", "#47a248", False),
        ("Oracle", "#f80000", False), ("Cosmos DB", "#0078d4", False),
        ("DynamoDB", "#4053d6", False),
    ])
    chips("stack-devops.svg", "DevOps & cloud", [
        ("Docker", "#2496ed", True), ("GitHub Actions", "#2088ff", True),
        ("AWS", "#ff9900", True), ("Azure", "#0078d4", True),
        ("Nginx", "#009639", False), ("Grafana", "#f46800", False),
        ("KQL", "#0078d4", False), ("Terraform · in progress", "#844fba", False),
    ])
    chips("stack-security.svg", "Security", [
        ("OWASP", CYAN, True), ("JWT", "#d63aff", True), ("OTP", "#ff2bd6", True),
        ("Dependency auditing", "#ffbd2e", True),
        ("Kali Linux", "#557c94", False), ("Burp Suite", "#ff6633", False),
        ("Nmap", "#4682b4", False), ("sqlmap", "#c9d1d9", False),
        ("Wireshark · basic", "#1679a7", False), ("Splunk · basic", "#65a637", False),
    ])

    button("contact-linkedin.svg", "LinkedIn", "/in/amaldonados")
    button("contact-email.svg", "Email", "andresmaldonado200338@gmail.com")
    button("contact-github.svg", "GitHub", "/maldoA10")
