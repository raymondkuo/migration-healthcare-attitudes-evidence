import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const siteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const pages = [
  ...fs.readdirSync(siteRoot).filter((file) => file.endsWith('.html')).map((file) => path.join(siteRoot, file)),
  ...fs.readdirSync(path.join(siteRoot, 'countries')).filter((file) => file.endsWith('.html')).map((file) => path.join(siteRoot, 'countries', file))
];
const errors = [];
let links = 0;

for (const file of pages) {
  const html = fs.readFileSync(file, 'utf8');
  if (!html.toLowerCase().includes('<!doctype html>')) errors.push(`${path.relative(siteRoot, file)}: missing doctype`);
  for (const match of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const href = match[1];
    if (/^(https?:|mailto:|#|data:|javascript:)/i.test(href)) continue;
    const clean = decodeURI(href.split('#')[0].split('?')[0]);
    if (!clean) continue;
    links += 1;
    if (!fs.existsSync(path.resolve(path.dirname(file), clean))) errors.push(`${path.relative(siteRoot, file)} -> ${href}`);
  }
}

const requestedWorkbook = 'data/migration_population_panel_40countries_2010-2022_final.xlsx';
const indexHtml = fs.readFileSync(path.join(siteRoot, 'index.html'), 'utf8');
const dataHtml = fs.readFileSync(path.join(siteRoot, 'data.html'), 'utf8');
const manifest = JSON.parse(fs.readFileSync(path.join(siteRoot, 'manifest', 'website_manifest.json'), 'utf8'));
const workbookHash = crypto.createHash('sha256').update(fs.readFileSync(path.join(siteRoot, requestedWorkbook))).digest('hex');

if (pages.length !== 46) errors.push(`expected 46 site pages, found ${pages.length}`);
if (!indexHtml.includes(requestedWorkbook)) errors.push('index.html is missing the requested workbook link');
if (!dataHtml.includes(requestedWorkbook)) errors.push('data.html is missing the requested workbook link');
if (manifest.secondary_workbook?.sha256 !== workbookHash) errors.push('website manifest workbook hash mismatch');
if (manifest.pages?.country_pages !== 40) errors.push('website manifest country page count mismatch');
if (manifest.archive?.country_year_rows !== 520) errors.push('website manifest panel row count mismatch');

if (errors.length) {
  console.error(errors.join('\n'));
  process.exitCode = 1;
} else {
  console.log(`Validated ${pages.length} site pages and ${links} local links; requested workbook link, manifest hash and page count all pass.`);
}
