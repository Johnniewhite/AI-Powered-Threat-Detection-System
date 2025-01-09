import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Fade,
  Card,
  CardContent,
  Divider,
  Chip,
  Stack,
  useTheme,
  alpha,
  IconButton
} from '@mui/material';
import { SecurityOutlined, WarningOutlined, CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import { detection } from '../services/api';
import { Detection } from '../types';

const ImageAnalysis: React.FC = () => {
  const theme = useTheme();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Detection | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select an image to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await detection.analyzeImage(file);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze image');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const renderAnalysisResult = () => {
    if (!result) return null;

    return (
      <Fade in={true} timeout={500}>
        <Card 
          elevation={3}
          sx={{
            mt: 4,
            background: alpha(theme.palette.background.paper, 0.8),
            backdropFilter: 'blur(10px)'
          }}
        >
          <CardContent>
            <Typography variant="h6" color="primary" gutterBottom>
              Analysis Results
            </Typography>
            
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                Threat Assessment
              </Typography>
              <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
                <Chip
                  label={`Threat Score: ${(result.threat_score * 100).toFixed(1)}%`}
                  color={result.threat_score > 0.7 ? 'error' : result.threat_score > 0.4 ? 'warning' : 'success'}
                  icon={<WarningOutlined />}
                />
                <Chip
                  label={`Confidence: ${(result.confidence_score * 100).toFixed(1)}%`}
                  color="primary"
                />
              </Stack>
            </Box>

            <Divider sx={{ my: 2 }} />

            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                Detected Indicators
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 2 }}>
                {result.analysis_results.indicators.map((indicator: string, index: number) => (
                  <Chip
                    key={index}
                    label={indicator}
                    size="small"
                    sx={{ mb: 1 }}
                  />
                ))}
              </Stack>
            </Box>

            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                Remediation Suggestions
              </Typography>
              <Stack spacing={1}>
                {result.remediation_suggestions.actions.map((action: string, index: number) => (
                  <Typography key={index} variant="body2" color="text.secondary">
                    • {action}
                  </Typography>
                ))}
              </Stack>
            </Box>

            <Box sx={{ mt: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Priority Level: {result.remediation_suggestions.priority.toUpperCase()}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Fade>
    );
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ mb: 4 }}>
          <SecurityOutlined sx={{ mr: 1, verticalAlign: 'bottom' }} />
          Image Analysis
        </Typography>

        <Paper 
          elevation={2} 
          sx={{ 
            p: 3,
            background: alpha(theme.palette.background.paper, 0.8),
            backdropFilter: 'blur(10px)'
          }}
        >
          <form onSubmit={handleSubmit}>
            <Box
              sx={{
                border: `2px dashed ${theme.palette.divider}`,
                borderRadius: 1,
                p: 3,
                textAlign: 'center',
                cursor: 'pointer',
                '&:hover': {
                  borderColor: theme.palette.primary.main,
                  backgroundColor: alpha(theme.palette.primary.main, 0.04),
                },
                mb: 2
              }}
              component="label"
            >
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                style={{ display: 'none' }}
                disabled={loading}
              />
              <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
              <Typography variant="body1" color="text.secondary">
                {file ? file.name : 'Click or drag to upload an image'}
              </Typography>
            </Box>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <IconButton
                color="primary"
                onClick={handleSubmit}
                disabled={loading || !file}
                size="large"
                sx={{
                  backgroundColor: theme.palette.primary.main,
                  color: 'white',
                  '&:hover': {
                    backgroundColor: theme.palette.primary.dark,
                  },
                  '&:disabled': {
                    backgroundColor: theme.palette.action.disabledBackground,
                  },
                }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : <CloudUploadIcon />}
              </IconButton>
            </Box>
          </form>
        </Paper>

        {renderAnalysisResult()}
      </Box>
    </Container>
  );
};

export default ImageAnalysis; 