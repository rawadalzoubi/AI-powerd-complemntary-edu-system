import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Box, Typography, Grid, Card, CardContent, Button, 
  Alert, Divider, LinearProgress, Chip, List, ListItem,
  ListItemText, Dialog, DialogTitle, DialogContent, 
  DialogActions, Radio, RadioGroup, FormControlLabel, FormControl
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import QuizIcon from '@mui/icons-material/Quiz';
import TimerIcon from '@mui/icons-material/Timer';
import AssessmentIcon from '@mui/icons-material/Assessment';
import studentDashboardService from '../../services/studentDashboardService';

const QuizContent = ({ quizzes }) => {
  const navigate = useNavigate();
  const [attempts, setAttempts] = useState({});
  const [loading, setLoading] = useState(false);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [quizDialogOpen, setQuizDialogOpen] = useState(false);
  const [currentAttempt, setCurrentAttempt] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [quizResult, setQuizResult] = useState(null);
  const [error, setError] = useState(null);

  // Fetch attempts data for each quiz
  useEffect(() => {
    const fetchQuizAttempts = async () => {
      if (!quizzes || quizzes.length === 0) return;
      
      const attemptsData = {};
      
      for (const quiz of quizzes) {
        try {
          const quizAttempts = await studentDashboardService.getQuizAttempts(quiz.id);
          attemptsData[quiz.id] = quizAttempts;
        } catch (err) {
          console.error(`Error fetching attempts for quiz ${quiz.id}:`, err);
          attemptsData[quiz.id] = [];
        }
      }
      
      setAttempts(attemptsData);
    };
    
    fetchQuizAttempts();
  }, [quizzes]);

  const handleStartQuiz = async (quiz) => {
    try {
      setLoading(true);
      setError(null);
      
      // Start a new quiz attempt
      const attempt = await studentDashboardService.startQuizAttempt(quiz.id);
      
      setSelectedQuiz(quiz);
      setCurrentAttempt(attempt);
      setCurrentQuestionIndex(0);
      setSelectedAnswers({});
      setQuizCompleted(false);
      setQuizResult(null);
      setQuizDialogOpen(true);
    } catch (err) {
      setError('Failed to start the quiz. Please try again later.');
      console.error('Error starting quiz:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseQuiz = () => {
    if (!quizCompleted && currentAttempt) {
      // Ask for confirmation before closing an incomplete quiz
      if (window.confirm('Are you sure you want to exit this quiz? Your progress will be lost.')) {
        setQuizDialogOpen(false);
      }
    } else {
      setQuizDialogOpen(false);
    }
  };

  const handleAnswerSelect = (questionId, answerId) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionId]: answerId
    });
  };

  const handleNextQuestion = async () => {
    if (!selectedQuiz || !currentAttempt) return;
    
    const currentQuestion = selectedQuiz.questions[currentQuestionIndex];
    const selectedAnswerId = selectedAnswers[currentQuestion.id];
    
    if (!selectedAnswerId) {
      alert('Please select an answer before proceeding.');
      return;
    }
    
    try {
      // Submit the answer
      await studentDashboardService.submitQuizAnswer(
        currentAttempt.id, 
        currentQuestion.id, 
        selectedAnswerId
      );
      
      // If this is the last question, complete the quiz
      if (currentQuestionIndex === selectedQuiz.questions.length - 1) {
        await completeQuiz();
      } else {
        // Otherwise, move to the next question
        setCurrentQuestionIndex(currentQuestionIndex + 1);
      }
    } catch (err) {
      setError('Failed to submit your answer. Please try again.');
      console.error('Error submitting answer:', err);
    }
  };

  const completeQuiz = async () => {
    try {
      setLoading(true);
      
      // Complete the quiz attempt
      const result = await studentDashboardService.completeQuizAttempt(currentAttempt.id);
      
      setQuizCompleted(true);
      setQuizResult(result);
      
      // Update the attempts list
      const updatedAttempts = {
        ...attempts,
        [selectedQuiz.id]: [result, ...(attempts[selectedQuiz.id] || [])]
      };
      
      setAttempts(updatedAttempts);
    } catch (err) {
      setError('Failed to complete the quiz. Please try again later.');
      console.error('Error completing quiz:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderQuizContent = () => {
    if (!selectedQuiz || !currentAttempt) return null;
    
    if (quizCompleted && quizResult) {
      // Render quiz results
      return (
        <Box>
          <Typography variant="h6" gutterBottom>
            Quiz Completed!
          </Typography>
          
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center',
            p: 3,
            bgcolor: 'background.paper',
            borderRadius: 2,
            boxShadow: 2,
            mb: 3
          }}>
            <Typography variant="h4" gutterBottom color="primary">
              {quizResult.percentage_score.toFixed(0)}%
            </Typography>
            
            <Typography variant="subtitle1" gutterBottom>
              Score: {quizResult.score} out of {quizResult.max_score}
            </Typography>
            
            <LinearProgress 
              variant="determinate" 
              value={quizResult.percentage_score} 
              sx={{ width: '100%', mt: 1, mb: 2, height: 10, borderRadius: 5 }}
            />
            
            <Chip 
              icon={<CheckCircleIcon />} 
              label={quizResult.percentage_score >= 70 ? "Passed" : "Needs Improvement"} 
              color={quizResult.percentage_score >= 70 ? "success" : "warning"}
              sx={{ mt: 1 }}
            />
          </Box>
          
          <Box sx={{ mt: 3 }}>
            <Button 
              variant="contained" 
              color="primary" 
              fullWidth
              onClick={handleCloseQuiz}
            >
              Close
            </Button>
          </Box>
        </Box>
      );
    }
    
    // Render quiz questions
    const currentQuestion = selectedQuiz.questions[currentQuestionIndex];
    
    return (
      <Box>
        <LinearProgress 
          variant="determinate" 
          value={(currentQuestionIndex / selectedQuiz.questions.length) * 100} 
          sx={{ mb: 3 }}
        />
        
        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
          Question {currentQuestionIndex + 1} of {selectedQuiz.questions.length}
        </Typography>
        
        <Typography variant="h6" gutterBottom>
          {currentQuestion.text}
        </Typography>
        
        <FormControl component="fieldset" sx={{ width: '100%', mt: 2 }}>
          <RadioGroup
            value={selectedAnswers[currentQuestion.id] || ''}
            onChange={(e) => handleAnswerSelect(currentQuestion.id, e.target.value)}
          >
            {currentQuestion.answers.map((answer) => (
              <FormControlLabel
                key={answer.id}
                value={answer.id.toString()}
                control={<Radio />}
                label={answer.text}
                sx={{ 
                  mb: 1, 
                  p: 1, 
                  borderRadius: 1,
                  '&:hover': { bgcolor: 'action.hover' } 
                }}
              />
            ))}
          </RadioGroup>
        </FormControl>
        
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'space-between' }}>
          <Button 
            variant="outlined" 
            onClick={handleCloseQuiz}
          >
            Exit Quiz
          </Button>
          
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleNextQuestion}
            disabled={!selectedAnswers[currentQuestion.id]}
          >
            {currentQuestionIndex === selectedQuiz.questions.length - 1 ? 'Submit Quiz' : 'Next Question'}
          </Button>
        </Box>
      </Box>
    );
  };

  if (!quizzes || quizzes.length === 0) {
    return (
      <Alert severity="info">
        No quizzes available for this lesson. Please check the other materials.
      </Alert>
    );
  }

  return (
    <>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Quizzes
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Test your understanding by taking these quizzes.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {quizzes.map((quiz) => {
          const quizAttempts = attempts[quiz.id] || [];
          const bestScore = quizAttempts.length > 0 
            ? Math.max(...quizAttempts.map(a => a.percentage_score || 0))
            : 0;
          const hasPassed = bestScore >= 70;
          
          return (
            <Grid item xs={12} sm={6} key={quiz.id}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {quiz.title}
                  </Typography>
                  
                  <Divider sx={{ my: 1 }} />
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <QuizIcon fontSize="small" sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="body2">
                        {quiz.questions.length} Questions
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <TimerIcon fontSize="small" sx={{ mr: 1, color: 'primary.main' }} />
                      <Typography variant="body2">
                        {Math.ceil(quiz.questions.length * 1.5)} min
                      </Typography>
                    </Box>
                  </Box>
                  
                  {quizAttempts.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Your Progress
                      </Typography>
                      
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <LinearProgress 
                          variant="determinate" 
                          value={bestScore} 
                          sx={{ flexGrow: 1, mr: 2, height: 8, borderRadius: 5 }}
                        />
                        <Typography variant="body2" color="text.secondary">
                          {bestScore.toFixed(0)}%
                        </Typography>
                      </Box>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="caption" color="text.secondary">
                          Attempts: {quizAttempts.length}
                        </Typography>
                        
                        {hasPassed && (
                          <Chip 
                            label="Passed" 
                            color="success" 
                            size="small"
                          />
                        )}
                      </Box>
                    </Box>
                  )}
                  
                  <Button
                    variant="contained"
                    color="primary"
                    fullWidth
                    onClick={() => handleStartQuiz(quiz)}
                    disabled={loading}
                    sx={{ mt: 2 }}
                  >
                    {quizAttempts.length > 0 ? 'Retake Quiz' : 'Start Quiz'}
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Quiz Dialog */}
      <Dialog
        open={quizDialogOpen}
        onClose={handleCloseQuiz}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedQuiz?.title}
        </DialogTitle>
        <DialogContent dividers>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            renderQuizContent()
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default QuizContent; 