#!/usr/bin/env node
// Collects mentions of other skills inside verbatim imports and writes
// skills/v-mode/contracts/reference-policy.md.
//
// Usage: node scripts/collect-references.mjs --source pstack=<dir> [--source <name>=<dir> ...] [--check]
//   --source  root of an upstream checkout, keyed by the source name in upstream.json
//   --check   do not write; exit 1 if the generated file would differ from the committed one
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadUpstream, walkMarkdown, rel, plannedSkillNames } from './lib.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const sources = {};
let check = false;
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--source') {
    const [name, dir] = args[++i].split(/=(.*)/s);
    sources[name] = dir;
  } else if (args[i] === '--check') check = true;
  else throw new Error(`unknown argument: ${args[i]}`);
}

const upstream = loadUpstream(root);
const shipped = plannedSkillNames(upstream);

const PATTERNS = [
  { kind: 'link', re: /\]\((?:\.\.\/)+([a-z][a-z0-9-]*)\/SKILL\.md\)/g },
  { kind: 'bold', re: /\*\*([a-z][a-z0-9-]*)\*\*(?: principle)? skill/g },
  { kind: 'code', re: /`([a-z][a-z0-9-]*)` skill/g },
  { kind: 'command', re: /`\/([a-z][a-z0-9-]*)`/g },
];

const rows = [];
for (const entry of upstream.imports.filter((e) => e.mode === 'verbatim')) {
  const srcRoot = sources[entry.source];
  if (!srcRoot) throw new Error(`missing --source for ${entry.source}`);
  const meta = upstream.sources[entry.source];
  const base = join(srcRoot, meta.path, entry.from);
  if (!existsSync(base)) throw new Error(`source path not found: ${base}`);
  const files = base.endsWith('.md') ? [base] : walkMarkdown(base);
  for (const file of files) {
    const lines = readFileSync(file, 'utf8').split(/\r?\n/);
    lines.forEach((line, idx) => {
      for (const { kind, re } of PATTERNS) {
        for (const m of line.matchAll(re)) {
          const name = m[1];
          const resolved = shipped.has(name) ? name : shipped.has(`principle-${name}`) ? `principle-${name}` : name;
          rows.push({
            file: `${entry.to}/${rel(base, file)}`,
            line: idx + 1,
            name: resolved,
            kind,
            shipped: shipped.has(resolved),
          });
        }
      }
    });
  }
}

rows.sort((a, b) => a.file.localeCompare(b.file) || a.line - b.line || a.name.localeCompare(b.name));
const external = rows.filter((r) => !r.shipped);
const internal = rows.filter((r) => r.shipped);

const md = [
  '# 출처 참조 정책',
  '',
  '> 이 파일은 `scripts/collect-references.mjs`가 만든다. 손으로 고치지 않는다.',
  '',
  '`upstream.json`에서 `mode: verbatim`으로 가져온 원문 안의 다른 스킬 언급 목록이다. 원문은 고치지 않는다.',
  '',
  'verbatim 원문 안의 참조는 가리키는 곳이 vstack 안이든 밖이든 모두 **출처 참조**다. 작업자는 따라가지 않는다([priority.md](priority.md) "출처 참조").',
  '',
  '## vstack에 없는 스킬을 가리키는 참조',
  '',
  '원문이 "그 스킬을 실행하라"고 해도 실행하지 않는다. 같은 일이 필요하면 오른쪽 열을 따른다.',
  '',
  '| 파일 | 줄 | 참조 | 형태 | vstack에서 대신 따르는 것 |',
  '| --- | --- | --- | --- | --- |',
  ...external.map((r) => `| \`${r.file}\` | ${r.line} | \`${r.name}\` | ${r.kind} | ${replacement(r.name)} |`),
  '',
  '## vstack 안을 가리키는 참조',
  '',
  'vstack에 있는(또는 들어올) 파일을 가리키지만, 이것도 출처 참조다. 작업자는 이 링크를 따라가 다른 원칙을 읽거나 적용하지 않는다. 명세·레시피가 후보로 준 원칙만 읽고 적용한다.',
  '',
  '| 파일 | 줄 | 참조 | 형태 |',
  '| --- | --- | --- | --- |',
  ...internal.map((r) => `| \`${r.file}\` | ${r.line} | \`${r.name}\` | ${r.kind} |`),
  '',
].join('\n');

function replacement(name) {
  const table = {
    'show-me-your-work': '결정 기록이 필요하면 관리자에게 알린다. 증거는 [evidence.md](evidence.md)',
    'benchmark-checklist': '수치 주장은 원칙 `explain-the-number` 본문의 절차만 따른다',
    'typescript-best-practices': '원칙 `type-system-discipline` 본문만 따른다',
    'maintain-verification-skill': '첫 버전 미포함. 기능 지도가 낡았으면 관리자에게 알린다',
  };
  return table[name] ?? '관리자에게 묻는다';
}

const target = join(root, 'skills/v-mode/contracts/reference-policy.md');
if (check) {
  const current = existsSync(target) ? readFileSync(target, 'utf8') : '';
  if (current.replace(/\r\n/g, '\n') !== md) {
    console.error('reference-policy.md is out of date. Run scripts/collect-references.mjs.');
    process.exit(1);
  }
  console.log(`reference-policy.md is up to date (${external.length} external, ${internal.length} internal).`);
} else {
  writeFileSync(target, md);
  console.log(`wrote ${rel(root, target)}: ${external.length} external, ${internal.length} internal.`);
}
