import { useCallback, useMemo } from 'react';
import {
  ActivityIndicator,
  NativeScrollEvent,
  NativeSyntheticEvent,
  SectionList,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import type { EnrichedMatch } from '@/types/models';
import { MatchCard } from './MatchCard';

interface GroupedMatchesListProps {
  matches: EnrichedMatch[];
  isFetchingPrevious: boolean;
  hasMorePrevious: boolean;
  loadNext: () => void;
  loadPrevious: () => void;
}

interface CompetitionGroup {
  name: string;
  matches: EnrichedMatch[];
}

interface DateGroup {
  dateLabel: string;
  dateValue: number;
  competitions: CompetitionGroup[];
}

// SectionList requires { title, data } shape; title carries full DateGroup metadata
type Section = { title: DateGroup; data: CompetitionGroup[] };

function groupMatches(matches: EnrichedMatch[]): Section[] {
  const byDate = new Map<string, Map<string, EnrichedMatch[]>>();
  const dateTsMap = new Map<string, number>();

  for (const match of matches) {
    const d = new Date(match.start_time);
    const label = d.toLocaleDateString(undefined, {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });

    if (!byDate.has(label)) {
      byDate.set(label, new Map());
      // Normalise to midnight so sorting is stable regardless of match time
      dateTsMap.set(label, new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime());
    }

    const byCompetition = byDate.get(label)!;
    const competitionName = match.competition.name;

    if (!byCompetition.has(competitionName)) {
      byCompetition.set(competitionName, []);
    }
    byCompetition.get(competitionName)!.push(match);
  }

  return Array.from(byDate.entries())
    .sort(([labelA], [labelB]) => dateTsMap.get(labelA)! - dateTsMap.get(labelB)!)
    .map(([label, competitionMap]) => {
      const dateGroup: DateGroup = {
        dateLabel: label,
        dateValue: dateTsMap.get(label)!,
        competitions: Array.from(competitionMap.entries()).map(([name, ms]) => ({
          name,
          matches: ms,
        })),
      };
      return { title: dateGroup, data: dateGroup.competitions };
    });
}

export function GroupedMatchesList({
  matches,
  isFetchingPrevious,
  hasMorePrevious,
  loadNext,
  loadPrevious,
}: GroupedMatchesListProps) {
  const sections = useMemo(() => groupMatches(matches), [matches]);

  /**
   * Trigger loadPrevious when the user scrolls to the very top of the list.
   * This replaces pull-to-refresh with a natural upward infinite-scroll gesture.
   */
  const handleScroll = useCallback(
    (event: NativeSyntheticEvent<NativeScrollEvent>) => {
      if (event.nativeEvent.contentOffset.y <= 0 && !isFetchingPrevious && hasMorePrevious) {
        loadPrevious();
      }
    },
    [isFetchingPrevious, hasMorePrevious, loadPrevious],
  );

  return (
    <SectionList
      sections={sections}
      contentContainerStyle={[styles.scrollContent, sections.length === 0 && styles.emptyContent]}
      showsVerticalScrollIndicator={false}
      // Prevent the list from jumping down when past matches are prepended at the top
      maintainVisibleContentPosition={{ minIndexForVisible: 0 }}
      // Fire scroll events frequently enough to catch y === 0 reliably on iOS
      scrollEventThrottle={16}
      onScroll={handleScroll}
      // Reaching the bottom loads the next page of upcoming matches
      onEndReached={loadNext}
      onEndReachedThreshold={0.5}
      // Show a spinner at the top while past matches are being fetched
      ListHeaderComponent={
        isFetchingPrevious ? (
          <View style={styles.headerLoader}>
            <ActivityIndicator size="small" color="#4f8ef7" />
          </View>
        ) : null
      }
      ListEmptyComponent={
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>No matches found</Text>
        </View>
      }
      ListFooterComponent={<View style={styles.footerSpacer} />}
      keyExtractor={(item, index) => `${item.name}-${index}`}
      renderSectionHeader={({ section }) => (
        <View style={styles.dateHeaderContainer}>
          <Text style={styles.dateHeaderText}>{section.title.dateLabel}</Text>
        </View>
      )}
      renderItem={({ item: compGroup }) => (
        <View style={styles.competitionBlock}>
          <View style={styles.competitionHeaderContainer}>
            <View style={styles.competitionDot} />
            <Text style={styles.competitionHeaderText}>{compGroup.name}</Text>
          </View>
          {compGroup.matches.map((match) => (
            <MatchCard key={match.id} match={match} />
          ))}
        </View>
      )}
    />
  );
}

const styles = StyleSheet.create({
  scrollContent: {
    paddingHorizontal: 16,
    paddingBottom: 32,
    paddingTop: 8,
  },
  emptyContent: {
    flex: 1,
  },
  emptyContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 32,
  },
  emptyText: {
    fontSize: 15,
    color: '#888',
    textAlign: 'center',
  },
  headerLoader: {
    paddingVertical: 12,
    alignItems: 'center',
  },
  footerSpacer: {
    paddingVertical: 8,
  },
  dateHeaderContainer: {
    backgroundColor: '#1a1a2e',
    borderRadius: 10,
    paddingVertical: 10,
    paddingHorizontal: 16,
    marginTop: 16,
    marginBottom: 8,
    alignItems: 'center',
  },
  dateHeaderText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#fff',
    letterSpacing: 0.5,
    textTransform: 'uppercase',
  },
  competitionBlock: {
    marginBottom: 4,
  },
  competitionHeaderContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 4,
    marginBottom: 4,
  },
  competitionDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#4f8ef7',
    marginRight: 8,
  },
  competitionHeaderText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#444',
    textTransform: 'uppercase',
    letterSpacing: 0.4,
  },
});
