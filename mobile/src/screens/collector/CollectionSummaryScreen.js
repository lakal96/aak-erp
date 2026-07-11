import React, { useEffect, useState } from 'react';
import { View, FlatList, StyleSheet } from 'react-native';
import { Text, Card, ActivityIndicator, Divider } from 'react-native-paper';
import { getCollectionSummary } from '../../services/api';

export default function CollectionSummaryScreen() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getCollectionSummary()
      .then(setSummary)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <View style={styles.center}><ActivityIndicator size="large" color="#1a56db" /></View>;
  if (error) return <Text style={styles.error}>{error}</Text>;

  return (
    <View style={styles.container}>
      <Text variant="titleLarge" style={styles.header}>Today's Summary</Text>

      <View style={styles.totals}>
        <View style={styles.totalCard}>
          <Text variant="bodySmall" style={styles.label}>Cash</Text>
          <Text variant="titleMedium" style={styles.cash}>LKR {summary?.total_cash?.toLocaleString()}</Text>
        </View>
        <View style={styles.totalCard}>
          <Text variant="bodySmall" style={styles.label}>Cheque</Text>
          <Text variant="titleMedium" style={styles.cheque}>LKR {summary?.total_cheque?.toLocaleString()}</Text>
        </View>
        <View style={styles.totalCard}>
          <Text variant="bodySmall" style={styles.label}>Grand Total</Text>
          <Text variant="titleLarge" style={styles.grand}>LKR {summary?.grand_total?.toLocaleString()}</Text>
        </View>
      </View>

      <Text variant="titleSmall" style={styles.listTitle}>
        {summary?.entry_count || 0} Collections
      </Text>
      <Divider />

      <FlatList
        data={summary?.entries || []}
        keyExtractor={(_, i) => String(i)}
        contentContainerStyle={styles.list}
        ListEmptyComponent={<Text style={styles.empty}>No collections yet today.</Text>}
        renderItem={({ item }) => (
          <View style={styles.row}>
            <Text variant="bodyMedium">{item.customer}</Text>
            <View style={{ alignItems: 'flex-end' }}>
              <Text variant="bodyMedium">LKR {item.amount?.toLocaleString()}</Text>
              <Text variant="bodySmall" style={styles.muted}>{item.payment_method}</Text>
            </View>
          </View>
        )}
        ItemSeparatorComponent={() => <Divider />}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  header: { padding: 16, fontWeight: 'bold', color: '#1e293b' },
  totals: { flexDirection: 'row', padding: 16, gap: 8 },
  totalCard: { flex: 1, backgroundColor: '#fff', borderRadius: 12, padding: 12, alignItems: 'center', elevation: 1 },
  label: { color: '#6b7280', marginBottom: 4 },
  cash: { color: '#10b981', fontWeight: 'bold' },
  cheque: { color: '#3b82f6', fontWeight: 'bold' },
  grand: { color: '#1a56db', fontWeight: 'bold' },
  listTitle: { paddingHorizontal: 16, paddingVertical: 8, color: '#374151' },
  list: { paddingHorizontal: 16, paddingBottom: 32 },
  row: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 12 },
  muted: { color: '#94a3b8' },
  empty: { textAlign: 'center', marginTop: 40, color: '#9ca3af' },
  error: { margin: 16, color: '#ef4444' },
});
