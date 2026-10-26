export type EvidenceKind = 'model-forecast' | 'synthetic-fixture' | 'sample-data';

export interface VectorContract {
  id: string;
  digest: string;
  dimensions: number;
}

export interface ForecastPoint {
  id: string;
  idea: string;
  vector: readonly number[];
  clusterId: string | null;
  x: number;
  y: number;
}

export interface SharedDefault {
  id: string;
  label: string;
  count: number;
  denominator: number;
  unknown: number;
  question: string;
}

export interface ForecastCluster {
  id: string;
  name: string;
  memberIds: readonly string[];
  assignmentRadius: number;
  defaults: readonly SharedDefault[];
  defaultsStatus: 'complete' | 'missing';
}

export interface ForecastRun {
  runId: string;
  event: string;
  evidenceKind: EvidenceKind;
  contract: VectorContract;
  points: readonly ForecastPoint[];
  clusters: readonly ForecastCluster[];
}

export interface Neighbor {
  id: string;
  distance: number;
}

export interface NearbyCluster {
  id: string;
  name: string;
  distance: number;
  memberCount: number;
}

export interface Placement {
  kind: 'personal' | 'sample';
  evidenceKind: EvidenceKind;
  idea: string;
  runId: string;
  contractDigest: string;
  neighbors: readonly Neighbor[];
  nearbyClusters: readonly NearbyCluster[];
  assignedClusterId: string | null;
  density: { meanDistance: number; percentile: number; k: number } | null;
  defaults: readonly SharedDefault[];
  missing: readonly string[];
  position: { x: number; y: number; approximate: true };
}

export interface Question {
  default: SharedDefault;
  status: 'pending' | 'answered' | 'skipped';
  answer: string;
}

export interface Interview {
  baseline: Placement;
  placements: readonly Placement[];
  questions: readonly Question[];
  current: number;
  phase: 'question' | 'rewrite' | 'complete';
  stopped: boolean;
  draftIdea: string;
  confirmedAvoided: readonly string[];
}
