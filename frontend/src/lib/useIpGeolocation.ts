/**
 * Custom hook for IP geolocation
 * Provides a simple interface for components to get location data
 */

import { useState, useEffect } from 'preact/hooks';
import { getIpGeolocationData, type IpGeolocationData } from './ipGeolocation';

export function useIpGeolocation() {
  const [data, setData] = useState<IpGeolocationData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') {
      setIsLoading(false);
      return;
    }

    const loadData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const geoData = await getIpGeolocationData();
        setData(geoData);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to load geolocation'));
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  return { data, isLoading, error };
}

