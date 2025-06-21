import React from 'react';
import { useSelector } from 'react-redux';
import { Box, Typography, Grid, Paper } from '@mui/material';

function DashboardPage() {
  // Получаем данные пользователя из Redux state
  const { user } = useSelector((state) => state.auth);

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Дашборд
      </Typography>
      <Typography variant="h6" sx={{ mb: 4 }}>
        {/* Приветствуем пользователя по имени, если оно есть */}
        Добро пожаловать, {user ? user.full_name : 'Пользователь'}!
      </Typography>
      <Grid container spacing={3}>
        {/* Пример виджета статистики */}
        <Grid item xs={12} md={6} lg={4}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column', height: 240 }}>
            <Typography variant="h6" color="primary" gutterBottom>
              Ваша статистика
            </Typography>
            {/* Здесь будет компонент со статистикой */}
            <Typography>Объектов в работе: 5</Typography>
            <Typography>Сделок в этом месяце: 2</Typography>
          </Paper>
        </Grid>
        {/* Пример виджета последних объектов */}
        <Grid item xs={12} md={6} lg={8}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
             <Typography variant="h6" color="primary" gutterBottom>
              Последние добавленные объекты
            </Typography>
            {/* Здесь будет список объектов */}
             <Typography>1. Квартира на ул. Ленина, д. 1</Typography>
             <Typography>2. Дом в п. Солнечный</Typography>
          </Paper>
        </Grid>
        {/* Пример виджета уведомлений */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" color="primary" gutterBottom>
              Новые уведомления
            </Typography>
            {/* Здесь будет список уведомлений */}
            <Typography>1. Статус объекта "Дом в п. Солнечный" изменен на "Задаток".</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default DashboardPage; 