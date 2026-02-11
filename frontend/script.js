const resumeEl = document.getElementById('resume');
const statusEl = document.getElementById('status');

let resumeState = {
  resume_id: null,
  content: '',
};

document.getElementById('generate').addEventListener('click', async () => {
  try {
    const profile = JSON.parse(document.getElementById('profile').value);
    const target_role = document.getElementById('targetRole').value;
    const target_company = document.getElementById('targetCompany').value;
    const keywords = document
      .getElementById('keywords')
      .value
      .split(',')
      .map((x) => x.trim())
      .filter(Boolean);

    const res = await fetch('/api/resume/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profile, target_role, target_company, keywords }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(JSON.stringify(data));

    resumeState = { resume_id: data.resume_id, content: data.content };
    resumeEl.textContent = data.content;
    statusEl.textContent = `Resume generated: ${data.resume_id}`;
  } catch (err) {
    statusEl.textContent = `Generate failed: ${err.message}`;
  }
});

document.getElementById('apply').addEventListener('click', async () => {
  try {
    if (!resumeState.resume_id) {
      throw new Error('Generate a resume first');
    }

    const jobs = JSON.parse(document.getElementById('jobs').value);
    const res = await fetch('/api/jobs/auto-apply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resume_id: resumeState.resume_id,
        resume_text: resumeState.content,
        jobs,
        auto_submit: true,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(JSON.stringify(data));

    statusEl.textContent = `Queued applications: ${data.queued}`;
  } catch (err) {
    statusEl.textContent = `Auto-apply failed: ${err.message}`;
  }
});
