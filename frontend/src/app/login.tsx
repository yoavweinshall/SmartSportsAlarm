import { Link } from 'expo-router';
import { useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  Text,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { supabase } from '@/lib/supabase';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  function validate(): boolean {
    if (!email.trim()) {
      Alert.alert('Missing field', 'Please enter your email address.');
      return false;
    }
    if (password.length < 6) {
      Alert.alert('Weak password', 'Password must be at least 6 characters.');
      return false;
    }
    return true;
  }

  async function handlePrimary() {
    if (!validate()) return;
    setLoading(true);
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password,
      });
      if (error) Alert.alert('Sign-in failed', error.message);
    } catch {
      Alert.alert('Error', 'An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <SafeAreaView className="flex-1 bg-neutral-100 dark:bg-black" edges={['top']}>
      <KeyboardAvoidingView
        className="flex-1"
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView
          contentContainerStyle={{ flexGrow: 1, justifyContent: 'center' }}
          keyboardShouldPersistTaps="handled"
          className="px-6">
          <Text className="text-center text-3xl font-bold text-neutral-900 dark:text-white">
            SmartSportsAlarm
          </Text>
          <Text className="mt-2 text-center text-neutral-500 dark:text-neutral-400">
            Sign in to your account
          </Text>

          <View className="mt-8 gap-4">
            <View>
              <Text className="mb-2 text-sm font-medium text-neutral-700 dark:text-neutral-300">
                Email
              </Text>
              <TextInput
                value={email}
                onChangeText={setEmail}
                placeholder="you@example.com"
                placeholderTextColor="#9ca3af"
                keyboardType="email-address"
                autoCapitalize="none"
                autoComplete="email"
                editable={!loading}
                className="rounded-xl border border-neutral-300 bg-white px-4 py-3 text-neutral-900 dark:border-neutral-600 dark:bg-neutral-900 dark:text-white"
              />
            </View>

            <View>
              <Text className="mb-2 text-sm font-medium text-neutral-700 dark:text-neutral-300">
                Password
              </Text>
              <TextInput
                value={password}
                onChangeText={setPassword}
                placeholder="••••••••"
                placeholderTextColor="#9ca3af"
                secureTextEntry
                autoComplete="current-password"
                editable={!loading}
                className="rounded-xl border border-neutral-300 bg-white px-4 py-3 text-neutral-900 dark:border-neutral-600 dark:bg-neutral-900 dark:text-white"
              />
            </View>
          </View>

          <Pressable
            onPress={handlePrimary}
            disabled={loading}
            className={`mt-8 flex-row items-center justify-center rounded-xl py-4 ${loading ? 'bg-blue-400' : 'bg-blue-600 active:opacity-90'}`}>
            {loading ? (
              <ActivityIndicator color="#ffffff" size="small" />
            ) : (
              <Text className="text-center text-lg font-semibold text-white">
                Sign in
              </Text>
            )}
          </Pressable>

          <View className="mb-8 mt-4 flex-row justify-center gap-1">
            <Text className="text-sm text-neutral-500 dark:text-neutral-400">
              Don't have an account?
            </Text>
            <Link href="/signup" asChild>
              <Pressable disabled={loading}>
                <Text className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                  Sign up
                </Text>
              </Pressable>
            </Link>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
