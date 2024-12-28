import React, { useState } from 'react';
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
  TextField,
  Button,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon,
  Delete as DeleteIcon,
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

const TextAnalysis: React.FC = () => {
  const theme = useTheme();
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const handleAnalyze = async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.post('/api/v1/detection/text', { text });
      setResult(response.data);
    } catch (err) {
      setError('Failed to analyze text. Please try again.');
      console.error('Error analyzing text:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setText('');
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

  const getProgressColor = (score: number) => {
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
          Text Analysis
        </Typography>
        <Typography variant="subtitle1">
          Enter text content for threat detection analysis
        </Typography>
      </Paper>

      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <TextField
              fullWidth
              multiline
              rows={10}
              variant="outlined"
              placeholder="Enter text to analyze..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-root': {
                  '&.Mui-focused fieldset': {
                    borderColor: theme.palette.primary.main,
                  },
                },
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
                {text.length} characters
              </Typography>
              <Box>
                <Tooltip title="Clear">
                  <IconButton
                    onClick={handleClear}
                    size="small"
                    disabled={!text || loading}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
                <Button
                  variant="contained"
                  onClick={handleAnalyze}
                  disabled={!text.trim() || loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <SecurityIcon />}
                  sx={{ ml: 1 }}
                >
                  Analyze
                </Button>
              </Box>
            </Box>
          </Paper>
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
                        <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                          <CircularProgress
                            variant="determinate"
                            value={result.threat_score * 100}
                            size={80}
                            sx={{ color: getProgressColor(result.threat_score) }}
                          />
                          <Box
                            sx={{
                              top: 0,
                              left: 0,
                              bottom: 0,
                              right: 0,
                              position: 'absolute',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                            }}
                          >
                            <Typography variant="caption" component="div">
                              {`${(result.threat_score * 100).toFixed(1)}%`}
                            </Typography>
                          </Box>
                        </Box>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="subtitle2" color="textSecondary">
                          Confidence
                        </Typography>
                        <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                          <CircularProgress
                            variant="determinate"
                            value={result.confidence_score * 100}
                            size={80}
                            sx={{ color: theme.palette.primary.main }}
                          />
                          <Box
                            sx={{
                              top: 0,
                              left: 0,
                              bottom: 0,
                              right: 0,
                              position: 'absolute',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                            }}
                          >
                            <Typography variant="caption" component="div">
                              {`${(result.confidence_score * 100).toFixed(1)}%`}
                            </Typography>
                          </Box>
                        </Box>
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

export default TextAnalysis; 