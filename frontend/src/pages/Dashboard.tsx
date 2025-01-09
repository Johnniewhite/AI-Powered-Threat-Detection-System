import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
  useTheme,
  alpha
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { dashboard } from '../services/api';

interface DashboardStats {
  total_detections: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  recent_detections: Array<{
    id: string;
    threat_score: number;
    threat_category: string;
    created_at: string;
  }>;
}

const Dashboard: React.FC = () => {
  const theme = useTheme();
  const { isAuthenticated } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      if (!isAuthenticated()) {
        setError('Authentication required');
        setLoading(false);
        return;
      }

      try {
        const data = await dashboard.getStats();
        setStats(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch dashboard stats');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [isAuthenticated]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  if (!stats) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="info">No dashboard data available</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Total Detections */}
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              background: alpha(theme.palette.background.paper, 0.8),
              backdropFilter: 'blur(10px)'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6" component="h2">
                Total Detections
              </Typography>
            </Box>
            <Typography variant="h3" component="p">
              {stats.total_detections}
            </Typography>
          </Paper>
        </Grid>

        {/* High Risk */}
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              background: alpha(theme.palette.background.paper, 0.8),
              backdropFilter: 'blur(10px)'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <WarningIcon color="error" sx={{ mr: 1 }} />
              <Typography variant="h6" component="h2">
                High Risk
              </Typography>
            </Box>
            <Typography variant="h3" component="p" color="error">
              {stats.high_risk_count}
            </Typography>
          </Paper>
        </Grid>

        {/* Medium Risk */}
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              background: alpha(theme.palette.background.paper, 0.8),
              backdropFilter: 'blur(10px)'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <SecurityIcon color="warning" sx={{ mr: 1 }} />
              <Typography variant="h6" component="h2">
                Medium Risk
              </Typography>
            </Box>
            <Typography variant="h3" component="p" color="warning.main">
              {stats.medium_risk_count}
            </Typography>
          </Paper>
        </Grid>

        {/* Low Risk */}
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              background: alpha(theme.palette.background.paper, 0.8),
              backdropFilter: 'blur(10px)'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <CheckCircleIcon color="success" sx={{ mr: 1 }} />
              <Typography variant="h6" component="h2">
                Low Risk
              </Typography>
            </Box>
            <Typography variant="h3" component="p" color="success.main">
              {stats.low_risk_count}
            </Typography>
          </Paper>
        </Grid>

        {/* Recent Detections */}
        <Grid item xs={12}>
          <Paper
            sx={{
              p: 2,
              background: alpha(theme.palette.background.paper, 0.8),
              backdropFilter: 'blur(10px)'
            }}
          >
            <Typography variant="h6" gutterBottom component="h2">
              Recent Detections
            </Typography>
            {stats.recent_detections.length > 0 ? (
              <Box>
                {stats.recent_detections.map((detection) => (
                  <Box
                    key={detection.id}
                    sx={{
                      py: 1,
                      borderBottom: 1,
                      borderColor: 'divider',
                      '&:last-child': { borderBottom: 0 }
                    }}
                  >
                    <Grid container alignItems="center" spacing={2}>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="subtitle2" color="text.secondary">
                          {new Date(detection.created_at).toLocaleDateString()}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Typography>{detection.threat_category}</Typography>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Typography
                          color={
                            detection.threat_score > 0.7
                              ? 'error'
                              : detection.threat_score > 0.4
                              ? 'warning.main'
                              : 'success.main'
                          }
                        >
                          Risk Score: {(detection.threat_score * 100).toFixed(1)}%
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>
                ))}
              </Box>
            ) : (
              <Typography color="text.secondary">No recent detections</Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard; 