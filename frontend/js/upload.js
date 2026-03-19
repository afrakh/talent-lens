let resFiles  = [];
let jdFile    = null;
let inputMode = 'write';

function setMode(mode) {
  inputMode = mode;
  document.getElementById('pane-write').style.display  = mode === 'write'  ? 'block' : 'none';
  document.getElementById('pane-upload').style.display = mode === 'upload' ? 'block' : 'none';
  document.getElementById('btn-write').classList.toggle('active',  mode === 'write');
  document.getElementById('btn-upload').classList.toggle('active', mode === 'upload');
}

function jdDragOver(e)   { e.preventDefault(); document.getElementById('jd-drop').classList.add('over'); }
function jdDragLeave()   { document.getElementById('jd-drop').classList.remove('over'); }
function jdDropped(e)    { e.preventDefault(); jdDragLeave(); handleJdFile(e.dataTransfer.files[0]); }
function jdBrowse(files) { handleJdFile(files[0]); }

function handleJdFile(file) {
  if (!file) return;
  if (!file.name.endsWith('.pdf') && !file.name.endsWith('.txt')) {
    showAlert('Only PDF or TXT files are supported.'); return;
  }
  jdFile = file;
  if (file.name.endsWith('.txt')) {
    const r = new FileReader();
    r.onload = e => { jdFile._text = e.target.result; };
    r.readAsText(file);
  }
  renderJdChip();
}

function renderJdChip() {
  const el = document.getElementById('jd-chip');
  if (!jdFile) { el.innerHTML = ''; return; }
  el.innerHTML = `
    <div class="file-item" style="margin-top:12px">
      ${_fileIcon()}
      <span class="fname">${jdFile.name}</span>
      <span class="fsize">${(jdFile.size / 1024).toFixed(0)} KB</span>
      <button class="file-remove" onclick="clearJdFile()">&#215;</button>
    </div>`;
}

function clearJdFile() {
  jdFile = null;
  document.getElementById('jd-chip').innerHTML   = '';
  document.getElementById('jd-file-input').value = '';
}

function resDragOver(e)   { e.preventDefault(); document.getElementById('res-drop').classList.add('over'); }
function resDragLeave()   { document.getElementById('res-drop').classList.remove('over'); }
function resDropped(e)    { e.preventDefault(); resDragLeave(); addResFiles(Array.from(e.dataTransfer.files)); }
function resBrowse(files) { addResFiles(Array.from(files)); }

function addResFiles(files) {
  const pdfs  = files.filter(f => f.name.endsWith('.pdf'));
  const fresh = pdfs.filter(f => !resFiles.find(r => r.name === f.name));
  const dupes = pdfs.length - fresh.length;

  resFiles = [...resFiles, ...fresh];
  if (dupes) showAlert(`${dupes} duplicate file(s) skipped.`);
  renderResFiles();
}

function removeResFile(i) { resFiles.splice(i, 1); renderResFiles(); }

function renderResFiles() {
  const el = document.getElementById('res-file-list');
  if (!resFiles.length) { el.innerHTML = ''; return; }

  el.innerHTML =
    resFiles.map((f, i) => `
      <div class="file-item">
        ${_fileIcon()}
        <span class="fname">${f.name}</span>
        <span class="fsize">${(f.size / 1024).toFixed(0)} KB</span>
        <button class="file-remove" onclick="removeResFile(${i})">&#215;</button>
      </div>`).join('') +
    `<div class="file-count">${resFiles.length} file${resFiles.length > 1 ? 's' : ''} selected</div>`;
}

function _fileIcon() {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
    <polyline points="14,2 14,8 20,8"/>
  </svg>`;
}