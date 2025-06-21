import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Box, Typography, Grid, Card, CardContent, CircularProgress, Avatar, Chip } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { alpha } from '@mui/material/styles';
import { getStats } from '../features/auth/authSlice';

// Импортируем иконки
import AssessmentIcon from '@mui/icons-material/Assessment';
import HomeWorkIcon from '@mui/icons-material/HomeWork';
import DoneAllIcon from '@mui/icons-material/DoneAll';

// Обновленный компонент для красивого отображения статистики с цветной подложкой
const StatCard = ({ title, value, icon, loading, bgColor }) => {
  const theme = useTheme();
  // Делаем цвет очень прозрачным, используя alpha
  const finalBgColor = typeof bgColor === 'string' && bgColor.includes('.')
    ? alpha(theme.palette[bgColor.split('.')[0]][bgColor.split('.')[1]], 0.1)
    : alpha(bgColor, 0.1);

  const finalTextColor = typeof bgColor === 'string' && bgColor.includes('.')
    ? theme.palette[bgColor.split('.')[0]].dark
    : bgColor;


  return (
    <Card sx={{ 
      display: 'flex', 
      alignItems: 'center', 
      p: 2, 
      backgroundColor: finalBgColor,
      color: finalTextColor,
      height: '100%'
    }}>
      <Avatar sx={{ bgcolor: finalTextColor, color: '#fff', mr: 2, width: 56, height: 56 }}>
        {icon}
      </Avatar>
      <Box>
        <Typography variant="h5" component="div" sx={{ fontWeight: 'bold' }}>
          {loading ? <CircularProgress size={24} color="inherit" /> : value}
        </Typography>
        <Typography variant="body2">{title}</Typography>
      </Box>
    </Card>
  );
};

function DashboardPage() {
  const dispatch = useDispatch();
  const { user, stats, isStatsLoading } = useSelector((state) => state.auth);

  useEffect(() => {
    dispatch(getStats());
  }, [dispatch]);

  const hasStats = stats && !isStatsLoading;
  const placeHolderItems = [
    { title: 'Квартира на ул. Ленина, д. 1', desc: '3-комнатная, 72 м², 5/9 эт.'},
    { title: 'Дом в п. Солнечный', desc: '2-этажный, 150 м², 10 сот.'},
    { title: 'Офис в центре', desc: '120 м², open space, панорамные окна'},
    { title: 'Складское помещение', desc: '500 м², высота потолков 8 м.'}
  ];

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box sx={{display: 'flex', alignItems: 'center', mb: 4}}>
        <Typography variant="h4">
          Добро пожаловать, {user ? user.full_name : 'Пользователь'}!
        </Typography>
      </Box>

      {/* Блок со статистикой */}
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard title="Объектов в работе" value={hasStats ? stats.properties_in_work_count : 0} icon={<HomeWorkIcon />} loading={isStatsLoading} bgColor="primary.light" />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard title="Всего сделок" value={hasStats ? stats.total_deals_count : 0} icon={<AssessmentIcon />} loading={isStatsLoading} bgColor="success.light" />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard title="Успешных сделок" value={hasStats ? stats.successful_deals_count : 0} icon={<DoneAllIcon />} loading={isStatsLoading} bgColor="warning.light" />
        </Grid>
        
        {hasStats && stats.properties_in_work_count === 0 && (
          <Grid item xs={12}>
            <Card sx={{ p: 2, backgroundColor: 'primary.light', color: 'primary.contrastText' }}>
              <Typography variant="h6">Начните свой путь к успеху!</Typography>
              <Typography>Добавьте свой первый объект в разделе "Объекты", чтобы увидеть, как ваша статистика растет.</Typography>
            </Card>
          </Grid>
        )}
      </Grid>
      
       <Typography variant="h5" sx={{ mt: 5, mb: 2 }}>
        Последние объекты
      </Typography>
      <Grid container spacing={3}>
        {placeHolderItems.map((item, index) => (
          <Grid item xs={12} sm={6} key={index}>
            <Card sx={{position: 'relative'}}>
              <Chip 
                label="Эксклюзивный объект" 
                color="primary" 
                size="small"
                sx={{ 
                  position: 'absolute',
                  top: 16,
                  right: 16,
                  zIndex: 1,
                  fontWeight: 'bold'
                }} 
              />
              <Box sx={{ height: 140, backgroundColor: 'grey.200' }}/>
              <CardContent>
                <Typography gutterBottom variant="h6" component="div">
                  {item.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {item.desc}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default DashboardPage; 