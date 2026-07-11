import React, { useEffect, useState } from 'react';
import { View, FlatList, StyleSheet, Alert } from 'react-native';
import {
  Text, Card, Button, Chip, ActivityIndicator, Portal, Modal,
  RadioButton, TextInput,
} from 'react-native-paper';
import { getTripDetail, updateDeliveryStop, startTrip, completeTrip } from '../../services/api';

const STATUS_COLORS = {
  Pending: '#6b7280',
  Delivered: '#10b981',
  Partial: '#f59e0b',
  Returned: '#ef4444',
};

export default function DeliveryDetailScreen({ route, navigation }) {
  const { tripName } = route.params;
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedStop, setSelectedStop] = useState(null);
  const [selectedIdx, setSelectedIdx] = useState(null);
  const [form, setForm] = useState({ status: 'Delivered', payment_collected: '', payment_method: 'Cash', cheque_number: '', notes: '' });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchTrip();
  }, []);

  const fetchTrip = async () => {
    try {
      const data = await getTripDetail(tripName);
      setTrip(data);
    } catch (err) {
      Alert.alert('Error', err.message);
    } finally {
      setLoading(false);
    }
  };

  const openStopModal = (stop, idx) => {
    setSelectedStop(stop);
    setSelectedIdx(idx);
    setForm({
      status: stop.status === 'Pending' ? 'Delivered' : stop.status,
      payment_collected: String(stop.payment_collected || ''),
      payment_method: stop.payment_method || 'Cash',
      cheque_number: stop.cheque_number || '',
      notes: stop.notes || '',
    });
    setModalVisible(true);
  };

  const handleSaveStop = async () => {
    setSaving(true);
    try {
      await updateDeliveryStop({
        trip_name: tripName,
        stop_idx: selectedIdx,
        status: form.status,
        payment_collected: parseFloat(form.payment_collected) || 0,
        payment_method: form.payment_method,
        cheque_number: form.cheque_number,
        notes: form.notes,
      });
      await fetchTrip();
      setModalVisible(false);
    } catch (err) {
      Alert.alert('Error', err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleStartTrip = async () => {
    try {
      await startTrip(tripName);
      await fetchTrip();
    } catch (err) {
      Alert.alert('Error', err.message);
    }
  };

  const handleCompleteTrip = async () => {
    Alert.alert('Complete Trip', 'Mark this trip as completed?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Complete', onPress: async () => {
          try {
            await completeTrip(tripName);
            navigation.goBack();
          } catch (err) {
            Alert.alert('Error', err.message);
          }
        },
      },
    ]);
  };

  if (loading || !trip) {
    return <View style={styles.center}><ActivityIndicator size="large" color="#1a56db" /></View>;
  }

  return (
    <View style={styles.container}>
      {/* Trip header */}
      <View style={styles.tripHeader}>
        <Text variant="titleMedium">{trip.name} — {trip.route_zone}</Text>
        <Text variant="bodySmall" style={styles.muted}>
          {trip.completed_stops}/{trip.total_stops} stops · Cash: LKR {trip.total_cash_collected?.toLocaleString() || '0'}
        </Text>
        <View style={styles.actionRow}>
          {trip.status === 'Draft' && (
            <Button mode="contained" onPress={handleStartTrip} style={styles.actionBtn}>
              Start Trip
            </Button>
          )}
          {trip.status === 'In Transit' && (
            <Button mode="outlined" onPress={handleCompleteTrip} style={styles.actionBtn}>
              Complete Trip
            </Button>
          )}
        </View>
      </View>

      {/* Stop list */}
      <FlatList
        data={trip.stops}
        keyExtractor={(_, i) => String(i)}
        contentContainerStyle={styles.list}
        renderItem={({ item, index }) => (
          <Card style={styles.card} onPress={() => openStopModal(item, index)}>
            <Card.Content>
              <View style={styles.row}>
                <Text variant="titleSmall">{item.customer_name || item.customer}</Text>
                <Chip
                  style={{ backgroundColor: STATUS_COLORS[item.status] + '22' }}
                  textStyle={{ color: STATUS_COLORS[item.status], fontWeight: '600', fontSize: 11 }}
                >
                  {item.status}
                </Chip>
              </View>
              {item.payment_collected > 0 && (
                <Text variant="bodySmall" style={styles.muted}>
                  Collected: LKR {item.payment_collected.toLocaleString()} ({item.payment_method})
                </Text>
              )}
              {item.outstanding_balance > 0 && (
                <Text variant="bodySmall" style={{ color: '#ef4444' }}>
                  Outstanding: LKR {item.outstanding_balance.toLocaleString()}
                </Text>
              )}
            </Card.Content>
          </Card>
        )}
      />

      {/* Stop update modal */}
      <Portal>
        <Modal
          visible={modalVisible}
          onDismiss={() => setModalVisible(false)}
          contentContainerStyle={styles.modal}
        >
          <Text variant="titleMedium" style={{ marginBottom: 12 }}>
            {selectedStop?.customer_name}
          </Text>

          <Text variant="labelMedium">Delivery Status</Text>
          <RadioButton.Group onValueChange={(v) => setForm({ ...form, status: v })} value={form.status}>
            {['Delivered', 'Partial', 'Returned'].map((s) => (
              <RadioButton.Item key={s} label={s} value={s} />
            ))}
          </RadioButton.Group>

          <TextInput
            label="Amount Collected (LKR)"
            value={form.payment_collected}
            onChangeText={(v) => setForm({ ...form, payment_collected: v })}
            keyboardType="numeric"
            mode="outlined"
            style={{ marginTop: 8 }}
          />

          <Text variant="labelMedium" style={{ marginTop: 8 }}>Payment Method</Text>
          <RadioButton.Group onValueChange={(v) => setForm({ ...form, payment_method: v })} value={form.payment_method}>
            {['Cash', 'Cheque', 'Credit'].map((m) => (
              <RadioButton.Item key={m} label={m} value={m} />
            ))}
          </RadioButton.Group>

          {form.payment_method === 'Cheque' && (
            <TextInput
              label="Cheque Number"
              value={form.cheque_number}
              onChangeText={(v) => setForm({ ...form, cheque_number: v })}
              mode="outlined"
              style={{ marginTop: 8 }}
            />
          )}

          <TextInput
            label="Notes"
            value={form.notes}
            onChangeText={(v) => setForm({ ...form, notes: v })}
            mode="outlined"
            style={{ marginTop: 8 }}
          />

          <Button
            mode="contained"
            onPress={handleSaveStop}
            loading={saving}
            disabled={saving}
            style={{ marginTop: 16 }}
          >
            Save
          </Button>
        </Modal>
      </Portal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  tripHeader: { backgroundColor: '#fff', padding: 16, borderBottomWidth: 1, borderBottomColor: '#e2e8f0' },
  muted: { color: '#6b7280', marginTop: 2 },
  actionRow: { flexDirection: 'row', marginTop: 10, gap: 8 },
  actionBtn: { borderRadius: 8 },
  list: { padding: 16, paddingBottom: 32 },
  card: { marginBottom: 10, borderRadius: 10 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  modal: { backgroundColor: '#fff', margin: 20, padding: 20, borderRadius: 16 },
});
