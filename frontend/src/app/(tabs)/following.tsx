import { ActivityIndicator, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { GroupedMatchesList } from '@/components/GroupedMatchesList';
import { useMatches } from '@/hooks/useMatches';

/**
 * Followed matches tab — shows only the matches the user is following,
 * sorted chronologically by start time (earliest first).
 */
export default function FollowingTabScreen() {
  const { matches, isLoading, isFetchingPrevious, hasMorePrevious, error, loadNext, loadPrevious } =
    useMatches({ followed_only: true });

  // Backend already returns matches ordered by start_time; sort locally to be safe
  const sorted = [...matches].sort(
    (a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime(),
  );

  return (
    <SafeAreaView className="flex-1 bg-neutral-100 dark:bg-black" edges={['top']}>
      <View className="border-b border-neutral-200 bg-white px-4 py-4 dark:border-neutral-800 dark:bg-neutral-950">
        <Text className="text-2xl font-bold text-neutral-900 dark:text-white">Following</Text>
        <Text className="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
          {error ? `Error: ${error}` : 'Matches you are following'}
        </Text>
      </View>

      {isLoading ? (
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
          <ActivityIndicator />
        </View>
      ) : (
        <GroupedMatchesList
          matches={sorted}
          isFetchingPrevious={isFetchingPrevious}
          hasMorePrevious={hasMorePrevious}
          loadNext={loadNext}
          loadPrevious={loadPrevious}
        />
      )}
    </SafeAreaView>
  );
}
