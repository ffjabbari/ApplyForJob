import { useEffect, useState } from 'react'
import { institutions } from '../api'

export default function Institutions() {
  const [list, setList] = useState([])
  const [form, setForm] = useState({ name: '', website: '', location: '', type: '' })

  const load = () => institutions.list().then(r => setList(r.data))
  useEffect(() => { load() }, [])

  const add = async () => {
    if (!form.name.trim()) return
    await institutions.create(form)
    setForm({ name: '', website: '', location: '', type: '' })
    load()
  }

  const toggleFav = async (id) => {
    await institutions.toggleFavorite(id)
    load()
  }

  const remove = async (id) => {
    await institutions.delete(id)
    load()
  }

  return (
    <div>
      <div className="page-title">Institutions</div>

      <div className="card" style={{ marginBottom: 24 }}>
        <strong style={{ display: 'block', marginBottom: 12 }}>Add Institution</strong>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 12 }}>
          <input placeholder="Name *" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} />
          <input placeholder="Website" value={form.website} onChange={e => setForm({ ...form, website: e.target.value })} />
          <input placeholder="Location" value={form.location} onChange={e => setForm({ ...form, location: e.target.value })} />
          <input placeholder="Type (University, Bank...)" value={form.type} onChange={e => setForm({ ...form, type: e.target.value })} />
        </div>
        <button className="primary" onClick={add}>+ Add Institution</button>
      </div>

      {list.map(inst => (
        <div key={inst.id} className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <span style={{ fontWeight: 600 }}>{inst.is_favorite ? '⭐ ' : ''}{inst.name}</span>
              <span style={{ color: '#90a4ae', fontSize: '0.8rem', marginLeft: 12 }}>
                {inst.type} · {inst.location}
              </span>
              {inst.website && (
                <a href={inst.website} target="_blank" rel="noreferrer"
                  style={{ color: '#7c83fd', fontSize: '0.8rem', marginLeft: 12 }}>
                  {inst.website} ↗
                </a>
              )}
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="ghost" onClick={() => toggleFav(inst.id)}>
                {inst.is_favorite ? '★ Unfav' : '☆ Fav'}
              </button>
              <button className="danger" onClick={() => remove(inst.id)}>✕</button>
            </div>
          </div>
        </div>
      ))}

      {list.length === 0 && (
        <div className="card"><p style={{ color: '#90a4ae' }}>No institutions yet. Add one above.</p></div>
      )}
    </div>
  )
}
