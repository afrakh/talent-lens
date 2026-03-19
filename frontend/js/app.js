/* ============================================================
   app.js
   ============================================================ */

let abortCtrl     = null;
let parsedResumes = [];
let rankings      = [];
let activeFilter  = 'all';
let activeSort    = 'score';

/* ════════════════════════════════════════════
   LOADER
════════════════════════════════════════════ */
const LOADER_STEPS = [
  { text: 'Reading resumes',      sub: 'Preparing results'          },
  { text: 'Understanding skills', sub: 'Matching against job requirements'  },
  { text: 'Comparing candidates', sub: 'Measuring relevance to the role'   },
  { text: 'AI review',            sub: 'Getting a holistic view of each CV' },
  { text: 'Preparing results',    sub: 'Almost there...'                    },
];

let _stepTimer = null, _clockTimer = null, _stepIdx = 0, _elapsed = 0;

function showLoader(numResumes) {
  _stepIdx = 0; _elapsed = 0;
  _renderLoaderStep();
  document.getElementById('loader').classList.add('show');
  const stepMs = Math.max(numResumes * 8000 + 10000, 20000) / LOADER_STEPS.length;
  _stepTimer  = setInterval(() => { _stepIdx = Math.min(_stepIdx + 1, LOADER_STEPS.length - 1); _renderLoaderStep(); }, stepMs);
  _clockTimer = setInterval(() => {
    _elapsed++;
    const el = document.getElementById('loader-elapsed');
    if (el) el.textContent = `${_elapsed}s elapsed`;
  }, 1000);
}

function hideLoader() {
  clearInterval(_stepTimer);
  clearInterval(_clockTimer);
  document.getElementById('loader').classList.remove('show');
}

function _renderLoaderStep() {
  const s   = LOADER_STEPS[_stepIdx];
  const txt = document.getElementById('loader-txt');
  const sub = document.getElementById('loader-sub');
  const dot = document.getElementById('loader-dots');
  if (txt) txt.textContent = s.text;
  if (sub) sub.textContent = s.sub;
  if (dot) dot.innerHTML = LOADER_STEPS.map((_, i) =>
    `<div class="progress-dot ${i <= _stepIdx ? 'active' : ''} ${i === _stepIdx ? 'current' : ''}"></div>`
  ).join('');
}

function cancelAnalysis() {
  if (abortCtrl) abortCtrl.abort();
  hideLoader();
  showAlert('Analysis cancelled.');
}

function showAlert(msg) {
  const el = document.getElementById('alert-err');
  el.textContent = msg;
  el.style.display = 'block';
}
function hideAlert() {
  document.getElementById('alert-err').style.display = 'none';
}

/* ════════════════════════════════════════════
   RUN FILTER
════════════════════════════════════════════ */
async function runFilter() {
  hideAlert();

  let jdText = '', jdTitle = '';

  if (inputMode === 'write') {
    jdTitle       = document.getElementById('jd-title').value.trim();
    const desc    = document.getElementById('jd-desc').value.trim();
    if (!jdTitle) { showAlert('Please enter a job title.');       return; }
    if (!desc)    { showAlert('Please enter a job description.'); return; }
    const company = document.getElementById('jd-company').value.trim();
    const req     = document.getElementById('req-skills').value.trim();
    const pref    = document.getElementById('pref-skills').value.trim();
    jdText = [jdTitle, company, desc, req, pref].filter(Boolean).join('\n');
  } else {
    if (!jdFile) { showAlert('Please upload a job description file.'); return; }
    jdText  = jdFile._text || `[PDF: ${jdFile.name}]`;
    jdTitle = jdFile.name.replace(/\.[^/.]+$/, '');
  }

  if (!resFiles.length) { showAlert('Please upload at least one resume PDF.'); return; }

  try { await apiHealth(); }
  catch { showAlert('Cannot reach the backend. Make sure uvicorn is running on port 8000.'); return; }

  showLoader(resFiles.length);
  abortCtrl = new AbortController();
  const { signal } = abortCtrl;
  const timeout = setTimeout(() => abortCtrl.abort(), 180_000);

  try {
    parsedResumes = await apiParseResumes(resFiles, signal);

    if (inputMode === 'upload' && jdFile?.name.endsWith('.pdf')) {
      const jdParsed = await apiParseResume(jdFile, signal);
      jdText = Object.values(jdParsed.sections || {}).join('\n') || jdText;
    }

    const jdData   = await apiParseJD(jdText, signal);
    const jdSkills = jdData.skills || [];

    const resumesPayload = {};
    parsedResumes.forEach(r => {
      resumesPayload[r.candidate_id] = {
        text:   Object.values(r.sections || {}).join('\n'),
        skills: r.skills || [],
      };
    });

    const rankData = await apiRankResumes(jdText, jdSkills, resumesPayload, signal);
    rankings = rankData.rankings || [];
    window._jdTitle = jdTitle;

    clearTimeout(timeout);
    hideLoader();
    activeFilter = 'all';
    activeSort   = 'score';
    renderResults();
    navigate('results');

  } catch (err) {
    clearTimeout(timeout);
    hideLoader();
    if (err.name === 'AbortError') {
      showAlert('Request timed out or was cancelled. Try again — first run may be slow.');
    } else {
      showAlert('Something went wrong: ' + err.message);
    }
  }
}

