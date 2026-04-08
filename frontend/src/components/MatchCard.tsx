import FontAwesome from '@expo/vector-icons/FontAwesome';
import { Pressable, Text, View } from 'react-native';

import type { Match, Team } from '@/types/models';

type Props = {
  match: Match;
  homeTeam: Team | undefined;
  awayTeam: Team | undefined;
  competitionLabel: string | null;
  following: boolean;
  onToggleFollow: () => void;
};

export function MatchCard({
  match,
  homeTeam,
  awayTeam,
  competitionLabel,
  following,
  onToggleFollow,
}: Props) {
  const climax = match.notified;

  return (
    <View
      className={`mb-3 rounded-2xl border-2 p-4 ${
        climax
          ? 'border-red-500 bg-red-50 shadow-lg shadow-red-500/40 dark:border-red-400 dark:bg-red-950/40'
          : 'border-neutral-200 bg-white dark:border-neutral-700 dark:bg-neutral-900'
      }`}>
      {climax && (
        <View className="mb-2 flex-row items-center gap-2">
          <FontAwesome name="bell" size={16} color="#dc2626" />
          <Text className="text-sm font-bold uppercase tracking-wide text-red-600 dark:text-red-400">
            Climax — Smart alarm
          </Text>
        </View>
      )}

      {competitionLabel ? (
        <Text className="mb-2 text-xs font-medium text-neutral-500 dark:text-neutral-400">
          {competitionLabel}
        </Text>
      ) : null}

      <View className="flex-row items-center justify-between">
        <View className="flex-1 flex-row items-center justify-between pr-2">
          <Text
            className="flex-1 text-base font-semibold text-neutral-900 dark:text-neutral-100"
            numberOfLines={1}>
            {homeTeam?.name ?? `Team #${match.home_team_id}`}
          </Text>
          <Text className="ml-2 text-xl font-bold text-neutral-900 dark:text-white">
            {match.home_score}
          </Text>
        </View>
        <Text className="mx-2 text-neutral-400">—</Text>
        <View className="flex-1 flex-row items-center justify-between pl-2">
          <Text
            className="flex-1 text-right text-base font-semibold text-neutral-900 dark:text-neutral-100"
            numberOfLines={1}>
            {awayTeam?.name ?? `Team #${match.away_team_id}`}
          </Text>
          <Text className="ml-2 text-xl font-bold text-neutral-900 dark:text-white">
            {match.away_score}
          </Text>
        </View>
      </View>

      <View className="mt-3 flex-row items-center justify-between">
        <View>
          <Text className="text-sm text-neutral-600 dark:text-neutral-300">
            {match.match_stage ?? 'Live'} · {match.game_time ?? '—'}
          </Text>
        </View>
        <Pressable
          onPress={onToggleFollow}
          className={`rounded-full px-4 py-2 ${
            following
              ? 'bg-blue-100 dark:bg-neutral-700'
              : 'bg-neutral-200 dark:bg-neutral-600'
          }`}
          accessibilityRole="button"
          accessibilityLabel={following ? 'Unfollow match' : 'Follow match'}>
          <Text
            className={`text-sm font-semibold ${
              following ? 'text-blue-700 dark:text-blue-300' : 'text-neutral-800 dark:text-neutral-100'
            }`}>
            {following ? 'Following' : 'Follow'}
          </Text>
        </Pressable>
      </View>
    </View>
  );
}
