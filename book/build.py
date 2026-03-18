#!/usr/bin/env python3
"""Build PDF and Web viewer from book chapters and SVG assets."""

import subprocess
import sys
from pathlib import Path

BOOK_DIR = Path(__file__).parent
CHAPTERS_DIR = BOOK_DIR / "chapters"
ASSETS_DIR = BOOK_DIR / "assets"
OUTPUT_DIR = BOOK_DIR / "output"
PDF_DIR = OUTPUT_DIR / "pdf"
WEB_DIR = OUTPUT_DIR / "web"

CHAPTER_FILES = [
    "ch01-agent-and-skill.md",
    "ch02-harness-concept.md",
    "ch03-architecture-patterns.md",
    "ch04-writing-agents.md",
    "ch05-writing-skills.md",
    "ch06-orchestrator-skill.md",
    "ch07-case-book-writing.md",
    "ch08-case-research-team.md",
    "ch09-case-code-generation.md",
    "ch10-harness-meta-skill.md",
    "ch11-debugging.md",
    "ch12-design-your-own.md",
]

# Map SVG files to chapters
SVG_MAP = {
    "ch01": "infographic-ch01-agent-vs-skill.svg",
    "ch02": "infographic-ch02-harness-overview.svg",
    "ch03": "infographic-ch03-architecture-patterns.svg",
    "ch06": "infographic-ch06-orchestrator-flow.svg",
    "ch07": "infographic-ch07-book-writer-architecture.svg",
    "ch08": "infographic-ch08-fanout-fanin-flow.svg",
    "ch12": "infographic-ch12-design-process.svg",
}

SVG_TITLES = {
    "ch01": "Agent vs Skill 비교 다이어그램",
    "ch02": "하네스 구성 요소 전체 맵",
    "ch03": "4가지 패턴 흐름도 + 선택 가이드",
    "ch06": "오케스트레이터 실행 흐름도",
    "ch07": "book-writer 하네스 전체 아키텍처",
    "ch08": "팬아웃/팬인 데이터 흐름도",
    "ch12": "하네스 설계 전체 프로세스 요약",
}


def read_svg(filename: str) -> str:
    svg_path = ASSETS_DIR / filename
    return svg_path.read_text(encoding="utf-8")


def build_combined_markdown() -> str:
    """Combine all chapters with SVG insertions into a single markdown."""
    parts = []
    for ch_file in CHAPTER_FILES:
        ch_key = ch_file[:4]  # e.g., "ch01"
        content = (CHAPTERS_DIR / ch_file).read_text(encoding="utf-8")
        parts.append(content)

        # Insert SVG after chapter content if mapped
        if ch_key in SVG_MAP:
            svg_content = read_svg(SVG_MAP[ch_key])
            title = SVG_TITLES.get(ch_key, "인포그래픽")
            parts.append(f"\n\n### 인포그래픽: {title}\n\n{svg_content}\n\n")

        parts.append("\n\n---\n\n")

    return "\n".join(parts)


