import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box, Typography, Button, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Modal, TextField, Select, MenuItem, FormControl, InputLabel, CircularProgress, Grid
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { createProperty, getProperties, reset } from '../features/properties/propertiesSlice';

// Fix for default icon issue with Leaflet and Webpack
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Map component to select location in modal
function LocationPicker({ onLocationSelect }) {
  const [position, setPosition] = useState(null);
  const map = useMapEvents({
    click(e) {
      setPosition(e.latlng);
      onLocationSelect(e.latlng);
      map.flyTo(e.latlng, map.getZoom());
    },
  });

  return position === null ? null : (
    <Marker position={position}></Marker>
  );
}

// Стили для модального окна
const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 400,
  bgcolor: 'background.paper',
  boxShadow: 24,
  p: 4,
};

function PropertiesPage() {
  const dispatch = useDispatch();
  const { properties, isLoading, isError, message } = useSelector((state) => state.properties);

  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    address: '',
    description: '',
    price: 0,
    status: 'active',
    latitude: null,
    longitude: null,
  });

  const handleOpen = () => setOpen(true);
  const handleClose = () => setOpen(false);

  const onChange = (e) => {
    setFormData((prevState) => ({
      ...prevState,
      [e.target.name]: e.target.value,
    }));
  };

  const handleLocationSelect = (latlng) => {
    setFormData(prevState => ({ ...prevState, latitude: latlng.lat, longitude: latlng.lng }));
  };

  const onSubmit = (e) => {
    e.preventDefault();
    dispatch(createProperty(formData))
      .unwrap()
      .then(() => {
        handleClose();
        dispatch(getProperties());
      })
      .catch((error) => console.error('Failed to create property:', error));
  };

  useEffect(() => {
    dispatch(getProperties());

    return () => {
      dispatch(reset());
    }
  }, [dispatch]);

  useEffect(() => {
    if (isError) {
      console.error(message); // Позже можно заменить на красивые уведомления
    }
  }, [isError, message]);

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Модальное окно для добавления объекта */}
      <Modal open={open} onClose={handleClose}>
        <Box sx={style} component="form" onSubmit={onSubmit}>
          <Typography variant="h6" component="h2" sx={{mb: 2}}>
            Новый объект
          </Typography>
          <TextField name="address" label="Адрес" value={formData.address} onChange={onChange} fullWidth required sx={{mb: 2}}/>
          <TextField name="description" label="Описание" value={formData.description} onChange={onChange} fullWidth multiline rows={4} sx={{mb: 2}}/>
          <TextField name="price" label="Цена" type="number" value={formData.price} onChange={onChange} fullWidth required sx={{mb: 2}}/>
           <FormControl fullWidth sx={{mb: 2}}>
            <InputLabel>Статус</InputLabel>
            <Select name="status" value={formData.status} label="Статус" onChange={onChange}>
              <MenuItem value="active">Активный</MenuItem>
              <MenuItem value="deal">В сделке</MenuItem>
              <MenuItem value="sold">Продан</MenuItem>
              <MenuItem value="archive">В архиве</MenuItem>
            </Select>
          </FormControl>
          <Typography sx={{mt: 2, mb: 1}}>Укажите расположение на карте</Typography>
          <Box sx={{height: 300, mb: 2}}>
            <MapContainer center={[55.75, 37.57]} zoom={10} style={{ height: '100%', width: '100%' }}>
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              />
              <LocationPicker onLocationSelect={handleLocationSelect} />
            </MapContainer>
          </Box>
          <Button type="submit" variant="contained" disabled={isLoading || !formData.latitude}>
            {isLoading ? 'Сохранение...' : 'Сохранить'}
          </Button>
        </Box>
      </Modal>

      <Grid container spacing={3}>
        {/* MAP VIEW */}
        <Grid item xs={12}>
          <Paper sx={{height: '50vh', p: 1}}>
            <MapContainer center={[55.75, 37.57]} zoom={9} style={{ height: '100%', width: '100%' }}>
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              {properties.map(prop => (
                prop.latitude && prop.longitude && (
                  <Marker key={prop.id} position={[prop.latitude, prop.longitude]}>
                    <Popup>
                      <b>{prop.address}</b><br/>{prop.price} ₽
                    </Popup>
                  </Marker>
                )
              ))}
            </MapContainer>
          </Paper>
        </Grid>

        {/* CONTROLS AND TABLE */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h4">Объекты недвижимости</Typography>
            <Button variant="contained" startIcon={<AddIcon />} onClick={handleOpen}>Добавить объект</Button>
          </Box>
          <Paper>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{fontWeight: 'bold'}}>Адрес</TableCell>
                    <TableCell sx={{fontWeight: 'bold'}}>Цена</TableCell>
                    <TableCell sx={{fontWeight: 'bold'}}>Статус</TableCell>
                    <TableCell sx={{fontWeight: 'bold'}}>Ответственный</TableCell>
                    <TableCell sx={{fontWeight: 'bold'}}>Действия</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {isLoading && properties.length === 0 ? (
                     <TableRow>
                      <TableCell colSpan={5} align="center">
                        <CircularProgress sx={{my: 4}}/>
                      </TableCell>
                    </TableRow>
                  ) : properties.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} align="center">
                        <Typography sx={{ p: 4 }}>
                          Объекты еще не добавлены. Нажмите "Добавить объект", чтобы начать.
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    properties.map((property) => (
                      <TableRow key={property.id}>
                        <TableCell>{property.address}</TableCell>
                        <TableCell>{new Intl.NumberFormat('ru-RU').format(property.price)} ₽</TableCell>
                        <TableCell sx={{textTransform: 'capitalize'}}>{property.status}</TableCell>
                        <TableCell>{property.realtor_id}</TableCell>
                        <TableCell>{/* Здесь будут кнопки действий */}</TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default PropertiesPage; 