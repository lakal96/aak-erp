import React from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import useAuthStore from '../store/authStore';

// Auth screens
import PhoneScreen from '../screens/auth/PhoneScreen';
import OTPScreen from '../screens/auth/OTPScreen';

// Driver screens
import DeliveryListScreen from '../screens/driver/DeliveryListScreen';
import DeliveryDetailScreen from '../screens/driver/DeliveryDetailScreen';

// Sales Rep screens
import CustomerListScreen from '../screens/sales/CustomerListScreen';
import CreateOrderScreen from '../screens/sales/CreateOrderScreen';

// Collector screens
import CashCollectionScreen from '../screens/collector/CashCollectionScreen';
import CollectionSummaryScreen from '../screens/collector/CollectionSummaryScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function DriverTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ color, size }) => {
          const icons = {
            Deliveries: 'truck-delivery',
            Profile: 'account-circle',
          };
          return <MaterialCommunityIcons name={icons[route.name]} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#1a56db',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen name="Deliveries" component={DeliveryListScreen} />
      <Tab.Screen name="Profile" component={ProfilePlaceholder} />
    </Tab.Navigator>
  );
}

function SalesRepTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ color, size }) => {
          const icons = {
            Customers: 'account-group',
            Orders: 'clipboard-list',
            Profile: 'account-circle',
          };
          return <MaterialCommunityIcons name={icons[route.name]} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#1a56db',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen name="Customers" component={CustomerListScreen} />
      <Tab.Screen name="Profile" component={ProfilePlaceholder} />
    </Tab.Navigator>
  );
}

function CollectorTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ color, size }) => {
          const icons = {
            Collections: 'cash-multiple',
            Summary: 'chart-bar',
            Profile: 'account-circle',
          };
          return <MaterialCommunityIcons name={icons[route.name]} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#1a56db',
        tabBarInactiveTintColor: 'gray',
      })}
    >
      <Tab.Screen name="Collections" component={CashCollectionScreen} />
      <Tab.Screen name="Summary" component={CollectionSummaryScreen} />
      <Tab.Screen name="Profile" component={ProfilePlaceholder} />
    </Tab.Navigator>
  );
}

// Minimal placeholder — replace with real ProfileScreen
function ProfilePlaceholder() {
  const logout = useAuthStore((s) => s.logout);
  const { Button, Text } = require('react-native-paper');
  const { View } = require('react-native');
  return (
    <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
      <Button mode="contained" onPress={logout}>Logout</Button>
    </View>
  );
}

function MainNavigator() {
  const role = useAuthStore((s) => s.user?.role);
  if (role === 'AAK Driver') return <DriverTabs />;
  if (role === 'AAK Sales Rep') return <SalesRepTabs />;
  if (role === 'AAK Collector') return <CollectorTabs />;
  // Manager sees all
  return <DriverTabs />;
}

export default function AppNavigator() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      {isAuthenticated ? (
        <>
          <Stack.Screen name="Main" component={MainNavigator} />
          <Stack.Screen
            name="DeliveryDetail"
            component={DeliveryDetailScreen}
            options={{ headerShown: true, title: 'Delivery' }}
          />
          <Stack.Screen
            name="CreateOrder"
            component={CreateOrderScreen}
            options={{ headerShown: true, title: 'New Order' }}
          />
        </>
      ) : (
        <>
          <Stack.Screen name="Phone" component={PhoneScreen} />
          <Stack.Screen name="OTP" component={OTPScreen} />
        </>
      )}
    </Stack.Navigator>
  );
}
