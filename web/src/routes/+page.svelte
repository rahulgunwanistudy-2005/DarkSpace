<script lang="ts">
  import { onMount, tick } from 'svelte';
  import Map from '../lib/Map.svelte';
  import Mark from '../lib/Mark.svelte';
  import { loadRun, type ViewRun } from '../lib/data.ts';
  import { startInterview, saveAnswerDraft, answerQuestion, skipQuestion, saveIdeaDraft, recordPlacement, rebaseInterview, stopInterview, confirmAvoided, exportHandoff, isCurrentPlacement } from '../../../packages/core/src/interview.ts';
  import { validateIdea } from '../../../packages/core/src/place.ts';
  import type { Interview, Placement } from '../../../packages/core/src/contracts.ts';

  const storageKey = 'darkspace.idea.v1';
  let run = $state<ViewRun | null>(null);
  let draft = $state('');
  let placement = $state<Placement | null>(null);
  let session = $state<Interview | null>(null);
  let panel = $state(true);
  let started = $state(false);
  let stale = $state(false);
  let busy = $state(false);
  let stage = $state('');
  let elapsed = $state(0);
  let message = $state('Loading the saved public forecast');
  let failure = $state(false);
  let storageAvailable = $state(true);
  let recovery = $state<{ draft: string; session: Interview | null; placement: Placement | null; started: boolean } | null>(null);
  let input: HTMLInputElement;
  let worker: Worker | null = null;
  let epoch = 0;
  let timer: ReturnType<typeof setInterval> | null = null;
  let timeout: ReturnType<typeof setTimeout> | null = null;
  let ready = false;
  let selectedDefault = 0;
  let authored = false;
  let handoffURL = $state<string | null>(null);
  $effect(() => {
    if (!session || session.phase!=='complete') { handoffURL=null; return; }
    const url=URL.createObjectURL(new Blob([exportHandoff(session)],{type:'text/markdown;charset=utf-8'}));
    handoffURL=url;
    return ()=>URL.revokeObjectURL(url);
  });

  function persist(): void {
    if (!ready || (!authored && !session)) return;
    const saved = recovery ? { ...recovery, draft } : { draft, session, placement: placement?.kind === 'personal' ? placement : null, started };
    try { localStorage.setItem(storageKey, JSON.stringify({ version: 1, ...saved })); }
    catch { storageAvailable=false; }
  }
  $effect(() => { draft; session; placement; started; if (ready) persist(); });

  function readRecovery(): void {
    try {
      const raw: unknown = JSON.parse(localStorage.getItem(storageKey) ?? 'null');
      if (!raw || typeof raw !== 'object' || !('version' in raw) || raw.version!==1 || !('draft' in raw) || typeof raw.draft!=='string' || !('session' in raw) || !('placement' in raw) || !('started' in raw) || typeof raw.started!=='boolean') return;
      const saved = raw as NonNullable<typeof recovery>;
      if (saved.session && (!Array.isArray(saved.session.questions) || saved.session.questions.length>5 || !Array.isArray(saved.session.placements) || !saved.session.placements.length || !saved.session.questions.every(value=>typeof value.answer==='string'))) return;
      recovery=saved; draft=saved.draft; authored=true;
    } catch { storageAvailable=false; }
  }
  function restore(): void {
    if (!recovery || !run) return;
    session=recovery.session; started=recovery.started;
    if (session && session.draftIdea!==draft) session=saveIdeaDraft(session,draft);
    const previous=recovery.placement ?? session?.placements.at(-1) ?? null;
    stale=Boolean(previous && !isCurrentPlacement(previous,run.runId,run.contract.digest));
    placement=stale ? null : previous;
    message=stale ? 'This was placed on an older forecast. Place again.' : '';
    recovery=null; panel=true;
  }
  async function initialize(): Promise<void> {
    try {
      run=await loadRun(); message=''; failure=false;
      if (!draft) draft=run.points[0]?.idea ?? '';
      if (!placement) placement=run.samplePlacements?.[0] ?? null;
      if(!worker && typeof Worker!=='undefined') {
        try {
          const warming=new Worker(new URL('../lib/placement.worker.ts',import.meta.url),{type:'module'});
          worker=warming;
          warming.onerror=()=>{if(worker===warming&&!busy){warming.terminate();worker=null;}};
          warming.postMessage({id:0,type:'warm'});
        } catch { worker=null; }
      }
      if (recovery) {
        try { if(sessionStorage.getItem('darkspace.methods-return')) { sessionStorage.removeItem('darkspace.methods-return'); restore(); } } catch { /* In-memory interaction still works. */ }
      }
    } catch(error) { failure=true; message=error instanceof Error ? error.message : 'The saved forecast could not be read. Try again.'; }
    ready=true;
  }
  onMount(() => { readRecovery(); void initialize(); return () => { persist(); cancel(false); }; });

  function clearTimers(): void {
    if (timer) clearInterval(timer);
    if (timeout) clearTimeout(timeout);
    timer=null; timeout=null;
  }
  function cancel(showMessage=true): void {
    epoch++; worker?.terminate(); worker=null; clearTimers(); busy=false;
    if(showMessage) { message='Placement canceled. Your sentence is unchanged.'; failure=false; }
  }
  function fail(text: string): void {
    cancel(false); message=text; failure=true; panel=true;
  }
  function placeCurrent(): void {
    if (busy) return;
    if (!run) { failure=true; message='The public forecast is unavailable. Your sentence is saved locally when storage is available.'; return; }
    authored=true;
    if (recovery) restore();
    try { validateIdea(draft); } catch(error) { fail(error instanceof Error?error.message:'The sentence cannot be placed.'); return; }
    const sentence=draft;
    const id=++epoch;
    const start=performance.now();
    busy=true; panel=true; failure=false; stage='Starting private placement'; message=''; elapsed=0;
    timer=setInterval(()=>elapsed=(performance.now()-start)/1000,100);
    timeout=setTimeout(()=>fail('Loading the local model took too long. Your sentence is unchanged. Try again or choose a saved sample.'),60000);
    try { worker ??= new Worker(new URL('../lib/placement.worker.ts',import.meta.url),{type:'module'}); }
    catch { fail('Private placement is unavailable in this browser. Your sentence is unchanged. Use a saved sample or try another browser.'); return; }
    worker.onerror=()=>fail('The local model could not start on this device. Try again or choose a saved sample. Your sentence is unchanged.');
    worker.onmessage=({data})=>{
      if (data.id!==epoch) return;
      if (data.type==='stage') {
        stage=data.message;
        if(data.message==='Reading your idea on this device') { if(timeout)clearTimeout(timeout); timeout=setTimeout(()=>fail('Placing this sentence took too long. Try again or edit it. Your sentence is unchanged.'),15000); }
      } else if(data.type==='error') fail(data.message);
      else if(data.type==='result') {
        clearTimers();busy=false;
        const result=data.result as Placement;
        placement=result;
        if(stale && session) session=rebaseInterview(session,result);
        else if(session?.phase==='rewrite') session=recordPlacement(session,result);
        else if(session && session.baseline.kind==='personal') session={...session,placements:[...session.placements,result],draftIdea:result.idea};
        else { session=startInterview(result);started=false; }
        stale=false;message='';failure=false;
        persist();
        if(started && session?.phase==='question') void focusQuestion();
      }
    };
    try { worker.postMessage({id,idea:sentence,run:$state.snapshot(run)}); }
    catch { fail('This browser could not read the forecast for private placement. Your sentence is unchanged. Try again.'); }
  }
  function useSample(sample: Placement): void {
    cancel(false); placement=sample; panel=true; message='Sample placement. Your own sentence has not been replaced or placed.';failure=false;
  }
  function begin(index=0): void {
    if(!session || placement?.kind!=='personal') return;
    if(index>=session.current && session.questions[index]?.status==='pending') {
      const questions=[...session.questions];
      const [chosen]=questions.splice(index,1); questions.splice(session.current,0,chosen!);
      session={...session,questions};
    }
    started=true;
    void focusQuestion();
  }
  async function focusQuestion(): Promise<void> {
    await tick();
    document.querySelector('.question')?.scrollIntoView({block:'start'});
    document.getElementById('answer')?.focus({preventScroll:true});
  }
  function saveAnswer(): void {
    if(!session)return;
    try { session=answerQuestion(session); input?.focus(); } catch(error) { message=error instanceof Error?error.message:''; }
  }
  function forget(): void {
    cancel(false); ready=false;
    draft='';session=null;placement=run?.samplePlacements?.[0]??null;started=false;stale=false;recovery=null;authored=false;failure=false;message='This idea has been forgotten on this device.';
    try { localStorage.removeItem(storageKey); } catch { storageAvailable=false; }
    ready=true;
  }
  function keys(event: KeyboardEvent): void {
    const target=event.target as HTMLElement;
    const editing=target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement || target.isContentEditable;
    if(event.key==='Escape') panel=false;
    if(event.key==='/'&&!editing) { event.preventDefault();input?.focus(); }
    if(!editing&&panel&&['ArrowDown','ArrowUp'].includes(event.key)) {
      const buttons=[...document.querySelectorAll<HTMLButtonElement>('.default-row')];
      if(buttons.length) { event.preventDefault(); selectedDefault=(selectedDefault+(event.key==='ArrowDown'?1:-1)+buttons.length)%buttons.length;buttons[selectedDefault]?.focus(); }
    }
  }
  function leavingForMethods(): void { persist();try{sessionStorage.setItem('darkspace.methods-return','1');}catch{ /* Storage is optional. */ } }
  const format=(value:number):string=>value.toFixed(1);
