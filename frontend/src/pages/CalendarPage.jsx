import React from 'react';
import { Box, Typography } from '@mui/material';

function CalendarPage() {
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Календарь
      </Typography>
      <Typography>
        Раздел с календарем событий, показов и сделок находится в разработке.
      </Typography>
    </Box>
  );
}

export default CalendarPage; 