/* ════════════════════════════════════════════
   FILTER & SORT
════════════════════════════════════════════ */
function _getLabel(score) {
  return score >= 75 ? 'Strong Match' : score >= 55 ? 'Moderate Match' : 'Weak Match';
}

function setFilter(filter) {
  activeFilter = filter;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('filter-' + filter).classList.add('active');
  _renderCards();
}

function setSort(sort) {
  activeSort = sort;
  document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('sort-' + sort).classList.add('active');
  _renderCards();
}

function _filteredSorted() {
  let list = [...rankings];

  // Filter
  if (activeFilter === 'strong')   list = list.filter(r => r.final_score >= 75);
  if (activeFilter === 'possible') list = list.filter(r => r.final_score >= 55 && r.final_score < 75);
  if (activeFilter === 'weak')     list = list.filter(r => r.final_score < 55);

  // Sort
  if (activeSort === 'score') list.sort((a, b) => b.final_score - a.final_score);
  if (activeSort === 'name') {
    const parsedMap = {};
    parsedResumes.forEach(r => { parsedMap[r.candidate_id] = r; });
    list.sort((a, b) => {
      const na = (parsedMap[a.candidate_id]?.name || '').toLowerCase();
      const nb = (parsedMap[b.candidate_id]?.name || '').toLowerCase();
      return na.localeCompare(nb);
    });
  }

  return list;
}

/* ════════════════════════════════════════════
   RENDER RESULTS
════════════════════════════════════════════ */
function renderResults() {
  if (!rankings.length) return;

  document.getElementById('results-empty').style.display   = 'none';
  document.getElementById('results-content').style.display = 'block';

  // Stats
  const strong   = rankings.filter(r => r.final_score >= 75).length;
  const possible = rankings.filter(r => r.final_score >= 55 && r.final_score < 75).length;
  document.getElementById('stat-screened').textContent = parsedResumes.length;
  document.getElementById('stat-ranked').textContent   = rankings.length;
  document.getElementById('stat-strong').textContent   = strong;
  document.getElementById('stat-possible').textContent = possible;

  _renderCards();
}

function _renderCards() {
  const parsedMap = {};
  parsedResumes.forEach(r => { parsedMap[r.candidate_id] = r; });

  const list = _filteredSorted();
  const container = document.getElementById('candidate-list');

  if (!list.length) {
    container.innerHTML = `
      <div class="empty-state" style="padding:40px">
        <p>No candidates match this filter.</p>
      </div>`;
    return;
  }

  container.innerHTML = list.map((r, i) => {
    const parsed = parsedMap[r.candidate_id] || {};

    let name  = parsed.name  || '';
    let email = parsed.email || '';
    if (name && email && name.includes(email)) name = name.replace(email, '').trim();
    if (!name) name = 'Candidate ' + (i + 1);

    const initials = name.split(' ').filter(Boolean).slice(0, 2)
                         .map(w => w[0].toUpperCase()).join('') || '?';

    const score    = Math.round(r.final_score);
    const lbl      = _getLabel(score);
    const badgeCls = score >= 75 ? 'badge-strong' : score >= 55 ? 'badge-moderate' : 'badge-weak';
    const cardCls  = score >= 75 ? 'card-strong'  : score >= 55 ? 'card-moderate'  : 'card-weak';
    const circleCls= score >= 75 ? 'circle-strong': score >= 55 ? 'circle-moderate': 'circle-weak';

    const matchedTags = (r.matched_skills || []).slice(0, 8)
      .map(s => `<span class="skill-tag skill-match">${s}</span>`).join('');
    const missingTags = (r.missing_skills || []).slice(0, 6)
      .map(s => `<span class="skill-tag skill-miss">${s}</span>`).join('');

    // Only show rank number when sorted by score
    const rankNum = activeSort === 'score' ? i + 1 : '—';

    return `
    <div class="candidate-card ${cardCls}">

      <div class="cand-top-row">
        <div class="cand-left">
          <div class="cand-rank-num">${rankNum}</div>
          <div class="cand-avatar">${initials}</div>
          <div class="cand-info">
            <div class="cand-name">${name}</div>
            ${email ? `<div class="cand-email">${email}</div>` : ''}
            <span class="badge ${badgeCls}">${lbl}</span>
          </div>
        </div>
        <div class="cand-score-circle ${circleCls}">
          <div class="score-circle-num">${score}%</div>
          <div class="score-circle-lbl">Match</div>
        </div>
      </div>

      ${r.llm_reasoning ? `<p class="cand-reasoning">${r.llm_reasoning}</p>` : ''}

      <div class="single-bar-row">
        <div class="score-label-row">
          <span>Overall match</span>
          <span>${score}%</span>
        </div>
        <div class="score-track">
          <div class="score-fill ${score >= 75 ? 'fill-teal' : score >= 55 ? 'fill-amber' : 'fill-red'}"
               style="width:${score}%"></div>
        </div>
      </div>

      ${matchedTags ? `
        <div class="skills-row">
          <div class="skills-label">Has these skills</div>
          <div>${matchedTags}</div>
        </div>` : ''}

      ${missingTags ? `
        <div class="skills-row">
          <div class="skills-label">Skills to check in interview</div>
          <div>${missingTags}</div>
        </div>` : ''}

    </div>`;
  }).join('');
}