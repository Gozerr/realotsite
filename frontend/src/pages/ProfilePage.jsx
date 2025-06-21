import React from 'react';
import { useSelector } from 'react-redux';
import { Box, Typography, Card, CardContent, Avatar, Grid } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

function ProfilePage() {
  const { user } = useSelector((state) => state.auth);

  // Пытаемся получить данные о риэлторе из вложенной структуры, если она есть
  const realtorData = user?.user || user;

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Мой профиль
      </Typography>
      <Card>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item>
              <Avatar sx={{ width: 80, height: 80, bgcolor: 'primary.main' }}>
                <AccountCircleIcon sx={{ width: 60, height: 60 }} />
              </Avatar>
            </Grid>
            <Grid item>
              <Typography variant="h5" component="div">
                {realtorData?.full_name || 'Имя не указано'}
              </Typography>
              <Typography color="text.secondary">
                {realtorData?.email || 'Email не указан'}
              </Typography>
               <Typography color="text.secondary" sx={{textTransform: 'capitalize'}}>
                Роль: {realtorData?.role || 'Роль не указана'}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
}

export default ProfilePage; 