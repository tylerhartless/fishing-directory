/**
 * Value Proposition Badges Component
 * Displays 4 key differentiators for the fishing directory
 */

export default function ValuePropositionBadges() {
  return (
    <div class="value-prop-section">
      <h2 class="section-header">
        <span class="header-prompt">↓</span> WHY USE THIS DIRECTORY?
      </h2>

      <div class="badge-grid">
        <div class="value-badge">
          <div class="badge-icon">✓</div>
          <div class="badge-content">
            <h3>COMMUNITY VALIDATED</h3>
            <p>Real catches from real anglers</p>
          </div>
        </div>

        <div class="value-badge">
          <div class="badge-icon">✓</div>
          <div class="badge-content">
            <h3>NO PRIVATE PROPERTY</h3>
            <p>Every spot is legal</p>
          </div>
        </div>

        <div class="value-badge">
          <div class="badge-icon">✓</div>
          <div class="badge-content">
            <h3>OFFICIAL DATA SOURCES</h3>
            <p>Wildlife programs + anglers</p>
          </div>
        </div>

        <div class="value-badge">
          <div class="badge-icon">✓</div>
          <div class="badge-content">
            <h3>3,300+ SPOTS & GROWING</h3>
            <p>More states launching</p>
          </div>
        </div>
      </div>
    </div>
  );
}
