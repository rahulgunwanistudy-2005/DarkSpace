import type { ForecastRun, Placement, SharedDefault, VectorContract } from './contracts.ts';

export class PlacementError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(message);
    this.name = 'PlacementError';
    this.code = code;
  }
}

function requireValue(condition: boolean, message: string): asserts condition {
  if (!condition) throw new PlacementError('invalid_run', message);
}

export function validateVector(vector: readonly number[], dimensions: number): void {
  requireValue(vector.length === dimensions, 'The vector dimensions do not match this forecast.');
  requireValue(vector.every(Number.isFinite), 'The vector contains a non-finite value.');
  const norm = Math.sqrt(vector.reduce((sum, value) => sum + value * value, 0));
  requireValue(Math.abs(norm - 1) <= 0.001, 'The vector must be L2-normalized.');
}

export function validateIdea(idea: string): void {
  if (idea.length > 1000) throw new PlacementError('long_input', 'Keep your idea to one sentence under 1,001 characters.');
  if (idea.replace(/\s/gu, '').length < 12 || idea.trim().split(/\s+/u).length < 3) {
    throw new PlacementError('short_input', 'Use at least three words and 12 non-whitespace characters to describe your idea.');
  }
}

function validateDefault(value: SharedDefault, size: number): void {
  requireValue(value.id.length > 0 && value.label.length > 0 && value.question.length > 0, 'A default is missing its label or question.');
  requireValue([value.count, value.denominator, value.unknown].every(Number.isSafeInteger), 'Default counts must be integers.');
  requireValue(value.denominator === size && value.count >= 0 && value.unknown >= 0 && value.count + value.unknown <= size, 'Default counts do not agree with cluster membership.');
}

export function validateRun(run: ForecastRun): void {
  requireValue(run.runId.length > 0 && run.contract.digest.length > 0, 'The forecast has no run or contract identity.');
  requireValue(Number.isSafeInteger(run.contract.dimensions) && run.contract.dimensions > 0, 'The vector dimensions are invalid.');
  requireValue(run.points.length > 0, 'There are no valid forecast vectors to place against.');
  const ids = new Set<string>();
  const pointsById = new Map(run.points.map(point => [point.id, point]));
  for (const point of run.points) {
    requireValue(point.id.length > 0 && !ids.has(point.id), 'Forecast point IDs must be unique.');
    ids.add(point.id);
    validateVector(point.vector, run.contract.dimensions);
    requireValue(Number.isFinite(point.x) && Number.isFinite(point.y), 'The map position is invalid.');
  }
  const clusterIds = new Set<string>();
  for (const cluster of run.clusters) {
    requireValue(cluster.id.length > 0 && !clusterIds.has(cluster.id), 'Cluster IDs must be unique.');
    clusterIds.add(cluster.id);
    requireValue(Number.isFinite(cluster.assignmentRadius) && cluster.assignmentRadius >= 0 && cluster.assignmentRadius <= 2, 'The cluster assignment radius is invalid.');
    requireValue(cluster.memberIds.length > 0 && new Set(cluster.memberIds).size === cluster.memberIds.length, 'Cluster membership must be non-empty and unique.');
    for (const id of cluster.memberIds) requireValue(pointsById.get(id)?.clusterId === cluster.id, 'A cluster member has inconsistent membership.');
    requireValue(new Set(cluster.defaults.map(value => value.id)).size === cluster.defaults.length, 'Default IDs must be unique within a cluster.');
    for (const value of cluster.defaults) validateDefault(value, cluster.memberIds.length);
    requireValue(cluster.defaultsStatus !== 'missing' || cluster.defaults.length === 0, 'Missing defaults cannot contain invented values.');
  }
  for (const point of run.points) {
    if (point.clusterId !== null) {
      requireValue(run.clusters.some(cluster => cluster.id === point.clusterId && cluster.memberIds.includes(point.id)), 'A point refers to an unknown cluster.');
    }
  }
}

export function cosineDistance(a: readonly number[], b: readonly number[]): number {
  requireValue(a.length === b.length, 'Cannot compare vectors with different dimensions.');
  return Math.max(0, Math.min(2, 1 - a.reduce((sum, value, index) => sum + value * b[index]!, 0)));
}

