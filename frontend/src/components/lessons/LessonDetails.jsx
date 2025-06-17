import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Box, Typography, Grid, Card, CardContent, Tabs, Tab, Button, 
  CircularProgress, Alert, Divider, Container, Paper 
} from '@mui/material';
import VideocamIcon from '@mui/icons-material/Videocam';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import QuizIcon from '@mui/icons-material/Quiz';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import studentDashboardService from '../../services/studentDashboardService';
import VideoLessonContent from './VideoLessonContent';
import PdfLessonContent from './PdfLessonContent';
import QuizContent from './QuizContent';

// Custom TabPanel component
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`lesson-tabpanel-${index}`}
      aria-labelledby={`lesson-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const LessonDetails = () => {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState(null);
  const [videoContents, setVideoContents] = useState([]);
  const [pdfContents, setPdfContents] = useState([]);
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    const fetchLessonData = async () => {
      try {
        setLoading(true);
        
        // Fetch the lesson details
        const lessonData = await studentDashboardService.getLessonDetails(lessonId);
        setLesson(lessonData);
        
        // Fetch video content
        const videoData = await studentDashboardService.getLessonContents(lessonId, 'VIDEO');
        setVideoContents(videoData);
        
        // Fetch PDF content
        const pdfData = await studentDashboardService.getLessonContents(lessonId, 'PDF');
        setPdfContents(pdfData);
        
        // Fetch quizzes
        const quizzesData = await studentDashboardService.getLessonQuizzes(lessonId);
        setQuizzes(quizzesData);
        
        setError(null);
      } catch (err) {
        setError('Failed to load lesson details. Please try again later.');
        console.error('Error fetching lesson details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchLessonData();
  }, [lessonId]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleBackClick = () => {
    navigate('/student/dashboard');
  };

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

  if (!lesson) {
    return <Alert severity="warning">Lesson not found or not assigned to you.</Alert>;
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={handleBackClick}
          sx={{ mb: 2 }}
        >
          Back to Dashboard
        </Button>
        
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            {lesson.name}
          </Typography>
          
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
            <Typography variant="body1" color="text.secondary">
              Subject: <strong>{lesson.subject}</strong>
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Grade Level: <strong>{lesson.level_display}</strong>
            </Typography>
          </Box>
          
          {lesson.description && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="body1">{lesson.description}</Typography>
            </>
          )}
        </Paper>
        
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={tabValue} 
            onChange={handleTabChange} 
            aria-label="lesson content tabs"
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab icon={<VideocamIcon />} label="Videos" id="lesson-tab-0" aria-controls="lesson-tabpanel-0" />
            <Tab icon={<PictureAsPdfIcon />} label="PDF Materials" id="lesson-tab-1" aria-controls="lesson-tabpanel-1" />
            <Tab icon={<QuizIcon />} label="Quizzes" id="lesson-tab-2" aria-controls="lesson-tabpanel-2" />
          </Tabs>
        </Box>
        
        <TabPanel value={tabValue} index={0}>
          <VideoLessonContent videoContents={videoContents} />
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
          <PdfLessonContent pdfContents={pdfContents} />
        </TabPanel>
        
        <TabPanel value={tabValue} index={2}>
          <QuizContent quizzes={quizzes} />
        </TabPanel>
      </Box>
    </Container>
  );
};

export default LessonDetails; 