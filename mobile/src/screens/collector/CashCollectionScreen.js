import React, { useEffect, useState, useCallback } from 'react';
import { View, FlatList, StyleSheet, Alert } from 'react-native';
import {
  Text, Card, Button, ActivityIndicator, Portal, Modal,
  TextInput, RadioButton, HelperText,
} from 'react-native-paper';
import { getPendingCollections, submitCollection } from '../../services/api';

export default function CashCollectionScreen() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState({ amount: '', payment_method: 'Cash', cheque_number: '', cheque_date: '', bank_name: '', notes: '' });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const fetchCollections = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getPendingCollections();
      setCustomers(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchCollections(); }, [fetchCollections]);

  const openModal = (customer) => {
    setSelected(customer);
    setForm({ amount: String(customer.outstanding_balance || ''), payment_method: 'Cash', cheque_number: '', cheque_date: '', bank_name: '', notes: '' });
    setModalVisible(true);
  };

  const handleSubmit = async () => {
    if (!form.amount || parseFloat(form.amount) <= 0) {
      Alert.alert('Validation', 'Enter a valid amount.');
      return;
    }
    setSaving(true);
    try {
      await submitCollection({
        customer: selected.customer,
        amount: parseFloat(form.amount),
        payment_method: form.payment_method,
        cheque_number: form.cheque_number,
        cheque_date: form.cheque_date,
        bank_name: form.bank_name,
        notes: form.notes,
      });
      Alert.alert('Success', `Collection recorded for ${selected.customer_name}`);
      setModalVisible(false);
      fetchCollections();
    } catch (err) {
      Alert.alert('Error', err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <View style={styles.center}><ActivityIndicator size="large" color="#1a56db" /></View>;

  return (
    <View style={styles.container}>
      <Text variant="titleLarge" style={styles.header}>Pending Collections</Text>

      {error ? <Text style={styles.error}>{error}</Text> : (
        <FlatList
          data={customers}
          keyExtractor={(item) => item.customer}
          contentContainerStyle={styles.list}
          ListEmptyComponent={<Text style={styles.empty}>No pending collections.</Text>}
          renderItem={({ item }) => (
            <Card style={styles.card}>
              <Card.Content>
                <Text variant="titleSmall">{item.customer_name}</Text>
                <Text variant="bodySmall" style={styles.outstanding}>
                  Outstanding: LKR {item.outstanding_balance?.toLocaleString()}
                </Text>
                {item.overdue_amount > 0 && (
                  <Text variant="bodySmall" style={styles.overdue}>
                    Overdue: LKR {item.overdue_amount?.toLocaleString()}
                  </Text>
                )}
              </Card.Content>
              <Card.Actions>
                <Button onPress={() => openModal(item)}>Collect</Button>
              </Card.Actions>
            </Card>
          )}
        />
      )}

      <Portal>
        <Modal
          visible={modalVisible}
          onDismiss={() => setModalVisible(false)}
          contentContainerStyle={styles.modal}
        >
          <Text variant="titleMedium" style={{ marginBottom: 8 }}>
            Collect from {selected?.customer_name}
          </Text>
          <Text variant="bodySmall" style={styles.outstanding}>
            Outstanding: LKR {selected?.outstanding_balance?.toLocaleString()}
          </Text>

          <TextInput
            label="Amount (LKR)"
            value={form.amount}
            onChangeText={(v) => setForm({ ...form, amount: v })}
            keyboardType="numeric"
            mode="outlined"
            style={{ marginTop: 12 }}
          />

          <Text variant="labelMedium" style={{ marginTop: 10 }}>Payment Method</Text>
          <RadioButton.Group
            onValueChange={(v) => setForm({ ...form, payment_method: v })}
            value={form.payment_method}
          >
            <RadioButton.Item label="Cash" value="Cash" />
            <RadioButton.Item label="Cheque" value="Cheque" />
          </RadioButton.Group>

          {form.payment_method === 'Cheque' && (
            <>
              <TextInput label="Cheque Number" value={form.cheque_number} onChangeText={(v) => setForm({ ...form, cheque_number: v })} mode="outlined" style={{ marginBottom: 8 }} />
              <TextInput label="Cheque Date (YYYY-MM-DD)" value={form.cheque_date} onChangeText={(v) => setForm({ ...form, cheque_date: v })} mode="outlined" style={{ marginBottom: 8 }} />
              <TextInput label="Bank Name" value={form.bank_name} onChangeText={(v) => setForm({ ...form, bank_name: v })} mode="outlined" style={{ marginBottom: 8 }} />
            </>
          )}

          <TextInput label="Notes" value={form.notes} onChangeText={(v) => setForm({ ...form, notes: v })} mode="outlined" style={{ marginBottom: 12 }} />

          <Button mode="contained" onPress={handleSubmit} loading={saving} disabled={saving}>
            Submit Collection
          </Button>
        </Modal>
      </Portal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  header: { padding: 16, fontWeight: 'bold', color: '#1e293b' },
  list: { paddingHorizontal: 16, paddingBottom: 32 },
  card: { marginBottom: 10, borderRadius: 10 },
  outstanding: { color: '#f59e0b', marginTop: 4 },
  overdue: { color: '#ef4444', marginTop: 2 },
  empty: { textAlign: 'center', marginTop: 60, color: '#9ca3af' },
  error: { margin: 16, color: '#ef4444' },
  modal: { backgroundColor: '#fff', margin: 20, padding: 20, borderRadius: 16 },
});
