import { lstat, mkdir, realpath, writeFile } from 'node:fs/promises';
import { join, sep } from 'node:path';

export function startingIdea(profile: string): string {
  const section = profile.match(/^## Initial Idea\s*\r?\n([\s\S]*?)(?=^## |$(?![\s\S]))/mu)?.[1];
  if (!section?.trim()) throw new Error('The learner profile has no Initial Idea section. Run 1-start first.');
  return section.replace(/^\r?\n/u, '').replace(/\r?\n\s*$/u, '');
}

export async function writeLocalHandoff(project: string, content: string): Promise<string> {
  const root = await realpath(project);
  const directory = join(root, 'darkspace-output');
  if (root.split(sep).some(part => ['devpost', '.agents', '.codex', 'skills'].includes(part))) throw new Error('The hand-off must be outside planning and skill directories.');
  try {
    if ((await lstat(directory)).isSymbolicLink()) throw new Error('The hand-off directory must not be a symbolic link.');
  } catch (error) { if (!(error instanceof Error && 'code' in error && error.code === 'ENOENT')) throw error; }
  await mkdir(directory, { recursive: true, mode: 0o700 });
  if (await realpath(directory) !== directory) throw new Error('The hand-off directory resolves through a symbolic link.');
  const target = join(directory, 'HANDOFF.md');
  await writeFile(target, content, { flag: 'wx', mode: 0o600 });
  return target;
}
