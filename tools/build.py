"""화이트 인더스트리 코리아 사이트 빌드.

index.src.html(한국어 원본)에서
  1) 호환 표(허브, 크랭크)를 채워 index.html(한국어)을 만들고
  2) i18n/en.json, i18n/ja.json 번역으로 en/index.html, ja/index.html을 만들고
  3) sitemap.xml을 다시 씁니다.

사용법: python3 tools/build.py
문구를 고친 뒤에는 python3 i18n/extract.py 로 ko.json을 갱신하고,
새로 생긴 문장을 i18n/tr_source.py에 (한국어, 영어, 일본어)로 추가하고
python3 i18n/tr_source.py 로 en.json / ja.json을 만든 다음 빌드합니다.
"""
import json, re, sys, pathlib, datetime
from bs4 import BeautifulSoup, NavigableString, Comment

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'i18n'))
from extract import HANGUL  # noqa: E402

SITE = 'https://white.rubiworkshop.com/'

# ---------------------------------------------------------------- fit tables
# 화이트 인더스트리 공식 기술 정보(whiteind.com 허브 가이드 · 크랭크 비교표, 2026-11 기준).
HUBS = [
  # 모델, 브레이크, 앞 액슬, 뒤 액슬, 로터, 구동, 무게(뒤), 용도
  ('T11', '림', 'QR 100', 'QR 130 · 135', '-', 'HG · XD/XDR · 캄파놀로', '248g', '로드, 올로드, 그래블'),
  ('MI5', '림', 'QR 100', 'QR 130 · 135', '-', 'HG 외', '272g', '로드, 그래블, 투어링, 클래식 MTB'),
  ('CLD', '디스크', 'QR 100 · 12 x 100 · 15 x 110', 'QR 135 · 12 x 142', '센터락', '프리허브 5종', '280g', '로드, 그래블, MTB, 투어링'),
  ('XMR', '디스크', '12 x 100 · 15 x 110', 'QR 135 · 12 x 142', '6볼트', '프리허브 5종', '256g', 'MTB, 그래블, 로드, 투어링'),
  ('CLD+ Boost', '디스크', '12 x 110 · 15 x 110', '12 x 148', '센터락', '프리허브 5종', '-', '부스트 MTB, 그래블'),
  ('XMR+ Boost', '디스크', '12 x 110 · 15 x 110', '12 x 148', '6볼트', '프리허브 5종', '-', '부스트 MTB, 그래블'),
  ('C157 Super Boost', '디스크', '-', '12 x 157', '센터락', '프리허브', '-', '트레일, 엔듀로'),
  ('ENO', '림 · 디스크', '-', '볼트온 130 · 135, 12 x 142', '6볼트 (Disc)', '프리휠 · 고정 코그', '388g (Disc)', '싱글스피드, 고정 기어, 시티'),
  ('Track', '림 · 브레이크 없음', '9 x 100', '10 x 120', '-', '고정 · 플립플롭', '293g', '트랙, 고정 기어'),
  ('MET', '림', 'QR 74', 'QR 112', '-', '브롬톤 4단', '227g', '브롬톤 4단 P · C · T 라인'),
]
CRANKS = [
  # 모델, 크랭크 암, 스핀들, Q 팩터, 1x 체인라인, 2x 체인라인, 비비 셸, 무게
  ('R30 · Road', 'R30 로드 암', 'R30 로드 스핀들', '158.5mm', '46.5mm', '45mm', '68 · 86mm', '560g (170mm)'),
  ('G30 · Gravel', 'M30 MTB 암', 'R30 로드 스핀들', '171mm', '46.5mm', '45mm', '68 · 86mm', '570g (175mm)'),
  ('A30 · Adventure', 'R30 로드 암', 'M30 MTB 스핀들', '163.5mm', '49mm', '47.5mm', '68 · 73 · 86 · 92mm', '565g (170mm)'),
  ('M30 · Mountain', 'M30 MTB 암', 'M30 MTB 스핀들', '176mm', '49mm', '47.5mm', '68 · 73 · 86 · 92mm', '575g (175mm)'),
]

def table(head, rows, left=()):
    h = '<table class="size fit"><thead><tr>' + ''.join(f'<th>{c}</th>' for c in head) + '</tr></thead><tbody>'
    for r in rows:
        h += f'<tr><th>{r[0]}</th>' + ''.join(f'<td class="l">{v}</td>' if i + 1 in left else f'<td>{v}</td>' for i, v in enumerate(r[1:])) + '</tr>'
    return h + '</tbody></table>'

def hub_table():
    return table(['모델', '브레이크', '앞 액슬', '뒤 액슬', '로터', '구동', '무게', '용도'], HUBS, left=(7,))

def crank_table():
    return table(['모델', '크랭크 암', '스핀들', 'Q 팩터', '1x 체인라인', '2x 체인라인', '비비 셸', '무게'], CRANKS)

def build_ko():
    s = (ROOT / 'index.src.html').read_text()
    s = s.replace('{{HUB_TABLE}}', hub_table()).replace('{{CRANK_TABLE}}', crank_table())
    assert '{{' not in s
    assert '\u2014' not in re.sub(r'<!--.*?-->', '', s, flags=re.S), 'em dash in Korean page'
    (ROOT / 'index.html').write_text(s)
    return s

