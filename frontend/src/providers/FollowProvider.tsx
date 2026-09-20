import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import { useAuth } from '@/providers/AuthProvider';
import type { EnrichedMatch } from '@/types/models';

type FollowContextValue = {
  followedIds: Set<number>;
  toggleFollow: (matchId: number) => Promise<void>;
};

const FollowContext = createContext<FollowContextValue | undefined>(undefined);

export function useFollow(): FollowContextValue {
  const value = useContext(FollowContext);
  if (!value) throw new Error('useFollow must be used within <FollowProvider>');
  return value;
}

export function FollowProvider({ children }: React.PropsWithChildren) {
  const { session } = useAuth();
  const [followedIds, setFollowedIds] = useState<Set<number>>(new Set());

  // Fetch the full list of followed match IDs when the session becomes available
  useEffect(() => {
    if (!session?.access_token) {
      setFollowedIds(new Set());
      return;
    }

    let cancelled = false;
    const baseUrl = process.env.EXPO_PUBLIC_API_URL;

    if (!baseUrl) {
      return () => {
        cancelled = true;
      };
    }

    async function fetchFollowed() {
      try {
        const res = await fetch(`${baseUrl}/matches/?followed_only=true`, {
          headers: { Authorization: `Bearer ${session!.access_token}` },
        });

        if (!res.ok) return;

        const json = (await res.json()) as { matches?: EnrichedMatch[] } | EnrichedMatch[];
        const data: EnrichedMatch[] = Array.isArray(json)
          ? json
          : (json as { matches?: EnrichedMatch[] }).matches ?? [];

        if (!cancelled) {
          setFollowedIds(new Set(data.map((m) => m.id)));
        }
      } catch (e) {
        console.error('[FollowProvider] Failed to fetch followed matches:', e);
      }
    }

    fetchFollowed();
    return () => {
      cancelled = true;
    };
  }, [session?.access_token]);

  const toggleFollow = useCallback(
    async (matchId: number) => {
      if (!session?.access_token) return;

      const wasFollowed = followedIds.has(matchId);

      // Optimistic update — flip the ID in the set immediately
      setFollowedIds((prev) => {
        const next = new Set(prev);
        if (wasFollowed) {
          next.delete(matchId);
        } else {
          next.add(matchId);
        }
        return next;
      });

      try {
        const baseUrl = process.env.EXPO_PUBLIC_API_URL;
        if (!baseUrl) {
          throw new Error('Missing EXPO_PUBLIC_API_URL');
        }
        const res = await fetch(`${baseUrl}/matches/${matchId}/follow`, {
          method: wasFollowed ? 'DELETE' : 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${session.access_token}`,
          },
        });

        if (!res.ok) {
          // Revert the optimistic update on failure
          setFollowedIds((prev) => {
            const next = new Set(prev);
            if (wasFollowed) {
              next.add(matchId);
            } else {
              next.delete(matchId);
            }
            return next;
          });
        }
      } catch (e) {
        console.error('[FollowProvider] toggleFollow error:', e);
        // Revert the optimistic update on network error
        setFollowedIds((prev) => {
          const next = new Set(prev);
          if (wasFollowed) {
            next.add(matchId);
          } else {
            next.delete(matchId);
          }
          return next;
        });
      }
    },
    [followedIds, session?.access_token],
  );

  const value = useMemo<FollowContextValue>(
    () => ({ followedIds, toggleFollow }),
    [followedIds, toggleFollow],
  );

  return <FollowContext.Provider value={value}>{children}</FollowContext.Provider>;
}
