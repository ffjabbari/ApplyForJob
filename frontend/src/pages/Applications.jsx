import { useEffect, useState } from 'react'
import { applications } from '../api'

const STATUS_COLOR = {
  pending: '', submitted: 'blue', rejected: 'red', interview: 'green', offer: 'green'
}

export default function Applications() {
  const [list, setList] = useState([])

  useEffect(() => {
    applications.list().then(r => setList(r.data))
  }, [])

  const updateStatus = async (id, status) => {
    await applications.update(id, { status })
    applications.list().then(r => setList(r.data))
  }

  return (
    <div>
      <div className="page-title">Applications</div>

      {list.length === 0
        ? <div className="card"><p style={{ color: '#90a4ae' }}>No applications yet.</p></div>
        : <div className="card" style={{ padding: 0 }}>
            <table>
              <thead>
                <tr>
                  <th>Job ID</th><th>Method</th><th>Status</th><th>Applied</th><th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {list.map(a => (
                  <tr key={a.id}>
                    <td>#{a.job_id}</td>
                    <td>{a.method || '—'}</td>
                    <td><span className={`badge ${STATUS_COLOR[a.status] || ''}`}>{a.status}</span></td>
                    <td>{new Date(a.applied_at).toLocaleDateString()}</td>
                    <td>
                      <select value={a.status} onChange={e => updateStatus(a.id, e.target.value)}
                        style={{ width: 'auto', padding: '4px 8px' }}>
                        {['pending','submitted','rejected','interview','offer'].map(s =>
                          <option key={s} value={s}>{s}</option>
                        )}
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
      }
    </div>
  )
}
