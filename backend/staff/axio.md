import axios from 'axios';

const api = axios.create({
baseURL: 'http://127.0.0.1:8000/api',
});

// Interceptor to handle 401 errors
api.interceptors.response.use(
(response) => response, // If request is successful, just return it
async (error) => {
const originalRequest = error.config;

        // If error is 401 and we haven't tried refreshing yet
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token'); // Or from cookies

                // Call the endpoint we just discussed
                const response = await axios.post('http://127.0.0.1:8000/api/auth/token/refresh/', {
                    refresh: refreshToken,
                });

                const { access } = response.data;

                // Update local storage and the failed request header
                localStorage.setItem('access_token', access);
                api.defaults.headers.common['Authorization'] = `Bearer ${access}`;

                return api(originalRequest); // Retry original request
            } catch (refreshError) {
                // If refresh token is also expired, log out the user
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }
        return Promise.reject(error);
    }

);

export default api;

import api from '@/lib/axios';

const fetchSuppliers = async () => {
try {
const response = await api.get('/suppliers/');
console.log(response.data);
} catch (err) {
console.error("Even after refresh, this failed.", err);
}
};