# ---------------------------------------------------------------- translate
LANG = {
 'en': {'locale': 'en_US', 'path': 'en/'},
 'ja': {'locale': 'ja_JP', 'path': 'ja/'},
}

def translate(ko_html, lang):
    tr = json.loads((ROOT / f'i18n/{lang}.json').read_text())
    missing = set()
    def t(s):
        k = s.strip()
        if not HANGUL.search(k):
            return s
        if k in tr:
            return s.replace(k, tr[k])
        missing.add(k)
        return s

    soup = BeautifulSoup(ko_html, 'html.parser')
    soup.html['lang'] = lang
    if soup.title:
        soup.title.string = t(soup.title.string)
    for m in soup.find_all('meta'):
        if m.has_attr('content'):
            m['content'] = t(m['content'])
    for sc in soup.find_all('script', type='application/ld+json'):
        data = json.loads(sc.string)
        def walk(o):
            if isinstance(o, dict):
                return {k: walk(v) for k, v in o.items()}
            if isinstance(o, list):
                return [walk(v) for v in o]
            if isinstance(o, str):
                return t(o)
            return o
        data = walk(data)
        for node in data.get('@graph', []):
            if node.get('@type') == 'WebSite':
                node['url'] = SITE + LANG[lang]['path']
                node['inLanguage'] = lang
        sc.string = '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    for el in soup.body.find_all(True):
        for a in ('alt', 'aria-label', 'title'):
            if el.has_attr(a):
                el[a] = t(el[a])

    def visit(el):
        if el.name in ('script', 'style'):
            return
        direct = any(isinstance(c, NavigableString) and not isinstance(c, Comment) and HANGUL.search(c) for c in el.children)
        if direct:
            k = el.decode_contents().strip()
            if k in tr:
                el.clear()
                frag = BeautifulSoup(tr[k], 'html.parser')
                for c in list(frag.contents):
                    el.append(c)
            else:
                missing.add(k)
            return
        for c in list(el.children):
            if getattr(c, 'name', None):
                visit(c)
    visit(soup.body)

    # canonical, og, hreflang self, language switcher
    soup.find('link', rel='canonical')['href'] = SITE + LANG[lang]['path']
    soup.find('meta', property='og:url')['content'] = SITE + LANG[lang]['path']
    soup.find('meta', property='og:locale')['content'] = LANG[lang]['locale']
    for a in soup.select('nav.lang a'):
        code = a['hreflang']
        a['href'] = '../' if code == 'ko' else ('./' if code == lang else f'../{code}/')
        if code == lang:
            a['class'] = ['on']; a['aria-current'] = 'page'
        else:
            a.attrs.pop('class', None); a.attrs.pop('aria-current', None)
    if lang == 'ja':
        # 일본어는 한글 서체(에스코어 드림) 대신 Noto Sans JP로 통일 (영문·숫자는 Pretendard 유지)
        style = soup.find('style')
        for tag in BeautifulSoup('<link rel="preconnect" href="https://fonts.googleapis.com">'
                                 '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                                 '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400&display=swap" rel="stylesheet">'
                                 '<style>:root{--font:"RubiLatin","Noto Sans JP","Hiragino Sans","Yu Gothic",system-ui,sans-serif}</style>',
                                 'html.parser').contents[:]:
            style.insert_after(tag) if tag.name == 'style' else style.insert_before(tag)

    out = str(soup)
    # 하위 폴더에서 이미지 경로 보정
    out = out.replace('src="images/', 'src="../images/').replace('url(images/', 'url(../images/').replace('href="images/', 'href="../images/')
    left = [k for k in missing]
    return out, left

def sitemap(html):
    imgs = sorted(set(re.findall(r'images/[\w/.-]+\.(?:jpg|png|webp)', html)))
    imgs = [i for i in imgs if not re.search(r'logo|favicon|apple-touch', i)]
    today = datetime.date.today().isoformat()
    alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{h}" href="{SITE}{p}"/>' for h, p in [('ko', ''), ('en', 'en/'), ('ja', 'ja/'), ('x-default', '')])
    urls = []
    for p in ['', 'en/', 'ja/']:
        u = f'  <url>\n    <loc>{SITE}{p}</loc>{alts}\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{"1.0" if not p else "0.8"}</priority>'
        if not p:
            u += ''.join(f'\n    <image:image><image:loc>{SITE}{i}</image:loc></image:image>' for i in imgs)
        urls.append(u + '\n  </url>')
    x = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
         'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
         + '\n'.join(urls) + '\n</urlset>\n')
    (ROOT / 'sitemap.xml').write_text(x)

if __name__ == '__main__':
    ko = build_ko()
    print('ko  index.html', len(ko))
    for lang in LANG:
        if not (ROOT / f'i18n/{lang}.json').exists():
            print(lang, 'skipped (no translation file)'); continue
        out, left = translate(ko, lang)
        d = ROOT / LANG[lang]['path']; d.mkdir(exist_ok=True)
        (d / 'index.html').write_text(out)
        hangul = len(HANGUL.findall(re.sub(r'<script(?![^>]*ld\+json).*?</script>', '', out, flags=re.S)))
        print(lang, f'{d.name}/index.html', len(out), 'untranslated units:', len(left), 'hangul chars left:', hangul)
        for k in left[:20]:
            print('   -', k[:90])
    sitemap(ko)
