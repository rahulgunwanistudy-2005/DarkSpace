import type { Interview, Placement } from './contracts.ts';

export function startInterview(placement: Placement): Interview {
  const questions = placement.defaults.filter(value => value.count / value.denominator > 0.5)
    .toSorted((a, b) => b.count / b.denominator - a.count / a.denominator || a.id.localeCompare(b.id, 'en'))
    .slice(0, 5).map(value => ({ default: value, status: 'pending' as const, answer: '' }));
  return {
    baseline: placement, placements: [placement], questions, current: 0,
    phase: questions.length > 0 ? 'question' : 'complete', stopped: false,
    draftIdea: placement.idea, confirmedAvoided: [],
  };
}

export function saveAnswerDraft(session: Interview, answer: string): Interview {
  if (session.phase !== 'question') throw new Error('There is no active question to edit.');
  return { ...session, questions: session.questions.map((question, index) => index === session.current ? { ...question, answer } : question) };
}

export function answerQuestion(session: Interview): Interview {
  if (session.phase !== 'question') throw new Error('There is no active question to answer.');
  if (!session.questions[session.current]?.answer.trim()) throw new Error('Write your answer or choose Skip.');
  return { ...session, phase: 'rewrite', questions: session.questions.map((question, index) => index === session.current ? { ...question, status: 'answered' } : question) };
}

export function skipQuestion(session: Interview): Interview {
  if (session.phase !== 'question') throw new Error('There is no active question to skip.');
  const current = session.current + 1;
  return { ...session, current, phase: current >= session.questions.length ? 'complete' : 'question', questions: session.questions.map((question, index) => index === session.current ? { ...question, status: 'skipped' } : question) };
}

export function saveIdeaDraft(session: Interview, idea: string): Interview {
  return { ...session, draftIdea: idea };
}

export function recordPlacement(session: Interview, placement: Placement): Interview {
  if (session.phase !== 'rewrite') throw new Error('Answer the current question before recording its rewrite.');
  const previous = session.placements.at(-1)!;
  if (placement.kind !== previous.kind || placement.evidenceKind !== previous.evidenceKind) throw new Error('A sample cannot replace a personal placement in the same interview.');
  if (placement.runId !== previous.runId || placement.contractDigest !== previous.contractDigest) throw new Error('The forecast changed. Place again explicitly on this forecast; keep the previous words.');
  const current = session.current + 1;
  return { ...session, placements: [...session.placements, placement], draftIdea: placement.idea, current, phase: current >= session.questions.length ? 'complete' : 'question' };
}

export function rebaseInterview(session: Interview, placement: Placement): Interview {
  if (placement.kind !== session.baseline.kind) throw new Error('A sample cannot replace personal work during forecast recovery.');
  return { ...session, placements: [...session.placements, placement], draftIdea: placement.idea };
}

export function stopInterview(session: Interview): Interview {
  return { ...session, phase: 'complete', stopped: true };
}

export function confirmAvoided(session: Interview, ids: readonly string[]): Interview {
  const known = new Set(session.questions.map(question => question.default.id));
  if (ids.some(id => !known.has(id))) throw new Error('Only defaults considered in this interview can be confirmed.');
  return { ...session, confirmedAvoided: [...new Set(ids)] };
}

export function isCurrentPlacement(placement: Placement, runId: string, contractDigest: string): boolean {
  return placement.runId === runId && placement.contractDigest === contractDigest;
}

function rawBlock(value: string): string {
  const longest = Math.max(0, ...[...value.matchAll(/`+/gu)].map(match => match[0].length));
  const fence = '`'.repeat(Math.max(3, longest + 1));
  return `${fence}text\n${value}\n${fence}`;
}

function metric(placement: Placement): string {
  return placement.density === null ? 'Unavailable' : `${placement.density.percentile.toFixed(2)} percentile (higher means less crowded; k=${placement.density.k}; mean distance=${placement.density.meanDistance})`;
}

export function exportHandoff(session: Interview): string {
  const first = session.baseline;
  const last = session.placements.at(-1)!;
  const lines = [
    '# Dark Space — Hand-off', '',
    `Evidence: ${first.evidenceKind}. Placement: ${first.kind}.`,
    'This informs your 2-scope brain dump. It is a starting point, not a completed scope or quality score.', '',
    `Original forecast run: ${first.runId}`, `Original vector contract: ${first.contractDigest}`,
    `Last evidence: ${last.evidenceKind}`, `Last forecast run: ${last.runId}`, `Last vector contract: ${last.contractDigest}`, '',
    '## Idea before', '', rawBlock(first.idea), '', metric(first), '',
    '## Idea after — last successful placement', '', rawBlock(last.idea), '', metric(last), '',
  ];
  if (session.draftIdea !== last.idea) lines.push('## Unplaced draft — no measurement', '', rawBlock(session.draftIdea), '');
  if (first.runId !== last.runId || first.contractDigest !== last.contractDigest) {
    lines.push('The forecast changed between these placements. Their percentiles are historical measurements on different references; no movement comparison is calculated.', '');
  } else if (first.density !== null && last.density !== null) {
    const difference = last.density.percentile - first.density.percentile;
    lines.push(`Measured percentile change: ${difference.toFixed(2)} percentage points. ${Math.abs(difference) < 1 ? 'The measured crowding changed little.' : difference < 0 ? 'The last placement is more crowded in this forecast.' : 'The last placement is less crowded in this forecast.'}`, 'This is not an assessment of idea quality.', '');
  }
  lines.push('## Crowded clusters near the idea', '');
  for (const [label, placement] of [['Before', first], ['After', last]] as const) {
    lines.push(`${label}:`, '');
    if (placement.nearbyClusters.length === 0) lines.push('No measured clusters available.', '');
    else lines.push(...placement.nearbyClusters.map(cluster => `- ${cluster.name}: ${cluster.memberCount} forecast samples; mean nearest-member cosine distance ${cluster.distance}.`), '');
  }
  lines.push('## Defaults considered and answers — exact words', '', `Question/default frequencies refer to the original forecast ${first.runId}.`, '');
  for (const question of session.questions) {
    const value = question.default;
    lines.push(`### ${value.label}`, '', `${value.count}/${value.denominator} cluster samples (${(100 * value.count / value.denominator).toFixed(2)}%); ${value.unknown} unknown.`, '', value.question, '', `Status: ${question.status}.`, '', rawBlock(question.answer), '');
  }
  if (session.questions.length === 0) lines.push('No majority defaults were available to ask.', '');
  lines.push('## Defaults avoided — user confirmation only', '');
  const confirmed = session.questions.filter(question => session.confirmedAvoided.includes(question.default.id));
  if (confirmed.length === 0) lines.push('None confirmed. An answer, a skip, or a percentile change does not establish avoidance.', '');
  else lines.push(...confirmed.map(question => `- ${question.default.label}: ${question.default.count}/${question.default.denominator}; user-confirmed, not model-verified.`), '');
  lines.push('## Successful placement trail', '');
  session.placements.forEach((placement, index) => lines.push(`${index + 1}. ${metric(placement)}; run ${placement.runId}; approximate map position (${placement.position.x}, ${placement.position.y}).`));
  const missing = [...new Set(session.placements.flatMap(placement => placement.missing))];
  lines.push('', `Missing result components: ${missing.length}.`, ...missing.map(value => `- ${value}`), '', `Interview ${session.stopped ? 'stopped by the builder' : session.phase === 'complete' ? 'completed' : 'in progress'}.`, '', 'Bring this file into your 2-scope brain dump. Your answers and scope remain yours.', '');
  return lines.join('\n');
}
