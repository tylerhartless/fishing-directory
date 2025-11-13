/**
 * Heat List (Species Prevalence System) for fishing spot detail pages
 * Replaces the old voting system with time-decay based species prevalence
 */

const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'  // Local development
  : `${window.location.origin}/api`;  // Production & staging

// Track current spot ID (updated on each init)
let spotId = null;

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

    // Separate reported species
    const reportedSpecies = data.species.filter(s => s.has_reports);

    if (reportedSpecies.length === 0) {
      container.innerHTML = `
        <div class="heat-list">
          <p class="no-reports-message">No catches reported yet. Log a catch to help other anglers.</p>
        </div>
      `;
      return;
    }

    const SHOWCASE_LIMIT = 3;
    const showcaseSpecies = reportedSpecies.slice(0, SHOWCASE_LIMIT);
    const moreSpecies = reportedSpecies.length > SHOWCASE_LIMIT
      ? reportedSpecies.slice(SHOWCASE_LIMIT)
      : [];

    // Render the heat list
    container.innerHTML = `
      <div class="heat-list">
        <ul class="species-list species-list-showcase">
          ${showcaseSpecies.map(species => renderSpeciesListItem(species)).join('')}
        </ul>
      </div>
      ${moreSpecies.length > 0 ? `
        <div class="show-more-container">
          <ul class="species-list species-list-more" id="more-species-list" hidden>
            ${moreSpecies.map(species => renderSpeciesListItem(species)).join('')}
          </ul>
          <button
            class="show-more-btn"
            id="show-more-species"
            data-count="${moreSpecies.length}"
            aria-expanded="false"
          >
            Show more +
          </button>
        </div>
      ` : ''}
    `;

    document.getElementById('show-more-species')?.addEventListener('click', toggleMoreSpecies);

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
  const rawIcon = (species.icon ?? '').trim();
  if (rawIcon && !rawIcon.includes('?')) {
    const glyphs = Array.from(rawIcon);
    if (glyphs.length === 1 && glyphs[0]) {
      return glyphs[0];
    }
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
 * Render a species list item
 */
function renderSpeciesListItem(species, options = {}) {
  const { includeIcon = true } = options;
  const tier = TIER_CONFIG[species.tier] || TIER_CONFIG.unreported;
  const rarityLabel = tier.label || 'Unreported';
  const icon = includeIcon ? getSpeciesIcon(species) : null;

  return `
    <li class="species-list-item ${species.tier}" data-species-id="${species.id}">
      <span class="species-list-name">
        ${icon ? `<span class="species-list-icon">${icon}</span>` : ''}
        <span>${escapeHtml(species.common_name)}</span>
      </span>
      <span class="species-list-tier" style="color: ${tier.color};">${rarityLabel}</span>
    </li>
  `;
}

/**
 * Toggle the additional species list visibility
 */
function toggleMoreSpecies() {
  const btn = document.getElementById('show-more-species');
  const list = document.getElementById('more-species-list');

  if (!btn || !list) {
    return;
  }

  const isHidden = list.hasAttribute('hidden');
  if (isHidden) {
    list.removeAttribute('hidden');
    btn.textContent = 'Show less −';
    btn.setAttribute('aria-expanded', 'true');
  } else {
    list.setAttribute('hidden', '');
    btn.textContent = 'Show more +';
    btn.setAttribute('aria-expanded', 'false');
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
                    ${escapeHtml(species.common_name)}
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

const logCatchHandler = () => openLogCatchModal();

function initHeatList() {
  const spotElement = document.querySelector('[data-spot-id]');
  const newSpotId = spotElement?.dataset.spotId;

  if (!newSpotId) {
    console.error('Spot ID missing; unable to load heat list.');
    return;
  }

  spotId = newSpotId;

  const container = document.getElementById('heat-list-container');
  if (container) {
    container.innerHTML = '<p class="loading">Loading species data...</p>';
  }

  const logCatchBtn = document.getElementById('log-catch-btn');
  if (logCatchBtn) {
    logCatchBtn.removeEventListener('click', logCatchHandler);
    logCatchBtn.addEventListener('click', logCatchHandler);
  }

  loadHeatList();
}

// Initialize when DOM is ready (covers both hard loads and Astro swaps)
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initHeatList, { once: true });
} else {
  initHeatList();
}

// Support Astro client-side navigation events if present
document.addEventListener('astro:page-load', initHeatList);
document.addEventListener('astro:after-swap', initHeatList);

