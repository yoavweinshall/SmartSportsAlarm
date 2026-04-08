import type { Competition, Match, Team } from '@/types/models';

export const mockCompetitions: Competition[] = [
  {
    id: 101,
    external_api_id: 'nba-001',
    country_id: 18,
    sport_id: 2,
    parent_id: null,
    name: 'NBA',
    name_for_url: 'nba',
    color: '#006BB7',
    metadata: {},
    created_at: '2026-01-01T00:00:00.000Z',
  },
  {
    id: 102,
    external_api_id: 'eurocup-001',
    country_id: 19,
    sport_id: 2,
    parent_id: null,
    name: 'Eurocup',
    name_for_url: 'eurocup',
    color: '#0072CE',
    metadata: {},
    created_at: '2026-01-01T00:00:00.000Z',
  },
];

export const mockTeams: Team[] = [
  {
    id: 1,
    external_api_id: 'team-lakers',
    sport_id: 2,
    country_id: 18,
    name: 'Los Angeles Lakers',
    short_name: 'Lakers',
    symbolic_name: 'LAL',
    name_for_url: 'lakers',
    primary_color: '#552583',
    secondary_color: '#FDB927',
    metadata: {},
    created_at: '2026-01-01T00:00:00.000Z',
  },
  {
    id: 2,
    external_api_id: 'team-celtics',
    sport_id: 2,
    country_id: 18,
    name: 'Boston Celtics',
    short_name: 'Celtics',
    symbolic_name: 'BOS',
    name_for_url: 'celtics',
    primary_color: '#007A33',
    secondary_color: '#BA9653',
    metadata: {},
    created_at: '2026-01-01T00:00:00.000Z',
  },
  {
    id: 3,
    external_api_id: 'team-maccabi',
    sport_id: 2,
    country_id: 6,
    name: 'Maccabi Tel Aviv',
    short_name: 'Maccabi',
    symbolic_name: 'MTA',
    name_for_url: 'maccabi-tel-aviv',
    primary_color: '#005EB8',
    secondary_color: '#FFD200',
    metadata: {},
    created_at: '2026-01-01T00:00:00.000Z',
  },
  {
    id: 4,
    external_api_id: 'team-partizan',
    sport_id: 2,
    country_id: 85,
    name: 'Partizan Belgrade',
    short_name: 'Partizan',
    symbolic_name: 'PAR',
    name_for_url: 'partizan',
    primary_color: '#000000',
    secondary_color: '#FFFFFF',
    metadata: {},
    created_at: '2026-01-01T00:00:00.000Z',
  },
];

export const mockMatches: Match[] = [
  {
    id: 1001,
    external_api_id: 4606736,
    competition_id: 101,
    home_team_id: 1,
    away_team_id: 2,
    start_time: '2026-03-17T19:00:00.000Z',
    stage_group: 3,
    match_stage: 'Q4',
    game_time: '01:42',
    home_score: 102,
    away_score: 99,
    metadata: {},
    updated_at: '2026-03-17T21:00:00.000Z',
    created_at: '2026-03-17T18:00:00.000Z',
    notified: true,
  },
  {
    id: 1002,
    external_api_id: 4686372,
    competition_id: 102,
    home_team_id: 3,
    away_team_id: 4,
    start_time: '2026-03-17T18:00:00.000Z',
    stage_group: 3,
    match_stage: 'Q3',
    game_time: '05:03',
    home_score: 49,
    away_score: 42,
    metadata: {},
    updated_at: '2026-03-17T19:30:00.000Z',
    created_at: '2026-03-17T17:00:00.000Z',
    notified: false,
  },
  {
    id: 1003,
    external_api_id: 4606730,
    competition_id: 101,
    home_team_id: 2,
    away_team_id: 1,
    start_time: '2026-03-17T20:30:00.000Z',
    stage_group: 3,
    match_stage: 'Q4',
    game_time: '00:45',
    home_score: 88,
    away_score: 87,
    metadata: {},
    updated_at: '2026-03-17T21:45:00.000Z',
    created_at: '2026-03-17T18:00:00.000Z',
    notified: true,
  },
];

export function teamMapById(teams: Team[]): Map<number, Team> {
  return new Map(teams.map((t) => [t.id, t]));
}

export function competitionNameById(
  competitions: Competition[],
  id: number | null
): string | null {
  if (id == null) return null;
  return competitions.find((c) => c.id === id)?.name ?? null;
}
