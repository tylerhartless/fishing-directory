/**
 * Heat List (Species Prevalence System) for fishing spot detail pages
 * Replaces the old voting system with time-decay based species prevalence
 */

const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'  // Local development
  : 'https://wherecanifish.com/api';  // Production

// Get spot ID from data attribute
const spotId = document.querySelector('[data-spot-id]')?.dataset.spotId;

if (!spotId) {
  console.error('No spot ID found');
}

// Tier configuration - using CSS color variables
// Note: Tier thresholds are configured in backend/api/get-heat-list.php
// These values are for display only - actual tier determination happens server-side
const TIER_CONFIG = {
  common: {
    label: 'Common',
    color: '#c41e1a',  // --boat-red (red)
    indicator: '●',
    threshold: 50  // Display reference only - actual threshold in PHP (launch: 50, mature: 5000)
  },
  uncommon: {
    label: 'Uncommon',
    color: '#e85d2a',  // --boat-orange (orange)
    indicator: '●',
    threshold: 20  // Display reference only - actual threshold in PHP (launch: 20, mature: 1000)
  },
  rare: {
    label: 'Rare',
    color: '#5c9dff',  // --badge-lake (blue)
    indicator: '●',
    threshold: 1
  },
  unreported: {
    label: 'Unreported',
    color: '#6b6b6b',  // --neutral-gray (gray)
    indicator: '[+]',
    threshold: 0
  }
};

/**
 * Load heat list data for the fishing spot
 */
async function loadHeatList() {
  const container = document.getElementById('heat-list-container');

  try {
    const response = await fetch(`${API_BASE}/get-heat-list.php?spot_id=${spotId}`);
    const data = await response.json();

    if (!data.success) {
      throw new Error('Failed to load heat list');
    }

    if (data.species.length === 0) {
      container.innerHTML = '<p class="no-data">No species data available for this location.</p>';
      return;
    }

    // Separate reported and unreported species
    const reportedSpecies = data.species.filter(s => s.has_reports);
    const unreportedSpecies = data.species.filter(s => !s.has_reports);

    // Dynamic list: Show all reported + backfill with top unreported until we have 7 items
    const displayLimit = 7;
    let displaySpecies = [...reportedSpecies];

    if (displaySpecies.length < displayLimit) {
      const backfillCount = displayLimit - displaySpecies.length;
      displaySpecies = displaySpecies.concat(unreportedSpecies.slice(0, backfillCount));
    }

    const remainingCount = data.species.length - displaySpecies.length;

    // Render the heat list
    container.innerHTML = `
      <div class="heat-list">
        ${displaySpecies.map(species => renderSpeciesItem(species)).join('')}
      </div>
      ${remainingCount > 0 ? `
        <button class="show-all-btn" id="show-all-species">
          Show all ${remainingCount} remaining species...
        </button>
        <div class="all-species-modal-backdrop" id="all-species-backdrop" style="display: none;"></div>
        <div class="all-species-list" id="all-species-list" style="display: none;">
          ${data.species.slice(displayLimit).map(species => renderSpeciesItem(species)).join('')}
        </div>
      ` : ''}
    `;

    // Add show all toggle
    document.getElementById('show-all-species')?.addEventListener('click', toggleShowAll);

    // Species items are NOT clickable - only the main "Log a Catch" button opens the modal

  } catch (error) {
    console.error('Error loading heat list:', error);
    container.innerHTML = '<p class="error">Unable to load species data</p>';
  }
}

/**
 * Get icon for species (with fallback if icon is missing or corrupted)
 */
function getSpeciesIcon(species) {
  // If icon exists and is not corrupted (not ????), use it
  if (species.icon && !species.icon.includes('?') && species.icon.trim() !== '') {
    return species.icon;
  }
  
  // Fallback icons based on common species names
  const iconMap = {
    'Largemouth Bass': '🎣',
    'Channel Catfish': '🐡',
    'Bluegill': '🐟',
    'Redear Sunfish': '🐠',
    'White Bass': '🐟',
    'Striped Bass': '🐟',
    'Blue Catfish': '🐡',
    'Flathead Catfish': '🐡',
    'Crappie': '🐠',
    'Sunfish': '🐠',
    'Carp': '🐟',
    'Gar': '🐊',
    'Trout': '🐟',
    'Redfish': '🐟',
    'Flounder': '🐟'
  };
  
  // Try to match by name
  for (const [name, icon] of Object.entries(iconMap)) {
    if (species.common_name.includes(name)) {
      return icon;
    }
  }
  
  // Default fallback
  return '🐟';
}

