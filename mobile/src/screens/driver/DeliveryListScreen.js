import React, { useEffect, useState, useCallback } from 'react';
import { View, FlatList, StyleSheet, RefreshControl } from 'react-native';
import { Text, Card, Chip, ActivityIndicator, Searchbar } from 'react-native-paper';
import { getMyTrips } from '../../services/api';

const STATUS_COLORS = {
  Draft: '#6b7280',
  'In Transit': '#f59e0b',
  Completed: '#10b981',
  'Partially Delivered': '#ef4444',
};

export default function DeliveryListScreen({ navigation }) {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const fetchTrips = useCallback(async () => {
    try {
      const data = await getMyTrips();
      setTrips(Array.isArray(data) ? data : []);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { fetchTrips(); }, [fetchTrips]);

  const onRefresh = () => { setRefreshing(true); fetchTrips(); };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#1a56db" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text variant="titleLarge" style={styles.header}>Today's Deliveries</Text>

      {error ? (
        <Text style={styles.error}>{error}</Text>
      ) : (
        <FlatList
          data={trips}
          keyExtractor={(item) => item.name}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
          contentContainerStyle={styles.list}
          ListEmptyComponent={
            <Text style={styles.empty}>No trips assigned for today.</Text>
          }
          renderItem={({ item }) => (
            <Card
              style={styles.card}
              onPress={() => navigation.navigate('DeliveryDetail', { tripName: item.name })}
            >
              <Card.Content>
                <View style={styles.row}>
                  <Text variant="titleMedium">{item.name}</Text>
                  <Chip
                    style={{ backgroundColor: STATUS_COLORS[item.status] + '22' }}
                    textStyle={{ color: STATUS_COLORS[item.status], fontWeight: '600' }}
                  >
                    {item.status}
                  </Chip>
                </View>
                <Text variant="bodyMedium" style={styles.zone}>
                  {item.route_zone || 'Zone not set'}
                </Text>
                <Text variant="bodySmall" style={styles.stops}>
                  {item.completed_stops}/{item.total_stops} stops completed
                </Text>
              </Card.Content>
            </Card>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  header: { padding: 16, fontWeight: 'bold', color: '#1e293b' },
  list: { paddingHorizontal: 16, paddingBottom: 24 },
  card: { marginBottom: 12, borderRadius: 12 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  zone: { marginTop: 4, color: '#6b7280' },
  stops: { marginTop: 4, color: '#94a3b8' },
  empty: { textAlign: 'center', marginTop: 60, color: '#9ca3af' },
  error: { margin: 16, color: '#ef4444' },
});
