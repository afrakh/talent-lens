const API = 'http://localhost:8000';

async function apiHealth() {
  const res = await fetch(`${API}/health`, { signal: AbortSignal.timeout(5000) });
  if (!res.ok) throw new Error('Backend not responding');
}

async function apiParseResumes(files, signal) {
  const form = new FormData();
  files.forEach(f => form.append('files', f));

  const res = await fetch(`${API}/resume/parse-multiple`, { method: 'POST', body: form, signal });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function apiParseResume(file, signal) {
  const form = new FormData();
  form.append('file', file);

  const res = await fetch(`${API}/resume/parse`, { method: 'POST', body: form, signal });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}


async function apiParseJD(jdText, signal) {
  const res = await fetch(`${API}/jd/parse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jd_text: jdText }),
    signal,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}


async function apiRankResumes(jdText, jdSkills, resumes, signal) {
  const res = await fetch(`${API}/scoring/rank`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jd_text: jdText, jd_skills: jdSkills, resumes }),
    signal,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}