/**
 * What Each Spot Includes Component
 * Shows the features available for each fishing spot listing
 * Uses retro-section for container styling
 */

export default function WhatEachSpotIncludes() {
  return (
    <div class="retro-section">
      <h2 class="retro-heading-md" style="text-align: center; margin-bottom: 1.5rem;">
        › WHAT EACH SPOT INCLUDES
      </h2>

      <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.75rem;">
        <li style="display: flex; align-items: center; gap: 1rem; font-family: var(--font-terminal); font-size: 1.15rem;">
          <span style="font-size: 1.5rem; flex-shrink: 0;">📍</span>
          <span>Address or GPS coordinates</span>
        </li>
        <li style="display: flex; align-items: center; gap: 1rem; font-family: var(--font-terminal); font-size: 1.15rem;">
          <span style="font-size: 1.5rem; flex-shrink: 0;">🅿️</span>
          <span>Amenities when available</span>
        </li>
        <li style="display: flex; align-items: center; gap: 1rem; font-family: var(--font-terminal); font-size: 1.15rem;">
          <span style="font-size: 1.5rem; flex-shrink: 0;">🐟</span>
          <span>Fish species caught there</span>
        </li>
        <li style="display: flex; align-items: center; gap: 1rem; font-family: var(--font-terminal); font-size: 1.15rem;">
          <span style="font-size: 1.5rem; flex-shrink: 0;">🗺️</span>
          <span>Map with navigation link</span>
        </li>
        <li style="display: flex; align-items: center; gap: 1rem; font-family: var(--font-terminal); font-size: 1.15rem;">
          <span style="font-size: 1.5rem; flex-shrink: 0;">⭐</span>
          <span>Quality ranking data</span>
        </li>
      </ul>
    </div>
  );
}
