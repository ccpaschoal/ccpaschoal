"""Gera os SVGs do perfil (visual moderno: mesh gradient, vidro, bento)."""
import base64, os, sys

S, OUT, CAR = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)

def b64(path):
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

FONT = b64(os.path.join(S, 'font', 'montserrat.woff2'))
FACE = ("@font-face{font-family:'M';font-weight:100 900;"
        f"src:url(data:font/woff2;base64,{FONT}) format('woff2')}}")
FF = "'M','Montserrat','Segoe UI',Arial,sans-serif"

# Paleta do banner e da logo CP: preto + vermelho e laranja neon
NAVY, NAVY2, DEEP = '#141414', '#1E1E1E', '#0A0A0A'
BLUE, BLUE2, SKY = '#5A0A06', '#E0442C', '#FF6A45'
WINE, WINE2 = '#FF2B1C', '#B3120A'
SAND, GOLD, GRAY = '#F5EDEA', '#FF6A45', '#CFC6C3'

def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;')

def svg(w, h, body, css=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}"><style>{FACE}'
            f'text{{font-family:{FF}}}{css}</style>{body}</svg>')

def write(name, content):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        f.write(content)

# animações reutilizáveis (estado final visível mesmo sem animação)
ANIM = """
.up{animation:up 1s cubic-bezier(.22,1,.36,1) backwards}
@keyframes up{from{opacity:0;transform:translateY(16px)}}
.tw{animation:tw 3.2s ease-in-out infinite}
@keyframes tw{50%{opacity:.25}}
.pulse{animation:pu 2s ease-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes pu{0%{transform:scale(1);opacity:.7}100%{transform:scale(3);opacity:0}}
"""

def mesh(w, h, rx, blobs, uid):
    """Fundo escuro com bolhas de cor desfocadas que se movem devagar + grão."""
    out = [f'<defs><clipPath id="cl{uid}"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>'
           f'<filter id="bl{uid}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{min(w,h)//6}"/></filter>'
           f'<filter id="gr{uid}"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/>'
           f'<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .5 0"/></filter></defs>',
           f'<g clip-path="url(#cl{uid})"><rect width="{w}" height="{h}" fill="{DEEP}"/>',
           f'<g filter="url(#bl{uid})">']
    for i, (cx, cy, r, color, op, dx, dy) in enumerate(blobs):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="{op}">'
                   f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" '
                   f'dur="{12 + i * 3}s" repeatCount="indefinite"/></circle>')
    out.append(f'</g><rect width="{w}" height="{h}" filter="url(#gr{uid})" opacity=".07"/></g>')
    out.append(f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{rx}" fill="none" stroke="#FFFFFF" stroke-opacity=".10"/>')
    return ''.join(out)

def glass(x, y, w, h, rx=22):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="#FFFFFF" fill-opacity=".045" '
            f'stroke="#FFFFFF" stroke-opacity=".10"/>')

def kicker(x, y, t, color=GOLD):
    return f'<text x="{x}" y="{y}" font-size="12" font-weight="700" letter-spacing="3" fill="{color}">{esc(t)}</text>'

def chip(x, y, t, size=14, pad=16, h=34, fill_op='.07', color=GRAY):
    w = int(len(t) * size * 0.62) + pad * 2
    return (f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="#FFFFFF" fill-opacity="{fill_op}" '
            f'stroke="#FFFFFF" stroke-opacity=".14"/><text x="{x + w/2}" y="{y + h/2 + size*0.36}" text-anchor="middle" '
            f'font-size="{size}" font-weight="600" fill="{color}">{esc(t)}</text></g>'), w