</script>

<svelte:head><title>Dark Space — Forecast instrument</title></svelte:head>
<svelte:window onkeydown={keys}/>

<main class:has-panel={panel}>
  <header class="instrument-header">
    <a class="wordmark" href="/" aria-label="Dark Space home"><span class="brand-symbol"><Mark size={26}/></span>Dark Space</a>
    <nav class="navigation" aria-label="Main navigation"><a class="active" href="/" aria-current="page">Forecast map</a><a href="/methods" onclick={leavingForMethods}>Methods <span aria-hidden="true">↗</span></a></nav>
    <span class="privacy-pill"><span aria-hidden="true"></span>Private by design</span>
  </header>
  <section class="workspace-intro" aria-labelledby="workspace-title">
    <div class="event-label"><span aria-hidden="true"></span>{run?.event??'Build With AI: Basics'}</div>
    <h1 id="workspace-title">Find room for your own idea.</h1>
    <p>{run?.evidenceKind==='synthetic-fixture'?'Synthetic test fixture. No real forecasts or entries.':'Forecast for this hackathon. These are not real entries.'}</p>
    {#if run}<div class="run-summary"><span><strong>{run.points.length}</strong> sampled ideas</span><span><strong>{run.clusters.length}</strong> {run.clusters.length===1?'cluster':'clusters'}</span><span>Forecast only <i aria-hidden="true"></i></span>{#if typeof run.provenance?.attempted==='number'}<span>{run.provenance.attempted} attempted · {String(run.provenance.failures)} failed</span>{/if}</div>{/if}
  </section>
  <div class="evidence-status"><span class="status-mark"></span>Historical backtest pending. No coverage claim is available.</div>
  {#if run}<Map {run} {placement} trail={session?.placements??[]}/>{/if}
  {#if recovery}<div class="recovery"><span>Continue where you left off.</span><button onclick={restore}>Continue</button><button class="quiet" onclick={forget}>Forget this idea</button></div>{/if}
  {#if !run}<section class="unavailable" aria-live="polite"><h2>{failure?'The forecast is unavailable':'Reading the saved forecast'}</h2><p>{message}</p><button onclick={()=>void initialize()}>Try again</button></section>{/if}

  {#if panel}<aside class="instrument-panel" aria-label="Idea neighborhood">
    <div class="panel-heading"><span class="panel-symbol"><Mark size={16}/></span><span>Idea neighborhood</span></div>
    <button class="close-panel quiet" aria-label="Close panel" onclick={()=>panel=false}>×</button>
    {#if busy}<div class="progress" role="status"><span>Placing on this device</span><h2>{stage}</h2><p class="timer">{elapsed.toFixed(1)} s</p><p>The map stays interactive. Your sentence stays here.</p><button onclick={()=>cancel()}>Cancel</button></div>
    {:else if stale}<div class="stale"><h2>This was placed on an older forecast.</h2><p>Your words and answers are still here. Old percentiles are not current.</p><button onclick={placeCurrent}>Place again</button></div>
    {:else if placement}
      <div class="placement-kind">{placement.kind==='sample'?'Sample placement':'Your idea’s neighborhood'}</div>
      {#if placement.density}<div class="percentile">{format(placement.density.percentile)}<span>th</span></div><div class="percentile-scale" aria-hidden="true"><i style:left="{Math.min(100,Math.max(0,placement.density.percentile))}%"></i><span>0</span><span>50</span><span>100</span></div><p class="metric-label">density percentile</p><p class="metric-meaning">Higher means less crowded in this sampled forecast. It does not mean a better idea.</p>{:else}<h2>Density unavailable</h2>{/if}
      <h2 class="cluster-name">{placement.assignedClusterId?run?.clusters.find(value=>value.id===placement?.assignedClusterId)?.name:'Outside the sampled clusters'}</h2>
      {#if placement.kind==='sample'}<p class="sample-note">Sample: {placement.idea}</p><p class="muted">Place your sentence to begin your own interview.</p>{/if}
      {#if placement.missing.length}<div class="missing"><strong>{placement.missing.length} missing {placement.missing.length===1?'component':'components'}</strong>{#each placement.missing as item}<p>{item}</p>{/each}</div>{/if}
      {#if session && placement.kind==='personal'}
        {#if session.placements.length>1 && session.baseline.runId===placement.runId && session.baseline.contractDigest===placement.contractDigest && session.baseline.density && placement.density}<p class="muted">Before {format(session.baseline.density.percentile)} → now {format(placement.density.percentile)} percentile. A result, not a target.</p>{/if}
        {#if started && session.phase==='question'}
          {@const question=session.questions[session.current]}
          {#if question}<section class="question"><p class="muted">Question {session.current+1} of {session.questions.length}</p>{#if session.baseline.runId!==run?.runId}<p class="muted">Question context comes from the earlier forecast; your answers were preserved.</p>{/if}<h2>{question.default.question}</h2><label for="answer">Your answer, in your own words</label><textarea id="answer" value={question.answer} oninput={event=>{if(session)session=saveAnswerDraft(session,event.currentTarget.value);}} rows="5"></textarea><div class="actions"><button onclick={saveAnswer}>Save answer</button><button class="quiet" onclick={()=>{if(session)session=skipQuestion(session);}}>Skip</button></div></section>{/if}
        {:else if session.phase==='rewrite'}<section class="question"><h2>Put your knowledge into your idea.</h2><p>Edit the sentence below, then place it again. The rewrite is yours.</p><button onclick={()=>input?.focus()}>Edit my idea</button></section>
        {:else if session.phase==='complete'}<section class="complete"><h2>{session.stopped?'Interview stopped. Your words are saved.':session.questions.length?'Your hand-off is ready.':'No majority defaults to ask about.'}</h2>{#if session.baseline.runId===placement.runId && session.baseline.density && placement.density}<p>{format(session.baseline.density.percentile)} → {format(placement.density.percentile)} percentile</p><p>{Math.abs(placement.density.percentile-session.baseline.density.percentile)<1?'The measured crowding changed little.':placement.density.percentile<session.baseline.density.percentile?'The idea is more crowded in this forecast.':'The idea is less crowded in this forecast.'}</p>{/if}<p>Percentile is a result, not the goal. Take the hand-off into your <strong>2-scope</strong> brain dump.</p><details><summary>Defaults you confirm you avoided</summary><p>Optional. An answer alone does not prove avoidance.</p>{#each session.questions as question}<label class="confirmation"><input type="checkbox" checked={session.confirmedAvoided.includes(question.default.id)} onchange={event=>{if(session){const ids=new Set(session.confirmedAvoided);if(event.currentTarget.checked)ids.add(question.default.id);else ids.delete(question.default.id);session=confirmAvoided(session,[...ids]);}}}/>{question.default.label}</label>{/each}</details>{#if handoffURL}<a class="signal-button download-link" href={handoffURL} download="DARKSPACE-HANDOFF.md">Download hand-off</a>{/if}</section>
        {:else}<section class="defaults"><h2>Shared defaults nearby</h2><p class="muted">Measured frequencies among forecast samples in the nearby cluster.</p>{#each session.questions as question,index}<button class="default-row" onclick={()=>begin(index)}><span>{(100*question.default.count/question.default.denominator).toFixed(0)}%<small>{question.default.count}/{question.default.denominator}</small></span><span>{question.default.label}</span></button>{/each}{#if session.questions.length}<button class="signal-button" onclick={()=>begin()}>Begin interview</button>{/if}</section>{/if}
        {#if session.phase!=='complete'}<button class="quiet stop" onclick={()=>{if(session)session=stopInterview(session);started=true;}}>Stop and keep my hand-off</button>{/if}
      {:else}<section class="defaults"><h2>Shared defaults nearby</h2>{#each placement.defaults.filter(value=>value.count/value.denominator>0.5).slice(0,5) as value}<div class="sample-default"><strong>{(100*value.count/value.denominator).toFixed(0)}%</strong><span>{value.label}</span></div>{/each}</section>{/if}
    {:else}<p class="muted">Your placement will appear here when the saved forecast and local model are available.</p>{/if}
    {#if message && run}<div class:failure class="message" role="status"><p>{message}</p>{#if failure}<div class="actions"><button onclick={placeCurrent}>Try again</button><button class="quiet" onclick={()=>input?.focus()}>Edit my idea</button></div>{/if}</div>{/if}
    {#if run?.samplePlacements?.length}<details class="saved-samples"><summary>Use a saved sample idea</summary>{#each run.samplePlacements as sample,index}<button onclick={()=>useSample(sample)}>Sample {index+1}: {sample.idea}</button>{/each}</details>{/if}
  </aside>{:else if placement}<button class="open-panel" onclick={()=>panel=true}>Open idea neighborhood</button>{/if}

  <form class="command-bar" onsubmit={event=>{event.preventDefault();placeCurrent();}}><label for="idea">{placement?.kind==='sample'?'Your idea · sample shown on map':'Your idea'} <kbd aria-hidden="true">/</kbd></label><div><input id="idea" bind:this={input} bind:value={draft} oninput={event=>{authored=true;if(session)session=saveIdeaDraft(session,event.currentTarget.value);}} readonly={busy} maxlength="1000" autocomplete="off" placeholder="Describe your idea in one sentence"/><button type="submit" disabled={busy} aria-label="Place your idea">Place idea <span aria-hidden="true">↵</span></button></div></form>
  <footer class="device-note"><span>{storageAvailable?'Saved on this device only. Clearing browser data removes it.':'This session only. Browser storage is unavailable.'}</span><button class="quiet" onclick={forget}>Forget this idea</button></footer>
</main>
