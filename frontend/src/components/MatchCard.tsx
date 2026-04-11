import { View, Text, StyleSheet, Pressable, ActivityIndicator } from 'react-native';
import type { EnrichedMatch } from '@/types/models';
import { useMemo, useState } from 'react';
import { useFollow } from '@/providers/FollowProvider';

interface MatchCardProps {
  match: EnrichedMatch;
}

const formatDateTime = (startTimeStr: string): string => {
  if (!startTimeStr) return '';
  const dateObj = new Date(startTimeStr);
  
  const datePart = dateObj.toLocaleDateString(undefined, { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
  const timePart = dateObj.toLocaleTimeString(undefined, { 
    hour: '2-digit', 
    minute: '2-digit' 
  });

  return `${datePart} • ${timePart}`;
};

export function MatchCard({ match }: MatchCardProps) {
  const { followedIds, toggleFollow } = useFollow();
  const isFollowed = followedIds.has(match.id);
  const [isActionLoading, setIsActionLoading] = useState(false);

  const dateTimeString = useMemo(() => {
    return formatDateTime(match.start_time);
  }, [match.start_time]);

  const handleFollowPress = async () => {
    if (isActionLoading) return;
    setIsActionLoading(true);
    await toggleFollow(match.id);
    setIsActionLoading(false);
  };

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.competitionText}>{match.competition.name}</Text>
      </View>

      <View style={styles.scoreRow}>
        <View style={styles.teamInfo}>
          <Text style={styles.teamNameText} numberOfLines={1}>{match.home_team.name}</Text>
        </View>
        
        <View style={styles.scoreboard}>
          <Text style={styles.scoreValue}>{match.home_score}</Text>
          <Text style={styles.scoreDivider}>—</Text>
          <Text style={styles.scoreValue}>{match.away_score}</Text>
        </View>

        <View style={styles.teamInfo}>
          <Text style={styles.teamNameText} numberOfLines={1}>{match.away_team.name}</Text>
        </View>
      </View>

      <View style={styles.statusRow}>
        <Text style={styles.matchStatus}>
          {match.status} {dateTimeString ? `• ${dateTimeString}` : ''}
        </Text>

        <Pressable 
          style={[styles.followButton, isFollowed && styles.followedButton]}
          onPress={handleFollowPress}
          disabled={isActionLoading}
        >
          {isActionLoading ? (
            <ActivityIndicator size="small" color={isFollowed ? "#fff" : "#333"} />
          ) : (
            <Text style={[styles.followButtonText, isFollowed && styles.followedButtonText]}>
              {isFollowed ? 'Following' : 'Follow'}
            </Text>
          )}
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    elevation: 2, 
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
  },
  header: {
    marginBottom: 12,
  },
  competitionText: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
  },
  scoreRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  teamInfo: {
    flex: 1,
    alignItems: 'center',
  },
  teamNameText: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
    textAlign: 'center',
  },
  scoreboard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    paddingVertical: 6,
    paddingHorizontal: 12,
    marginHorizontal: 8,
  },
  scoreValue: {
    fontSize: 18,
    color: '#333',
    fontWeight: '700',
  },
  scoreDivider: {
    fontSize: 14,
    color: '#ccc',
    paddingHorizontal: 8,
    fontWeight: '500',
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  matchStatus: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
    flex: 1,
    marginRight: 8,
  },
  followButton: {
    backgroundColor: '#eee',
    borderRadius: 20,
    paddingVertical: 8,
    paddingHorizontal: 18,
    minWidth: 80,
    alignItems: 'center',
    justifyContent: 'center',
  },
  followedButton: {
    backgroundColor: '#ccc',
  },
  followButtonText: {
    fontSize: 14,
    color: '#333',
    fontWeight: '600',
  },
  followedButtonText: {
    color: '#fff',
  }
});
