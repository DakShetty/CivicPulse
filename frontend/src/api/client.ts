import {
  User,
  Issue,
  IssueCategory,
  IssueCluster,
  AnalyticsSummary,
  Hotspot,
  ReportRecord,
  AuditEvent,
} from '../types';

const BASE_URL = '/api/v1';

function getAuthHeader(): Record<string, string> {
  const token = localStorage.getItem('civicpulse_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
    ...options.headers,
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || `HTTP error ${response.status}`);
  }

  return data as T;
}

export const api = {
  // System Health
  getHealth: () => request<{ status: string; database: string; environment: string }>('/health'),

  // Auth
  login: (email: string, password: string) =>
    request<{ token: string; user: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  register: (display_name: string, email: string, password: string, role: string = 'reporter') =>
    request<{ token?: string; user: User; pending_approval?: boolean; message?: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ display_name, email, password, role }),
    }),

  getMe: () => request<{ user: User }>('/auth/me'),

  getPendingWorkers: () => request<User[]>('/auth/workers/pending'),
  getAllWorkers: () => request<User[]>('/auth/workers'),
  approveWorker: (userId: number) =>
    request<{ message: string; user: User }>(`/auth/workers/${userId}/approve`, { method: 'POST' }),
  rejectWorker: (userId: number) =>
    request<{ message: string }>(`/auth/workers/${userId}/reject`, { method: 'POST' }),
  createAdminUser: (display_name: string, email: string, password: string) =>
    request<{ message: string; user: User }>('/auth/create-admin', {
      method: 'POST',
      body: JSON.stringify({ display_name, email, password }),
    }),

  // Categories
  getCategories: () => request<IssueCategory[]>('/issues/categories'),

  // Issues
  getIssues: (params: Record<string, string | number> = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== '') query.append(key, String(val));
    });
    return request<{ total: number; page: number; limit: number; pages: number; issues: Issue[] }>(
      `/issues?${query.toString()}`
    );
  },

  getIssue: (id: number) => request<Issue>(`/issues/${id}`),

  trackIssue: (ref: string) => request<Issue>(`/issues/track/${encodeURIComponent(ref)}`),

  createIssue: async (formData: FormData) => {
    const headers = getAuthHeader();
    const response = await fetch(`${BASE_URL}/issues`, {
      method: 'POST',
      headers,
      body: formData,
    });
    
    let data: any = {};
    const text = await response.text();
    try {
      data = JSON.parse(text);
    } catch {
      data = { error: text ? text.slice(0, 150) : `Server responded with status ${response.status}` };
    }

    if (!response.ok) throw new Error(data.error || 'Failed to submit issue');
    return data as { message: string; public_reference: string; issue: Issue; duplicate_detected?: any };
  },

  updateStatus: (issueId: number, status: string, note: string, rejection_reason?: string) =>
    request<{ message: string; issue: Issue }>(`/issues/${issueId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status, note, rejection_reason }),
    }),

  assignWorker: (issueId: number, field_worker_id: number, notes?: string) =>
    request<{ message: string; issue: Issue }>(`/issues/${issueId}/assign`, {
      method: 'POST',
      body: JSON.stringify({ field_worker_id, notes }),
    }),

  // Clusters
  getClusters: () => request<IssueCluster[]>('/clusters'),
  getCluster: (id: number) => request<IssueCluster>(`/clusters/${id}`),
  reviewClusterMember: (memberId: number, action: 'confirmed' | 'separated' | 'dismissed', notes?: string) =>
    request<{ message: string; member: any }>(`/clusters/members/${memberId}/review`, {
      method: 'POST',
      body: JSON.stringify({ action, notes }),
    }),

  // Analytics
  getAnalyticsSummary: () => request<AnalyticsSummary>('/analytics/summary'),
  getHotspots: () => request<Hotspot[]>('/analytics/hotspots'),

  // Reports
  getReports: () => request<ReportRecord[]>('/reports'),
  generateReport: (report_type: 'summary_csv' | 'summary_pdf', title?: string) =>
    request<{ message: string; report: ReportRecord; download_url: string }>('/reports', {
      method: 'POST',
      body: JSON.stringify({ report_type, title }),
    }),

  // Audit
  getAuditEvents: () => request<AuditEvent[]>('/audit'),
};
