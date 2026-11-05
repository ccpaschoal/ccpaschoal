// Gera dist/stats.svg com as estatísticas do perfil, no visual do portfólio.
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';

const user = process.env.GH_USER;
const query = `query($login:String!){ user(login:$login){
  repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false){
    totalCount
    nodes{ languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name } } } }
  }
  contributionsCollection{ totalCommitContributions contributionCalendar{ totalContributions } }
}}`;

const res = await fetch('https://api.github.com/graphql', {
  method: 'POST',
  headers: { Authorization: `Bearer ${process.env.GITHUB_TOKEN}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({ query, variables: { login: user } }),
});
const json = await res.json();
if (!json.data?.user) throw new Error(JSON.stringify(json));
const u = json.data.user;

const langs = {};
for (const r of u.repositories.nodes) for (const e of r.languages.edges) {
  langs[e.node.name] = (langs[e.node.name] || 0) + e.size;
}
const total = Object.values(langs).reduce((s, n) => s + n, 0) || 1;
const PALETTE = ['#8B1E2D', '#D9B65C', '#6BA3D8', '#F1E6C8'];
const top = Object.entries(langs).sort((a, b) => b[1] - a[1]).slice(0, 4)
  .map(([name, size], i) => ({ name, pct: size / total, color: PALETTE[i] }));

const stats = [
  ['Contribuições', 'no último ano', u.contributionsCollection.contributionCalendar.totalContributions],
  ['Commits', 'no último ano', u.contributionsCollection.totalCommitContributions],
  ['Repositórios', 'públicos', u.repositories.totalCount],
  ['Linguagens', 'usadas', Object.keys(langs).length],
];

const font = readFileSync('assets/montserrat.woff2').toString('base64');
const W = 600, H = 300, P = 24, G = 12;
const tw = (W - 2 * P - G) / 2, th = 78;

const tiles = stats.map(([k, sub, v], i) => {
  const x = P + (i % 2) * (tw + G), y = 78 + Math.floor(i / 2) * (th + G);
  return `<g class="up" style="animation-delay:${0.1 * (i + 1)}s">
<rect x="${x}" y="${y}" width="${tw}" height="${th}" rx="18" fill="#FFFFFF" fill-opacity=".045" stroke="#FFFFFF" stroke-opacity=".10"/>
<text x="${x + 20}" y="${y + 50}" font-size="34" font-weight="800" letter-spacing="-1" fill="url(#num)">${v}</text>
<text x="${x + tw - 20}" y="${y + 34}" text-anchor="end" font-size="14" font-weight="700" fill="#F1E6C8">${k}</text>
<text x="${x + tw - 20}" y="${y + 54}" text-anchor="end" font-size="12" font-weight="500" fill="#D9DEE4" fill-opacity=".8">${sub}</text></g>`;
}).join('');

let bx = P;
const barW = W - 2 * P;
const bar = top.map(l => {
  const w = Math.max(3, l.pct * barW);
  const r = `<rect x="${bx.toFixed(1)}" y="262" width="${w.toFixed(1)}" height="8" fill="${l.color}"/>`;
  bx += w;
  return r;
}).join('');
const legend = top.map((l, i) =>
  `<circle cx="${P + 5 + i * 138}" cy="${252 - 4}" r="4.5" fill="${l.color}"/><text x="${P + 16 + i * 138}" y="252" font-size="12" font-weight="600" fill="#D9DEE4">${l.name} <tspan fill-opacity=".7">${(l.pct * 100).toFixed(0)}%</tspan></text>`
).join('');

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
<style>
@font-face{font-family:'M';font-weight:100 900;src:url(data:font/woff2;base64,${font}) format('woff2')}
text{font-family:'M','Montserrat','Segoe UI',Arial,sans-serif}
.up{animation:up .9s cubic-bezier(.22,1,.36,1) backwards}
@keyframes up{from{opacity:0;transform:translateY(12px)}}
.grow{transform-origin:${P}px 266px;animation:g 1.4s cubic-bezier(.22,1,.36,1) .6s backwards}
@keyframes g{from{transform:scaleX(0)}}
</style>
<defs>
<clipPath id="cl"><rect width="${W}" height="${H}" rx="28"/></clipPath>
<filter id="bl" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="55"/></filter>
<linearGradient id="num" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F1E6C8"/><stop offset="1" stop-color="#D9B65C"/></linearGradient>
<clipPath id="bc"><rect x="${P}" y="262" width="${barW}" height="8" rx="4"/></clipPath>
</defs>
<g clip-path="url(#cl)"><rect width="${W}" height="${H}" fill="#0A1F30"/>
<g filter="url(#bl)">
<circle cx="80" cy="40" r="140" fill="#8B1E2D" opacity=".6"><animateTransform attributeName="transform" type="translate" values="0 0;40 30;0 0" dur="13s" repeatCount="indefinite"/></circle>
<circle cx="560" cy="280" r="150" fill="#2C5282" opacity=".8"><animateTransform attributeName="transform" type="translate" values="0 0;-40 -20;0 0" dur="16s" repeatCount="indefinite"/></circle>
</g></g>
<rect x=".5" y=".5" width="${W - 1}" height="${H - 1}" rx="28" fill="none" stroke="#FFFFFF" stroke-opacity=".10"/>
<text x="${P}" y="42" font-size="12" font-weight="700" letter-spacing="3" fill="#D9B65C">NO GITHUB</text>
<text x="${P}" y="64" font-size="20" font-weight="800" letter-spacing="-.5" fill="#F1E6C8">Meus números</text>
<text x="${W - P}" y="42" text-anchor="end" font-size="11" font-weight="600" letter-spacing="1.5" fill="#D9DEE4" fill-opacity=".7">ATUALIZA SOZINHO ✦</text>
${tiles}
${legend}
<g clip-path="url(#bc)"><rect x="${P}" y="262" width="${barW}" height="8" fill="#FFFFFF" fill-opacity=".08"/><g class="grow">${bar}</g></g>
</svg>`;

mkdirSync('dist', { recursive: true });
writeFileSync('dist/stats.svg', svg);
console.log('stats.svg gerado');
