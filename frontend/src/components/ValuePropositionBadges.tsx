/**
 * Value Proposition Badges Component
 * Displays 4 key differentiators for the fishing directory
 * Uses retro-section for container styling
 */

export default function ValuePropositionBadges() {
  return (
    <div class="retro-section">
      <div class="retro-grid" style="grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
        <div class="value-badge">
          <div style="font-size: 1.5rem; margin-right: 1rem;">✓</div>
          <div>
            <h3 class="retro-heading-sm">COMMUNITY VALIDATED</h3>
            <p style="margin: 0.5rem 0 0 0; font-family: var(--font-terminal); font-size: 1.2rem; text-align: left;">Real catches from real anglers</p>
          </div>
        </div>

        <div class="value-badge">
          <div style="font-size: 1.5rem; margin-right: 1rem;">✓</div>
          <div>
            <h3 class="retro-heading-sm">NO PRIVATE PROPERTY</h3>
            <p style="margin: 0.5rem 0 0 0; font-family: var(--font-terminal); font-size: 1.2rem; text-align: left;">Every spot is legal</p>
          </div>
        </div>

        <div class="value-badge">
          <div style="font-size: 1.5rem; margin-right: 1rem;">✓</div>
          <div>
            <h3 class="retro-heading-sm">OFFICIAL DATA SOURCES</h3>
            <p style="margin: 0.5rem 0 0 0; font-family: var(--font-terminal); font-size: 1.2rem; text-align: left;">Wildlife programs + anglers</p>
          </div>
        </div>

        <div class="value-badge">
          <div style="font-size: 1.5rem; margin-right: 1rem;">✓</div>
          <div>
            <h3 class="retro-heading-sm">3,300+ SPOTS & GROWING</h3>
            <p style="margin: 0.5rem 0 0 0; font-family: var(--font-terminal); font-size: 1.2rem; text-align: left;">More states launching</p>
          </div>
        </div>
      </div>
    </div>
  );
}
