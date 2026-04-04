import { useCallback, useState } from 'react';

/**
 * Local follow state per match id (replace with API later).
 */
export function useFollowedMatches() {
  const [followedIds, setFollowedIds] = useState<Set<number>>(new Set());

  const toggle = useCallback((matchId: number) => {
    setFollowedIds((prev) => {
      const next = new Set(prev);
      if (next.has(matchId)) {
        next.delete(matchId);
      } else {
        next.add(matchId);
      }
      return next;
    });
  }, []);

  const isFollowing = useCallback(
    (matchId: number) => followedIds.has(matchId),
    [followedIds]
  );

  return { toggle, isFollowing };
}
