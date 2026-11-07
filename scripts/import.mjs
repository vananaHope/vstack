#!/usr/bin/env node
// Copies upstream files into vstack as upstream.json describes.
//   verbatim  copy every file (overwrite). With --check, report files that differ from the source.
//   adapted   seed the destination from the source only when the destination file is missing.
//             Existing files are local edits and are never overwritten.
//   extracted not copied; the destination is written by hand. Reported if missing.
//   moved     not handled here yet (stage 3).
//
// Usage: node scripts/import.mjs --stage <n> --source <name>=<dir> [...] [--check]
import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadUpstream, walkFiles, rel } from './lib.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
let stage = null;
let check = false;
const sources = {};
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--stage') stage = Number(args[++i]);
  else if (args[i] === '--check') check = true;
  else if (args[i] === '--source') {
    const [name, dir] = args[++i].split(/=(.*)/s);
    sources[name] = dir;
  } else throw new Error(`unknown argument: ${args[i]}`);
}
if (stage === null) throw new Error('--stage is required');

const upstream = loadUpstream(root);
const normalize = (buf) => buf.toString('utf8').replace(/\r\n/g, '\n');
const isText = (p) => !/\.(png|jpe?g|gif|ico|pdf)$/i.test(p);
const report = { copied: 0, same: 0, drift: [], seeded: 0, kept: 0, missing: [] };

for (const entry of upstream.imports) {
  if (entry.stage > stage || entry.mode === 'moved') continue;
  const dest = join(root, entry.to);
  if (entry.mode === 'extracted') {
    if (!existsSync(dest)) report.missing.push(`${entry.to} (extracted, write by hand)`);
    continue;
  }
  const srcRoot = sources[entry.source];
  if (!srcRoot) throw new Error(`missing --source ${entry.source}=<dir>`);
  const base = join(srcRoot, upstream.sources[entry.source].path, entry.from);
  if (!existsSync(base)) throw new Error(`source not found: ${base}`);
  const excluded = new Set(entry.exclude ?? []);
  const files = statSync(base).isFile() ? [base] : walkFiles(base);

  for (const file of files) {
    const inSrc = statSync(base).isFile() ? '' : rel(base, file);
    if (excluded.has(inSrc)) continue;
    const target = inSrc ? join(dest, inSrc) : dest;
    const buf = readFileSync(file);
    const data = isText(file) ? Buffer.from(normalize(buf)) : buf;

    if (entry.mode === 'verbatim') {
      const same = existsSync(target) && Buffer.compare(isText(file) ? Buffer.from(normalize(readFileSync(target))) : readFileSync(target), data) === 0;
      if (same) { report.same++; continue; }
      if (check) { report.drift.push(rel(root, target)); continue; }
      mkdirSync(dirname(target), { recursive: true });
      writeFileSync(target, data);
      report.copied++;
    } else if (entry.mode === 'adapted') {
      if (existsSync(target)) { report.kept++; continue; }
      if (check) { report.missing.push(`${rel(root, target)} (adapted, not seeded)`); continue; }
      mkdirSync(dirname(target), { recursive: true });
      writeFileSync(target, data);
      report.seeded++;
    }
  }
}

for (const d of report.drift) console.error(`DRIFT    ${d} differs from its verbatim source`);
for (const m of report.missing) console.error(`MISSING  ${m}`);
console.log(
  `verbatim: ${report.copied} copied, ${report.same} unchanged, ${report.drift.length} drift. ` +
  `adapted: ${report.seeded} seeded, ${report.kept} kept. missing: ${report.missing.length}.`,
);
process.exit(report.drift.length || (check && report.missing.length) ? 1 : 0);
