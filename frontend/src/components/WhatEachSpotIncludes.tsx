/**
 * What Each Spot Includes Component
 * Shows the features available for each fishing spot listing
 */

export default function WhatEachSpotIncludes() {
  return (
    <div class="spot-features-section">
      <h2 class="section-header">
        <span class="header-prompt">›</span> WHAT EACH SPOT INCLUDES
      </h2>

      <ul class="features-list">
        <li>
          <span class="feature-icon">📍</span>
          <span class="feature-text">Address or GPS coordinates</span>
        </li>
        <li>
          <span class="feature-icon">🅿️</span>
          <span class="feature-text">Amenities when available</span>
        </li>
        <li>
          <span class="feature-icon">🐟</span>
          <span class="feature-text">Fish species caught there</span>
        </li>
        <li>
          <span class="feature-icon">🗺️</span>
          <span class="feature-text">Map with navigation link</span>
        </li>
        <li>
          <span class="feature-icon">⭐</span>
          <span class="feature-text">Quality ranking data</span>
        </li>
      </ul>
    </div>
  );
}
