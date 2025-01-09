import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
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
  alpha
} from '@mui/material';
import { SecurityOutlined, SendOutlined, WarningOutlined } from '@mui/icons-material';
import { detection } from '../services/api';

interface Detection {
  threat_score: number;
  confidence_score: number;
  threat_category: string;
  analysis_results: {
    details: string;
    indicators: string[];
  };
  remediation_suggestions: {
    actions: string[];
    priority: string;
  };
}

const TextAnalysis: React.FC = () => {
  const theme = useTheme();
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Detection | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await detection.analyzeText(text);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze text');
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
          Text Analysis
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
            <TextField
              fullWidth
              multiline
              rows={6}
              variant="outlined"
              placeholder="Enter text to analyze for potential security threats..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={loading}
              sx={{ mb: 2 }}
            />

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                size="large"
                disabled={loading || !text.trim()}
                startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SendOutlined />}
              >
                {loading ? 'Analyzing...' : 'Analyze Text'}
              </Button>
            </Box>
          </form>
        </Paper>

        {renderAnalysisResult()}
      </Box>
    </Container>
  );
};

export default TextAnalysis; 