import FontAwesome from '@expo/vector-icons/FontAwesome';
import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { useFonts } from 'expo-font';
import { Stack, useRouter, usePathname, useRootNavigationState } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';
import 'react-native-reanimated';

import '../../global.css';

import { useColorScheme } from '@/components/useColorScheme';
import { AuthProvider, useAuth } from '@/providers/AuthProvider';
import { FollowProvider } from '@/providers/FollowProvider';

export {
  ErrorBoundary,
} from 'expo-router';

export const unstable_settings = {
  initialRouteName: 'login',
};

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded, error] = useFonts({
    SpaceMono: require('../assets/fonts/SpaceMono-Regular.ttf'),
    ...FontAwesome.font,
  });

  useEffect(() => {
    if (error) throw error;
  }, [error]);

  useEffect(() => {
    if (loaded) SplashScreen.hideAsync();
  }, [loaded]);

  if (!loaded) return null;

  return (
    <AuthProvider>
      <FollowProvider>
        <RootLayoutNav />
      </FollowProvider>
    </AuthProvider>
  );
}

function RootLayoutNav() {
  const colorScheme = useColorScheme();
  const { session, isLoading } = useAuth();
  const pathname = usePathname();
  const rootNavState = useRootNavigationState();
  const router = useRouter();
  useEffect(() => {
    // Ensure the navigation tree is mounted before calling router.
    if (!rootNavState?.key) return;
    if (isLoading) return;

    const onAuthRoute = pathname === '/login' || pathname === '/signup';

    if (!session && !onAuthRoute) {
      router.replace('/login');
      return;
    }

    if (session && onAuthRoute) {
      router.replace('/');
    }
  }, [isLoading, pathname, rootNavState?.key, session]);

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      {/*
       * AuthProvider wraps the Stack so every screen can call useAuth().
       * useSegments and useRouter inside AuthProvider work because Expo Router
       * exposes its navigation context at the framework level — independently
       * of where <Stack> sits in the React tree.
       */}
      <Stack>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="login" options={{ headerShown: false }} />
        <Stack.Screen name="signup" options={{ headerShown: false }} />
        <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
      </Stack>
    </ThemeProvider>
  );
}
