import { readFile, access } from 'node:fs/promises';
import { createInterface } from 'node:readline';
import { resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadEmbedder } from './embed.ts';
import { place, validateRun } from './place.ts';
import { startInterview, saveAnswerDraft, answerQuestion, skipQuestion, stopInterview, saveIdeaDraft, recordPlacement, confirmAvoided, exportHandoff } from './interview.ts';
import { startingIdea, writeLocalHandoff } from './companion-io.ts';
import type { ForecastRun } from './contracts.ts';

const repository = resolve(fileURLToPath(new URL('../../../', import.meta.url)));
const project = resolve(process.argv[2] ?? process.cwd());
if (!process.stdin.isTTY || !process.stdout.isTTY) {
  console.error('Run this companion yourself in an interactive local terminal. Personal ideas and answers must not be captured by a hosted agent.');
  process.exitCode = 1;
} else {
  const privateRun=resolve(repository,'.darkspace-local/bundles/current/data/current.json');
  let runPath=privateRun;
  try { await access(runPath); } catch { runPath=resolve(repository,'web/static/data/current.json'); }
  const run = JSON.parse(await readFile(runPath, 'utf8')) as ForecastRun;
  validateRun(run);
  if (run.evidenceKind !== 'model-forecast') throw new Error('The companion requires an actual public forecast.');
  const profile = await readFile(resolve(project, 'devpost/learner-profile.md'), 'utf8');
  let idea = startingIdea(profile);
  const terminal = createInterface({ input: process.stdin, output: process.stdout, terminal: true });
  const lines = terminal[Symbol.asyncIterator]();
  async function read(): Promise<string | null> { const value = await lines.next(); return value.done ? null : value.value; }
  console.log('Dark Space · local companion\nYour words stay on this device. No scope or Skill Pack files are edited.\nStarting idea from your learner profile:\n' + idea);
  console.log('\nPress Enter to keep it, type your one-sentence idea to edit it, or /stop to leave.');
  const edited = await read();
  if (edited === null || edited === '/stop') terminal.close();
  else {
    if (edited.length) idea = edited;
    const assets = resolve(repository, '.cache/placement-assets');
    console.log('Loading the verified local placement model.');
    const embedder = await loadEmbedder(async path => new Uint8Array(await readFile(resolve(assets, path))), resolve(assets, 'runtime') + sep);
    try {
      async function measure(sentence: string) {
        console.log('Reading your idea locally, finding nearby ideas, and measuring crowding.');
        return place(run, { idea: sentence, vector: await embedder.embed(sentence), contract: run.contract, kind: 'personal' });
      }
      let session = startInterview(await measure(idea));
      console.log('\nNearby forecast clusters:');
      for (const cluster of session.baseline.nearbyClusters) console.log(`- ${cluster.name}: ${cluster.memberCount} sampled ideas`);
      console.log('\nShared wording nearby (model outputs, not real entrants):');
      for (const question of session.questions) console.log(`- ${question.default.label}: ${question.default.count}/${question.default.denominator}`);
      if (!session.questions.length) console.log('No majority defaults were found. No questions are invented.');
      while (session.phase !== 'complete') {
        const question = session.questions[session.current]!;
        console.log(`\nQuestion ${session.current + 1} of ${session.questions.length}\n${question.default.question}\nType your own answer. A line containing /done saves it; /skip skips; /stop ends the interview. Lines beginning // preserve a literal command (//done becomes /done).`);
        const answer: string[] = [];
        let command: string | null = null;
        while (command === null) {
          const line = await read();
          if (line === null) { command = '/stop'; break; }
          if (['/done', '/skip', '/stop'].includes(line)) command = line;
          else answer.push(line.startsWith('//') ? line.slice(1) : line);
        }
        session = saveAnswerDraft(session, answer.join('\n'));
        if (command === '/stop') { session = stopInterview(session); break; }
        if (command === '/skip') { session = skipQuestion(session); continue; }
        try { session = answerQuestion(session); }
        catch { console.log('The answer is empty. Answer in your own words or use /skip.'); continue; }
        while (session.phase === 'rewrite') {
          console.log('\nRewrite your idea in one sentence and press Enter, or /stop to keep the hand-off. Your previous sentence:\n' + session.draftIdea);
          const rewrite = await read();
          if (rewrite === null || rewrite === '/stop') { session = stopInterview(session); break; }
          session = saveIdeaDraft(session, rewrite);
          try { session = recordPlacement(session, await measure(rewrite)); }
          catch (error) { console.log(error instanceof Error ? error.message : 'Placement failed. Edit and try again.'); }
        }
      }
      if (session.questions.length) {
        console.log('\nOptional: enter the numbers of defaults you confirm you avoided, separated by spaces. Enter leaves none confirmed.');
        session.questions.forEach((question, index) => console.log(`${index + 1}. ${question.default.label}`));
        const raw = await read();
        const numbers = raw?.trim() ? raw.trim().split(/\s+/u).map(Number) : [];
        if (numbers.every(value => Number.isInteger(value) && value > 0 && value <= session.questions.length)) session = confirmAvoided(session, numbers.map(value => session.questions[value - 1]!.default.id));
        else console.log('No defaults confirmed: the supplied numbers were not valid.');
      }
      const output = await writeLocalHandoff(project, exportHandoff(session));
      console.log('\nHand-off saved locally: ' + output + '\nBring this file into your 2-scope brain dump. Scoping remains yours.');
    } finally { await embedder.close(); terminal.close(); }
  }
}
