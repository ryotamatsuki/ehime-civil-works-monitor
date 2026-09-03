import { readFile, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const dataset = JSON.parse(await readFile(path.join(root, 'public/data/projects.json'), 'utf8'));
const phase26 = JSON.parse(await readFile(path.join(root, 'public/data/phase26-inventory.json'), 'utf8'));
const reconciliation = JSON.parse(await readFile(path.join(root, 'public/data/phase26-reconciliation.json'), 'utf8'));
const phase27 = JSON.parse(await readFile(path.join(root, 'public/data/phase27-inventory.json'), 'utf8'));
const indexHtml = await readFile(path.join(root, 'dist/index.html'), 'utf8');
const excluded = new Set(reconciliation.excludedExistingRoadIds.map((item) => item.candidateId));
const roadIds = [
  ...phase26.roads.filter((row) => !excluded.has(row[0])).map((row) => row[0]),
  ...reconciliation.roadAdditions.map((row) => row[0]),
];
const projectIds = [
  ...dataset.projects.map((project) => project.id),
  ...roadIds,
  ...phase26.sabo.map((row) => row[0]),
  ...phase27.projects.map((row) => row[0]),
];

for (const projectId of projectIds) {
  const dir = path.join(root, 'dist/projects', projectId);
  await mkdir(dir, { recursive: true });
  await writeFile(path.join(dir, 'index.html'), indexHtml, 'utf8');
}

console.log(`Generated ${projectIds.length} detail page entry points.`);
