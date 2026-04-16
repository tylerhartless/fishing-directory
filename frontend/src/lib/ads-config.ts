/**
 * Centralized ad configuration for Google AdSense integration.
 *
 * Controlled by two environment variables:
 *   PUBLIC_ADS_ENABLED  – master toggle ("true" to enable)
 *   PUBLIC_ADSENSE_PUBLISHER_ID – your ca-pub-XXXXX id
 *
 * When both are set ads render; otherwise every ad component renders nothing.
 */

export const PUBLISHER_ID: string =
  import.meta.env.PUBLIC_ADSENSE_PUBLISHER_ID ?? '';

export const ADS_ENABLED: boolean =
  import.meta.env.PUBLIC_ADS_ENABLED === 'true';

/** Number of result cards between in-feed ad slots */
export const AD_FREQUENCY = 8;

/**
 * Named ad-slot map.  Values will be real AdSense slot IDs once the account
 * is approved.  Until then they stay empty and the components show
 * dev-placeholders instead.
 */
export const AD_SLOTS = {
  sidebarLeft: '',
  sidebarRight: '',
  inFeed: '',
  inlineHorizontal: '',
  sidebarContent: '',
} as const;

export type AdSlotName = keyof typeof AD_SLOTS;
