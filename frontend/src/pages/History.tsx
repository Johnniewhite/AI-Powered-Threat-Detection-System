import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import dayjs from 'dayjs';
import { detection } from '../services/api';

interface Detection {
  id: string;
  detection_type: string;
  threat_score: number;
  threat_category: string;
  created_at: string;
  confidence_score: number;
  analysis_results: Record<string, string>;
  remediation_suggestions: Record<string, string[]>;
}

export const History: React.FC = () => {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const data = await detection.getList(page * rowsPerPage, rowsPerPage);
        setDetections(data);
      } catch (err) {
        setError('Failed to load detection history');
        console.error('History fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [page, rowsPerPage]);

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const getThreatColor = (score: number) => {
    if (score >= 0.7) return 'error';
    if (score >= 0.4) return 'warning';
    return 'success';
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '60vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Paper
          sx={{
            p: 3,
            mb: 4,
            background: 'linear-gradient(45deg, #2196f3, #1976d2)',
            color: 'white',
          }}
        >
          <Typography variant="h4" gutterBottom>
            Detection History
          </Typography>
          <Typography variant="subtitle1">
            View your past threat detection results
          </Typography>
        </Paper>

        {error ? (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        ) : (
          <Paper>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Threat Type</TableCell>
                    <TableCell>Threat Score</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {detections
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((detection) => (
                      <TableRow key={detection.id}>
                        <TableCell>
                          {dayjs(detection.created_at).format('MMM D, YYYY h:mm A')}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={detection.detection_type?.toUpperCase() || 'N/A'}
                            size="small"
                            color="primary"
                          />
                        </TableCell>
                        <TableCell>{detection.threat_category || 'N/A'}</TableCell>
                        <TableCell>
                          <Chip
                            label={`${Math.round(detection.threat_score * 100)}%`}
                            size="small"
                            color={getThreatColor(detection.threat_score)}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                </TableBody>
              </Table>
            </TableContainer>
            <TablePagination
              rowsPerPageOptions={[5, 10, 25]}
              component="div"
              count={detections.length}
              rowsPerPage={rowsPerPage}
              page={page}
              onPageChange={handleChangePage}
              onRowsPerPageChange={handleChangeRowsPerPage}
            />
          </Paper>
        )}
      </Box>
    </Container>
  );
};

export default History; 