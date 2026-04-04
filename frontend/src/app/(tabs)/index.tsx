import { FlatList, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { MatchCard } from '@/components/MatchCard';
import {
  competitionNameById,
  mockCompetitions,
  mockMatches,
  mockTeams,
  teamMapById,
} from '@/constants/mockData';
import { useFollowedMatches } from '@/hooks/useFollowedMatches';

/**
 * Live scores tab — route file (no separate screens/ layer).
 */
export default function LiveTabScreen() {
  const teamsById = teamMapById(mockTeams);
  const { toggle, isFollowing } = useFollowedMatches();

  return (
    <SafeAreaView className="flex-1 bg-neutral-100 dark:bg-black" edges={['top']}>
      <View className="border-b border-neutral-200 bg-white px-4 py-4 dark:border-neutral-800 dark:bg-neutral-950">
        <Text className="text-2xl font-bold text-neutral-900 dark:text-white">Live scores</Text>
        <Text className="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
          Mock data — backend wiring comes next
        </Text>
      </View>
      <FlatList
        data={mockMatches}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={{ paddingHorizontal: 16, paddingBottom: 32, paddingTop: 8 }}
        renderItem={({ item }) => (
          <MatchCard
            match={item}
            homeTeam={item.home_team_id != null ? teamsById.get(item.home_team_id) : undefined}
            awayTeam={item.away_team_id != null ? teamsById.get(item.away_team_id) : undefined}
            competitionLabel={competitionNameById(mockCompetitions, item.competition_id)}
            following={isFollowing(item.id)}
            onToggleFollow={() => toggle(item.id)}
          />
        )}
      />
    </SafeAreaView>
  );
}
