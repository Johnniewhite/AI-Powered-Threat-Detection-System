import React, { useState, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Grid,
  useTheme,
  Button,
  IconButton,
  Tooltip,
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../services/api';

interface AnalysisResult {
  threat_score: number;
  confidence_score: number;
  threat_category: string;
  analysis_results: {
    details: string;
  };
  remediation_suggestions: {
    actions: string[];
  };
}

const ImageAnalysis: React.FC = () => {
  const theme = useTheme();
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setResult(null);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.bmp'],
    },
    maxFiles: 1,
    multiple: false,
  });

  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/api/v1/detection/image', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResult(response.data);
    } catch (err) {
      setError('Failed to analyze image. Please try again.');
      console.error('Error analyzing image:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
  };

  const getThreatIcon = (score: number) => {
    if (score >= 0.7) return <ErrorIcon sx={{ color: theme.palette.error.main }} />;
    if (score >= 0.4) return <WarningIcon sx={{ color: theme.palette.warning.main }} />;
    return <CheckCircleIcon sx={{ color: theme.palette.success.main }} />;
  };

  const getThreatColor = (score: number) => {
    if (score >= 0.7) return theme.palette.error.main;
    if (score >= 0.4) return theme.palette.warning.main;
    return theme.palette.success.main;
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper
        sx={{
          p: 3,
          mb: 4,
          background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
          color: 'white',
        }}
      >
        <Typography variant="h4" gutterBottom>
          Image Analysis
        </Typography>
        <Typography variant="subtitle1">
          Upload an image for threat detection analysis
        </Typography>
      </Paper>

      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Paper
            {...getRootProps()}
            sx={{
              p: 3,
              textAlign: 'center',
              cursor: 'pointer',
              backgroundColor: isDragActive
                ? theme.palette.action.hover
                : theme.palette.background.paper,
              border: `2px dashed ${
                isDragActive ? theme.palette.primary.main : theme.palette.divider
              }`,
              '&:hover': {
                backgroundColor: theme.palette.action.hover,
              },
            }}
          >
            <input {...getInputProps()} />
            <UploadIcon sx={{ fontSize: 48, color: theme.palette.primary.main }} />
            <Typography variant="h6" sx={{ mt: 2 }}>
              {isDragActive
                ? 'Drop the image here'
                : 'Drag and drop an image here, or click to select'}
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
              Supported formats: JPEG, PNG, GIF, BMP
            </Typography>
          </Paper>

          {preview && (
            <Box sx={{ mt: 3, position: 'relative' }}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
              >
                <Paper sx={{ p: 2 }}>
                  <img
                    src={preview}
                    alt="Preview"
                    style={{
                      width: '100%',
                      height: 'auto',
                      maxHeight: '300px',
                      objectFit: 'contain',
                    }}
                  />
                  <Box
                    sx={{
                      mt: 2,
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <Typography variant="body2" color="textSecondary">
                      {file?.name}
                    </Typography>
                    <Box>
                      <Tooltip title="Clear">
                        <IconButton onClick={handleClear} size="small">
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Analyze">
                        <IconButton
                          onClick={handleAnalyze}
                          disabled={loading}
                          color="primary"
                          size="small"
                        >
                          {loading ? (
                            <CircularProgress size={24} />
                          ) : (
                            <SecurityIcon />
                          )}
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>
                </Paper>
              </motion.div>
            </Box>
          )}
        </Grid>

        <Grid item xs={12} md={6}>
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
              >
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              </motion.div>
            )}

            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
              >
                <Card>
                  <CardContent>
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        mb: 2,
                      }}
                    >
                      {getThreatIcon(result.threat_score)}
                      <Typography
                        variant="h6"
                        sx={{ ml: 1, color: getThreatColor(result.threat_score) }}
                      >
                        {result.analysis_results.details}
                      </Typography>
                    </Box>

                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="subtitle2" color="textSecondary">
                          Threat Score
                        </Typography>
                        <Typography variant="h4">
                          {(result.threat_score * 100).toFixed(1)}%
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="subtitle2" color="textSecondary">
                          Confidence
                        </Typography>
                        <Typography variant="h4">
                          {(result.confidence_score * 100).toFixed(1)}%
                        </Typography>
                      </Grid>
                    </Grid>

                    <Box sx={{ mt: 3 }}>
                      <Typography variant="subtitle2" color="textSecondary">
                        Recommended Actions
                      </Typography>
                      {result.remediation_suggestions.actions.map((action, index) => (
                        <Alert
                          key={index}
                          severity={
                            result.threat_score >= 0.7
                              ? 'error'
                              : result.threat_score >= 0.4
                              ? 'warning'
                              : 'success'
                          }
                          sx={{ mt: 1 }}
                        >
                          {action}
                        </Alert>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </Grid>
      </Grid>
    </Container>
  );
};

export default ImageAnalysis; 