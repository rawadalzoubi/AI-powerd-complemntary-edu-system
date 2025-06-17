import React, { useState } from 'react';
import { 
  Box, Typography, Grid, Card, CardContent, 
  Button, Alert, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import DownloadIcon from '@mui/icons-material/Download';
import VisibilityIcon from '@mui/icons-material/Visibility';

// Backend URL for media files
const BACKEND_URL = 'http://localhost:8000';

// Helper function to get proxy URL for PDF files to avoid CORS issues
const getPdfProxyUrl = (url) => {
  if (!url) return '';
  
  console.log("Original PDF URL:", url);
  
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
  
  // Create the proxy URL
  const proxyUrl = `${BACKEND_URL}/api/pdf-proxy/?file=${encodeURIComponent(relativePath)}`;
  console.log("PDF Proxy URL:", proxyUrl);
  return proxyUrl;
};

// Helper function to get file serving URL (used for downloads)
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

// Helper function to get full URL for media files (used for display)
const getFullMediaUrl = (url) => {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  if (url.startsWith('/media/')) return `${BACKEND_URL}${url}`;
  return `${BACKEND_URL}/media/${url}`; 
};

// Helper function to get PDF viewer URL using Google PDF Viewer as fallback
const getPdfViewerUrl = (url) => {
  if (!url) return '';
  
  const fullUrl = getFullMediaUrl(url);
  console.log("Full PDF URL:", fullUrl);
  
  // Use Google PDF Viewer as a reliable fallback
  return `https://docs.google.com/viewer?url=${encodeURIComponent(fullUrl)}&embedded=true`;
};

const PdfLessonContent = ({ pdfContents }) => {
  const [selectedPdf, setSelectedPdf] = useState(null);
  const [pdfDialogOpen, setPdfDialogOpen] = useState(false);
  const [pdfError, setPdfError] = useState(false);

  const handleViewPdf = (pdf) => {
    setPdfError(false);
    setSelectedPdf({
      ...pdf,
      file: pdf.file,
      viewerUrl: getPdfViewerUrl(pdf.file)
    });
    setPdfDialogOpen(true);
    console.log("Opening PDF with Google Viewer:", getPdfViewerUrl(pdf.file));
  };

  const handleCloseDialog = () => {
    setPdfDialogOpen(false);
    setSelectedPdf(null);
    setPdfError(false);
  };

  const handlePdfError = (error) => {
    console.error("PDF failed to load:", error);
    setPdfError(true);
  };

  const handleDownloadPdf = (pdfUrl, title) => {
    // Get file serving URL
    const fileUrl = getFileServingUrl(pdfUrl);
    console.log("Downloading PDF from URL:", fileUrl);
    
    // Create a link element
    const link = document.createElement('a');
    link.href = fileUrl;
    
    // Set download attribute with filename
    link.download = title.replace(/\s+/g, '_').toLowerCase() + '.pdf';
    
    // Append to the document
    document.body.appendChild(link);
    
    // Trigger the download
    link.click();
    
    // Clean up
    document.body.removeChild(link);
  };

  if (!pdfContents || pdfContents.length === 0) {
    return (
      <Alert severity="info">
        No PDF materials available for this lesson. Please check the other materials.
      </Alert>
    );
  }

  return (
    <>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          PDF Materials
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Download and review these PDF materials to reinforce your understanding.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {pdfContents.map((pdf) => (
          <Grid item xs={12} sm={6} md={4} key={pdf.id}>
            <Card 
              sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                },
              }}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <PictureAsPdfIcon 
                    sx={{ 
                      fontSize: 40, 
                      color: '#f44336', 
                      mr: 2 
                    }} 
                  />
                  <Typography variant="h6" component="div">
                    {pdf.title}
                  </Typography>
                </Box>
                
                <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<VisibilityIcon />}
                    fullWidth
                    onClick={() => handleViewPdf(pdf)}
                  >
                    View PDF
                  </Button>
                  <Button
                    variant="outlined"
                    color="primary"
                    startIcon={<DownloadIcon />}
                    fullWidth
                    onClick={() => handleDownloadPdf(pdf.file, pdf.title)}
                  >
                    Download PDF
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* PDF Viewer Dialog */}
      <Dialog
        open={pdfDialogOpen}
        onClose={handleCloseDialog}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          {selectedPdf?.title}
        </DialogTitle>
        <DialogContent sx={{ height: '80vh', p: 0 }}>
          {selectedPdf && (
            <>
              {!pdfError ? (
                <iframe 
                  src={selectedPdf.viewerUrl}
                  style={{ width: '100%', height: '100%', border: 'none' }}
                  onError={handlePdfError}
                  title={selectedPdf.title}
                />
              ) : (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography variant="body1" color="error" gutterBottom>
                    The PDF could not be displayed in the browser.
                  </Typography>
                  <Button 
                    onClick={() => handleDownloadPdf(selectedPdf.file, selectedPdf.title)}
                    variant="contained" 
                    color="primary"
                    sx={{ mt: 2 }}
                  >
                    Download PDF
                  </Button>
                </Box>
              )}
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Close</Button>
          <Button 
            onClick={() => handleDownloadPdf(selectedPdf?.file, selectedPdf?.title)}
            color="primary"
          >
            Download
          </Button>
        </DialogActions>
      </Dialog>

      <Box sx={{ mt: 4 }}>
        <Alert severity="info">
          <Typography variant="body2">
            TIP: For better learning experience, download all PDF materials and study them along with the video lessons.
          </Typography>
        </Alert>
      </Box>
    </>
  );
};

export default PdfLessonContent; 