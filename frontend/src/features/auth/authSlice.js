import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

// Получаем пользователя из localStorage
const user = JSON.parse(localStorage.getItem('user'));

export const login = createAsyncThunk('auth/login', async (userData, thunkAPI) => {
  try {
    const params = new URLSearchParams();
    params.append('username', userData.email);
    params.append('password', userData.password);

    const response = await axios.post(`${API_URL}/token`, params);
    
    if (response.data) {
      // Сохраняем токен в localStorage
      localStorage.setItem('user', JSON.stringify(response.data));
    }
    return response.data;
  } catch (error) {
    const message =
      (error.response && error.response.data && error.response.data.detail) ||
      error.message ||
      error.toString();
    return thunkAPI.rejectWithValue(message);
  }
});

export const getStats = createAsyncThunk('auth/getStats', async (_, thunkAPI) => {
  try {
    const token = thunkAPI.getState().auth.user.access_token;
    const config = {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    };
    const response = await axios.get(`${API_URL}/stats/me`, config);
    return response.data;
  } catch (error) {
     const message =
      (error.response && error.response.data && error.response.data.detail) ||
      error.message ||
      error.toString();
    return thunkAPI.rejectWithValue(message);
  }
});

export const logout = createAsyncThunk('auth/logout', async () => {
  localStorage.removeItem('user');
});

const initialState = {
  user: user ? user : null,
  isError: false,
  isSuccess: false,
  isLoading: false,
  message: '',
  stats: null,
  isStatsLoading: false,
};

export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    reset: (state) => {
      state.isLoading = false;
      state.isSuccess = false;
      state.isError = false;
      state.message = '';
      state.stats = null;
      state.isStatsLoading = false;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isSuccess = true;
        state.user = action.payload;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.isError = true;
        state.message = action.payload;
        state.user = null;
      })
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.stats = null;
      })
      .addCase(getStats.pending, (state) => {
        state.isStatsLoading = true;
      })
      .addCase(getStats.fulfilled, (state, action) => {
        state.isStatsLoading = false;
        state.stats = action.payload;
      })
      .addCase(getStats.rejected, (state, action) => {
        state.isStatsLoading = false;
        console.error("Failed to load stats:", action.payload);
      });
  },
});

export const { reset } = authSlice.actions;
export default authSlice.reducer; 