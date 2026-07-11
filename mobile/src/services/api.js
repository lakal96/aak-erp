import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'https://erp.aakagency.lk';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Auth token injection ───────────────────────────────────────────────────────
api.interceptors.request.use(async (config) => {
  const apiKey = await SecureStore.getItemAsync('api_key');
  const apiSecret = await SecureStore.getItemAsync('api_secret');
  if (apiKey && apiSecret) {
    config.headers['Authorization'] = `token ${apiKey}:${apiSecret}`;
  }
  return config;
});

// ── Global error handler ──────────────────────────────────────────────────────
api.interceptors.response.use(
  (res) => res.data?.message ?? res.data,
  (error) => {
    const msg =
      error.response?.data?.exception ||
      error.response?.data?.message ||
      error.message ||
      'Network error';
    return Promise.reject(new Error(msg));
  },
);

// ── Auth ──────────────────────────────────────────────────────────────────────
export const sendOTP = (phone) =>
  api.post('/api/method/aak_agency.api.auth.send_otp', { phone });

export const verifyOTP = (phone, otp) =>
  api.post('/api/method/aak_agency.api.auth.verify_otp', { phone, otp });

export const getCurrentUser = () =>
  api.get('/api/method/aak_agency.api.auth.get_current_user');

// ── Delivery (Driver) ─────────────────────────────────────────────────────────
export const getMyTrips = (trip_date) =>
  api.get('/api/method/aak_agency.api.delivery.get_my_trips', { params: { trip_date } });

export const getTripDetail = (trip_name) =>
  api.get('/api/method/aak_agency.api.delivery.get_trip_detail', { params: { trip_name } });

export const updateDeliveryStop = (payload) =>
  api.post('/api/method/aak_agency.api.delivery.update_delivery_stop', payload);

export const startTrip = (trip_name) =>
  api.post('/api/method/aak_agency.api.delivery.start_trip', { trip_name });

export const completeTrip = (trip_name) =>
  api.post('/api/method/aak_agency.api.delivery.complete_trip', { trip_name });

// ── Orders (Sales Rep) ────────────────────────────────────────────────────────
export const getCustomerList = (params) =>
  api.get('/api/method/aak_agency.api.orders.get_customer_list', { params });

export const getCustomerDetail = (customer) =>
  api.get('/api/method/aak_agency.api.orders.get_customer_detail', { params: { customer } });

export const createOrder = (payload) =>
  api.post('/api/method/aak_agency.api.orders.create_order', payload);

export const getMyOrders = (params) =>
  api.get('/api/method/aak_agency.api.orders.get_my_orders', { params });

// ── Collections (Collector) ───────────────────────────────────────────────────
export const getPendingCollections = (zone) =>
  api.get('/api/method/aak_agency.api.collections.get_pending_collections', { params: { zone } });

export const submitCollection = (payload) =>
  api.post('/api/method/aak_agency.api.collections.submit_collection', payload);

export const getCollectionSummary = (collection_date) =>
  api.get('/api/method/aak_agency.api.collections.get_collection_summary', {
    params: { collection_date },
  });
