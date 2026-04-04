import { useState } from 'react';
import { Pressable, Text, TextInput, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

/**
 * Login tab — route file (no separate screens/ layer).
 */
export default function LoginTabScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  return (
    <SafeAreaView className="flex-1 bg-neutral-100 dark:bg-black" edges={['top']}>
      <View className="flex-1 justify-center px-6">
        <Text className="text-center text-3xl font-bold text-neutral-900 dark:text-white">
          SmartSportsAlarm
        </Text>
        <Text className="mt-2 text-center text-neutral-500 dark:text-neutral-400">
          Sign in (dummy UI — no auth yet)
        </Text>

        <View className="mt-10 gap-4">
          <View>
            <Text className="mb-2 text-sm font-medium text-neutral-700 dark:text-neutral-300">Email</Text>
            <TextInput
              value={email}
              onChangeText={setEmail}
              placeholder="you@example.com"
              placeholderTextColor="#9ca3af"
              keyboardType="email-address"
              autoCapitalize="none"
              className="rounded-xl border border-neutral-300 bg-white px-4 py-3 text-neutral-900 dark:border-neutral-600 dark:bg-neutral-900 dark:text-white"
            />
          </View>
          <View>
            <Text className="mb-2 text-sm font-medium text-neutral-700 dark:text-neutral-300">Password</Text>
            <TextInput
              value={password}
              onChangeText={setPassword}
              placeholder="••••••••"
              placeholderTextColor="#9ca3af"
              secureTextEntry
              className="rounded-xl border border-neutral-300 bg-white px-4 py-3 text-neutral-900 dark:border-neutral-600 dark:bg-neutral-900 dark:text-white"
            />
          </View>
        </View>

        <Pressable
          className="mt-8 rounded-xl bg-blue-600 py-4 active:opacity-90"
          onPress={() => {
            /* API later */
          }}>
          <Text className="text-center text-lg font-semibold text-white">Sign in</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}
