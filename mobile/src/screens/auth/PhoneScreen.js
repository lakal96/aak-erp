import React, { useState } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { Text, TextInput, Button, HelperText } from 'react-native-paper';
import { sendOTP } from '../../services/api';

export default function PhoneScreen({ navigation }) {
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const isValidPhone = /^\+?[0-9]{9,15}$/.test(phone.trim());

  const handleSend = async () => {
    if (!isValidPhone) {
      setError('Enter a valid phone number (e.g. +94771234567)');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await sendOTP(phone.trim());
      navigation.navigate('OTP', { phone: phone.trim() });
    } catch (err) {
      setError(err.message || 'Failed to send OTP. Try again.');
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
          AAK Agency
        </Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          Enter your mobile number to sign in
        </Text>

        <TextInput
          label="Mobile Number"
          value={phone}
          onChangeText={setPhone}
          keyboardType="phone-pad"
          mode="outlined"
          placeholder="+94771234567"
          style={styles.input}
          autoFocus
        />
        <HelperText type="error" visible={!!error}>
          {error}
        </HelperText>

        <Button
          mode="contained"
          onPress={handleSend}
          loading={loading}
          disabled={loading || !phone}
          style={styles.button}
          contentStyle={styles.buttonContent}
        >
          Send OTP
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
  input: { marginBottom: 4 },
  button: { marginTop: 16, borderRadius: 8 },
  buttonContent: { paddingVertical: 6 },
});
