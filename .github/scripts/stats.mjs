// Gera dist/stats.svg com as estatísticas do perfil, nas cores do portfólio.
import { mkdirSync, writeFileSync } from 'node:fs';

const user = process.env.GH_USER;
const query = `query($login:String!){ user(login:$login){
  createdAt
  repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false){
    totalCount
    nodes{ stargazerCount languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name color } } } }
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

const repos = u.repositories.nodes;
const stars = repos.reduce((s, r) => s + r.stargazerCount, 0);
const langs = {};
for (const r of repos) for (const e of r.languages.edges) {
  langs[e.node.name] ??= { size: 0, color: e.node.color || '#AEB7C2' };
  langs[e.node.name].size += e.size;
}
const total = Object.values(langs).reduce((s, l) => s + l.size, 0) || 1;
const top = Object.entries(langs).sort((a, b) => b[1].size - a[1].size).slice(0, 4);

const stats = [
  ['Contribuições no último ano', u.contributionsCollection.contributionCalendar.totalContributions],
  ['Commits no último ano', u.contributionsCollection.totalCommitContributions],
  ['Repositórios públicos', u.repositories.totalCount],
  ['Estrelas recebidas', stars],
];

const W = 480, H = 230;
let x = 25;
const bar = top.map(([, l]) => {
  const w = Math.max(2, (l.size / total) * (W - 50));
  const r = `<rect x="${x.toFixed(1)}" y="168" width="${w.toFixed(1)}" height="8" fill="${l.color}"/>`;
  x += w;
  return r;
}).join('');
const legend = top.map(([name, l], i) =>
  `<g transform="translate(${25 + i * 112},196)"><circle cx="5" cy="-4" r="5" fill="${l.color}"/><text x="15" y="0" class="l">${name} ${((l.size / total) * 100).toFixed(0)}%</text></g>`
).join('');

const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
<style>
  .t{font:700 18px 'Montserrat','Segoe UI',sans-serif;fill:#F1E6C8}
  .k{font:500 13px 'Montserrat','Segoe UI',sans-serif;fill:#D9DEE4}
  .v{font:700 14px 'Montserrat','Segoe UI',sans-serif;fill:#D9B65C}
  .l{font:500 11px 'Montserrat','Segoe UI',sans-serif;fill:#D9DEE4}
  .row{animation:in .6s ease backwards}
  @keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}
  .s{font:600 11px 'Montserrat','Segoe UI',sans-serif;fill:#D9B65C;letter-spacing:3px}
  .grow{transform-origin:25px 172px;animation:g 1.2s cubic-bezier(.22,1,.36,1) .9s backwards}
  @keyframes g{from{transform:scaleX(0)}}
</style>
<defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0F2A40"/><stop offset="1" stop-color="#1A3A52"/></linearGradient></defs>
<rect width="${W}" height="${H}" rx="18" fill="url(#b)"/>
<rect x=".5" y=".5" width="${W - 1}" height="${H - 1}" rx="18" fill="none" stroke="#2C5282"/>
<clipPath id="k"><rect width="${W}" height="${H}" rx="18"/></clipPath><rect x="0" y="0" width="${W}" height="6" fill="#8B1E2D" clip-path="url(#k)"/>
<text x="${W - 25}" y="38" class="s" text-anchor="end">ATUALIZADO SOZINHO</text>
<text x="25" y="40" class="t">✦ Estatísticas</text>
${stats.map(([k, v], i) => `<g class="row" style="animation-delay:${0.15 * (i + 1)}s"><text x="25" y="${72 + i * 22}" class="k">${k}</text><text x="${W - 25}" y="${72 + i * 22}" class="v" text-anchor="end">${v}</text></g>`).join('\n')}
<clipPath id="c"><rect x="25" y="168" width="${W - 50}" height="8" rx="4"/></clipPath>
<g clip-path="url(#c)"><rect x="25" y="168" width="${W - 50}" height="8" fill="#0F2A40"/><g class="grow">${bar}</g></g>
${legend}
</svg>`;

mkdirSync('dist', { recursive: true });
writeFileSync('dist/stats.svg', svg);
console.log('stats.svg gerado');
