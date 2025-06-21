import React from 'react';
import { Box, Typography } from '@mui/material';

function ClientsPage() {
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Клиенты
      </Typography>
      <Typography>
        Раздел для управления клиентской базой находится в разработке.
      </Typography>
    </Box>
  );
}

export default ClientsPage; 