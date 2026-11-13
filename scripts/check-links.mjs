#!/usr/bin/env node
// Checks the execution path of vstack: every markdown file under skills/ except
// verbatim imports (their mentions are source references, see reference-policy.md).
//
// 1. Standard path references must resolve:
//      [text](path), [text](path "title"), [text](<path>), [id]: path   (against the file's folder)
//      `<vstack>/path`                                                   (against the plugin root)
// 2. Non-standard references fail: an inline code path (`scripts/x.sh`) that resolves,
//    from the file's folder, to a vstack file that exists (or is a planned file target)
//    must be rewritten as a link or a <vstack>/ path. Inline paths that do not resolve
//    inside vstack are taken as paths in the target project and are not checked.
//    A dependency that was never carried over is caught by the closure check (4).
// 3. Skill references must name a skill vstack ships, and tool-specific invocation
//    phrases ("Skill tool") are not allowed (workers on other runtimes cannot follow them).
// 4. Closure (with --source): every file an adapted or extracted source file points to
//    must have been carried into vstack, or be listed in the entry's "dropped".
//    Moved entries are owned by vstack and their source is archived, so they are not compared.
//
// Skipped: URLs, #anchors, paths that still hold a <placeholder>.
// Usage: node scripts/check-links.mjs [--root <dir>] [--stage <n>] [--source <name>=<dir> ...]
import { readFileSync, existsSync, statSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  loadUpstream, walkMarkdown, rel, importFor, plannedTargets, plannedSkillNames,
  pathRefs, skillRefs, isUrlOrAnchor,
} from './lib.mjs';

const args = process.argv.slice(2);
let root = join(dirname(fileURLToPath(import.meta.url)), '..');
let stage = Infinity;
const sources = {};
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--root') root = resolve(args[++i]);
  else if (args[i] === '--stage') stage = Number(args[++i]);
  else if (args[i] === '--source') {
    const [name, dir] = args[++i].split(/=(.*)/s);
    sources[name] = dir;
  } else throw new Error(`unknown argument: ${args[i]}`);
}

const upstream = loadUpstream(root);
const planned = plannedTargets(upstream);
const shipped = plannedSkillNames(upstream);
const runtimeCommands = new Set(upstream.runtime_commands?.names ?? []);
const userCommands = new Set(upstream.user_commands?.names ?? []);
const failures = [];
const later = [];
let checked = 0;

function planFor(target) {
  return planned.find((p) => target === p.to || target.startsWith(p.to + '/'));
}

function judgeTarget(at, abs, form) {
  checked++;
  const target = rel(root, abs).replace(/\/$/, '');
  if (existsSync(abs)) return;
  const plan = planFor(target);
  if (plan && plan.stage > stage) later.push({ at, target, stage: plan.stage });
  else failures.push({ kind: 'BROKEN', at, detail: `${target} (${form})` });
}

for (const file of walkMarkdown(join(root, 'skills'))) {
  const repoPath = rel(root, file);
  const imp = importFor(upstream, repoPath);
  if (imp && imp.mode === 'verbatim') continue;
  if (imp && imp.stage > stage) continue;

  const lines = readFileSync(file, 'utf8').split(/\r?\n/);
  let fence = null;
  lines.forEach((line, idx) => {
    const fm = line.match(/^\s*(`{3,}|~{3,})/);
    if (fm) {
      if (!fence) fence = fm[1];
      else if (fm[1][0] === fence[0] && fm[1].length >= fence.length) fence = null;
      return;
    }
    const at = `${repoPath}:${idx + 1}`;
    const { standard, inline } = pathRefs(line, { inFence: !!fence });

    for (const { form, raw } of standard) {
      if (isUrlOrAnchor(raw)) continue;
      const path = decodeURI(raw.split('#')[0]);
      if (!path || /[<>]/.test(path)) continue;
      judgeTarget(at, resolve(form === 'vstack' ? root : dirname(file), path), form);
    }

    for (const { raw } of inline) {
      if (/[<>]/.test(raw)) continue;
      const abs = resolve(dirname(file), raw);
      const target = rel(root, abs);
      if (target.startsWith('..')) continue;
      if (existsSync(abs) || planned.some((p) => p.to === target)) {
        failures.push({ kind: 'NONSTANDARD', at, detail: `\`${raw}\` points inside vstack. Write it as [..](${raw}) or \`<vstack>/${target}\`` });
      }
    }

    const { names, tool } = skillRefs(line);
    for (const { name } of names) {
      const local = name.startsWith('vstack:') ? name.slice('vstack:'.length) : name;
      if (!shipped.has(local) && !shipped.has(`principle-${local}`) && !runtimeCommands.has(name) && !userCommands.has(name)) {
        failures.push({ kind: 'SKILL', at, detail: `\`${name}\` is not a vstack skill` });
      }
    }
    if (tool) failures.push({ kind: 'TOOL', at, detail: 'tool-specific invocation ("Skill tool"). Write "read <path> and follow it"' });
  });
}

// Closure: compare adapted/extracted imports against their sources.
for (const entry of upstream.imports) {
  if (entry.stage > stage || !['adapted', 'extracted'].includes(entry.mode)) continue;
  const srcRoot = sources[entry.source];
  if (!srcRoot) {
    failures.push({ kind: 'CLOSURE', at: entry.to, detail: `needs --source ${entry.source}=<dir> to check closure` });
    continue;
  }
  const base = join(srcRoot, upstream.sources[entry.source].path, entry.from);
  if (!existsSync(base)) {
    failures.push({ kind: 'CLOSURE', at: entry.to, detail: `source not found: ${base}` });
    continue;
  }
  const isFile = statSync(base).isFile();
  const srcDir = isFile ? dirname(base) : base;
  const dropped = new Set((entry.dropped ?? []).map((d) => d.path));
  const excluded = new Set(entry.exclude ?? []);
  for (const file of isFile ? [base] : walkMarkdown(base)) {
    const lines = readFileSync(file, 'utf8').split(/\r?\n/);
    lines.forEach((line, idx) => {
      const { standard, inline } = pathRefs(line, { inFence: false });
      for (const { raw } of [...standard, ...inline]) {
        if (isUrlOrAnchor(raw) || /[<>]/.test(raw)) continue;
        const abs = resolve(dirname(file), raw.split('#')[0]);
        const inSrc = rel(srcDir, abs);
        if (inSrc.startsWith('..') || !existsSync(abs) || !statSync(abs).isFile()) continue;
        if (isFile && abs === base) continue;
        if (dropped.has(inSrc) || excluded.has(inSrc)) continue;
        const dest = isFile ? null : join(root, entry.to, inSrc);
        if (!dest || !existsSync(dest)) {
          failures.push({
            kind: 'NOT CARRIED',
            at: `${entry.source}:${rel(srcDir, file)}:${idx + 1}`,
            detail: `${inSrc} is referenced in the source but not in ${entry.to} and not listed in "dropped"`,
          });
        }
      }
    });
  }
}

for (const p of later) console.log(`planned      ${p.at} -> ${p.target} (stage ${p.stage})`);
for (const f of failures) console.error(`${f.kind.padEnd(12)} ${f.at} ${f.detail}`);
console.log(`checked ${checked} paths: ${failures.length} failures, ${later.length} planned for a later stage.`);
process.exit(failures.length ? 1 : 0);
