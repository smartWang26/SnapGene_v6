#!/usr/bin/env python3
"""Generate Download_SG.html from downloadable files beside this script.

Usage on macOS:
  cd /Users/wang/Desktop/snapgene
  python3 build_download_page.py
"""
from __future__ import annotations

from datetime import datetime
import argparse
from html import escape
from pathlib import Path
from urllib.parse import quote
import sys

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / 'Download_SG.html'
INDEX = ROOT / 'index.html'
EXCLUDE_FILES = {'build_download_page.py', 'Download_SG.html', 'index.html', '.nojekyll', '.DS_Store', 'README-部署.txt'}
EXCLUDE_DIRS = {'.git', '.svn', '__pycache__', '.venv', 'node_modules'}


def human_size(num: int) -> str:
    value = float(num)
    for unit in ('B', 'KB', 'MB', 'GB', 'TB'):
        if value < 1024 or unit == 'TB':
            return f'{value:.0f} {unit}' if unit == 'B' else f'{value:.1f} {unit}'
        value /= 1024
    return f'{value:.1f} TB'


def gather_files() -> list[tuple[Path, int]]:
    items = []
    for p in ROOT.rglob('*'):
        if p.is_symlink() or not p.is_file():
            continue
        rel = p.relative_to(ROOT)
        if p.name in EXCLUDE_FILES or any(part.startswith('.') or part in EXCLUDE_DIRS for part in rel.parts):
            continue
        try:
            size = p.stat().st_size
        except OSError:
            continue
        items.append((rel, size))
    return sorted(items, key=lambda item: str(item[0]).casefold())


def render_row(rel: Path, size: int, base_url: str = "") -> str:
    name = escape(rel.name)
    folder = escape(str(rel.parent)) if str(rel.parent) != '.' else '根目录'
    ext = rel.suffix[1:].upper() if rel.suffix else '文件'
    ext = escape(ext[:10])
    # Percent-encode each component while retaining / for subdirectories.
    href = base_url.rstrip('/') + '/' + quote(rel.as_posix(), safe='/') if base_url else quote(rel.as_posix(), safe='/')
    searchable = escape(f'{rel.name} {rel.parent} {ext}'.lower(), quote=True)
    return f'''<article class="file" data-search="{searchable}">
      <div class="file-symbol" aria-hidden="true">{ext}</div>
      <div class="details">
        <div class="file-name" title="{escape(rel.as_posix(), quote=True)}">{name}</div>
        <div class="meta"><span>{folder}</span><span>{human_size(size)}</span></div>
      </div>
      <a class="download" href="{escape(href, quote=True)}" download="{escape(rel.name, quote=True)}" aria-label="下载 {name}">下载 <span aria-hidden="true">↓</span></a>
    </article>'''