# ---------------------------------------------------------------- HERO
def hero():
    """Banner com o nome completo (arte da Camilla) + selo de disponível."""
    W, H = 1200, 460
    img = b64(os.path.join(S, 'banner.jpg'))
    body = [f'<defs><clipPath id="hc"><rect width="{W}" height="{H}" rx="28"/></clipPath></defs>',
            f'<g clip-path="url(#hc)"><rect width="{W}" height="{H}" fill="{DEEP}"/>'
            f'<image width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" '
            f'href="data:image/jpeg;base64,{img}" xlink:href="data:image/jpeg;base64,{img}"/></g>',
            f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="28" fill="none" stroke="{WINE}" stroke-opacity=".35"/>']
    body.append('<g class="up">'
                f'<rect x="48" y="40" width="318" height="36" rx="18" fill="#000" fill-opacity=".55" stroke="{GOLD}" stroke-opacity=".5"/>'
                f'<circle cx="70" cy="58" r="5" fill="{WINE}" class="pulse"/><circle cx="70" cy="58" r="5" fill="{WINE}"/>'
                f'<text x="86" y="63" font-size="12.5" font-weight="700" letter-spacing="2.2" fill="{SAND}">DISPONÍVEL PARA PROJETOS</text></g>')
    x = W - 48
    chips = []
    for t in reversed(['Social Media & Web Design', 'Rio de Janeiro']):
        c, w = chip(0, 0, t)
        x -= w
        chips.append(chip(x, 40, t, fill_op='.55', color=SAND)[0].replace('fill="#FFFFFF" fill-opacity=".55"', 'fill="#000" fill-opacity=".55"', 1))
        x -= 10
    body.append(f'<g class="up" style="animation-delay:.2s">{"".join(chips)}</g>')
    write('hero.svg', svg(W, H, ''.join(body), ANIM))

# ---------------------------------------------------------------- BENTO
def bento():
    W, H = 1200, 600
    G = 16
    body = ['<defs>'
            f'<linearGradient id="gu" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{SAND}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient>'
            f'<filter id="bb" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="50"/></filter>'
            f'<clipPath id="all"><rect width="{W}" height="{H}" rx="28"/></clipPath></defs>',
            f'<g clip-path="url(#all)"><rect width="{W}" height="{H}" fill="{DEEP}"/>',
            '<g filter="url(#bb)">',
            f'<circle cx="160" cy="80" r="160" fill="{WINE}" opacity=".55"><animateTransform attributeName="transform" type="translate" values="0 0;40 30;0 0" dur="14s" repeatCount="indefinite"/></circle>',
            f'<circle cx="1050" cy="120" r="170" fill="{BLUE}" opacity=".7"><animateTransform attributeName="transform" type="translate" values="0 0;-40 30;0 0" dur="16s" repeatCount="indefinite"/></circle>',
            f'<circle cx="620" cy="560" r="180" fill="{SKY}" opacity=".28"><animateTransform attributeName="transform" type="translate" values="0 0;30 -30;0 0" dur="18s" repeatCount="indefinite"/></circle>',
            '</g></g>',
            f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="28" fill="none" stroke="#FFFFFF" stroke-opacity=".10"/>']
    P = 24
    # linha 1
    aw = 760; bx = P + aw + G; bw = W - P - bx
    body.append(f'<g class="up">{glass(P, P, aw, 240)}')
    body.append(kicker(P + 32, P + 46, 'SOBRE MIM'))
    for i, line in enumerate(['Transformo ideias em conteúdo visual para',
                              'redes sociais, com cuidado em cada detalhe:',
                              'tipografia, cor e composição.']):
        body.append(f'<text x="{P+32}" y="{P + 92 + i*34}" font-size="25" font-weight="600" letter-spacing="-.5" fill="{SAND}">{esc(line)}</text>')
    body.append(f'<rect x="{P+32}" y="{P+182}" width="3" height="26" rx="1.5" fill="{WINE}"/>'
                f'<text x="{P+46}" y="{P+201}" font-size="15" font-style="italic" font-weight="500" fill="{GRAY}">Cada peça deve transmitir uma mensagem, não só preencher o feed.</text></g>')
    body.append(f'<g class="up" style="animation-delay:.1s">{glass(bx, P, bw, 240)}')
    body.append(f'<text x="{bx + bw - 26}" y="{P + 200}" text-anchor="end" font-size="150" font-weight="800" fill="#FFFFFF" fill-opacity=".05">∑π</text>')
    body.append(kicker(bx + 32, P + 46, 'FORMAÇÃO'))
    body.append(f'<text x="{bx+30}" y="{P+128}" font-size="64" font-weight="800" letter-spacing="-2" fill="url(#gu)">UFRJ</text>')
    body.append(f'<text x="{bx+32}" y="{P+166}" font-size="16" font-weight="600" fill="{GRAY}">Bacharelado em</text>'
                f'<text x="{bx+32}" y="{P+190}" font-size="16" font-weight="600" fill="{GRAY}">Ciências Matemáticas</text></g>')
    # linha 2
    y2 = P + 240 + G; h2 = H - P - y2
    cw = (W - 2 * P - 2 * G) / 3
    cols = [
        ('SOCIAL MEDIA', 'Conteúdo para redes', WINE,
         ['Posts e carrosséis', 'Stories', 'Identidade visual', 'Materiais promocionais', 'Pacotes de conteúdo']),
        ('WEB DESIGN', 'Sites sob medida', SKY,
         ['Sites e portfólios responsivos', 'Layout, tipografia e cores', 'Animações e interações', 'Modo claro e escuro', 'Publicação no GitHub Pages']),
    ]
    for k, (kk, title, accent, items) in enumerate(cols):
        x = P + k * (cw + G)
        body.append(f'<g class="up" style="animation-delay:{.2 + k*.1}s">{glass(x, y2, cw, h2)}')
        body.append(f'<rect x="{x+32}" y="{y2+30}" width="28" height="4" rx="2" fill="{accent}"/>')
        body.append(kicker(x + 32, y2 + 60, kk))
        body.append(f'<text x="{x+32}" y="{y2+94}" font-size="24" font-weight="700" letter-spacing="-.5" fill="{SAND}">{esc(title)}</text>')
        for i, it in enumerate(items):
            yy = y2 + 136 + i * 30
            body.append(f'<circle cx="{x+37}" cy="{yy-5}" r="3.5" fill="{accent}"/>'
                        f'<text x="{x+52}" y="{yy}" font-size="15.5" font-weight="500" fill="{GRAY}">{esc(it)}</text>')
        body.append('</g>')
    x = P + 2 * (cw + G)
    body.append(f'<g class="up" style="animation-delay:.4s">{glass(x, y2, cw, h2)}')
    body.append(f'<rect x="{x+32}" y="{y2+30}" width="28" height="4" rx="2" fill="{GOLD}"/>')
    body.append(kicker(x + 32, y2 + 60, 'FERRAMENTAS'))
    body.append(f'<text x="{x+32}" y="{y2+94}" font-size="24" font-weight="700" letter-spacing="-.5" fill="{SAND}">Do rascunho ao ar</text>')
    cx, cy = x + 32, y2 + 116
    for t in ['Canva', 'Figma', 'HTML', 'CSS', 'JavaScript', 'Git', 'GitHub Pages']:
        c, w = chip(0, 0, t, size=14, pad=14, h=32)
        if cx + w > x + cw - 28:
            cx, cy = x + 32, cy + 42
        body.append(chip(cx, cy, t, size=14, pad=14, h=32)[0])
        cx += w + 8
    body.append('</g>')
    write('bento.svg', svg(W, H, ''.join(body), ANIM))

# ---------------------------------------------------------------- PROJETOS
def project(name, file, title, desc, url, accent, uid):
    W, H = 400, 360
    img = b64(os.path.join(S, 'shots', file))
    body = [mesh(W, H, 24, [(60, 330, 130, accent, .55, 20, -20), (360, 20, 120, BLUE, .6, -20, 20)], uid)]
    # janela do navegador
    bx, by, bw = 20, 20, W - 40
    bh = int(bw * 450 / 720) + 30
    body.append(f'<defs><clipPath id="sc{uid}"><rect x="{bx}" y="{by+30}" width="{bw}" height="{bh-30}" rx="0"/></clipPath>'
                f'<clipPath id="wn{uid}"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="14"/></clipPath></defs>')
    body.append(f'<g clip-path="url(#wn{uid})"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{NAVY}"/>'
                f'<rect x="{bx}" y="{by}" width="{bw}" height="30" fill="#FFFFFF" fill-opacity=".08"/>')
    for i, c in enumerate(['#FF5F57', '#FEBC2E', '#28C840']):
        body.append(f'<circle cx="{bx + 16 + i*14}" cy="{by+15}" r="4.5" fill="{c}"/>')
    body.append(f'<rect x="{bx+66}" y="{by+7}" width="{bw-82}" height="16" rx="8" fill="#000" fill-opacity=".25"/>'
                f'<text x="{bx+78}" y="{by+19}" font-size="10" font-weight="500" fill="{GRAY}" fill-opacity=".8">{esc(url)}</text>')
    body.append(f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -10;0 0" dur="9s" repeatCount="indefinite"/>'
                f'<image x="{bx}" y="{by+30}" width="{bw}" height="{bh-30+10}" preserveAspectRatio="xMidYMin slice" clip-path="url(#sc{uid})" '
                f'href="data:image/jpeg;base64,{img}" xlink:href="data:image/jpeg;base64,{img}"/></g></g>')
    body.append(f'<rect x="{bx+.5}" y="{by+.5}" width="{bw-1}" height="{bh-1}" rx="14" fill="none" stroke="#FFFFFF" stroke-opacity=".18"/>')
    ty = by + bh + 40
    body.append(f'<text x="24" y="{ty}" font-size="21" font-weight="700" letter-spacing="-.4" fill="{SAND}">{esc(title)}</text>')
    body.append(f'<text x="24" y="{ty+26}" font-size="14" font-weight="500" fill="{GRAY}">{esc(desc)}</text>')
    body.append(f'<circle cx="{W-44}" cy="{ty+4}" r="20" fill="{accent}"/>'
                f'<path d="M{W-50} {ty+10} L{W-38} {ty-2} M{W-47} {ty-2} L{W-38} {ty-2} L{W-38} {ty+7}" stroke="{NAVY if accent in (GOLD, SKY) else SAND}" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    write(name, svg(W, H, ''.join(body), ANIM))

# ---------------------------------------------------------------- TÍTULOS DE SEÇÃO (claro e escuro)
def label(name, num, text):
    W, H = 1200, 64
    for theme, main, sub, line in [('dark', SAND, GOLD, '#FFFFFF'), ('light', NAVY, WINE, NAVY)]:
        tw = int(len(text) * 22 * 0.68)
        body = (f'<text x="2" y="42" font-size="15" font-weight="700" letter-spacing="2" fill="{sub}">{num}</text>'
                f'<text x="44" y="43" font-size="26" font-weight="800" letter-spacing="-.6" fill="{main}">{esc(text)}</text>'
                f'<rect x="{64 + tw}" y="34" width="{W - 70 - tw}" height="1" fill="{line}" fill-opacity=".18"/>')
        write(f'{name}-{theme}.svg', svg(W, H, body))

# ---------------------------------------------------------------- BOTÕES DE CONTATO
def button(name, k, v, accent):
    W, H = 290, 84
    body = [mesh(W, H, 22, [(40, 70, 70, accent, .7, 20, -10), (260, 10, 60, BLUE, .7, -20, 10)], name[:3])]
    body.append(f'<text x="24" y="36" font-size="11.5" font-weight="700" letter-spacing="2.6" fill="{GOLD}">{esc(k)}</text>'
                f'<text x="24" y="60" font-size="{15 if len(v) < 24 else 13}" font-weight="600" fill="{SAND}">{esc(v)}</text>'
                f'<circle cx="{W-38}" cy="{H/2}" r="16" fill="#FFFFFF" fill-opacity=".1" stroke="#FFFFFF" stroke-opacity=".2"/>'
                f'<path d="M{W-43} {H/2+5} L{W-33} {H/2-5} M{W-41} {H/2-5} L{W-33} {H/2-5} L{W-33} {H/2+3}" stroke="{SAND}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    write(name, svg(W, H, ''.join(body)))

# ---------------------------------------------------------------- RODAPÉ
def footer():
    W, H = 1200, 70
    for theme, main, line in [('dark', GRAY, '#FFFFFF'), ('light', NAVY, NAVY)]:
        body = (f'<defs><linearGradient id="fl" x1="0" x2="1"><stop offset="0" stop-color="{WINE}"/><stop offset=".5" stop-color="{GOLD}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient></defs>'
                f'<rect x="0" y="10" width="{W}" height="2" rx="1" fill="url(#fl)"/>'
                f'<text x="{W/2}" y="50" text-anchor="middle" font-size="14" font-weight="600" letter-spacing="2" fill="{main}">CADA DETALHE PENSADO COM CARINHO  <tspan fill="{GOLD}">✦</tspan>  CAMILLA PASCHOAL · 2026</text>')
        write(f'footer-{theme}.svg', svg(W, H, body))

hero(); bento()
project('proj-portfolio.svg', 'portfolio.jpg', 'Meu portfólio', 'Design de social media', 'ccpaschoal.github.io', WINE, 'p1')
project('proj-vanessa.svg', 'vanessa.jpg', 'Vanessa Chaves', 'Orientação parental TDAH | TEA', 'ccpaschoal.github.io/vanessachavestdah', BLUE2, 'p2')
project('proj-aconchego.svg', 'aconchego.jpg', 'Aconchego', 'Festas e eventos · Trindade-GO', 'aconchegoeventos.pages.dev', GOLD, 'p3')
project('proj-chapa.svg', 'chapa.jpg', 'Chapa 62', 'Hamburgueria · pedido no WhatsApp', 'ccpaschoal.github.io/hamburgueria', WINE2, 'p4')
project('proj-aura.svg', 'aura.jpg', 'AURA', 'Loja de fone Bluetooth', 'lojaaura.pages.dev', SKY, 'p5')
for n, num, t in [('t-sobre', '01', 'Quem sou eu'), ('t-sites', '02', 'Sites que eu criei'),
                  ('t-github', '03', 'Meu GitHub'), ('t-contato', '04', 'Vamos conversar?')]:
    label(n, num, t)
button('btn-whatsapp.svg', 'WHATSAPP', '(21) 98256-6564', WINE)
button('btn-email.svg', 'E-MAIL', 'camillacpaschoal@gmail.com', BLUE2)
button('btn-instagram.svg', 'INSTAGRAM', '@camillapaschoal', WINE2)
button('btn-linkedin.svg', 'LINKEDIN', 'camillapaschoal', BLUE)
footer()
print('ok')
