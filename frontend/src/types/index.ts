export interface QualificationIssue {
  score: number;
  issues: string[];
}

export interface Qualification {
  completeness: QualificationIssue;
  clarity: QualificationIssue;
  feasibility: QualificationIssue;
  consistency: QualificationIssue;
  overall_gap: number;
  recommendations: string[];
}

export interface QualificationResponse {
  qualification: Qualification;
  gap: number;
}

export interface ValidationResponse {
  valid: boolean;
  gap: number;
}

export interface GenerateTADResponse {
  tad_markdown: string;
}

export interface RequirementsInput {
  requirements: string;
}

export interface GenerateTADInput {
  requirements: Record<string, any>;
}
