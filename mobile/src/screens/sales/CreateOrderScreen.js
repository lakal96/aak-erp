import React, { useState } from 'react';
import { View, FlatList, StyleSheet, Alert, ScrollView } from 'react-native';
import { Text, TextInput, Button, Card, IconButton, Divider } from 'react-native-paper';
import { createOrder } from '../../services/api';
import { useNavigation } from '@react-navigation/native';

// Static CBL chocolate item list — in production this would come from ERPNext
const CBL_ITEMS = [
  { item_code: 'CBL-MUNCHEE-DARK-80G', item_name: 'Munchee Dark 80g', rate: 120 },
  { item_code: 'CBL-MUNCHEE-MILK-80G', item_name: 'Munchee Milk 80g', rate: 115 },
  { item_code: 'CBL-CHOC-ORANGE-40G', item_name: 'Chocolate Orange 40g', rate: 65 },
  { item_code: 'CBL-MUNCHEE-WHITE-80G', item_name: 'Munchee White 80g', rate: 120 },
  { item_code: 'CBL-RICHOCO-200G', item_name: 'Richoco 200g', rate: 250 },
];

export default function CreateOrderScreen({ route }) {
  const { customer } = route.params;
  const navigation = useNavigation();
  const [items, setItems] = useState(
    CBL_ITEMS.map((item) => ({ ...item, qty: '0' }))
  );
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const updateQty = (index, value) => {
    const updated = [...items];
    updated[index].qty = value.replace(/[^0-9]/g, '');
    setItems(updated);
  };

  const orderItems = items.filter((i) => parseInt(i.qty) > 0);
  const grandTotal = orderItems.reduce((sum, i) => sum + (parseInt(i.qty) * i.rate), 0);

  const handleSubmit = async () => {
    if (orderItems.length === 0) {
      Alert.alert('Validation', 'Add at least one item with quantity > 0.');
      return;
    }
    setLoading(true);
    try {
      const result = await createOrder({
        customer: customer.name,
        items: orderItems.map((i) => ({
          item_code: i.item_code,
          qty: parseInt(i.qty),
          rate: i.rate,
        })),
        notes,
      });
      Alert.alert('Order Created', `Order ${result.order_name} — LKR ${result.grand_total?.toLocaleString()}`, [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    } catch (err) {
      Alert.alert('Error', err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Card style={styles.customerCard}>
        <Card.Content>
          <Text variant="titleMedium">{customer.customer_name}</Text>
          <Text variant="bodySmall" style={styles.muted}>{customer.territory}</Text>
        </Card.Content>
      </Card>

      <Text variant="titleSmall" style={styles.sectionTitle}>Items</Text>

      {items.map((item, index) => (
        <View key={item.item_code} style={styles.itemRow}>
          <View style={styles.itemInfo}>
            <Text variant="bodyMedium">{item.item_name}</Text>
            <Text variant="bodySmall" style={styles.muted}>LKR {item.rate}</Text>
          </View>
          <View style={styles.qtyControl}>
            <IconButton
              icon="minus"
              size={18}
              onPress={() => updateQty(index, String(Math.max(0, parseInt(item.qty || '0') - 1)))}
            />
            <TextInput
              value={item.qty}
              onChangeText={(v) => updateQty(index, v)}
              keyboardType="numeric"
              mode="outlined"
              style={styles.qtyInput}
              dense
            />
            <IconButton
              icon="plus"
              size={18}
              onPress={() => updateQty(index, String(parseInt(item.qty || '0') + 1))}
            />
          </View>
        </View>
      ))}

      <Divider style={styles.divider} />

      <TextInput
        label="Notes"
        value={notes}
        onChangeText={setNotes}
        mode="outlined"
        multiline
        style={styles.notes}
      />

      <View style={styles.totalRow}>
        <Text variant="titleMedium">Total</Text>
        <Text variant="titleMedium" style={{ color: '#1a56db' }}>
          LKR {grandTotal.toLocaleString()}
        </Text>
      </View>

      <Button
        mode="contained"
        onPress={handleSubmit}
        loading={loading}
        disabled={loading || orderItems.length === 0}
        style={styles.submitBtn}
        contentStyle={styles.submitContent}
      >
        Place Order ({orderItems.length} items)
      </Button>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  content: { padding: 16, paddingBottom: 40 },
  customerCard: { marginBottom: 16, borderRadius: 10 },
  sectionTitle: { fontWeight: 'bold', marginBottom: 12, color: '#374151' },
  muted: { color: '#6b7280', marginTop: 2 },
  itemRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  itemInfo: { flex: 1 },
  qtyControl: { flexDirection: 'row', alignItems: 'center' },
  qtyInput: { width: 50, textAlign: 'center' },
  divider: { marginVertical: 16 },
  notes: { marginBottom: 16 },
  totalRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  submitBtn: { borderRadius: 10 },
  submitContent: { paddingVertical: 6 },
});
