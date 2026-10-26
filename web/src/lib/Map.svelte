<script lang="ts">
  import { onMount } from 'svelte';
  import { select } from 'd3-selection';
  import { zoom, zoomIdentity, type ZoomBehavior, type ZoomTransform } from 'd3-zoom';
  import { quadtree } from 'd3-quadtree';
  import type { ForecastPoint, Placement } from '../../../packages/core/src/contracts.ts';
  import type { ViewRun } from './data.ts';
  let { run, placement, trail = [] }: { run: ViewRun; placement: Placement | null; trail?: readonly Placement[] } = $props();
  let canvas: HTMLCanvasElement;
  let width = 1, height = 1;
  let transform: ZoomTransform = zoomIdentity;
  let behavior: ZoomBehavior<HTMLCanvasElement, unknown>;
  let hover = $state<ForecastPoint | null>(null);
  let showList = $state(false);
  let selectedId = $state('');
  let animation = 0;
  let displayedPosition: { x: number; y: number } | null = null;
  let previousPlacement: Placement | null = null;
  let lastPlacementKey = '';
  let screenPoints: { x: number; y: number; point: ForecastPoint }[] = [];
  const extent = (axis: 'x' | 'y'): [number, number] => {
    const values = run.points.map(point => point[axis]);
    return [Math.min(...values), Math.max(...values)];
  };
  function position(point: { x: number; y: number }): [number, number] {
    const [minX, maxX] = extent('x'), [minY, maxY] = extent('y');
    const usableWidth = width;
    const scale = Math.min(Math.max(usableWidth - 150, 80) / Math.max(maxX - minX, 1), Math.max(height - 200, 70) / Math.max(maxY - minY, 1));
    return transform.apply([usableWidth / 2 + (point.x - (minX + maxX) / 2) * scale, height / 2 + (point.y - (minY + maxY) / 2) * scale]);
  }
  function draw(): void {
    const context = canvas?.getContext('2d');
    if (!context) return;
    const ratio = Math.min(devicePixelRatio || 1, 2);
    canvas.width = width * ratio; canvas.height = height * ratio;
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, width, height);
    screenPoints = run.points.map(point => { const [x, y] = position(point); return { x, y, point }; });
    const labels: { x: number; y: number; width: number; height: number }[] = [];
    for (const cluster of run.clusters) {
      const members = screenPoints.filter(value => value.point.clusterId === cluster.id);
      if (!members.length) continue;
      const x = members.reduce((sum, value) => sum + value.x, 0) / members.length;
      const y = members.reduce((sum, value) => sum + value.y, 0) / members.length;
      const radius = Math.max(35, Math.sqrt(members.length) * 12 * transform.k);
      const halo = context.createRadialGradient(x, y, 0, x, y, radius);
      halo.addColorStop(0, 'rgba(158,248,57,.10)'); halo.addColorStop(1, 'rgba(158,248,57,0)');
      context.fillStyle = halo; context.fillRect(x-radius,y-radius,radius*2,radius*2);
      context.font = '13px "IBM Plex Sans"'; context.fillStyle = '#bdc6ad';
      const labelWidth = Math.min(context.measureText(cluster.name).width,Math.max(40,width-32));
      const labelX = Math.max(16, Math.min(x + 12, width - labelWidth - 16));
      const candidates = [-28,-52,-4,20,-76,44,68,-100].map(offset=>({x:labelX,y:Math.max(44,Math.min(y+offset,height-85)),width:labelWidth,height:18}));
      const label=candidates.find(candidate=>!labels.some(other=>candidate.x<other.x+other.width+6&&candidate.x+candidate.width+6>other.x&&candidate.y<other.y+other.height+4&&candidate.y+candidate.height+4>other.y));
      if(label){labels.push(label);context.fillText(cluster.name,label.x,label.y,labelWidth);}
    }
    for (const value of screenPoints) {
      context.beginPath(); context.arc(value.x, value.y, hover?.id === value.point.id ? 5 : 2.7, 0, Math.PI * 2);
      context.strokeStyle = hover?.id === value.point.id ? '#e8ebe3' : 'rgba(178,194,151,.7)'; context.lineWidth = 1; context.stroke();
    }
    const currentTrail = trail.filter(value => value.runId === run.runId);
    if (currentTrail.length > 1) {
      context.beginPath();
      currentTrail.forEach((value, index) => { const [x,y]=position(value.position); if (!index) context.moveTo(x,y); else context.lineTo(x,y); });
      context.strokeStyle = '#8ab954'; context.lineWidth = 1.5; context.stroke();
    }
    if (placement?.runId === run.runId) {
      const [x,y] = position(displayedPosition ?? placement.position);
      context.beginPath(); context.arc(x,y,18,0,Math.PI*2); context.strokeStyle='rgba(200,250,131,.3)'; context.stroke();
      context.beginPath(); context.arc(x,y,5,0,Math.PI*2); context.fillStyle='#c8fa83'; context.fill();
      context.font='12px "IBM Plex Sans"'; context.fillText(placement.kind === 'sample' ? 'Sample idea' : 'Your idea',x+14,y+5);
    }
  }
  onMount(() => {
    const observer = new ResizeObserver(entries => { const box=entries[0]!.contentRect; width=box.width; height=box.height; draw(); });
    observer.observe(canvas);
    behavior = zoom<HTMLCanvasElement, unknown>().scaleExtent([0.6, 6]).on('zoom', event => { if(event.sourceEvent){cancelAnimationFrame(animation);displayedPosition=null;} transform=event.transform; draw(); });
    select(canvas).call(behavior);
    return () => { cancelAnimationFrame(animation); observer.disconnect(); select(canvas).on('.zoom',null); };
  });
  $effect(() => { run; placement; trail; hover; if (canvas) draw(); });
  $effect(() => {
    const value = placement;
    if (!canvas || !behavior || !value || value.runId !== run.runId) return;
    const key = `${value.kind}:${value.runId}:${value.idea}`;
    if (key === lastPlacementKey) return;
    lastPlacementKey = key;
    cancelAnimationFrame(animation);
    const previous = previousPlacement?.runId === run.runId ? previousPlacement.position : value.position;
    previousPlacement = value;
    displayedPosition = value.position;
    if (value.kind !== 'personal' || matchMedia('(prefers-reduced-motion: reduce)').matches) { draw(); return; }
    const from = transform;
    const base = from.invert(position(value.position));
    const scale = Math.min(3, Math.max(1.5, from.k));
    const destination = zoomIdentity.translate(width/2-base[0]*scale, height/2-base[1]*scale).scale(scale);
    const began = performance.now();
    function frame(now: number): void {
      const progress = Math.min(1, (now-began)/650);
      const eased = 1-(1-progress)**3;
      displayedPosition = { x: previous.x+(value!.position.x-previous.x)*eased, y: previous.y+(value!.position.y-previous.y)*eased };
      const camera = zoomIdentity.translate(from.x+(destination.x-from.x)*eased, from.y+(destination.y-from.y)*eased).scale(from.k+(destination.k-from.k)*eased);
      select(canvas).call(behavior.transform,camera);
      if(progress<1) animation=requestAnimationFrame(frame);
      else displayedPosition=null;
    }
    animation=requestAnimationFrame(frame);
  });
  function inspect(event: PointerEvent): void {
    const rect=canvas.getBoundingClientRect();
    const tree=quadtree<{x:number;y:number;point:ForecastPoint}>().x(value=>value.x).y(value=>value.y).addAll(screenPoints);
    hover=tree.find(event.clientX-rect.left,event.clientY-rect.top,14)?.point ?? null;
  }
