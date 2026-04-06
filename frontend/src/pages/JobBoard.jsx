import { useEffect, useState } from 'react'
import { jobs, resumes } from '../api'

const STATUS_COLORS = { new: 'blue', viewed: '', applied: 'green', expired: 'red' }

export default function JobBoard() {
  const [jobList, setJobList] = useState([])
  const [filter, setFilter] = useState('')
  const [building, setBuilding] = useState(null)

  const load = (status = '') => {
    jobs.list(status || undefined).then(r => setJobList(r.data))
  }

  useEffect(() => { load() }, [])

  const [builtFor, setBuiltFor] = useState(null)

  const buildResume = async (jobId) => {
    setBuilding(jobId)
    try {
      await resumes.build(jobId)
      setBuiltFor(jobId)
      setTimeout(() => setBuiltFor(null), 3000)
    } catch (e) {
      console.error('Error building resume', e)
    }
    setBuilding(null)
  }

  const setStatus = async (id, status) => {
    await jobs.updateStatus(id, status)
    load(filter)
  }

  return (
    <div>
      <div className="page-title">Job Board</div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {['', 'new', 'viewed', 'applied', 'expired'].map(s => (
          <button key={s} className={filter === s ? 'primary' : 'ghost'}
            onClick={() => { setFilter(s); load(s) }}>
            {s || 'All'}
          </button>
        ))}
      </div>

      {jobList.length === 0
        ? <div className="card"><p style={{ color: '#90a4ae' }}>No jobs found. Run a scan from the Dashboard.</p></div>
        : jobList.map(j => (
          <div key={j.id} className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ fontWeight: 600, marginBottom: 4 }}>{j.title}</div>
                <div style={{ color: '#90a4ae', fontSize: '0.85rem' }}>{j.location || 'Location N/A'}</div>
                {j.url && <a href={j.url} target="_blank" rel="noreferrer"
                  style={{ color: '#7c83fd', fontSize: '0.8rem' }}>View Posting ↗</a>}
              </div>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <span className={`badge ${STATUS_COLORS[j.status] || ''}`}>{j.status}</span>
                <button className="ghost" style={{ fontSize: '0.8rem' }}
                  onClick={() => setStatus(j.id, 'viewed')}>Mark Viewed</button>
                <button className="primary" style={{ fontSize: '0.8rem' }}
                  onClick={() => buildResume(j.id)} disabled={building === j.id}>
                  {building === j.id ? 'Building...' : builtFor === j.id ? '✓ Built' : '📝 Build Resume'}
                </button>
              </div>
            </div>
            {j.description && (
              <p style={{ marginTop: 12, color: '#90a4ae', fontSize: '0.85rem', lineHeight: 1.6 }}>
                {j.description.slice(0, 300)}{j.description.length > 300 ? '...' : ''}
              </p>
            )}
          </div>
        ))
      }
    </div>
  )
}
