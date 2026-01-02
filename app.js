const submitBtn = document.getElementById('submit');
const urlInput = document.getElementById('url');
const statusDiv = document.getElementById('status');
const accessLinkContainer = document.getElementById('accessLinkContainer');
const accessLinkSpan = document.getElementById('accessLink');
const transcriptDiv = document.getElementById('transcript');
const summaryDiv = document.getElementById('summary');
const chatDiv = document.getElementById('chat');
const questionInput = document.getElementById('question');
const askBtn = document.getElementById('ask');
const chatAnswerDiv = document.getElementById('chatAnswer');

let accessLink = "";

submitBtn.addEventListener('click', async () => {
  const url = urlInput.value;
  statusDiv.textContent = "Submitting...";
  
  const res = await fetch('/jobs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  });
  
  const data = await res.json();
  accessLink = data.access_link;
  accessLinkSpan.textContent = accessLink;
  accessLinkContainer.style.display = "block";
  
  pollStatus();
});

async function pollStatus() {
  const res = await fetch(`/jobs/${accessLink}/status`);
  const data = await res.json();
  statusDiv.textContent = "Status: " + data.status;
  
  if (data.status === "done") {
    loadResult();
  } else if (data.status === "failed") {
    statusDiv.textContent += " (failed)";
  } else {
    setTimeout(pollStatus, 5000);
  }
}

async function loadResult() {
  const res = await fetch(`/jobs/${accessLink}/result`);
  const data = await res.json();
  
  transcriptDiv.style.display = "block";
  summaryDiv.style.display = "block";
  chatDiv.style.display = "block";
  
  transcriptDiv.textContent = "Transcript:\n" + data.transcript;
  summaryDiv.textContent = "Summary:\n" + data.summary;
}

askBtn.addEventListener('click', async () => {
  const question = questionInput.value;
  const res = await fetch(`/jobs/${accessLink}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  });
  
  const data = await res.json();
  chatAnswerDiv.textContent = data.answer;
});
