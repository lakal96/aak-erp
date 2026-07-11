import React, { useState, useRef } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { Text, TextInput, Button, HelperText } from 'react-native-paper';
import { verifyOTP } from '../../services/api';
import useAuthStore from '../../store/authStore';

export default function OTPScreen({ route }) {
  const { phone } = route.params;
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const login = useAuthStore((s) => s.login);

  const handleVerify = async () => {
    if (otp.length !== 6) {
      setError('Enter the 6-digit code sent to your phone.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const result = await verifyOTP(phone, otp);
      await login(result);
    } catch (err) {
      setError(err.message || 'Invalid OTP. Try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={styles.inner}>
        <Text variant="headlineMedium" style={styles.title}>
          Verify OTP
        </Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          Code sent to {phone}
        </Text>

        <TextInput
          label="6-digit code"
          value={otp}
          onChangeText={setOtp}
          keyboardType="number-pad"
          mode="outlined"
          maxLength={6}
          style={styles.input}
          autoFocus
        />
        <HelperText type="error" visible={!!error}>
          {error}
        </HelperText>

        <Button
          mode="contained"
          onPress={handleVerify}
          loading={loading}
          disabled={loading || otp.length !== 6}
          style={styles.button}
          contentStyle={styles.buttonContent}
        >
          Sign In
        </Button>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  inner: { flex: 1, justifyContent: 'center', paddingHorizontal: 24 },
  title: { textAlign: 'center', fontWeight: 'bold', color: '#1a56db', marginBottom: 8 },
  subtitle: { textAlign: 'center', color: '#6b7280', marginBottom: 32 },
  input: { marginBottom: 4, letterSpacing: 8, fontSize: 24 },
  button: { marginTop: 16, borderRadius: 8 },
  buttonContent: { paddingVertical: 6 },
});
