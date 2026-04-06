import { useEffect, useState } from 'react'
import { profile } from '../api'

export default function Profile() {
  const [user, setUser] = useState({ name: '', email: '', phone: '', bio: '' })
  const [skills, setSkills] = useState([])
  const [experiences, setExperiences] = useState([])
  const [newSkill, setNewSkill] = useState({ skill: '', level: '' })
  const [newExp, setNewExp] = useState({ company: '', title: '', start_date: '', end_date: '', description: '' })
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    profile.get().then(r => setUser(r.data)).catch(() => {})
    profile.getSkills().then(r => setSkills(r.data)).catch(() => {})
    profile.getExperience().then(r => setExperiences(r.data)).catch(() => {})
  }, [])

  const save = async () => {
    await profile.update(user)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const addSkill = async () => {
    if (!newSkill.skill.trim()) return
    await profile.addSkill(newSkill)
    setNewSkill({ skill: '', level: '' })
    profile.getSkills().then(r => setSkills(r.data))
  }

  const removeSkill = async (id) => {
    await profile.deleteSkill(id)
    profile.getSkills().then(r => setSkills(r.data))
  }

  const addExp = async () => {
    if (!newExp.company.trim()) return
    await profile.addExperience(newExp)
    setNewExp({ company: '', title: '', start_date: '', end_date: '', description: '' })
    profile.getExperience().then(r => setExperiences(r.data))
  }

  return (
    <div>
      <div className="page-title">Profile</div>

      <div className="card" style={{ marginBottom: 24 }}>
        <strong style={{ display: 'block', marginBottom: 12 }}>Personal Info</strong>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 12 }}>
          <input placeholder="Name" value={user.name} onChange={e => setUser({ ...user, name: e.target.value })} />
          <input placeholder="Email" value={user.email} onChange={e => setUser({ ...user, email: e.target.value })} />
          <input placeholder="Phone" value={user.phone || ''} onChange={e => setUser({ ...user, phone: e.target.value })} />
        </div>
        <textarea rows={3} placeholder="Bio / Summary" value={user.bio || ''}
          onChange={e => setUser({ ...user, bio: e.target.value })} style={{ marginBottom: 12 }} />
        <button className="primary" onClick={save}>{saved ? '✓ Saved' : 'Save Profile'}</button>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <strong style={{ display: 'block', marginBottom: 12 }}>Skills</strong>
        <div style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap' }}>
          {skills.map(s => (
            <span key={s.id} className="badge" style={{ cursor: 'pointer' }} onClick={() => removeSkill(s.id)}>
              {s.skill}{s.level ? ` (${s.level})` : ''} ✕
            </span>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <input placeholder="Skill" value={newSkill.skill} onChange={e => setNewSkill({ ...newSkill, skill: e.target.value })} />
          <input placeholder="Level" value={newSkill.level} onChange={e => setNewSkill({ ...newSkill, level: e.target.value })} style={{ maxWidth: 120 }} />
          <button className="ghost" onClick={addSkill}>+ Add</button>
        </div>
      </div>

      <div className="card">
        <strong style={{ display: 'block', marginBottom: 12 }}>Experience</strong>
        {experiences.map(e => (
          <div key={e.id} style={{ marginBottom: 12, paddingBottom: 12, borderBottom: '1px solid #2a2d3a' }}>
            <div style={{ fontWeight: 600 }}>{e.title} — {e.company}</div>
            <div style={{ color: '#90a4ae', fontSize: '0.8rem' }}>{e.start_date} – {e.end_date || 'present'}</div>
            {e.description && <p style={{ fontSize: '0.85rem', marginTop: 4 }}>{e.description}</p>}
          </div>
        ))}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginTop: 12 }}>
          <input placeholder="Company" value={newExp.company} onChange={e => setNewExp({ ...newExp, company: e.target.value })} />
          <input placeholder="Title" value={newExp.title} onChange={e => setNewExp({ ...newExp, title: e.target.value })} />
          <input placeholder="Start date" value={newExp.start_date} onChange={e => setNewExp({ ...newExp, start_date: e.target.value })} />
          <input placeholder="End date" value={newExp.end_date} onChange={e => setNewExp({ ...newExp, end_date: e.target.value })} />
        </div>
        <textarea rows={2} placeholder="Description" value={newExp.description}
          onChange={e => setNewExp({ ...newExp, description: e.target.value })}
          style={{ marginTop: 10, marginBottom: 10 }} />
        <button className="ghost" onClick={addExp}>+ Add Experience</button>
      </div>
    </div>
  )
}
