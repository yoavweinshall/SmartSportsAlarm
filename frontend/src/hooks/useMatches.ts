import { useCallback, useEffect, useRef, useState } from 'react';

import { useAuth } from '@/providers/AuthProvider';
import type { EnrichedMatch } from '@/types/models';

export type FetchMatchesParams = {
  is_live?: boolean;
  competition_id?: number;
  team_id?: number;
  followed_only?: boolean;
};

type MatchesState = {
  matches: EnrichedMatch[];
  isLoading: boolean;
  isFetchingNext: boolean;
  isFetchingPrevious: boolean;
  hasMoreNext: boolean;
  hasMorePrevious: boolean;
  error: string | null;
  loadNext: () => Promise<void>;
  loadPrevious: () => Promise<void>;
};

// Must match the `limit` default on the backend so hasMore inference is correct
const PAGE_SIZE = 50;
const REFRESH_INTERVAL_MS = 60_000;
const PREVIOUS_LOAD_COOLDOWN_MS = 500;

const isLiveMatch = (match: EnrichedMatch) => Number(match.stage_group) === 3;

const sortMatches = (items: EnrichedMatch[]) =>
  [...items].sort((a, b) => {
    const startTimeOrder = new Date(a.start_time).getTime() - new Date(b.start_time).getTime();
    if (startTimeOrder !== 0) return startTimeOrder;

    return a.id - b.id;
  });

const uniqueMatches = (items: EnrichedMatch[]) => {
  const byId = new Map<number, EnrichedMatch>();
  for (const match of items) {
    if (match?.id !== undefined && match?.id !== null) {
      byId.set(match.id, match);
    }
  }
  return Array.from(byId.values());
};

