document.addEventListener('DOMContentLoaded', () => {
  const taskInput = document.getElementById('task-input');
  const runBtn = document.getElementById('run-btn');
  const executionLog = document.getElementById('execution-log');
  const statusDot = document.getElementById('agent-status-dot');
  const statusText = document.getElementById('agent-status-text');
  const loader = document.getElementById('loader');

  runBtn.addEventListener('click', executeTask);
  taskInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') executeTask();
  });

  async function executeTask() {
    const task = taskInput.value.trim();
    if (!task) return;

    // Reset UI
    executionLog.innerHTML = '';
    runBtn.disabled = true;
    statusDot.className = 'status-dot dot-busy';
    statusText.innerText = 'Status: Reasoner active...';
    loader.style.display = 'inline-block';

    try {
      const response = await fetch('/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        renderSteps(data.steps);
        statusDot.className = 'status-dot dot-online';
        statusText.innerText = 'Status: Task Completed';
      } else {
        addStep('ERROR', data.error, 'error');
        statusDot.className = 'status-dot dot-online';
        statusText.innerText = 'Status: Error Encountered';
      }
    } catch (err) {
      addStep('SYSTEM ERROR', err.message, 'error');
    } finally {
      runBtn.disabled = false;
      loader.style.display = 'none';
      taskInput.value = '';
    }
  }

  function renderSteps(steps) {
    steps.forEach((step, index) => {
      setTimeout(() => {
        addStep(step.type, step.content, step.status || 'success');
      }, index * 800); // Stagger results for better UX
    });
  }

  function addStep(header, content, status = 'success') {
    const stepDiv = document.createElement('div');
    stepDiv.className = 'step';
    
    const headerDiv = document.createElement('div');
    headerDiv.className = 'step-header';
    headerDiv.innerText = header;

    const bodyDiv = document.createElement('div');
    bodyDiv.className = 'step-body';
    bodyDiv.innerHTML = formatContent(content);
    
    if (status === 'error') {
      bodyDiv.classList.add('error');
    } else if (status === 'success' && header === 'RESULT') {
       bodyDiv.classList.add('result');
    }

    stepDiv.appendChild(headerDiv);
    stepDiv.appendChild(bodyDiv);
    executionLog.appendChild(stepDiv);
    
    // Auto-scroll
    stepDiv.scrollIntoView({ behavior: 'smooth' });
  }

  function formatContent(content) {
    if (typeof content === 'object') {
      return `<pre>${JSON.stringify(content, null, 2)}</pre>`;
    }
    return content.replace(/\n/g, '<br>');
  }
});
