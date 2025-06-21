import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

// Async thunk для создания объекта
export const createProperty = createAsyncThunk('properties/create', async (propertyData, thunkAPI) => {
  try {
    const token = thunkAPI.getState().auth.user.access_token;
    const config = {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    };
    const response = await axios.post(`${API_URL}/properties/`, propertyData, config);
    return response.data;
  } catch (error) {
    const message =
      (error.response && error.response.data && error.response.data.detail) ||
      error.message ||
      error.toString();
    return thunkAPI.rejectWithValue(message);
  }
});

// Async thunk для получения списка объектов
export const getProperties = createAsyncThunk('properties/getAll', async (_, thunkAPI) => {
  try {
    const token = thunkAPI.getState().auth.user.access_token;
    const config = {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    };
    const response = await axios.get(`${API_URL}/properties/`, config);
    return response.data;
  } catch (error) {
    const message =
      (error.response && error.response.data && error.response.data.detail) ||
      error.message ||
      error.toString();
    return thunkAPI.rejectWithValue(message);
  }
});

const initialState = {
  properties: [],
  isLoading: false,
  isError: false,
  message: '',
};

export const propertiesSlice = createSlice({
  name: 'properties',
  initialState,
  reducers: {
    reset: (state) => initialState,
  },
  extraReducers: (builder) => {
    builder
      .addCase(createProperty.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(createProperty.fulfilled, (state, action) => {
        state.isLoading = false;
        // Мы не будем вручную добавлять объект в список, 
        // вместо этого мы перезапросим весь список для актуальности.
      })
      .addCase(createProperty.rejected, (state, action) => {
        state.isLoading = false;
        state.isError = true;
        state.message = action.payload;
      })
      // Обработчики для getProperties
      .addCase(getProperties.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(getProperties.fulfilled, (state, action) => {
        state.isLoading = false;
        state.properties = action.payload;
      })
      .addCase(getProperties.rejected, (state, action) => {
        state.isLoading = false;
        state.isError = true;
        state.message = action.payload;
      });
  },
});

export const { reset } = propertiesSlice.actions;
export default propertiesSlice.reducer; 