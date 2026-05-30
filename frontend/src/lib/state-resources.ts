/**
 * Per-state external resources for the "Before You Go" panel.
 *
 * Every spot has a `state` code, so this is the deterministic data source
 * for license / regulations links — no per-spot data required.
 *
 * Populated states have real agency URLs. Stub entries (empty strings) are
 * intentional: callers should branch on whether a URL is non-empty rather
 * than rendering broken or fabricated links.
 *
 * `stateParksLicenseFree` is only `true` where the state's parks policy
 * is documented (e.g., TPWD). Defaults to `false` everywhere else.
 */

export interface StateResources {
  /** Short agency abbreviation, e.g. 'TPWD' */
  agencyName: string;
  /** Full agency name, e.g. 'Texas Parks & Wildlife Department' */
  agencyFullName: string;
  /** Direct link to the state's fishing license purchase page */
  licenseUrl: string;
  /** Link to the state's fishing regulations page */
  regulationsUrl: string;
  /** Whether the state's parks allow license-free fishing */
  stateParksLicenseFree: boolean;
}

const STUB = (name: string): StateResources => ({
  agencyName: '',
  agencyFullName: name,
  licenseUrl: '',
  regulationsUrl: '',
  stateParksLicenseFree: false,
});

export const STATE_RESOURCES: Record<string, StateResources> = {
  TX: {
    agencyName: 'TPWD',
    agencyFullName: 'Texas Parks & Wildlife Department',
    licenseUrl: 'https://tpwd.texas.gov/business/licenses/online_sales/',
    regulationsUrl: 'https://tpwd.texas.gov/regulations/outdoor-annual/fishing/',
    stateParksLicenseFree: true,
  },

  AL: STUB('Alabama Wildlife & Freshwater Fisheries'),
  AK: STUB('Alaska Department of Fish & Game'),
  AZ: STUB('Arizona Game & Fish Department'),
  AR: STUB('Arkansas Game & Fish Commission'),
  CA: STUB('California Department of Fish & Wildlife'),
  CO: STUB('Colorado Parks & Wildlife'),
  CT: STUB('Connecticut Department of Energy & Environmental Protection'),
  DE: STUB('Delaware Division of Fish & Wildlife'),
  FL: STUB('Florida Fish & Wildlife Conservation Commission'),
  GA: STUB('Georgia Department of Natural Resources'),
  HI: STUB('Hawaii Division of Aquatic Resources'),
  ID: STUB('Idaho Department of Fish & Game'),
  IL: STUB('Illinois Department of Natural Resources'),
  IN: STUB('Indiana Department of Natural Resources'),
  IA: STUB('Iowa Department of Natural Resources'),
  KS: STUB('Kansas Department of Wildlife & Parks'),
  KY: STUB('Kentucky Department of Fish & Wildlife Resources'),
  LA: STUB('Louisiana Department of Wildlife & Fisheries'),
  ME: STUB('Maine Department of Inland Fisheries & Wildlife'),
  MD: STUB('Maryland Department of Natural Resources'),
  MA: STUB('Massachusetts Division of Fisheries & Wildlife'),
  MI: STUB('Michigan Department of Natural Resources'),
  MN: STUB('Minnesota Department of Natural Resources'),
  MS: STUB('Mississippi Department of Wildlife, Fisheries & Parks'),
  MO: STUB('Missouri Department of Conservation'),
  MT: STUB('Montana Fish, Wildlife & Parks'),
  NE: STUB('Nebraska Game & Parks Commission'),
  NV: STUB('Nevada Department of Wildlife'),
  NH: STUB('New Hampshire Fish & Game Department'),
  NJ: STUB('New Jersey Division of Fish & Wildlife'),
  NM: STUB('New Mexico Department of Game & Fish'),
  NY: STUB('New York State Department of Environmental Conservation'),
  NC: STUB('North Carolina Wildlife Resources Commission'),
  ND: STUB('North Dakota Game & Fish Department'),
  OH: STUB('Ohio Division of Wildlife'),
  OK: STUB('Oklahoma Department of Wildlife Conservation'),
  OR: STUB('Oregon Department of Fish & Wildlife'),
  PA: STUB('Pennsylvania Fish & Boat Commission'),
  RI: STUB('Rhode Island Department of Environmental Management'),
  SC: STUB('South Carolina Department of Natural Resources'),
  SD: STUB('South Dakota Game, Fish & Parks'),
  TN: STUB('Tennessee Wildlife Resources Agency'),
  UT: STUB('Utah Division of Wildlife Resources'),
  VT: STUB('Vermont Fish & Wildlife Department'),
  VA: STUB('Virginia Department of Wildlife Resources'),
  WA: STUB('Washington Department of Fish & Wildlife'),
  WV: STUB('West Virginia Division of Natural Resources'),
  WI: STUB('Wisconsin Department of Natural Resources'),
  WY: STUB('Wyoming Game & Fish Department'),
};

export function getStateResources(stateCode: string): StateResources {
  return STATE_RESOURCES[stateCode] ?? STUB('your state wildlife agency');
}
