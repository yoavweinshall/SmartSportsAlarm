import React from 'react';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import { Link, Tabs } from 'expo-router';
import { ActivityIndicator, Pressable, View } from 'react-native';

import Colors from '@/constants/Colors';
import { useColorScheme } from '@/components/useColorScheme';
import { useClientOnlyValue } from '@/components/useClientOnlyValue';
import { useAuth } from '@/providers/AuthProvider';

function TabBarIcon(props: {
  name: React.ComponentProps<typeof FontAwesome>['name'];
  color: string;
}) {
  return <FontAwesome size={28} style={{ marginBottom: -3 }} {...props} />;
}

export default function TabLayout() {
  const colorScheme = useColorScheme();
  const { session, isLoading } = useAuth();

  // Call ALL hooks unconditionally before any early return.
  // useClientOnlyValue uses useState + useEffect internally (native version),
  // so it MUST be called on every render regardless of auth state.
  const headerShown = useClientOnlyValue(false, true);

  // #region agent log
  console.log('[DEBUG][H-I] TabLayout — isLoading:', isLoading, 'hasSession:', !!session, 'headerShown:', headerShown);
  fetch('http://127.0.0.1:7390/ingest/0ca4486e-1b32-4202-ad02-57ca54191351',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'89800c'},body:JSON.stringify({sessionId:'89800c',runId:'fix-hooks',location:'(tabs)/_layout.tsx:render',message:'TabLayout rendered',data:{isLoading,hasSession:!!session,headerShown},timestamp:Date.now()})}).catch(()=>{});
  // #endregion

  // #region agent log
  console.log('[DEBUG][f1cbd7][T1] TabLayout hooks executed', {
    isLoading,
    hasSession: !!session,
  });
  // #endregion

  if (isLoading) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
        <ActivityIndicator />
      </View>
    );
  }

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: Colors[colorScheme ?? 'light'].tint,
        headerShown,
      }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Live',
          tabBarIcon: ({ color }) => <TabBarIcon name="bolt" color={color} />,
          headerRight: () => (
            <Link href="/modal" asChild>
              <Pressable>
                {({ pressed }) => (
                  <FontAwesome
                    name="info-circle"
                    size={25}
                    color={Colors[colorScheme ?? 'light'].text}
                    style={{ marginRight: 15, opacity: pressed ? 0.5 : 1 }}
                  />
                )}
              </Pressable>
            </Link>
          ),
        }}
      />
    </Tabs>
  );
}