/**
 * Render a single species item
 */
function renderSpeciesItem(species) {
  const tier = TIER_CONFIG[species.tier];
  const isUnreported = species.tier === 'unreported';
  const icon = getSpeciesIcon(species);

  return `
    <div class="species-item ${species.tier}"
         data-species-id="${species.id}"
         data-species-name="${escapeHtml(species.common_name)}">
      <span class="species-indicator" style="color: ${tier.color};">${tier.indicator}</span>
      <span class="species-icon">${icon}</span>
      <span class="species-name">${escapeHtml(species.common_name)}</span>
      ${isUnreported ?
        '<span class="species-subtitle">Be the first!</span>' :
        `<span class="species-tier" style="color: ${tier.color};">${tier.label}</span>`
      }
    </div>
  `;
}

/**
 * Toggle show all species (opens in modal/dropdown)
 */
function toggleShowAll() {
  const btn = document.getElementById('show-all-species');
  const list = document.getElementById('all-species-list');
  const backdrop = document.getElementById('all-species-backdrop');

  if (list.style.display === 'none' || list.style.display === '') {
    // Show as modal overlay
    if (backdrop) backdrop.style.display = 'block';
    list.style.display = 'block';
    list.classList.add('all-species-modal');
    btn.textContent = 'Show less...';
    
    // Add close button if not exists
    if (!list.querySelector('.close-all-species')) {
      const closeBtn = document.createElement('button');
      closeBtn.className = 'close-all-species';
      closeBtn.textContent = '×';
      closeBtn.addEventListener('click', closeAllSpecies);
      list.insertBefore(closeBtn, list.firstChild);
    }
    
    // Close on backdrop click
    if (backdrop) {
      backdrop.addEventListener('click', closeAllSpecies);
    }
  } else {
    closeAllSpecies();
  }
}

/**
 * Close the all species modal
 */
function closeAllSpecies() {
  const btn = document.getElementById('show-all-species');
  const list = document.getElementById('all-species-list');
  const backdrop = document.getElementById('all-species-backdrop');
  
  if (backdrop) backdrop.style.display = 'none';
  if (list) {
    list.style.display = 'none';
    list.classList.remove('all-species-modal');
  }
  if (btn) {
    const remainingCount = list ? list.querySelectorAll('.species-item').length : 0;
    btn.textContent = `Show all ${remainingCount} remaining species...`;
  }
}

/**
 * Open the "Log a Catch" modal
 */
function openLogCatchModal(preselectedSpeciesId = null, preselectedSpeciesName = null) {
  // Load species list for dropdown
  loadSpeciesForModal(preselectedSpeciesId, preselectedSpeciesName);
}

/**
 * Load species list for the modal dropdown
 */
