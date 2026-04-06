import { useEffect, useState } from 'react'
import { domains, jobs } from '../api'

export default function Dashboard() {
  const [domainList, setDomainList] = useState([])
  const [newJobs, setNewJobs] = useState([])
  const [newDomain, setNewDomain] = useState('')
  const [scanning, setScanning] = useState(false)

  useEffect(() => {
    domains.list().then(r => setDomainList(r.data))
    jobs.newJobs().then(r => setNewJobs(r.data)).catch(() => {})
  }, [])

  const activate = async (id) => {
    await domains.activate(id)
    const r = await domains.list()
    setDomainList(r.data)
  }

  const addDomain = async () => {
    if (!newDomain.trim()) return
    await domains.create({ name: newDomain })
    setNewDomain('')
    const r = await domains.list()
    setDomainList(r.data)
  }

  const scan = async () => {
    setScanning(true)
    await jobs.scan()
    setTimeout(() => setScanning(false), 3000)
  }

  const activeDomain = domainList.find(d => d.is_active)

  return (
    <div>
      <div className="page-title">Dashboard</div>

      <div className="card" style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <strong>Active Domain: {activeDomain ? activeDomain.name : 'None'}</strong>
          <button className="primary" onClick={scan} disabled={scanning}>
            {scanning ? 'Scanning...' : '🔍 Scan Now'}
          </button>
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {domainList.map(d => (
            <button key={d.id} onClick={() => activate(d.id)}
              className={d.is_active ? 'primary' : 'ghost'}>
              {d.name}
            </button>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 8, marginTop: 16 }}>
          <input value={newDomain} onChange={e => setNewDomain(e.target.value)}
            placeholder="New domain name..." style={{ maxWidth: 240 }} />
          <button className="ghost" onClick={addDomain}>+ Add</button>
        </div>
      </div>

      <div className="card">
        <strong>New Jobs ({newJobs.length})</strong>
        {newJobs.length === 0
          ? <p style={{ color: '#90a4ae', marginTop: 12 }}>No new jobs. Run a scan to find positions.</p>
          : <table style={{ marginTop: 12 }}>
              <thead><tr><th>Title</th><th>Location</th><th>Scanned</th></tr></thead>
              <tbody>
                {newJobs.slice(0, 10).map(j => (
                  <tr key={j.id}>
                    <td>{j.title}</td>
                    <td>{j.location || '—'}</td>
                    <td>{new Date(j.scanned_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
        }
      </div>
    </div>
  )
}
