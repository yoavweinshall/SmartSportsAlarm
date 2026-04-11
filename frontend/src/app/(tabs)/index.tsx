import { ActivityIndicator, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { GroupedMatchesList } from '@/components/GroupedMatchesList';
import { useMatches } from '@/hooks/useMatches';

/**
 * Live scores tab — route file (no separate screens/ layer).
 */
export default function LiveTabScreen() {
  const { matches, isLoading, isFetchingPrevious, hasMorePrevious, error, loadNext, loadPrevious } =
    useMatches({ is_live: true });

  return (
    <SafeAreaView className="flex-1 bg-neutral-100 dark:bg-black" edges={['top']}>
      <View className="border-b border-neutral-200 bg-white px-4 py-4 dark:border-neutral-800 dark:bg-neutral-950">
        <Text className="text-2xl font-bold text-neutral-900 dark:text-white">Live scores</Text>
        <Text className="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
          {error ? `Error: ${error}` : 'Live matches from backend'}
        </Text>
      </View>
      {isLoading ? (
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
          <ActivityIndicator />
        </View>
      ) : (
        <GroupedMatchesList
          matches={matches}
          isFetchingPrevious={isFetchingPrevious}
          hasMorePrevious={hasMorePrevious}
          loadNext={loadNext}
          loadPrevious={loadPrevious}
        />
      )}
    </SafeAreaView>
  );
}
