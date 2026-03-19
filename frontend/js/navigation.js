function navigate(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-link[data-page]').forEach(a => a.classList.remove('active'));

  const page = document.getElementById('page-' + pageId);
  const link = document.querySelector(`.nav-link[data-page="${pageId}"]`);
  if (page) page.classList.add('active');
  if (link) link.classList.add('active');
}

document.addEventListener('DOMContentLoaded', () => navigate('screen'));