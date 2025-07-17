// Lokalne uwierzytelnianie - zastąpienie API
import { mockData } from '../utils/mockData';

// Cache dla lepszej wydajności
const authCache = new Map();

export const localAuthAPI = {
  // Szybkie uwierzytelnianie z cache
  login: async (username, password) => {
    return new Promise((resolve, reject) => {
      // Symulacja opóźnienia API dla UX
      setTimeout(() => {
        // Sprawdź cache najpierw
        const cacheKey = `${username}:${password}`;
        if (authCache.has(cacheKey)) {
          resolve(authCache.get(cacheKey));
          return;
        }

        // Znajdź użytkownika w danych lokalnych
        const user = mockData.users.find(u => 
          u.username === username && u.password === password
        );

        if (user) {
          const result = {
            access_token: `local_token_${user.id}_${Date.now()}`,
            token_type: 'bearer',
            user: {
              id: user.id,
              username: user.username,
              type: user.type,
              role: user.role,
              company_id: user.company_id,
              company_name: user.company_name,
              created_at: new Date().toISOString()
            }
          };
          
          // Zapisz w cache
          authCache.set(cacheKey, result);
          resolve(result);
        } else {
          reject(new Error('Invalid credentials'));
        }
      }, 100); // Krótkie opóźnienie dla UX
    });
  },

  // Szybka walidacja tokenu
  validateToken: (token) => {
    return token && token.startsWith('local_token_');
  },

  // Wylogowanie z czyszczeniem cache
  logout: () => {
    authCache.clear();
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};

// Eksport dla kompatybilności
export default localAuthAPI;