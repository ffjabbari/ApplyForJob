import { Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import JobBoard from './pages/JobBoard'
import ResumeBuilder from './pages/ResumeBuilder'
import Applications from './pages/Applications'
import Institutions from './pages/Institutions'
import Profile from './pages/Profile'

const nav = [
  { to: '/',             icon: '🏠', label: 'Dashboard' },
  { to: '/jobs',         icon: '🔍', label: 'Job Board' },
  { to: '/resumes',      icon: '📝', label: 'Resumes' },
  { to: '/applications', icon: '🚀', label: 'Applications' },
  { to: '/institutions', icon: '🏛️', label: 'Institutions' },
  { to: '/profile',      icon: '👤', label: 'Profile' },
]

export default function App() {
  return (
    <div className="layout">
      <nav className="sidebar">
        <h2>🤖 JobHunter AI</h2>
        {nav.map(({ to, icon, label }) => (
          <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => isActive ? 'active' : ''}>
            {icon} {label}
          </NavLink>
        ))}
      </nav>
      <main className="main">
        <Routes>
          <Route path="/"             element={<Dashboard />} />
          <Route path="/jobs"         element={<JobBoard />} />
          <Route path="/resumes"      element={<ResumeBuilder />} />
          <Route path="/applications" element={<Applications />} />
          <Route path="/institutions" element={<Institutions />} />
          <Route path="/profile"      element={<Profile />} />
        </Routes>
      </main>
    </div>
  )
}
