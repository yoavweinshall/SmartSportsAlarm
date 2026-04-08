-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.competitions (
  id integer NOT NULL DEFAULT nextval('competitions_id_seq'::regclass),
  external_api_id text NOT NULL UNIQUE,
  country_id integer,
  sport_id integer,
  parent_id integer,
  name text NOT NULL,
  name_for_url text UNIQUE,
  color character varying,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT competitions_pkey PRIMARY KEY (id),
  CONSTRAINT competitions_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.countries(id),
  CONSTRAINT competitions_sport_id_fkey FOREIGN KEY (sport_id) REFERENCES public.sports(id),
  CONSTRAINT competitions_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.competitions(id)
);
CREATE TABLE public.countries (
  id integer NOT NULL DEFAULT nextval('countries_id_seq'::regclass),
  external_api_id text NOT NULL UNIQUE,
  name text NOT NULL,
  name_for_url text UNIQUE,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT countries_pkey PRIMARY KEY (id)
);
CREATE TABLE public.matches (
  id integer NOT NULL DEFAULT nextval('matches_id_seq'::regclass),
  external_api_id integer NOT NULL UNIQUE,
  competition_id integer,
  home_team_id integer,
  away_team_id integer,
  start_time timestamp with time zone NOT NULL,
  stage_group integer NOT NULL,
  match_stage text,
  game_time text,
  home_score integer DEFAULT 0,
  away_score integer DEFAULT 0,
  metadata jsonb DEFAULT '{}'::jsonb,
  updated_at timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone DEFAULT now(),
  notified boolean DEFAULT false,
  CONSTRAINT matches_pkey PRIMARY KEY (id),
  CONSTRAINT matches_competition_id_fkey FOREIGN KEY (competition_id) REFERENCES public.competitions(id),
  CONSTRAINT matches_home_team_id_fkey FOREIGN KEY (home_team_id) REFERENCES public.teams(id),
  CONSTRAINT matches_away_team_id_fkey FOREIGN KEY (away_team_id) REFERENCES public.teams(id)
);
CREATE TABLE public.profiles (
  id uuid NOT NULL,
  username text NOT NULL UNIQUE,
  push_token text,
  timezone text DEFAULT 'Asia/Jerusalem'::text,
  is_enabled boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT profiles_pkey PRIMARY KEY (id),
  CONSTRAINT profiles_id_fkey FOREIGN KEY (id) REFERENCES auth.users(id)
);
CREATE TABLE public.sports (
  id integer NOT NULL DEFAULT nextval('sports_id_seq'::regclass),
  external_api_id text NOT NULL UNIQUE,
  name text NOT NULL,
  name_for_url text UNIQUE,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT sports_pkey PRIMARY KEY (id)
);
CREATE TABLE public.team_competitions (
  team_id integer NOT NULL,
  competition_id integer NOT NULL,
  CONSTRAINT team_competitions_pkey PRIMARY KEY (team_id, competition_id),
  CONSTRAINT team_competitions_competition_id_fkey FOREIGN KEY (competition_id) REFERENCES public.competitions(id),
  CONSTRAINT team_competitions_team_id_fkey FOREIGN KEY (team_id) REFERENCES public.teams(id)
);
CREATE TABLE public.teams (
  id integer NOT NULL DEFAULT nextval('teams_id_seq'::regclass),
  external_api_id text NOT NULL UNIQUE,
  sport_id integer,
  country_id integer,
  name text NOT NULL,
  short_name text,
  symbolic_name character varying,
  name_for_url text,
  primary_color character varying,
  secondary_color character varying,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT teams_pkey PRIMARY KEY (id),
  CONSTRAINT teams_sport_id_fkey FOREIGN KEY (sport_id) REFERENCES public.sports(id),
  CONSTRAINT teams_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.countries(id)
);
CREATE TABLE public.user_followed_matches (
  user_id uuid NOT NULL,
  match_id integer NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_followed_matches_pkey PRIMARY KEY (user_id, match_id),
  CONSTRAINT user_followed_matches_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(id),
  CONSTRAINT user_followed_matches_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.matches(id)
);