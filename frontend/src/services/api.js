import axios from 'axios';

// Get backend URL from environment
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only redirect to login if we're not already on the login page
    if (error.response?.status === 401 && !window.location.pathname.includes('/panel')) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/panel';
    }
    return Promise.reject(error);
  }
);

// Auth API - FastAPI endpoints
export const authAPI = {
  login: async (username, password) => {
    try {
      const response = await api.post('/api/auth/login', { username, password });
      return response.data;
    } catch (error) {
      // Re-throw error for proper handling in LoginPage
      throw error;
    }
  },
};

// Cache dla API calls - optymalizacja wydajności
const apiCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minut

const getCachedData = (key) => {
  const cached = apiCache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }
  return null;
};

const setCachedData = (key, data) => {
  apiCache.set(key, {
    data,
    timestamp: Date.now()
  });
};

// Companies API - z cache
export const companiesAPI = {
  getAll: async () => {
    const cacheKey = 'companies_all';
    const cached = getCachedData(cacheKey);
    if (cached) return cached;

    const response = await api.get('/api/companies');
    setCachedData(cacheKey, response.data);
    return response.data;
  },
  
  create: async (company) => {
    const response = await api.post('/api/companies', company);
    // Wyczyść cache po dodaniu nowej firmy
    apiCache.delete('companies_all');
    return response.data;
  },
  
  update: async (id, company) => {
    const response = await api.put(`/api/companies/${id}`, company);
    // Wyczyść cache po aktualizacji
    apiCache.delete('companies_all');
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/api/companies/${id}`);
    // Wyczyść cache po usunięciu
    apiCache.delete('companies_all');
    return response.data;
  },
};

// Users API - z cache
export const usersAPI = {
  getAll: async () => {
    const cacheKey = 'users_all';
    const cached = getCachedData(cacheKey);
    if (cached) return cached;

    const response = await api.get('/api/users');
    setCachedData(cacheKey, response.data);
    return response.data;
  },
  
  create: async (user) => {
    const response = await api.post('/api/users', user);
    apiCache.delete('users_all');
    return response.data;
  },
  
  update: async (id, user) => {
    const response = await api.put(`/api/users/${id}`, user);
    apiCache.delete('users_all');
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/api/users/${id}`);
    apiCache.delete('users_all');
    return response.data;
  },
};

// Employees API - z cache
export const employeesAPI = {
  getAll: async () => {
    const cacheKey = 'employees_all';
    const cached = getCachedData(cacheKey);
    if (cached) return cached;

    const response = await api.get('/api/employees');
    setCachedData(cacheKey, response.data);
    return response.data;
  },
  
  create: async (employee) => {
    const response = await api.post('/api/employees', employee);
    apiCache.delete('employees_all');
    return response.data;
  },
  
  update: async (id, employee) => {
    const response = await api.put(`/api/employees/${id}`, employee);
    apiCache.delete('employees_all');
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/api/employees/${id}`);
    apiCache.delete('employees_all');
    return response.data;
  },
  
  generateQR: async (id) => {
    const response = await api.get(`/api/employees/${id}/qr`);
    return response.data;
  },
  
  downloadQRPDF: async (id, employeeName) => {
    try {
      console.log('Downloading PDF for employee:', employeeName, 'ID:', id);
      console.log('API URL:', API_BASE_URL);
      
      const response = await api.get(`/api/employees/${id}/qr-pdf`, {
        responseType: 'blob'
      });
      
      console.log('Response received:', response.status);
      
      // Create download link
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const safeName = employeeName.replace(/[^a-zA-Z0-9]/g, '_');
      link.download = `qr_code_${safeName}.pdf`;
      link.style.display = 'none';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('PDF download completed successfully');
      return response.data;
    } catch (error) {
      console.error('Error downloading PDF:', error);
      throw error;
    }
  },
};

// Time Entries API - z cache
export const timeEntriesAPI = {
  getAll: async () => {
    const cacheKey = 'time_entries_all';
    const cached = getCachedData(cacheKey);
    if (cached) return cached;

    const response = await api.get('/api/time-entries');
    setCachedData(cacheKey, response.data);
    return response.data;
  },
  
  create: async (timeEntry) => {
    const response = await api.post('/api/time-entries', timeEntry);
    apiCache.delete('time_entries_all');
    return response.data;
  },
  
  update: async (id, timeEntry) => {
    const response = await api.put(`/api/time-entries/${id}`, timeEntry);
    apiCache.delete('time_entries_all');
    return response.data;
  },
  
  delete: async (id) => {
    const response = await api.delete(`/api/time-entries/${id}`);
    apiCache.delete('time_entries_all');
    return response.data;
  },
};

// Employee Summary API - z cache
export const employeeSummaryAPI = {
  getSummary: async (month, year) => {
    const cacheKey = `employee_summary_${month}_${year}`;
    const cached = getCachedData(cacheKey);
    if (cached) return cached;

    const params = new URLSearchParams();
    if (month) params.append('month', month);
    if (year) params.append('year', year);
    
    const response = await api.get(`/api/employee-summary?${params}`);
    setCachedData(cacheKey, response.data);
    return response.data;
  },
  
  getEmployeeMonths: async (employeeId) => {
    const cacheKey = `employee_months_${employeeId}`;
    const cached = getCachedData(cacheKey);
    if (cached) return cached;

    const response = await api.get(`/api/employee-months/${employeeId}`);
    setCachedData(cacheKey, response.data);
    return response.data;
  },
  
  getEmployeeDays: async (employeeId, yearMonth) => {
    const cacheKey = `employee_days_${employeeId}_${yearMonth}`;
    const cached = getCachedData(cacheKey);
    if (cached) return cached;

    const response = await api.get(`/api/employee-days/${employeeId}/${yearMonth}`);
    setCachedData(cacheKey, response.data);
    return response.data;
  },
};

// QR Scan API
export const qrScanAPI = {
  processScan: async (qrCode, userId) => {
    const response = await api.post('/api/qr-scan', { qr_code: qrCode, user_id: userId });
    // Wyczyść cache po skanowaniu QR
    apiCache.delete('time_entries_all');
    return response.data;
  },
};

export default api;