import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, symlink, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { startingIdea, writeLocalHandoff } from '../src/companion-io.ts';

test('local companion extracts only the starting idea without rewriting its words', () => {
  assert.equal(startingIdea('# Profile\n\n## Initial Idea\n  My own words.  \n\n## Background\nPrivate context'), '  My own words.  ');
  assert.throws(() => startingIdea('## Background\nNo idea'), /Initial Idea/);
});

test('handoff refuses protected paths, symlinks and overwrite while preserving exact text', async () => {
  const root = await mkdtemp(join(tmpdir(), 'darkspace-companion-'));
  try {
    const text = '  own words\n```\nanswer  \n';
    const output = await writeLocalHandoff(root, text);
    assert.equal(await readFile(output, 'utf8'), text);
    await assert.rejects(writeLocalHandoff(root, 'replacement'), /EEXIST/);
    const protectedProject = join(root, 'devpost');
    await mkdir(protectedProject);
    await assert.rejects(writeLocalHandoff(protectedProject, text), /outside/);
    const linkedProject = join(root, 'other');
    await mkdir(linkedProject);
    await symlink(protectedProject, join(linkedProject, 'darkspace-output'));
    await assert.rejects(writeLocalHandoff(linkedProject, text), /symbolic link/);
  } finally { await rm(root, { recursive: true, force: true }); }
});
