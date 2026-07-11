import React, { useEffect, useState, useCallback } from 'react';
import { View, FlatList, StyleSheet } from 'react-native';
import { Text, Card, Searchbar, ActivityIndicator, Chip } from 'react-native-paper';
import { getCustomerList } from '../../services/api';

const ZONES = ['All', 'Wattala', 'Makola', 'Malwana', 'Kadana', 'Hadala', 'Mahabage'];

export default function CustomerListScreen({ navigation }) {
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState('');
  const [zone, setZone] = useState('All');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchCustomers = useCallback(async () => {
    setLoading(true);
    try {
      const result = await getCustomerList({
        zone: zone === 'All' ? undefined : zone,
        search: search || undefined,
      });
      setCustomers(result?.customers || []);
      setError('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [zone, search]);

  useEffect(() => {
    const timer = setTimeout(fetchCustomers, 400);
    return () => clearTimeout(timer);
  }, [fetchCustomers]);

  return (
    <View style={styles.container}>
      <Text variant="titleLarge" style={styles.header}>Customers</Text>

      <Searchbar
        placeholder="Search by name..."
        value={search}
        onChangeText={setSearch}
        style={styles.searchbar}
      />

      {/* Zone filter chips */}
      <View style={styles.chipRow}>
        {ZONES.map((z) => (
          <Chip
            key={z}
            selected={zone === z}
            onPress={() => setZone(z)}
            style={styles.chip}
          >
            {z}
          </Chip>
        ))}
      </View>

      {loading ? (
        <View style={styles.center}><ActivityIndicator size="large" color="#1a56db" /></View>
      ) : error ? (
        <Text style={styles.error}>{error}</Text>
      ) : (
        <FlatList
          data={customers}
          keyExtractor={(item) => item.name}
          contentContainerStyle={styles.list}
          ListEmptyComponent={<Text style={styles.empty}>No customers found.</Text>}
          renderItem={({ item }) => (
            <Card
              style={styles.card}
              onPress={() => navigation.navigate('CreateOrder', { customer: item })}
            >
              <Card.Content>
                <Text variant="titleSmall">{item.customer_name}</Text>
                <Text variant="bodySmall" style={styles.muted}>
                  {item.territory || 'No zone'} · {item.mobile_no || 'No phone'}
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
  searchbar: { marginHorizontal: 16, marginBottom: 8, borderRadius: 10 },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', paddingHorizontal: 12, marginBottom: 8, gap: 6 },
  chip: { marginBottom: 4 },
  list: { paddingHorizontal: 16, paddingBottom: 24 },
  card: { marginBottom: 10, borderRadius: 10 },
  muted: { color: '#6b7280', marginTop: 2 },
  empty: { textAlign: 'center', marginTop: 60, color: '#9ca3af' },
  error: { margin: 16, color: '#ef4444' },
});
