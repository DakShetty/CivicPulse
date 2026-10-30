import React from 'react';
import { User, UserRole } from '../types';
import {
  Activity,
  PlusCircle,
  LayoutDashboard,
  HardHat,
  GitMerge,
  BarChart3,
  Search,
  UserCheck,
  FileText,
  ShieldAlert,
  LogOut,
  UserCheck2,
} from 'lucide-react';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  currentUser: User | null;
  onQuickRoleSwitch: (role: UserRole) => void;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setCurrentTab,
  currentUser,
  onQuickRoleSwitch,
  onLogout,
}) => {
  const role = currentUser?.role;

  return (
    <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-50">
      {/* Demo Notification Banner */}
      <div className="bg-gradient-to-r from-teal-700 via-sky-800 to-slate-900 px-4 py-1.5 text-center text-[11px] font-medium tracking-wide flex items-center justify-center gap-2">
        <ShieldAlert className="w-3.5 h-3.5 text-teal-300" />
        <span>CivicPulse Platform | Role-Based Civic Operations Hub | Fictional Community Architecture</span>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Platform Name */}
          <div
            className="flex items-center gap-3 cursor-pointer"
            onClick={() => {
              if (role === 'field_worker') setCurrentTab('field');
              else if (role === 'reporter') setCurrentTab('report');
              else setCurrentTab('dashboard');
            }}
          >
            <div className="w-9 h-9 rounded-lg bg-teal-500 flex items-center justify-center shadow-lg shadow-teal-500/30">
              <Activity className="w-5 h-5 text-slate-950 stroke-[2.5]" />
            </div>
            <div>
              <span className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
                Civic<span className="text-teal-400">Pulse</span>
              </span>
              <span className="text-[10px] text-slate-400 block -mt-1 font-mono">Infrastructure Intelligence</span>
            </div>
          </div>

          {/* Navigation Tabs based on Role */}
          {currentUser && (
            <nav className="hidden md:flex items-center gap-1">
              {/* Citizen or Admin can report */}
              {(role === 'reporter' || role === 'admin') && (
                <button
                  onClick={() => setCurrentTab('report')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                    currentTab === 'report'
                      ? 'bg-teal-500 text-slate-950 font-bold shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <PlusCircle className="w-4 h-4" />
                  <span>Report Issue</span>
                </button>
              )}

              {/* Operations Map */}
              <button
                onClick={() => setCurrentTab('dashboard')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  currentTab === 'dashboard'
                    ? 'bg-teal-500 text-slate-950 font-bold shadow-sm'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                <LayoutDashboard className="w-4 h-4" />
                <span>{role === 'admin' ? 'Operations Map' : 'Civic Map'}</span>
              </button>

              {/* Admin Only: Clusters */}
              {role === 'admin' && (
                <button
                  onClick={() => setCurrentTab('clusters')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                    currentTab === 'clusters'
                      ? 'bg-teal-500 text-slate-950 font-bold shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <GitMerge className="w-4 h-4" />
                  <span>Duplicate Clusters</span>
                </button>
              )}

              {/* Admin Only: Analytics */}
              {role === 'admin' && (
                <button
                  onClick={() => setCurrentTab('analytics')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                    currentTab === 'analytics'
                      ? 'bg-teal-500 text-slate-950 font-bold shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <BarChart3 className="w-4 h-4" />
                  <span>SLA & Analytics</span>
                </button>
              )}

              {/* Field Worker or Admin: Field Worker view */}
              {(role === 'field_worker' || role === 'admin') && (
                <button
                  onClick={() => setCurrentTab('field')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                    currentTab === 'field'
                      ? 'bg-teal-500 text-slate-950 font-bold shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <HardHat className="w-4 h-4" />
                  <span>{role === 'admin' ? 'Field Hub' : 'My Work Orders'}</span>
                </button>
              )}

              {/* Admin Only: Worker Approvals */}
              {role === 'admin' && (
                <button
                  onClick={() => setCurrentTab('approvals')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                    currentTab === 'approvals'
                      ? 'bg-teal-500 text-slate-950 font-bold shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <UserCheck2 className="w-4 h-4" />
                  <span>Worker Approvals</span>
                </button>
              )}

              {/* All: Track Issue */}
              <button
                onClick={() => setCurrentTab('track')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                  currentTab === 'track'
                    ? 'bg-teal-500 text-slate-950 font-bold shadow-sm'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800'
                }`}
              >
                <Search className="w-4 h-4" />
                <span>Track Reference</span>
              </button>

              {/* Admin Only: Exports */}
              {role === 'admin' && (
                <button
                  onClick={() => setCurrentTab('reports')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                    currentTab === 'reports'
                      ? 'bg-teal-500 text-slate-950 font-bold shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  <FileText className="w-4 h-4" />
                  <span>Exports</span>
                </button>
              )}
            </nav>
          )}

          {/* User Status, Role Switcher & Logout */}
          <div className="flex items-center gap-2.5">
            {currentUser ? (
              <>
                {/* Fast Role Switcher */}
                <div className="hidden lg:flex items-center bg-slate-800 rounded-lg p-1 border border-slate-700 text-[11px]">
                  <span className="text-slate-400 px-2 font-medium flex items-center gap-1">
                    <UserCheck className="w-3.5 h-3.5 text-teal-400" />
                    Switch:
                  </span>
                  <button
                    onClick={() => onQuickRoleSwitch('admin')}
                    className={`px-2 py-0.5 rounded font-semibold transition ${
                      currentUser.role === 'admin' ? 'bg-teal-500 text-slate-950' : 'text-slate-300 hover:text-white'
                    }`}
                  >
                    Admin
                  </button>
                  <button
                    onClick={() => onQuickRoleSwitch('field_worker')}
                    className={`px-2 py-0.5 rounded font-semibold transition ${
                      currentUser.role === 'field_worker' ? 'bg-amber-500 text-slate-950' : 'text-slate-300 hover:text-white'
                    }`}
                  >
                    Worker
                  </button>
                  <button
                    onClick={() => onQuickRoleSwitch('reporter')}
                    className={`px-2 py-0.5 rounded font-semibold transition ${
                      currentUser.role === 'reporter' ? 'bg-sky-500 text-slate-950' : 'text-slate-300 hover:text-white'
                    }`}
                  >
                    Citizen
                  </button>
                </div>

                {/* User Profile Pill */}
                <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
                  <div className="text-right">
                    <div className="text-xs font-bold text-white max-w-[120px] truncate">
                      {currentUser.display_name}
                    </div>
                    <span
                      className={`inline-block text-[9px] uppercase font-bold tracking-wider px-1.5 py-0.2 rounded ${
                        currentUser.role === 'admin'
                          ? 'bg-teal-900/60 text-teal-300 border border-teal-700/50'
                          : currentUser.role === 'field_worker'
                          ? 'bg-amber-900/60 text-amber-300 border border-amber-700/50'
                          : 'bg-sky-900/60 text-sky-300 border border-sky-700/50'
                      }`}
                    >
                      {currentUser.role === 'admin'
                        ? 'Admin'
                        : currentUser.role === 'field_worker'
                        ? 'Worker'
                        : 'Citizen'}
                    </span>
                  </div>

                  <button
                    onClick={onLogout}
                    title="Sign Out"
                    className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-rose-400 hover:bg-slate-700 transition"
                  >
                    <LogOut className="w-4 h-4" />
                  </button>
                </div>
              </>
            ) : (
              <button
                onClick={() => setCurrentTab('login')}
                className="px-3.5 py-1.5 rounded-lg bg-teal-500 text-slate-950 font-bold text-xs hover:bg-teal-400 transition"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
