export type UserRole = 'reporter' | 'field_worker' | 'admin';

export interface User {
  id: number;
  display_name: string;
  email?: string;
  role: UserRole;
  is_active: boolean;
  created_at?: string;
}

export interface IssueCategory {
  id: number;
  name: string;
  code: string;
  description: string;
  default_severity_weight: number;
  sla_hours: number;
  is_active: boolean;
}

export interface IssueAttachment {
  id: number;
  issue_id: number;
  original_filename: string;
  file_type: string;
  file_size_bytes: number;
  download_url?: string;
  created_at: string;
}

export interface StatusHistoryItem {
  id: number;
  issue_id: number;
  old_status: string | null;
  new_status: string;
  actor_name: string;
  actor_role: string;
  note: string | null;
  created_at: string;
}

export interface Issue {
  id: number;
  public_reference: string;
  category: IssueCategory | null;
  title: string;
  description: string;
  approximate_address: string;
  ward_or_district: string;
  latitude: number;
  longitude: number;
  severity: number;
  safety_hazard: boolean;
  impacts_critical_infrastructure: boolean;
  priority_score: number;
  priority_explanation: string;
  status: 'Submitted' | 'Triaged' | 'Assigned' | 'In Progress' | 'Resolved' | 'Verified' | 'Rejected';
  cluster_id: number | null;
  is_cluster_representative: boolean;
  created_at: string;
  acknowledged_at: string | null;
  assigned_at: string | null;
  resolved_at: string | null;
  verified_at: string | null;
  attachments_count: number;
  attachments?: IssueAttachment[];
  history?: StatusHistoryItem[];
  assigned_worker?: {
    id: number;
    display_name: string;
  } | null;
  reporter?: {
    id: number;
    display_name: string;
    email: string;
  };
}

export interface ClusterMemberLink {
  id: number;
  cluster_id: number;
  issue_id: number;
  issue_reference: string;
  issue_title: string;
  issue_category: string;
  similarity_score: number;
  distance_km: number;
  text_similarity: number;
  similarity_explanation: string;
  reviewed_status: 'pending_review' | 'confirmed' | 'separated' | 'dismissed';
  reviewed_by: string | null;
  reviewed_at: string | null;
  created_at: string;
}

export interface IssueCluster {
  id: number;
  title: string;
  representative_issue_id: number;
  status: string;
  member_count: number;
  created_at: string;
  links: ClusterMemberLink[];
  representative_issue?: Issue;
}

export interface AnalyticsSummary {
  is_demo_data: boolean;
  total_issues: number;
  open_issues: number;
  resolved_issues: number;
  overdue_issues: number;
  unacknowledged_overdue: number;
  unresolved_overdue: number;
  active_clusters: number;
  avg_acknowledge_hours: number;
  avg_resolve_hours: number;
  status_breakdown: Record<string, number>;
  category_breakdown: Array<{ category: string; count: number }>;
}

export interface Hotspot {
  area: string;
  issue_count: number;
  avg_priority: number;
  safety_hazards: number;
  top_category: string;
}

export interface ReportRecord {
  id: number;
  title: string;
  report_type: string;
  s3_object_key: string;
  file_size_bytes: number;
  status: string;
  download_url?: string;
  created_at: string;
}

export interface AuditEvent {
  id: number;
  action: string;
  entity_type: string;
  entity_id: string;
  actor_name: string;
  actor_role: string;
  metadata_json: string;
  created_at: string;
}
