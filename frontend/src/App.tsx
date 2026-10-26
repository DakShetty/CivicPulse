import React, { useState, useEffect } from 'react';
import { User, Issue, IssueCategory, UserRole } from './types';
import { api } from './api/client';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { ReportIssuePage } from './pages/ReportIssuePage';
import { ClustersPage } from './pages/ClustersPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { FieldWorkerPage } from './pages/FieldWorkerPage';
import { TrackIssuePage } from './pages/TrackIssuePage';
import { ReportsPage } from './pages/ReportsPage';

export function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [categories, setCategories] = useState<IssueCategory[]>([]);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTrackRef, setSearchTrackRef] = useState('');

  // Initial load: authenticate default demo user and fetch data
  const loadInitialData = async () => {
    try {
      // Auto-login as admin by default for seamless classroom evaluation
      if (!localStorage.getItem('civicpulse_token')) {
        const loginRes = await api.login('admin@civicpulse.local', 'AdminPass123!');
        localStorage.setItem('civicpulse_token', loginRes.token);
        setCurrentUser(loginRes.user);
      } else {
        const meRes = await api.getMe();
        setCurrentUser(meRes.user);
      }

      const [cats, issuesRes] = await Promise.all([
        api.getCategories(),
        api.getIssues({ limit: 100 }),
      ]);
      setCategories(cats);
      setIssues(issuesRes.issues);
    } catch (err) {
      console.error('Initial load error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  // Fast role switcher for classroom viva demo
  const handleQuickRoleSwitch = async (role: UserRole) => {
    try {
      let email = 'admin@civicpulse.local';
      let pass = 'AdminPass123!';
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

      // Auto route to corresponding view
      if (role === 'field_worker') setCurrentTab('field');
      else if (role === 'reporter') setCurrentTab('report');
      else setCurrentTab('dashboard');
    } catch (err: any) {
      alert(`Role switch error: ${err.message}`);
    }
  };

  const handleRefreshIssues = async () => {
    try {
      const res = await api.getIssues({ limit: 100 });
      setIssues(res.issues);
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
      />

      <main className="flex-1">
        {loading ? (
          <div className="py-24 text-center text-xs text-slate-500 font-medium">
            Connecting to CivicPulse backend services...
          </div>
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

            {currentTab === 'clusters' && <ClustersPage />}

            {currentTab === 'analytics' && <AnalyticsPage />}

            {currentTab === 'field' && (
              <FieldWorkerPage issues={issues} onRefresh={handleRefreshIssues} />
            )}

            {currentTab === 'track' && (
              <TrackIssuePage initialReference={searchTrackRef} />
            )}

            {currentTab === 'reports' && <ReportsPage />}
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