export function densityReference(run: ForecastRun): readonly number[] {
  validateRun(run);
  const k = Math.min(10, run.points.length - 1);
  if (k < 1) return [];
  return run.points.map(point => {
    const distances = run.points.filter(other => other.id !== point.id)
      .map(other => cosineDistance(point.vector, other.vector)).sort((a, b) => a - b);
    return distances.slice(0, k).reduce((sum, value) => sum + value, 0) / k;
  });
}

export function place(
  run: ForecastRun,
  query: { idea: string; vector: readonly number[]; contract: VectorContract; kind: 'personal' | 'sample' },
): Placement {
  validateRun(run);
  validateIdea(query.idea);
  if (query.contract.digest !== run.contract.digest || query.contract.id !== run.contract.id || query.contract.dimensions !== run.contract.dimensions) {
    throw new PlacementError('contract_mismatch', 'This idea was embedded with a different model or runtime. Place again using this forecast’s model.');
  }
  validateVector(query.vector, run.contract.dimensions);
  const ranked = run.points.map(point => ({ point, distance: cosineDistance(query.vector, point.vector) }))
    .sort((a, b) => a.distance - b.distance || a.point.id.localeCompare(b.point.id, 'en'));
  const neighbors = ranked.slice(0, Math.min(10, run.points.length));
  const k = Math.min(10, run.points.length - 1);
  const missing: string[] = [];
  let density: Placement['density'] = null;
  if (run.points.length >= 11) {
    const meanDistance = ranked.slice(0, k).reduce((sum, value) => sum + value.distance, 0) / k;
    const reference = densityReference(run);
    const lower = reference.filter(value => value < meanDistance).length;
    const tied = reference.filter(value => value === meanDistance).length;
    density = { meanDistance, percentile: 100 * (lower + 0.5 * tied) / reference.length, k };
  } else missing.push('density: at least 11 forecast vectors are required');
  const nearbyClusters = run.clusters.map(cluster => {
    const members = ranked.filter(value => value.point.clusterId === cluster.id).slice(0, 3);
    return { id: cluster.id, name: cluster.name, distance: members.reduce((sum, value) => sum + value.distance, 0) / members.length, memberCount: cluster.memberIds.length };
  }).sort((a, b) => a.distance - b.distance || a.id.localeCompare(b.id, 'en')).slice(0, 3);
  const nearestPoint = ranked[0]!;
  const candidate = run.clusters.find(cluster => cluster.id === nearestPoint.point.clusterId);
  const assignedClusterId = candidate && nearestPoint.distance <= candidate.assignmentRadius ? candidate.id : null;
  const contextCluster = run.clusters.find(cluster => cluster.id === (assignedClusterId ?? nearbyClusters[0]?.id));
  const defaults = contextCluster?.defaultsStatus === 'complete' ? [...contextCluster.defaults].sort((a, b) => b.count / b.denominator - a.count / a.denominator || a.id.localeCompare(b.id, 'en')) : [];
  if (!contextCluster || contextCluster.defaultsStatus === 'missing') missing.push('defaults: no measured defaults available for the nearest cluster');
  const exact = neighbors.filter(value => value.distance === 0);
  const displayNeighbors = exact.length > 0 ? exact : neighbors;
  const weights = displayNeighbors.map(value => exact.length > 0 ? 1 : 1 / Math.max(value.distance, 1e-9));
  const total = weights.reduce((sum, value) => sum + value, 0);
  const coordinate = (axis: 'x' | 'y'): number => displayNeighbors.reduce((sum, value, index) => sum + value.point[axis] * weights[index]!, 0) / total;
  return {
    kind: query.kind, evidenceKind: run.evidenceKind, idea: query.idea, runId: run.runId,
    contractDigest: run.contract.digest, neighbors: neighbors.map(value => ({ id: value.point.id, distance: value.distance })),
    nearbyClusters, assignedClusterId, density, defaults, missing,
    position: { x: coordinate('x'), y: coordinate('y'), approximate: true },
  };
}
