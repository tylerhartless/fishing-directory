/**
 * Dynamic content loader for fishing spot detail pages
 * Loads fishing reports and vote data via API
 */

const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost/api'  // Local development
  : 'https://yourdomain.com/api';  // Production

// Get spot ID from data attribute
const spotId = document.querySelector('[data-spot-id]')?.dataset.spotId;

if (!spotId) {
  console.error('No spot ID found');
}

/**
 * Load fishing reports
 */
async function loadReports() {
  const container = document.getElementById('reports-container');

  try {
    const response = await fetch(`${API_BASE}/reports.php?spot_id=${spotId}`);
    const data = await response.json();

    if (!data.success || data.reports.length === 0) {
      container.innerHTML = '<p class="no-data">No fishing reports yet. Be the first to share your catch!</p>';
      return;
    }

    // Render reports
    container.innerHTML = data.reports.map(report => `
      <div class="report-card">
        <div class="report-header">
          <strong>${escapeHtml(report.fish_species)}</strong>
          <span class="count">${report.catch_count} caught</span>
        </div>
        <div class="report-date">${formatDate(report.report_date)}</div>
        ${report.notes ? `<p class="report-notes">${escapeHtml(report.notes)}</p>` : ''}
      </div>
    `).join('');

  } catch (error) {
    console.error('Error loading reports:', error);
    container.innerHTML = '<p class="error">Unable to load fishing reports</p>';
  }
}

/**
 * Load fish species votes
 */
async function loadVotes() {
  const container = document.getElementById('fish-votes-container');

  try {
    const response = await fetch(`${API_BASE}/get-votes.php?spot_id=${spotId}`);
    const data = await response.json();

    if (!data.success) {
      throw new Error('Failed to load votes');
    }

    // Render vote interface
    const voteOptions = [
      { type: 'largemouth_bass', label: 'Largemouth Bass', icon: '🐟' },
      { type: 'catfish', label: 'Catfish', icon: '🐡' },
      { type: 'crappie', label: 'Crappie', icon: '🐠' },
      { type: 'striped_bass', label: 'Striped Bass', icon: '🐟' },
      { type: 'white_bass', label: 'White Bass', icon: '🐟' },
      { type: 'sunfish', label: 'Sunfish', icon: '🐠' },
    ];

    const voteCounts = {};
    data.votes.forEach(vote => {
      voteCounts[vote.vote_type] = vote.count;
    });

    container.innerHTML = `
      <div class="vote-grid">
        ${voteOptions.map(option => `
          <button class="vote-button" data-vote-type="${option.type}">
            <span class="vote-icon">${option.icon}</span>
            <span class="vote-label">${option.label}</span>
            <span class="vote-count">${voteCounts[option.type] || 0}</span>
          </button>
        `).join('')}
      </div>
    `;

    // Add click handlers
    document.querySelectorAll('.vote-button').forEach(button => {
      button.addEventListener('click', () => submitVote(button.dataset.voteType));
    });

  } catch (error) {
    console.error('Error loading votes:', error);
    container.innerHTML = '<p class="error">Unable to load fish species data</p>';
  }
}

/**
 * Submit a vote for a fish species
 */
async function submitVote(voteType) {
  try {
    const response = await fetch(`${API_BASE}/vote.php`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        spot_id: parseInt(spotId),
        vote_type: voteType
      })
    });

    const data = await response.json();

    if (data.success) {
      // Reload votes to show updated counts
      loadVotes();
      showNotification('Vote recorded!');
    } else {
      showNotification('Failed to record vote', 'error');
    }

  } catch (error) {
    console.error('Error submitting vote:', error);
    showNotification('Network error', 'error');
  }
}

/**
 * Handle "Add Report" button click
 */
document.getElementById('add-report-btn')?.addEventListener('click', () => {
  // For now, just show an alert. You can implement a modal form later.
  const species = prompt('What fish did you catch?');
  const count = prompt('How many?');
  const notes = prompt('Any notes? (optional)');

  if (species && count) {
    submitReport(species, count, notes);
  }
});

/**
 * Submit a fishing report
 */
async function submitReport(species, count, notes) {
  try {
    const response = await fetch(`${API_BASE}/submit-report.php`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        spot_id: parseInt(spotId),
        fish_species: species,
        catch_count: parseInt(count),
        report_date: new Date().toISOString().split('T')[0],
        notes: notes || ''
      })
    });

    const data = await response.json();

    if (data.success) {
      showNotification('Report submitted! It will appear after review.');
    } else {
      showNotification(data.error || 'Failed to submit report', 'error');
    }

  } catch (error) {
    console.error('Error submitting report:', error);
    showNotification('Network error', 'error');
  }
}

/**
 * Copy coordinates to clipboard
 */
document.querySelector('.copy-coords')?.addEventListener('click', function() {
  const coords = this.dataset.coords;
  navigator.clipboard.writeText(coords).then(() => {
    this.textContent = 'Copied!';
    setTimeout(() => {
      this.textContent = 'Copy';
    }, 2000);
  });
});

/**
 * Utility: Escape HTML to prevent XSS
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Utility: Format date nicely
 */
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'success') {
  // Simple notification implementation
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    background: ${type === 'error' ? '#f44336' : '#4caf50'};
    color: white;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    z-index: 1000;
  `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.remove();
  }, 3000);
}

// Initialize on page load
if (spotId) {
  loadReports();
  loadVotes();
}