async function loadSpeciesForModal(preselectedSpeciesId = null, preselectedSpeciesName = null) {
  try {
    const response = await fetch(`${API_BASE}/get-heat-list.php?spot_id=${spotId}`);
    const data = await response.json();

    if (!data.success) {
      throw new Error('Failed to load species');
    }

    // Create modal HTML
    const modalHtml = `
      <div class="modal-overlay" id="log-catch-modal">
        <div class="modal-content">
          <div class="modal-header">
            <h3>Log a Catch</h3>
            <button class="modal-close" id="close-modal">&times;</button>
          </div>
          <form id="log-catch-form">
            <div class="form-group">
              <label for="species-select">Species *</label>
              <select id="species-select" required>
                <option value="">-- Select Species --</option>
                ${data.species.map(species => `
                  <option value="${species.id}" ${species.id === preselectedSpeciesId ? 'selected' : ''}>
                    ${species.icon} ${escapeHtml(species.common_name)}
                  </option>
                `).join('')}
              </select>
            </div>
            <div class="form-group">
              <label for="catch-date">Date Caught *</label>
              <input
                type="date"
                id="catch-date"
                required
                max="${new Date().toISOString().split('T')[0]}"
                value="${new Date().toISOString().split('T')[0]}"
              />
              <small>Catches must be within the last 30 days</small>
            </div>
            <div class="form-actions">
              <button type="button" class="btn-cancel" id="cancel-log-catch">Cancel</button>
              <button type="submit" class="btn-submit">Log Catch</button>
            </div>
          </form>
        </div>
      </div>
    `;

    // Add modal to page
    const existingModal = document.getElementById('log-catch-modal');
    if (existingModal) {
      existingModal.remove();
    }

    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Add event listeners
    document.getElementById('close-modal').addEventListener('click', closeLogCatchModal);
    document.getElementById('cancel-log-catch').addEventListener('click', closeLogCatchModal);
    document.getElementById('log-catch-form').addEventListener('submit', handleLogCatchSubmit);

    // Close on outside click
    document.getElementById('log-catch-modal').addEventListener('click', (e) => {
      if (e.target.id === 'log-catch-modal') {
        closeLogCatchModal();
      }
    });

  } catch (error) {
    console.error('Error loading species for modal:', error);
    showNotification('Unable to open form', 'error');
  }
}

/**
 * Close the log catch modal
 */
function closeLogCatchModal() {
  const modal = document.getElementById('log-catch-modal');
  if (modal) {
    modal.remove();
  }
}

/**
 * Handle form submission
 */
async function handleLogCatchSubmit(e) {
  e.preventDefault();

  const speciesId = parseInt(document.getElementById('species-select').value);
  const catchDate = document.getElementById('catch-date').value;

  if (!speciesId || !catchDate) {
    showNotification('Please fill in all required fields', 'error');
    return;
  }

  // Validate date is within last 30 days
  const catchTimestamp = new Date(catchDate).getTime();
  const now = new Date().getTime();
  const thirtyDaysAgo = now - (30 * 24 * 60 * 60 * 1000);

  if (catchTimestamp > now) {
    showNotification('Catch date cannot be in the future', 'error');
    return;
  }

  if (catchTimestamp < thirtyDaysAgo) {
    showNotification('Catch date must be within the last 30 days', 'error');
    return;
  }

  // Submit the catch
  try {
    const response = await fetch(`${API_BASE}/log-catch.php`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        spot_id: parseInt(spotId),
        species_id: speciesId,
        catch_date: catchDate
      })
    });

    const data = await response.json();

    if (data.success) {
      showNotification('Catch logged successfully!');
      closeLogCatchModal();
      // Reload heat list to show updated data
      setTimeout(() => loadHeatList(), 500);
    } else {
      showNotification(data.error || 'Failed to log catch', 'error');
    }

  } catch (error) {
    console.error('Error logging catch:', error);
    showNotification('Network error. Please try again.', 'error');
  }
}

/**
 * Utility: Escape HTML to prevent XSS
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Show notification toast
 */
function showNotification(message, type = 'success') {
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    background: ${type === 'error' ? '#c41e1a' : '#4a6741'};
    color: white;
    border-radius: 4px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    z-index: 10000;
    font-family: 'VT323', monospace;
    font-size: 1.2rem;
    animation: slideIn 0.3s ease-out;
  `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease-in';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Add animation styles
if (!document.getElementById('heat-list-animations')) {
  const style = document.createElement('style');
  style.id = 'heat-list-animations';
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(400px); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
      from { transform: translateX(0); opacity: 1; }
      to { transform: translateX(400px); opacity: 0; }
    }
  `;
  document.head.appendChild(style);
}

// Initialize on page load
if (spotId) {
  loadHeatList();
}

// Add global button handler for main "Log a Catch" button
document.getElementById('log-catch-btn')?.addEventListener('click', () => {
  openLogCatchModal();
});
