/**
 * Value Proposition Badges Component
 * Displays 4 key differentiators for the fishing directory
 * Uses retro-section for container styling
 */

export default function ValuePropositionBadges() {
  return (
    <div class="retro-section">
      <div class="retro-grid grid-auto-fit">
        <div class="value-badge flex">
          <div class="font-size-lg flex-shrink-0 mr-lg">✓</div>
          <div>
            <h3 class="text-left">COMMUNITY VALIDATED</h3>
            <p class="font-body-text font-size-base text-left mt-sm mb-0">Real catches from real anglers</p>
          </div>
        </div>

        <div class="value-badge flex">
          <div class="font-size-lg flex-shrink-0 mr-lg">✓</div>
          <div>
            <h3 class="text-left">NO PRIVATE PROPERTY</h3>
            <p class="font-body-text font-size-base text-left mt-0">Every spot is legal</p>
          </div>
        </div>

        <div class="value-badge flex">
          <div class="font-size-lg flex-shrink-0 mr-lg">✓</div>
          <div>
            <h3 class="text-left">OFFICIAL DATA SOURCES</h3>
            <p class="font-body-text font-size-base text-left mt-0">Wildlife programs + anglers</p>
          </div>
        </div>

        <div class="value-badge flex">
          <div class="font-size-lg flex-shrink-0 mr-lg">✓</div>
          <div>
            <h3 class="text-left">3,300+ SPOTS & GROWING</h3>
            <p class="font-body-text font-size-base text-left mt-0">More states launching</p>
          </div>
        </div>
      </div>
    </div>
  );
}