def render(files: list[tuple[Path, int]], base_url: str = "") -> str:
    rows = '\n'.join(render_row(rel, size, base_url) for rel, size in files)
    total = human_size(sum(size for _, size in files))
    updated = datetime.now().strftime('%Y-%m-%d %H:%M')
    if not rows:
        rows = '<div class="empty" id="no-files">当前没有可下载文件。请把文件放到本网页所在文件夹，再运行生成脚本。</div>'
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="color-scheme" content="light" />
  <title>SnapGene 资源下载</title>
  <style>
    :root {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; color: #1a2440; background: #f5f7fb; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; }}
    .hero {{ background: linear-gradient(120deg, #142a52, #245ba5); color: white; padding: 64px 24px 100px; }}
    .container {{ max-width: 960px; margin: auto; }}
    .eyebrow {{ display: inline-block; color: #c9dcff; background: #ffffff1f; border: 1px solid #ffffff2b; padding: 8px 13px; border-radius: 99px; font-size: 13px; }}
    h1 {{ font-size: clamp(32px, 5vw, 45px); letter-spacing: -.6px; margin: 22px 0 12px; }}
    .subtitle {{ color: #d6e5ff; line-height: 1.7; max-width: 680px; margin: 0; }}
    main {{ padding: 0 24px 48px; margin-top: -50px; }}
    .panel {{ background: white; box-shadow: 0 15px 50px #0b244012; border: 1px solid #e6eaf2; border-radius: 18px; overflow: hidden; }}
    .toolbar {{ display: flex; gap: 15px; flex-wrap: wrap; justify-content: space-between; align-items: center; padding: 25px; border-bottom: 1px solid #edf0f5; }}
    .toolbar h2 {{ margin: 0 0 5px; font-size: 20px; }}
    .summary {{ margin: 0; font-size: 13px; color: #73809a; }}
    .search {{ width: min(100%, 310px); border: 1px solid #d6deeb; border-radius: 11px; padding: 12px 14px; background: #fafbfe; font-size: 14px; outline: none; }}
    .search:focus {{ border-color: #3675cd; box-shadow: 0 0 0 3px #3675cd15; }}
    #files {{ padding: 8px 25px 20px; }}
    .file {{ display: flex; align-items: center; gap: 16px; min-height: 84px; padding: 16px 0; border-bottom: 1px solid #edf0f5; }}
    .file:last-child {{ border-bottom: 0; }}
    .file[hidden] {{ display: none; }}
    .file-symbol {{ flex-shrink: 0; display: grid; place-items: center; width: 50px; height: 50px; border: 1px solid #d8e7fa; background: #eef5ff; color: #275c9b; border-radius: 12px; font-size: 11px; font-weight: 750; overflow: hidden; }}
    .details {{ flex: 1; min-width: 0; }}
    .file-name {{ font-size: 15px; font-weight: 650; overflow-wrap: anywhere; }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 10px 18px; margin-top: 7px; font-size: 12px; color: #7c889e; }}
    .download {{ color: white; text-decoration: none; background: #2568bf; border-radius: 9px; font-size: 13px; font-weight: 650; padding: 11px 16px; white-space: nowrap; transition: background .15s; }}
    .download:hover {{ background: #154c95; }}
    .download:focus-visible {{ outline: 3px solid #81b6ff; outline-offset: 2px; }}
    .empty {{ padding: 55px 16px; text-align: center; color: #7a8597; line-height: 1.7; }}
    .foot {{ text-align: center; color: #75829a; font-size: 12px; margin: 26px auto; line-height: 1.8; }}
    @media (max-width: 600px) {{ .hero {{ padding-top: 44px; }} .toolbar {{ align-items: stretch; }} .search {{ width: 100%; }} #files {{ padding: 0 17px 12px; }} .file {{ gap: 10px; }} .file-symbol {{ width: 40px; height: 44px; }} .download {{ padding: 10px 12px; }} }}
  </style>
</head>
<body>
  <header class="hero"><div class="container">
    <span class="eyebrow">资源共享 · Download Center</span>
    <h1>SnapGene 资源下载</h1>
    <p class="subtitle">浏览文件列表，搜索所需资源，点击“下载”获取文件。请仅分发您有权共享的资源。</p>
  </div></header>
  <main class="container">
    <section class="panel" aria-label="文件下载列表">
      <div class="toolbar">
        <div><h2>可下载文件</h2><p class="summary">共 <span id="count">{len(files)}</span> 个文件 · 总大小 {total}</p></div>
        <input class="search" type="search" id="search" placeholder="搜索文件名或文件夹…" aria-label="搜索文件" />
      </div>
      <div id="files">{rows}</div>
      <div id="no-match" class="empty" hidden>没有找到匹配的文件，请尝试其他关键词。</div>
    </section>
    <p class="foot">文件目录更新于 {updated} · 网页需与下载文件一起部署，保留相对目录结构。</p>
  </main>
  <script>
    const search = document.getElementById('search');
    const items = Array.from(document.querySelectorAll('.file'));
    const count = document.getElementById('count');
    const noMatch = document.getElementById('no-match');
    search.addEventListener('input', () => {{
      const q = search.value.trim().toLocaleLowerCase();
      let visible = 0;
      for (const item of items) {{
        const match = item.dataset.search.includes(q);
        item.hidden = !match;
        if (match) visible++;
      }}
      count.textContent = visible;
      noMatch.hidden = visible !== 0 || items.length === 0;
    }});
  </script>
</body>
</html>
'''


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate a public SnapGene download page')
    parser.add_argument('--base-url', default='', help='Public URL prefix for files hosted elsewhere, e.g. https://files.example.com')
    args = parser.parse_args()
    if args.base_url and not args.base_url.startswith(('https://', 'http://')):
        parser.error('--base-url 必须以 https:// 或 http:// 开头')
    files = gather_files()
    content = render(files, args.base_url)
    OUTPUT.write_text(content, encoding='utf-8')
    INDEX.write_text(content, encoding='utf-8')
    (ROOT / '.nojekyll').touch()
    print(f'已生成: {OUTPUT}、{INDEX}')
    print(f'收录 {len(files)} 个文件，总大小 {human_size(sum(s for _, s in files))}')
    large = [(p, n) for p,n in files if n > 25 * 1024 * 1024]
    huge = [(p, n) for p,n in files if n > 100 * 1024 * 1024]
    if large:
        print(f'注意：{len(large)} 个文件超过 GitHub 网页上传单文件 25 MiB 上限。')
    if huge:
        print(f'警告：{len(huge)} 个文件超过 GitHub 普通 Git 对象 100 MiB 限制，应改用 R2 或 VPS 等文件托管方式：')
        for p,n in huge[:12]:
            print(f'  - {p}  ({human_size(n)})')
    if args.base_url:
        print('下载链接使用外部域名前缀，文件必须另外上传到该文件服务器并保持相对路径。')
    else:
        print('下载链接为相对路径，网页和所有下载文件必须一起部署，保持原有目录结构。')


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'生成失败：{exc}', file=sys.stderr)
        sys.exit(1)
