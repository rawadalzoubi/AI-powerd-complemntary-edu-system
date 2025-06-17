import React, { useState } from 'react';
import { 
  Box, Typography, Grid, Card, CardContent, CardMedia, 
  Button, Alert, List, ListItem, ListItemIcon, ListItemText,
  Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import OndemandVideoIcon from '@mui/icons-material/OndemandVideo';

// Backend URL for media files
const BACKEND_URL = 'http://localhost:8000';

// Helper function to get file serving URL (for downloads)
const getFileServingUrl = (url) => {
  if (!url) return '';
  
  // Extract the relative path from the full URL
  let relativePath = url;
  if (url.startsWith('http://') || url.startsWith('https://')) {
    const urlObj = new URL(url);
    relativePath = urlObj.pathname;
  }
  
  // Make sure we have a proper media path
  if (!relativePath.startsWith('/media/') && !relativePath.startsWith('media/')) {
    relativePath = `/media/${relativePath}`;
  }
  
  // Create the file serving URL
  return `${BACKEND_URL}/api/file-serve/?file=${encodeURIComponent(relativePath)}`;
};

// Helper function to get full URL for media files
const getFullMediaUrl = (url) => {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  if (url.startsWith('/media/')) return `${BACKEND_URL}${url}`;
  return `${BACKEND_URL}/media/${url}`; 
};

const VideoLessonContent = ({ videoContents }) => {
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [videoDialogOpen, setVideoDialogOpen] = useState(false);
  const [videoError, setVideoError] = useState(false);

  const handleVideoClick = (video) => {
    setVideoError(false);
    setSelectedVideo({
      ...video,
      // Ensure we have the full URL to the media file
      file: getFullMediaUrl(video.file)
    });
    setVideoDialogOpen(true);
    console.log("Opening video URL:", getFullMediaUrl(video.file));
  };

  const handleCloseDialog = () => {
    setVideoDialogOpen(false);
    setSelectedVideo(null);
    setVideoError(false);
  };

  const handleVideoError = () => {
    console.error("Video failed to load:", selectedVideo?.file);
    setVideoError(true);
  };

  if (!videoContents || videoContents.length === 0) {
    return (
      <Alert severity="info">
        No video content available for this lesson. Please check the other materials.
      </Alert>
    );
  }

  return (
    <>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Video Lessons
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Watch the following video lessons to understand the concepts better.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {videoContents.map((video) => (
          <Grid item xs={12} sm={6} md={4} key={video.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardMedia
                component="div"
                sx={{
                  pt: '56.25%', // 16:9 aspect ratio
                  position: 'relative',
                  bgcolor: 'rgba(0, 0, 0, 0.08)',
                }}
              >
                <Box
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <OndemandVideoIcon sx={{ fontSize: 60, color: 'primary.main' }} />
                </Box>
              </CardMedia>
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h6" component="div" gutterBottom>
                  {video.title}
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<PlayArrowIcon />}
                    fullWidth
                    onClick={() => handleVideoClick(video)}
                  >
                    Watch Video
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Video Player Dialog */}
      <Dialog
        open={videoDialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedVideo?.title}
        </DialogTitle>
        <DialogContent>
          {selectedVideo && (
            <Box sx={{ width: '100%', mt: 2 }}>
              {!videoError ? (
              <video
                controls
                width="100%"
                height="auto"
                style={{ maxHeight: '70vh' }}
                src={selectedVideo.file}
                  onError={handleVideoError}
                  autoPlay
              >
                  <source src={selectedVideo.file} type="video/mp4" />
                  <source src={selectedVideo.file} type="video/webm" />
                Your browser does not support the video tag.
              </video>
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="error" gutterBottom>
                    The video could not be played. It might be in a format not supported by your browser.
                  </Typography>
                  <Button 
                    href={getFileServingUrl(selectedVideo.file)} 
                    download 
                    variant="contained" 
                    color="primary"
                    sx={{ mt: 2 }}
                  >
                    Download Video
                  </Button>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Close</Button>
          <Button 
            href={getFileServingUrl(selectedVideo?.file)} 
            download
            color="primary"
          >
            Download
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default VideoLessonContent; 