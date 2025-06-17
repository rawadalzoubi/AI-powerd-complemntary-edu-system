import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Card, CardContent, Typography, Grid, Button, Box, 
  CircularProgress, Chip, Divider, Alert
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { format } from 'date-fns';
import SchoolIcon from '@mui/icons-material/School';
import AssignmentIcon from '@mui/icons-material/Assignment';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import PersonIcon from '@mui/icons-material/Person';

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  transition: 'transform 0.3s, box-shadow 0.3s',
  '&:hover': {
    transform: 'translateY(-5px)',
    boxShadow: theme.shadows[8],
  },
}));

const AssignedLessonsList = ({ assignments, loading, error, onViewLesson }) => {
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!assignments || assignments.length === 0) {
    return (
      <Alert severity="info">
        You don't have any assigned lessons yet. Please contact your advisor.
      </Alert>
    );
  }

  return (
    <Box sx={{ mt: 2 }}>
      <Grid container spacing={3}>
        {assignments.map((assignment) => (
          <Grid item xs={12} sm={6} md={4} key={assignment.id}>
            <StyledCard>
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h6" component="div" gutterBottom>
                  {assignment.lesson_name}
                </Typography>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <SchoolIcon fontSize="small" sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="body2" color="text.secondary">
                    Subject: {assignment.lesson_subject}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <PersonIcon fontSize="small" sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="body2" color="text.secondary">
                    Assigned by: {assignment.advisor_name}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <CalendarTodayIcon fontSize="small" sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="body2" color="text.secondary">
                    Assigned on: {format(new Date(assignment.assigned_date), 'MMM dd, yyyy')}
                  </Typography>
                </Box>
                
                {assignment.due_date && (
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AssignmentIcon fontSize="small" sx={{ mr: 1, color: 'warning.main' }} />
                    <Typography variant="body2" color="warning.main">
                      Due by: {format(new Date(assignment.due_date), 'MMM dd, yyyy')}
                    </Typography>
                  </Box>
                )}
                
                <Divider sx={{ my: 1.5 }} />
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Chip 
                    label={assignment.completed ? 'Completed' : 'In Progress'} 
                    color={assignment.completed ? 'success' : 'primary'} 
                    size="small"
                  />
                  
                  {onViewLesson ? (
                    <Button 
                      variant="contained" 
                      size="small"
                      onClick={() => onViewLesson(assignment.lesson)}
                    >
                      View Lesson
                    </Button>
                  ) : (
                    <Button 
                      component={Link} 
                      to={`/student/lessons/${assignment.lesson}`} 
                      variant="contained" 
                      size="small"
                    >
                      View Lesson
                    </Button>
                  )}
                </Box>
              </CardContent>
            </StyledCard>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default AssignedLessonsList; 