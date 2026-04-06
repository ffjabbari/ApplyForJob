import { useEffect, useState } from 'react'
import { resumes, jobs } from '../api'

export default function ResumeBuilder() {
  const [list, setList] = useState([])
  const [jobMap, setJobMap] = useState({})
  const [expanded, setExpanded] = useState(null)

  useEffect(() => {
    resumes.list().then(r => {
      setList(r.data)
      // fetch job titles for each resume
      const ids = [...new Set(r.data.map(x => x.job_id).filter(Boolean))]
      ids.forEach(id => {
        jobs.get(id).then(j => setJobMap(m => ({ ...m, [id]: j.data })))
      })
    })
  }, [])

  return (
    <div>
      <div className="page-title">Resumes</div>
      <p style={{ color: '#90a4ae', marginBottom: 20, fontSize: '0.875rem' }}>
        Each resume is tailored to its specific job posting by GPT-4.
      </p>

      {list.length === 0
        ? <div className="card"><p style={{ color: '#90a4ae' }}>No resumes yet. Go to Job Board and click "Build Resume" on a job.</p></div>
        : list.map(r => {
          const job = jobMap[r.job_id]
          let content = null
          try { content = JSON.parse(r.content_json) } catch {}

          return (
            <div key={r.id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ fontWeight: 600 }}>
                    {job ? job.title : `Job #${r.job_id}`}
                  </div>
                  {job && <div style={{ color: '#90a4ae', fontSize: '0.8rem', marginTop: 2 }}>{job.location}</div>}
                  <div style={{ color: '#555', fontSize: '0.75rem', marginTop: 2 }}>Resume #{r.id} · v{r.version}</div>
                </div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  {r.pdf_path && (
                    <a href={resumes.pdfUrl(r.id)} target="_blank" rel="noreferrer">
                      <button className="ghost">📄 PDF</button>
                    </a>
                  )}
                  {r.docx_path && (
                    <a href={resumes.docxUrl(r.id)} target="_blank" rel="noreferrer">
                      <button className="ghost">📝 DOCX</button>
                    </a>
                  )}
                  <button className="ghost" onClick={() => setExpanded(expanded === r.id ? null : r.id)}>
                    {expanded === r.id ? 'Hide ▲' : 'View ▼'}
                  </button>
                </div>
              </div>

              {content && (
                <p style={{ marginTop: 10, color: '#90a4ae', fontSize: '0.85rem', fontStyle: 'italic' }}>
                  {content.summary}
                </p>
              )}

              {expanded === r.id && content && (
                <div style={{ marginTop: 16, borderTop: '1px solid #2a2d3a', paddingTop: 16 }}>
                  {content.cover_letter && (
                    <div style={{ marginBottom: 16 }}>
                      <div style={{ fontWeight: 600, marginBottom: 6 }}>Cover Letter</div>
                      <p style={{ color: '#ccc', fontSize: '0.875rem', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
                        {content.cover_letter}
                      </p>
                    </div>
                  )}
                  {content.skills?.length > 0 && (
                    <div style={{ marginBottom: 12 }}>
                      <div style={{ fontWeight: 600, marginBottom: 6 }}>Skills</div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                        {content.skills.map((s, i) => (
                          <span key={i} className="badge">{s}</span>
                        ))}
                      </div>
                    </div>
                  )}
                  {content.experience?.length > 0 && (
                    <div>
                      <div style={{ fontWeight: 600, marginBottom: 6 }}>Experience</div>
                      {content.experience.map((e, i) => (
                        <div key={i} style={{ marginBottom: 10 }}>
                          <div style={{ fontWeight: 500 }}>{e.title} — {e.company}</div>
                          <p style={{ color: '#90a4ae', fontSize: '0.85rem' }}>{e.description}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })
      }
    </div>
  )
}
