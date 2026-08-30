import { readFile, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const dataset = JSON.parse(await readFile(path.join(root, 'public/data/projects.json'), 'utf8'));
const indexHtml = await readFile(path.join(root, 'dist/index.html'), 'utf8');

for (const project of dataset.projects) {
  const dir = path.join(root, 'dist/projects', project.id);
  await mkdir(dir, { recursive: true });
  await writeFile(path.join(dir, 'index.html'), indexHtml, 'utf8');
}

console.log(`Generated ${dataset.projects.length} detail page entry points.`);