def build_pdf_html(combined_md: str) -> str:
    """Convert combined markdown to HTML for PDF via pandoc, then wrap with styles."""
    # Use pandoc to convert markdown to HTML fragment
    result = subprocess.run(
        [
            "pandoc",
            "-f", "markdown",
            "-t", "html5",
            "--highlight-style=tango",
            "--wrap=none",
        ],
        input=combined_md,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"pandoc error: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    body_html = result.stdout
    return body_html


def build_pdf():
    """Build PDF using pandoc -> HTML -> weasyprint."""
    print("Building PDF...")
    combined_md = build_combined_markdown()
    body_html = build_pdf_html(combined_md)

    # Read all SVGs for inline embedding (already in body_html via markdown)
    cover_html = """
    <div class="cover-page">
        <div class="cover-content">
            <h1 class="cover-title">하네스 엔지니어링 실전 가이드</h1>
            <p class="cover-subtitle">Claude Code의 Agent + Skill 구조를 활용한 자동화 체계 구축법</p>
            <div class="cover-divider"></div>
            <p class="cover-author">AI-Assisted Publication</p>
        </div>
    </div>
    """

    full_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
@page {{
    size: A4;
    margin: 2.5cm 2cm 2.5cm 2cm;
    @top-center {{
        content: "하네스 엔지니어링 실전 가이드";
        font-size: 9pt;
        color: #888;
    }}
    @bottom-center {{
        content: counter(page);
        font-size: 9pt;
        color: #888;
    }}
}}
@page :first {{
    @top-center {{ content: none; }}
    @bottom-center {{ content: none; }}
    margin: 0;
}}
body {{
    font-family: -apple-system, "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic", sans-serif;
    font-size: 11pt;
    line-height: 1.8;
    color: #1a1a1a;
}}
.cover-page {{
    page: cover;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    background: linear-gradient(135deg, #1e3a5f 0%, #2c5f8a 100%);
    color: white;
    text-align: center;
    page-break-after: always;
}}
.cover-content {{
    padding: 3cm;
}}
.cover-title {{
    font-size: 32pt;
    font-weight: 700;
    margin-bottom: 0.5em;
    line-height: 1.3;
}}
.cover-subtitle {{
    font-size: 14pt;
    font-weight: 300;
    opacity: 0.9;
    margin-bottom: 2em;
}}
.cover-divider {{
    width: 100px;
    height: 3px;
    background: rgba(255,255,255,0.5);
    margin: 1.5em auto;
}}
.cover-author {{
    font-size: 12pt;
    opacity: 0.7;
}}
h1 {{
    font-size: 22pt;
    color: #1e3a5f;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    page-break-before: always;
    border-bottom: 2px solid #1e3a5f;
    padding-bottom: 0.3em;
}}
h1:first-of-type {{
    page-break-before: auto;
}}
h2 {{
    font-size: 16pt;
    color: #2c5f8a;
    margin-top: 1.2em;
    margin-bottom: 0.4em;
}}
h3 {{
    font-size: 13pt;
    color: #3a7ca5;
    margin-top: 1em;
    margin-bottom: 0.3em;
}}
h4 {{
    font-size: 11.5pt;
    color: #4a8cb5;
    margin-top: 0.8em;
}}
p {{
    margin: 0.5em 0;
    text-align: justify;
}}
code {{
    background: #f4f4f4;
    padding: 0.15em 0.4em;
    border-radius: 3px;
    font-family: "SF Mono", "Fira Code", "Consolas", monospace;
    font-size: 0.9em;
    color: #c7254e;
}}
pre {{
    background: #282c34;
    color: #abb2bf;
    padding: 1em;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 9.5pt;
    line-height: 1.5;
    margin: 1em 0;
    page-break-inside: avoid;
}}
pre code {{
    background: none;
    color: inherit;
    padding: 0;
    font-size: inherit;
}}
blockquote {{
    border-left: 4px solid #3a7ca5;
    margin: 1em 0;
    padding: 0.5em 1em;
    background: #f0f7fc;
    color: #333;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    font-size: 10pt;
    page-break-inside: avoid;
}}
th, td {{
    border: 1px solid #ddd;
    padding: 0.5em 0.8em;
    text-align: left;
}}
th {{
    background: #f0f7fc;
    color: #1e3a5f;
    font-weight: 600;
}}
tr:nth-child(even) {{
    background: #fafafa;
}}
hr {{
    border: none;
    border-top: 1px solid #ddd;
    margin: 2em 0;
}}
svg {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1.5em auto;
    page-break-inside: avoid;
}}
ul, ol {{
    margin: 0.5em 0;
    padding-left: 1.5em;
}}
li {{
    margin: 0.2em 0;
}}
strong {{
    color: #1e3a5f;
}}
</style>
</head>
<body>
{cover_html}
{body_html}
</body>
</html>"""

    html_path = PDF_DIR / "harness-engineering-guide.html"
    html_path.write_text(full_html, encoding="utf-8")

    # Convert HTML to PDF using weasyprint
    pdf_path = PDF_DIR / "harness-engineering-guide.pdf"
    subprocess.run(
        ["weasyprint", str(html_path), str(pdf_path)],
        check=True,
    )
    print(f"PDF created: {pdf_path}")


def build_web():
    """Build single-page web viewer with chapter navigation."""
    print("Building web viewer...")
    combined_md = build_combined_markdown()

    # Convert each chapter separately for navigation
    chapters_html = []
    toc_items = []

    for i, ch_file in enumerate(CHAPTER_FILES):
        ch_key = ch_file[:4]
        content = (CHAPTERS_DIR / ch_file).read_text(encoding="utf-8")

        # Extract chapter title
        first_line = content.strip().split("\n")[0]
        title = first_line.lstrip("# ").strip()

        # Add SVG if mapped
        if ch_key in SVG_MAP:
            svg_content = read_svg(SVG_MAP[ch_key])
            svg_title = SVG_TITLES.get(ch_key, "인포그래픽")
            content += f"\n\n### 인포그래픽: {svg_title}\n\n{svg_content}\n\n"

        # Convert to HTML
        result = subprocess.run(
            [
                "pandoc",
                "-f", "markdown",
                "-t", "html5",
                "--highlight-style=tango",
                "--wrap=none",
            ],
            input=content,
            capture_output=True,
            text=True,
        )
        ch_html = result.stdout
        ch_id = f"chapter-{i+1}"
        chapters_html.append(f'<section id="{ch_id}" class="chapter">{ch_html}</section>')
        short_title = title.split(":")[0] if ":" in title else title
        toc_items.append(f'<a href="#{ch_id}" onclick="showChapter({i})">{short_title}</a>')

    toc_html = "\n".join(toc_items)
    chapters_joined = "\n".join(chapters_html)

    web_html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>하네스 엔지니어링 실전 가이드</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<style>
:root {{
    --bg: #ffffff;
    --text: #1a1a1a;
    --text-secondary: #555;
    --sidebar-bg: #f8f9fa;
    --sidebar-border: #e0e0e0;
    --accent: #1e3a5f;
    --accent-light: #2c5f8a;
    --code-bg: #282c34;
    --code-text: #abb2bf;
    --blockquote-bg: #f0f7fc;
    --table-header: #f0f7fc;
    --table-border: #ddd;
    --table-stripe: #fafafa;
    --link: #2c5f8a;
    --nav-active: #1e3a5f;
    --nav-active-text: #fff;
    --cover-from: #1e3a5f;
    --cover-to: #2c5f8a;
}}
[data-theme="dark"] {{
    --bg: #1a1a2e;
    --text: #e0e0e0;
    --text-secondary: #aaa;
    --sidebar-bg: #16213e;
    --sidebar-border: #2a3a5c;
    --accent: #7ec8e3;
    --accent-light: #a8d8ea;
    --code-bg: #0f0f23;
    --code-text: #ccc;
    --blockquote-bg: #1a2744;
    --table-header: #1a2744;
    --table-border: #2a3a5c;
    --table-stripe: #1e2a47;
    --link: #7ec8e3;
    --nav-active: #7ec8e3;
    --nav-active-text: #1a1a2e;
    --cover-from: #0f0f23;
    --cover-to: #1a2744;
}}
* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}
body {{
    font-family: -apple-system, "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.8;
    display: flex;
    min-height: 100vh;
    transition: background 0.3s, color 0.3s;
}}
/* Sidebar */
.sidebar {{
    width: 280px;
    min-width: 280px;
    background: var(--sidebar-bg);
    border-right: 1px solid var(--sidebar-border);
    height: 100vh;
    position: fixed;
    overflow-y: auto;
    z-index: 100;
    transition: transform 0.3s, background 0.3s;
}}
.sidebar-header {{
    padding: 1.5em 1em 1em;
    border-bottom: 1px solid var(--sidebar-border);
}}
.sidebar-header h2 {{
    font-size: 1em;
    color: var(--accent);
    line-height: 1.4;
}}
.sidebar-header p {{
    font-size: 0.75em;
    color: var(--text-secondary);
    margin-top: 0.3em;
}}
.sidebar nav {{
    padding: 0.5em 0;
}}
.sidebar nav a {{
    display: block;
    padding: 0.6em 1.2em;
    text-decoration: none;
    color: var(--text);
    font-size: 0.85em;
    border-left: 3px solid transparent;
    transition: all 0.2s;
}}
.sidebar nav a:hover {{
    background: rgba(30, 58, 95, 0.08);
    border-left-color: var(--accent);
}}
.sidebar nav a.active {{
    background: var(--nav-active);
    color: var(--nav-active-text);
    border-left-color: var(--nav-active);
    font-weight: 600;
}}
.sidebar-footer {{
    padding: 1em;
    border-top: 1px solid var(--sidebar-border);
    display: flex;
    gap: 0.5em;
    align-items: center;
}}
.theme-toggle {{
    background: none;
    border: 1px solid var(--sidebar-border);
    padding: 0.4em 0.8em;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8em;
    color: var(--text);
    transition: all 0.2s;
}}
.theme-toggle:hover {{
    border-color: var(--accent);
}}
/* Main Content */
.main {{
    margin-left: 280px;
    flex: 1;
    max-width: 900px;
    padding: 2em 3em 4em;
}}
/* Chapter styles */
.chapter {{
    display: none;
}}
.chapter.active {{
    display: block;
    animation: fadeIn 0.3s ease;
}}
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
/* Typography */
h1 {{
    font-size: 1.8em;
    color: var(--accent);
    margin: 0.8em 0 0.4em;
    border-bottom: 2px solid var(--accent);
    padding-bottom: 0.2em;
}}
h2 {{
    font-size: 1.4em;
    color: var(--accent-light);
    margin: 1.2em 0 0.4em;
}}
h3 {{
    font-size: 1.15em;
    color: var(--accent-light);
    margin: 1em 0 0.3em;
}}
h4 {{
    font-size: 1.05em;
    margin: 0.8em 0 0.2em;
}}
p {{
    margin: 0.6em 0;
}}
a {{
    color: var(--link);
}}
code {{
    background: var(--code-bg);
    color: #e06c75;
    padding: 0.15em 0.4em;
    border-radius: 3px;
    font-family: "SF Mono", "Fira Code", "Consolas", monospace;
    font-size: 0.88em;
}}
pre {{
    background: var(--code-bg);
    color: var(--code-text);
    padding: 1.2em;
    border-radius: 8px;
    overflow-x: auto;
    font-size: 0.88em;
    line-height: 1.6;
    margin: 1em 0;
}}
pre code {{
    background: none;
    color: inherit;
    padding: 0;
}}
blockquote {{
    border-left: 4px solid var(--accent);
    padding: 0.6em 1.2em;
    margin: 1em 0;
    background: var(--blockquote-bg);
    border-radius: 0 6px 6px 0;
}}
table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    font-size: 0.9em;
}}
th, td {{
    border: 1px solid var(--table-border);
    padding: 0.5em 0.8em;
    text-align: left;
}}
th {{
    background: var(--table-header);
    color: var(--accent);
    font-weight: 600;
}}
tr:nth-child(even) {{
    background: var(--table-stripe);
}}
hr {{
    border: none;
    border-top: 1px solid var(--sidebar-border);
    margin: 2em 0;
}}
ul, ol {{
    margin: 0.5em 0;
    padding-left: 1.5em;
}}
li {{
    margin: 0.2em 0;
}}
strong {{
    color: var(--accent);
}}
svg {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1.5em auto;
    border-radius: 8px;
}}
/* Navigation buttons */
.chapter-nav {{
    display: flex;
    justify-content: space-between;
    margin-top: 3em;
    padding-top: 1.5em;
    border-top: 1px solid var(--sidebar-border);
}}
.chapter-nav button {{
    background: var(--accent);
    color: white;
    border: none;
    padding: 0.6em 1.5em;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9em;
    transition: opacity 0.2s;
}}
.chapter-nav button:hover {{
    opacity: 0.85;
}}
.chapter-nav button:disabled {{
    opacity: 0.3;
    cursor: default;
}}
/* Mobile */
.menu-toggle {{
    display: none;
    position: fixed;
    top: 1em;
    left: 1em;
    z-index: 200;
    background: var(--accent);
    color: white;
    border: none;
    padding: 0.5em 0.8em;
    border-radius: 6px;
    font-size: 1.2em;
    cursor: pointer;
}}
@media (max-width: 768px) {{
    .sidebar {{
        transform: translateX(-100%);
    }}
    .sidebar.open {{
        transform: translateX(0);
    }}
    .main {{
        margin-left: 0;
        padding: 1.5em 1.2em 3em;
    }}
    .menu-toggle {{
        display: block;
    }}
    h1 {{
        font-size: 1.4em;
        margin-top: 2em;
    }}
}}
</style>
</head>
<body>
<button class="menu-toggle" onclick="toggleSidebar()">&#9776;</button>
<aside class="sidebar" id="sidebar">
    <div class="sidebar-header">
        <h2>하네스 엔지니어링 실전 가이드</h2>
        <p>Claude Code Agent + Skill 자동화</p>
    </div>
    <nav id="toc">
        {toc_html}
    </nav>
    <div class="sidebar-footer">
        <button class="theme-toggle" onclick="toggleTheme()">Dark Mode</button>
    </div>
</aside>
<main class="main">
    {chapters_joined}
</main>
<script>
hljs.highlightAll();

const chapters = document.querySelectorAll('.chapter');
const tocLinks = document.querySelectorAll('#toc a');
let currentChapter = 0;

function showChapter(index) {{
    chapters.forEach(c => c.classList.remove('active'));
    tocLinks.forEach(a => a.classList.remove('active'));
    chapters[index].classList.add('active');
    tocLinks[index].classList.add('active');
    currentChapter = index;
    window.scrollTo(0, 0);
    // Close sidebar on mobile
    document.getElementById('sidebar').classList.remove('open');
    // Add nav buttons
    addNavButtons(index);
}}

function addNavButtons(index) {{
    // Remove existing nav
    const existing = document.querySelector('.chapter.active .chapter-nav');
    if (existing) existing.remove();

    const nav = document.createElement('div');
    nav.className = 'chapter-nav';

    const prevBtn = document.createElement('button');
    prevBtn.textContent = 'Prev';
    prevBtn.disabled = index === 0;
    prevBtn.onclick = () => showChapter(index - 1);

    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Next';
    nextBtn.disabled = index === chapters.length - 1;
    nextBtn.onclick = () => showChapter(index + 1);

    nav.appendChild(prevBtn);
    nav.appendChild(nextBtn);
    chapters[index].appendChild(nav);
}}

function toggleSidebar() {{
    document.getElementById('sidebar').classList.toggle('open');
}}

function toggleTheme() {{
    const body = document.body;
    const btn = document.querySelector('.theme-toggle');
    if (body.getAttribute('data-theme') === 'dark') {{
        body.removeAttribute('data-theme');
        btn.textContent = 'Dark Mode';
        localStorage.setItem('theme', 'light');
    }} else {{
        body.setAttribute('data-theme', 'dark');
        btn.textContent = 'Light Mode';
        localStorage.setItem('theme', 'dark');
    }}
}}

// Init
if (localStorage.getItem('theme') === 'dark') {{
    document.body.setAttribute('data-theme', 'dark');
    document.querySelector('.theme-toggle').textContent = 'Light Mode';
}}
showChapter(0);

// Keyboard navigation
document.addEventListener('keydown', (e) => {{
    if (e.key === 'ArrowRight' && currentChapter < chapters.length - 1) {{
        showChapter(currentChapter + 1);
    }} else if (e.key === 'ArrowLeft' && currentChapter > 0) {{
        showChapter(currentChapter - 1);
    }}
}});
</script>
</body>
</html>"""

    web_path = WEB_DIR / "index.html"
    web_path.write_text(web_html, encoding="utf-8")
    print(f"Web viewer created: {web_path}")


if __name__ == "__main__":
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    WEB_DIR.mkdir(parents=True, exist_ok=True)

    build_web()
    build_pdf()
    print("\nDone!")