</script>

<div class="map-surface">
  <div class="map-heading"><span><span class="map-indicator" aria-hidden="true"></span>Forecast landscape</span><span>Pan to explore · scroll to zoom</span></div>
  <canvas bind:this={canvas} onpointermove={inspect} onpointerleave={() => hover=null} aria-label="Forecast map. Hollow rings are sampled model ideas. Use Browse ideas for the same point details by keyboard."></canvas>
  <div class="map-tools"><span class="ring"></span> Forecast ideas <button onclick={() => showList=!showList} aria-expanded={showList}>Browse ideas</button><button aria-label="Zoom in" onclick={() => select(canvas).call(behavior.scaleBy,1.4)}>+</button><button aria-label="Zoom out" onclick={() => select(canvas).call(behavior.scaleBy,1/1.4)}>−</button></div>
  {#if showList}<div class="browse"><label for="point-select">Forecast idea</label><select id="point-select" bind:value={selectedId} onchange={event => hover=run.points.find(point=>point.id===event.currentTarget.value)??null}><option value="">Choose an idea</option>{#each run.points as point,index}<option value={point.id}>Idea {index+1}: {point.idea}</option>{/each}</select></div>{/if}
  {#if hover}<div class="point-card" role="status"><span>Forecast idea {run.points.findIndex(point=>point.id===hover?.id)+1}</span><p>{hover.idea}</p><small>{run.bundleKind==='fixture'?'sample data · Made-up forecast.':'Model output. Not a real entry.'}</small></div>{/if}
  <div class="projection-note">{run.bundleKind==='fixture'?'sample data · Authored layout.':'A projection of sampled ideas.'} Screen distance does not measure novelty.</div>
</div>
