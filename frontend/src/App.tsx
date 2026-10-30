import React, { useState, useEffect } from 'react';
import { User, Issue, IssueCategory, UserRole } from './types';
import { api } from './api/client';
import { Navbar } from './components/Navbar';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { ReportIssuePage } from './pages/ReportIssuePage';
import { ClustersPage } from './pages/ClustersPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { FieldWorkerPage } from './pages/FieldWorkerPage';
import { TrackIssuePage } from './pages/TrackIssuePage';
import { ReportsPage } from './pages/ReportsPage';
import { WorkerApprovalsPage } from './pages/WorkerApprovalsPage';

export function App() {
  const [currentTab, setCurrentTab] = useState('login');
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [categories, setCategories] = useState<IssueCategory[]>([]);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTrackRef, setSearchTrackRef] = useState('');

  const loadData = async () => {
    try {
      const [cats, issuesRes] = await Promise.all([
        api.getCategories(),
        api.getIssues({ limit: 100 }),
      ]);
      setCategories(cats);
      setIssues(issuesRes.issues);
    } catch (err) {
      console.error('Failed to load issues or categories:', err);
    }
  };

  // Initial load: check for active token session
  const checkSession = async () => {
    const token = localStorage.getItem('civicpulse_token');
    if (token) {
      try {
        const meRes = await api.getMe();
        setCurrentUser(meRes.user);
        // Direct to role dashboard
        if (meRes.user.role === 'field_worker') setCurrentTab('field');
        else if (meRes.user.role === 'reporter') setCurrentTab('report');
        else setCurrentTab('dashboard');

        await loadData();
      } catch (err) {
        console.warn('Session expired or invalid token:', err);
        localStorage.removeItem('civicpulse_token');
        setCurrentUser(null);
        setCurrentTab('login');
      }
    } else {
      setCurrentUser(null);
      setCurrentTab('login');
    }
    setLoading(false);
  };

  useEffect(() => {
    checkSession();
    loadData();
  }, []);

  useEffect(() => {
    if (currentTab !== 'login' && issues.length === 0) {
      loadData();
    }
  }, [currentTab]);

  const handleLoginSuccess = async (user: User, token: string) => {
    setCurrentUser(user);
    // Role-based redirect to respective protected dashboard
    if (user.role === 'field_worker') {
      setCurrentTab('field');
    } else if (user.role === 'reporter') {
      setCurrentTab('report');
    } else {
      setCurrentTab('dashboard');
    }
    await loadData();
  };

  const handleLogout = () => {
    localStorage.removeItem('civicpulse_token');
    setCurrentUser(null);
    setCurrentTab('login');
  };

  // Fast role switcher for classroom viva demo
  const handleQuickRoleSwitch = async (role: UserRole) => {
    try {
      let email = 'admin@civicpulse.org';
      let pass = 'Admin@123';
      if (role === 'field_worker') {
        email = 'fieldworker@civicpulse.local';
        pass = 'WorkerPass123!';
      } else if (role === 'reporter') {
        email = 'citizen@civicpulse.local';
        pass = 'CitizenPass123!';
      }

      const res = await api.login(email, pass);
      localStorage.setItem('civicpulse_token', res.token);
      setCurrentUser(res.user);

      // Auto route to corresponding role view
      if (role === 'field_worker') setCurrentTab('field');
      else if (role === 'reporter') setCurrentTab('report');
      else setCurrentTab('dashboard');

      await loadData();
    } catch (err: any) {
      alert(`Role switch error: ${err.message}`);
    }
  };

  const handleRefreshIssues = async () => {
    try {
      const res = await api.getIssues({ limit: 100 });
      if (res && res.issues) {
        setIssues(res.issues);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleNavigateToTrack = (ref: string) => {
    setSearchTrackRef(ref);
    setCurrentTab('track');
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        currentUser={currentUser}
        onQuickRoleSwitch={handleQuickRoleSwitch}
        onLogout={handleLogout}
      />

      <main className="flex-1">
        {loading ? (
          <div className="py-24 text-center text-xs text-slate-500 font-medium">
            Connecting to CivicPulse backend services...
          </div>
        ) : !currentUser ? (
          <LoginPage onLoginSuccess={handleLoginSuccess} />
        ) : (
          <>
            {currentTab === 'report' && (
              <ReportIssuePage
                categories={categories}
                onIssueSubmitted={handleRefreshIssues}
                onNavigateToTrack={handleNavigateToTrack}
              />
            )}

            {currentTab === 'dashboard' && (
              <DashboardPage
                issues={issues}
                categories={categories}
                currentUser={currentUser}
                onRefresh={handleRefreshIssues}
              />
            )}

            {currentTab === 'clusters' && currentUser.role === 'admin' && <ClustersPage />}

            {currentTab === 'analytics' && currentUser.role === 'admin' && <AnalyticsPage />}

            {currentTab === 'field' && (
              <FieldWorkerPage issues={issues} onRefresh={handleRefreshIssues} />
            )}

            {currentTab === 'approvals' && currentUser.role === 'admin' && <WorkerApprovalsPage />}

            {currentTab === 'track' && (
              <TrackIssuePage initialReference={searchTrackRef} />
            )}

            {currentTab === 'reports' && currentUser.role === 'admin' && <ReportsPage />}

            {/* If tab is not accessible by current role, fallback to default dashboard */}
            {['clusters', 'analytics', 'approvals', 'reports'].includes(currentTab) &&
              currentUser.role !== 'admin' && (
                <div className="max-w-md mx-auto my-16 p-6 bg-white rounded-2xl border border-slate-200 text-center space-y-3">
                  <div className="text-sm font-bold text-slate-900">Access Restricted</div>
                  <p className="text-xs text-slate-500">
                    This section requires Administrator privileges.
                  </p>
                  <button
                    onClick={() =>
                      setCurrentTab(currentUser.role === 'field_worker' ? 'field' : 'report')
                    }
                    className="px-4 py-2 rounded-lg bg-teal-600 text-white text-xs font-semibold"
                  >
                    Return to My Dashboard
                  </button>
                </div>
              )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            <span className="font-bold text-slate-700">CivicPulse Platform</span> &bull; Cloud Computing Mini Project &bull; Custom VPC & EC2 Architecture
          </div>
          <div className="text-[11px] text-slate-400">
            Fictional educational data &bull; No live municipal affiliation
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
