import { useEffect, useRef } from 'preact/hooks';

/**
 * Preact component for injecting an ad slot inside client-rendered
 * result grids (e.g. SearchWidget infinite-scroll).
 *
 * Shows a dev-placeholder when no publisher ID / slot ID is configured.
 */

interface InFeedAdProps {
  publisherId: string;
  slotId: string;
  index: number;
}

export default function InFeedAd({ publisherId, slotId, index }: InFeedAdProps) {
  const insRef = useRef<HTMLModElement | null>(null);

  const hasRealAd = publisherId.length > 0 && slotId.length > 0;

  useEffect(() => {
    if (hasRealAd && insRef.current) {
      // Guard against double-push (view transitions, re-renders)
      if (!insRef.current.getAttribute('data-adsbygoogle-status')) {
        try {
          ((window as any).adsbygoogle = (window as any).adsbygoogle || []).push({});
        } catch (_) {
          /* AdSense script not loaded yet — safe to ignore */
        }
      }
    }
  }, [hasRealAd]);

  if (hasRealAd) {
    return (
      <div class="ad-slot ad-slot-in-feed" key={`ad-${index}`}>
        <ins
          ref={insRef as any}
          class="adsbygoogle"
          style="display:block"
          data-ad-client={`ca-pub-${publisherId}`}
          data-ad-slot={slotId}
          data-ad-format="fluid"
          data-full-width-responsive="true"
        />
      </div>
    );
  }

  // Dev placeholder
  return (
    <div class="ad-slot ad-slot-in-feed" key={`ad-${index}`}>
      <div class="ad-slot-placeholder">Ad</div>
    </div>
  );
}
