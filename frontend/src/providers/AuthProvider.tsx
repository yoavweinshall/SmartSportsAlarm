import type { Session } from '@supabase/supabase-js';
import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

import { supabase } from '@/lib/supabase';
import type { Profile } from '@/types/models';

type AuthContextValue = {
  session: Session | null;
  profile: Profile | null;
  isLoading: boolean;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error('useAuth must be used within <AuthProvider>');
  return value;
}

async function loadProfile(userId: string): Promise<Profile | null> {
  const { data, error } = await supabase
    .from('profiles')
    .select('*')
    .eq('id', userId)
    .single();

  if (error) {
    console.warn('[AuthProvider] Failed to load profile:', error.message);
    return null;
  }

  return (data as Profile) ?? null;
}

export function AuthProvider({ children }: React.PropsWithChildren) {
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const sync = async (nextSession: Session | null) => {
      setSession(nextSession);
      if (!nextSession?.user?.id) {
        setProfile(null);
        return;
      }

      const nextProfile = await loadProfile(nextSession.user.id);
      if (!cancelled) setProfile(nextProfile);
    };

    supabase.auth.getSession().then(({ data }) => {
      if (cancelled) return;
      sync(data.session ?? null).finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    });

    const { data } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      if (cancelled) return;
      sync(nextSession ?? null);
    });

    return () => {
      cancelled = true;
      data.subscription.unsubscribe();
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ session, profile, isLoading }),
    [session, profile, isLoading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
