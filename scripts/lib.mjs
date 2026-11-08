import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, relative, sep } from 'node:path';

export function loadUpstream(root) {
  return JSON.parse(readFileSync(join(root, 'upstream.json'), 'utf8'));
}

export function walkFiles(dir, filter = () => true) {
  if (!existsSync(dir)) return [];
  if (statSync(dir).isFile()) return filter(dir) ? [dir] : [];
  const out = [];
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) out.push(...walkFiles(p, filter));
    else if (filter(p)) out.push(p);
  }
  return out;
}

export function walkMarkdown(dir) {
  return walkFiles(dir, (p) => p.endsWith('.md'));
}

export function toPosix(p) {
  return p.split(sep).join('/');
}

export function rel(root, p) {
  return toPosix(relative(root, p));
}

// Skill folder names vstack ships or plans to ship, in any stage.
export function plannedSkillNames(upstream) {
  const names = new Set();
  for (const entry of [...upstream.imports, ...upstream.own]) {
    const m = entry.to.match(/^skills\/([^/]+)/);
    if (m) names.add(m[1]);
  }
  return names;
}

// The import entry whose destination contains this repo-relative path, if any.
export function importFor(upstream, repoPath) {
  return upstream.imports.find((e) => repoPath === e.to || repoPath.startsWith(e.to + '/'));
}

export function plannedTargets(upstream) {
  return [...upstream.imports, ...upstream.own].map((e) => ({ to: e.to, stage: e.stage }));
}

const EXT = '(?:md|sh|mjs|cjs|js|ts|py|json|ya?ml|tsv|txt)';

// Path references written in a markdown line, split into the standard forms
// (checked as execution references) and inline code paths (non-standard).
// Placeholders such as <name> are left in; callers decide what to skip.
export function pathRefs(line, { inFence }) {
  const standard = [];
  const inline = [];
  if (!inFence) {
    const prose = line.replace(/(`+)(?:(?!\1).)*?\1/g, (s) => ' '.repeat(s.length));
    for (const m of prose.matchAll(/\]\(\s*<([^>]+)>(?:\s+"[^"]*")?\s*\)/g)) standard.push({ form: 'link', raw: m[1] });
    for (const m of prose.matchAll(/\]\(\s*([^)\s<][^)\s]*)(?:\s+"[^"]*")?\s*\)/g)) standard.push({ form: 'link', raw: m[1] });
    const def = prose.match(/^\s{0,3}\[[^\]]+\]:\s*<?([^>\s]+)>?/);
    if (def) standard.push({ form: 'refdef', raw: def[1] });
  }
  for (const m of line.matchAll(/`<vstack>\/([^`\s]+)`/g)) standard.push({ form: 'vstack', raw: m[1] });
  const inlineRe = new RegExp('`((?!<vstack>)[^`\\s]+\\.' + EXT + ')`', 'g');
  for (const m of line.matchAll(inlineRe)) inline.push({ form: 'inline', raw: m[1] });
  return { standard, inline };
}

// Mentions of a skill by name, plus tool-specific invocation phrases.
export function skillRefs(line) {
  const out = [];
  const patterns = [
    /\*\*([a-z][a-z0-9-]*)\*\*(?: principle)? (?:skill|스킬)/g,
    /`([a-z][a-z0-9-]*)` (?:skill|스킬)/g,
    /`\/([a-z][a-z0-9-]*(?::[a-z][a-z0-9-]*)?)`/g,
    /Skill tool with "([a-z][a-z0-9-]*)"/g,
  ];
  for (const re of patterns) for (const m of line.matchAll(re)) out.push({ name: m[1] });
  const tool = /\b(?:call|use|invoke) the Skill tool\b|Skill (?:tool|도구)/.test(line);
  return { names: out, tool };
}

export function isUrlOrAnchor(raw) {
  return /^[a-z][a-z0-9+.-]*:/i.test(raw) || raw.startsWith('#');
}