export function useMatches(params: FetchMatchesParams = {}): MatchesState {
  const { session } = useAuth();
  const [matches, setMatches] = useState<EnrichedMatch[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetchingNext, setIsFetchingNext] = useState(false);
  const [isFetchingPrevious, setIsFetchingPrevious] = useState(false);
  const [hasMoreNext, setHasMoreNext] = useState(true);
  const [hasMorePrevious, setHasMorePrevious] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const isLoadingPreviousRef = useRef(false);
  const lastPreviousLoadAtRef = useRef(0);

  // Serialize params so callbacks/effects only re-run when values actually change
  const paramsKey = JSON.stringify(params);

  /**
   * Builds a fully-qualified matches URL for the given cursor + direction.
   * When cursor is undefined the backend defaults to midnight of the current day.
   */
  const buildUrl = useCallback(
    (cursor?: string, direction: 'forward' | 'backward' = 'forward'): string | null => {
      const baseUrl = process.env.EXPO_PUBLIC_API_URL;
      if (!baseUrl) return null;

      const query = new URLSearchParams({ direction, limit: String(PAGE_SIZE) });
      if (cursor) query.set('cursor', cursor);

      const entries = Object.entries(params) as [string, boolean | number | undefined][];
      for (const [key, value] of entries) {
        if (value !== undefined) query.set(key, String(value));
      }

      return `${baseUrl}/matches/?${query.toString()}`;
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [paramsKey],
  );

  /** Fetches one page of matches and returns the array. Throws on HTTP errors. */
  const fetchPage = useCallback(
    async (cursor?: string, direction: 'forward' | 'backward' = 'forward'): Promise<EnrichedMatch[]> => {
      const url = buildUrl(cursor, direction);
      if (!url || !session?.access_token) return [];

      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${session.access_token}` },
      });

      if (!res.ok) {
        const text = await res.text().catch(() => '');
        throw new Error(text || `Request failed (${res.status})`);
      }

      const json = (await res.json()) as { matches?: EnrichedMatch[] } | EnrichedMatch[];
      // Backend wraps the list under a "matches" key; fall back to a bare array for safety
      const data = Array.isArray(json) ? json : (json as { matches?: EnrichedMatch[] }).matches ?? [];
      return Array.isArray(data) ? data : [];
    },
    [session?.access_token, buildUrl],
  );

  // Initial load — re-runs whenever the session token or filter params change
  useEffect(() => {
    let cancelled = false;

    if (!session?.access_token) {
      setMatches([]);
      setError(null);
      setIsLoading(false);
      return;
    }

    if (!process.env.EXPO_PUBLIC_API_URL) {
      setMatches([]);
      setError('Missing EXPO_PUBLIC_API_URL');
      setIsLoading(false);
      return;
    }

    // Reset pagination state on every fresh load
    setHasMoreNext(true);
    setHasMorePrevious(true);
    setIsLoading(true);
    setError(null);

    // No cursor → backend defaults to midnight of the current day (forward direction)
    fetchPage()
      .then((data) => {
        if (!cancelled && data.length > 0) {
          setMatches(sortMatches(uniqueMatches(data)));
          // If the page is smaller than the limit there is nothing further ahead
          setHasMoreNext(data.length >= PAGE_SIZE);
        }

        // If there are no matches today or later, seed the list with the closest older page.
        if (!cancelled && data.length === 0) {
          return fetchPage(undefined, 'backward').then((previousData) => {
            if (cancelled) return;
            setMatches(sortMatches(uniqueMatches(previousData)));
            setHasMorePrevious(previousData.length >= PAGE_SIZE);
            setHasMoreNext(previousData.length > 0);
          });
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setMatches([]);
          setError(e instanceof Error ? e.message : 'Unknown error');
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.access_token, paramsKey]);

  // Refresh game data in the background without showing the initial-load state again.
  useEffect(() => {
    if (!session?.access_token) return;

    let cancelled = false;

    const refresh = async () => {
      try {
        const data = await fetchPage();
        if (cancelled) return;

        setMatches((currentMatches) => {
          if (params.is_live) {
            const uniqueData = uniqueMatches(data);
            return JSON.stringify(currentMatches) === JSON.stringify(uniqueData) ? currentMatches : uniqueData;
          }

          const refreshedById = new Map(data.map((match) => [match.id, match]));
          const merged = currentMatches.map((match) => refreshedById.get(match.id) ?? match);
          const knownIds = new Set(currentMatches.map((match) => match.id));
          const newMatches = data.filter((match) => !knownIds.has(match.id));
          const nextMatches = sortMatches(uniqueMatches([...merged, ...newMatches]));

          return JSON.stringify(currentMatches) === JSON.stringify(nextMatches) ? currentMatches : nextMatches;
        });
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : 'Unknown error');
        }
      }
    };

    const intervalId = setInterval(refresh, REFRESH_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(intervalId);
    };
  }, [session?.access_token, fetchPage]);

  /**
   * Loads the next page of upcoming matches and appends them.
   * Uses the last known match as the forward cursor (+1 ms to exclude it from the response).
   */
  const loadNext = useCallback(async () => {
    if (isFetchingNext || !hasMoreNext || matches.length === 0 || !session?.access_token) return;

    // +1 ms ensures the backend's >= does not re-fetch the last already-shown match
    const nonLiveMatches = matches.filter((match) => !isLiveMatch(match));
    const lastMatch = nonLiveMatches[nonLiveMatches.length - 1] ?? matches[matches.length - 1];
    const cursorMs = new Date(lastMatch.start_time).getTime() + 1;
    const cursor = new Date(cursorMs).toISOString();

    setIsFetchingNext(true);
    try {
      const newMatches = await fetchPage(cursor, 'forward');
      setHasMoreNext(newMatches.length >= PAGE_SIZE);
      setMatches((prev) => sortMatches(uniqueMatches([...prev, ...newMatches])));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setIsFetchingNext(false);
    }
  }, [isFetchingNext, hasMoreNext, matches, session?.access_token, fetchPage]);

  /**
   * Loads the previous page of past matches and prepends them.
   * Uses the first known match as the backward cursor (exclusive — backend uses <).
   */
  const loadPrevious = useCallback(async () => {
    if (
      isLoadingPreviousRef.current ||
      Date.now() - lastPreviousLoadAtRef.current < PREVIOUS_LOAD_COOLDOWN_MS ||
      isFetchingPrevious ||
      !hasMorePrevious ||
      matches.length === 0 ||
      !session?.access_token
    ) return;

    isLoadingPreviousRef.current = true;
    lastPreviousLoadAtRef.current = Date.now();

    // The backend uses strict < for backward direction so this cursor value is excluded
    const nonLiveMatches = matches.filter((match) => !isLiveMatch(match));
    const firstMatch = nonLiveMatches[0] ?? matches[0];
    const cursor = firstMatch.start_time;

    setIsFetchingPrevious(true);
    try {
      const newMatches = await fetchPage(cursor, 'backward');
      setHasMorePrevious(newMatches.length >= PAGE_SIZE);
      setMatches((prev) => sortMatches(uniqueMatches([...newMatches, ...prev])));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      isLoadingPreviousRef.current = false;
      setIsFetchingPrevious(false);
    }
  }, [isFetchingPrevious, hasMorePrevious, matches, session?.access_token, fetchPage]);

  return {
    matches,
    isLoading,
    isFetchingNext,
    isFetchingPrevious,
    hasMoreNext,
    hasMorePrevious,
    error,
    loadNext,
    loadPrevious,
  };
}
