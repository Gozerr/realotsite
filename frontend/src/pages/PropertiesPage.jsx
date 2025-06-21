import React from 'react';
import { Box, Typography, Button, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

// Данные-заглушки, пока мы не получаем их с бэкенда
const placeholderProperties = [];

function PropertiesPage() {
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4">
          Объекты недвижимости
        </Typography>
        <Button variant="contained" startIcon={<AddIcon />}>
          Добавить объект
        </Button>
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
              {placeholderProperties.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <Typography sx={{ p: 4 }}>
                      Объекты еще не добавлены. Нажмите "Добавить объект", чтобы начать.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                placeholderProperties.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell>{row.address}</TableCell>
                    <TableCell>{row.price}</TableCell>
                    <TableCell>{row.status}</TableCell>
                    <TableCell>{row.realtor}</TableCell>
                    <TableCell>{/* Здесь будут кнопки действий */}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}

export default PropertiesPage; 