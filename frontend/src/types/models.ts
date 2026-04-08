/**
 * Mirrors `backend/app/schemas/schema.sql` — matches, teams, competitions, profiles.
 */

export interface Profile {
  id: string;
  username: string;
  push_token: string | null;
  timezone: string;
  is_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface Competition {
  id: number;
  external_api_id: string;
  country_id: number | null;
  sport_id: number | null;
  parent_id: number | null;
  name: string;
  name_for_url: string | null;
  color: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface Team {
  id: number;
  external_api_id: string;
  sport_id: number | null;
  country_id: number | null;
  name: string;
  short_name: string | null;
  symbolic_name: string | null;
  name_for_url: string | null;
  primary_color: string | null;
  secondary_color: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface Match {
  id: number;
  external_api_id: number;
  competition_id: number | null;
  home_team_id: number | null;
  away_team_id: number | null;
  start_time: string;
  stage_group: number;
  match_stage: string | null;
  game_time: string | null;
  home_score: number;
  away_score: number;
  metadata: Record<string, unknown>;
  updated_at: string | null;
  created_at: string | null;
  notified: boolean;
}
