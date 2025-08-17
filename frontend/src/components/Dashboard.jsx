import React from 'react';
import { useQuery } from 'react-query';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Security as SecurityIcon,
  VideoLibrary as VideoIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Help as HelpIcon,
  Visibility as ViewIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import api from '../api';

function Dashboard() {
  const navigate = useNavigate();
  
  const { data: dashboardData, isLoading, error } = useQuery(
    'dashboard',
    async () => {
      const response = await api.get('/video/dashboard');
      return response.data;
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        Failed to load dashboard data: {error.message}
      </Alert>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'verified':
        return 'success';
      case 'suspicious':
        return 'error';
      case 'uncertain':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getClassificationColor = (classification) => {
    switch (classification) {
      case 'real':
        return 'success';
      case 'deepfake':
        return 'error';
      case 'uncertain':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getClassificationIcon = (classification) => {
    switch (classification) {
      case 'real':
        return <CheckIcon />;
      case 'deepfake':
        return <WarningIcon />;
      case 'uncertain':
        return <HelpIcon />;
      default:
        return <HelpIcon />;
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      
      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <VideoIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Total Videos
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData?.total_videos || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <CheckIcon color="success" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Real Videos
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData?.real_count || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <WarningIcon color="error" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Deepfakes
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData?.deepfake_count || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <SecurityIcon color="warning" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="h6">
                    Suspicious Locations
                  </Typography>
                  <Typography variant="h4">
                    {dashboardData?.geospatial_suspicious || 0}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Analyses Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Analyses
          </Typography>
          
          {dashboardData?.recent_analyses && dashboardData.recent_analyses.length > 0 ? (
            <TableContainer component={Paper} variant="outlined">
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Tracking ID</TableCell>
                    <TableCell>Classification</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Geospatial</TableCell>
                    <TableCell>Processing Time</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {dashboardData.recent_analyses.map((analysis) => (
                    <TableRow key={analysis.tracking_id}>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {analysis.tracking_id.slice(0, 8)}...
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          icon={getClassificationIcon(analysis.classification)}
                          label={analysis.classification}
                          color={getClassificationColor(analysis.classification)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {(analysis.confidence * 100).toFixed(1)}%
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {analysis.geospatial_verification ? (
                          <Chip
                            label={analysis.geospatial_verification}
                            color={getStatusColor(analysis.geospatial_verification)}
                            size="small"
                          />
                        ) : (
                          <Typography variant="body2" color="textSecondary">
                            N/A
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {analysis.processing_time.toFixed(2)}s
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            onClick={() => navigate(`/analysis/${analysis.tracking_id}`)}
                          >
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Box textAlign="center" py={4}>
              <Typography color="textSecondary">
                No analyses yet. Upload a video to get started!
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}

export default Dashboard;
