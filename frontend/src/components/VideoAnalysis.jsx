import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Security as SecurityIcon,
  LocationOn as LocationIcon,
  VideoLibrary as VideoIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Help as HelpIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import api from '../api';

function VideoAnalysis() {
  const { trackingId } = useParams();
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchAnalysisData();
  }, [trackingId]);

  const fetchAnalysisData = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/video/analysis/${trackingId}`);
      setAnalysisData(response.data);
      setError('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch analysis data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchAnalysisData();
    setRefreshing(false);
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

  const getGeospatialColor = (status) => {
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

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error">
        {error}
        <Button onClick={handleRefresh} sx={{ ml: 2 }}>
          Retry
        </Button>
      </Alert>
    );
  }

  if (!analysisData) {
    return (
      <Alert severity="warning">
        No analysis data found for this video.
      </Alert>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">
          Video Analysis Results
        </Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={handleRefresh}
          disabled={refreshing}
        >
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </Button>
      </Box>

      {/* Video Information */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Video Information
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="textSecondary">
                Tracking ID:
              </Typography>
              <Typography variant="body1" fontFamily="monospace">
                {analysisData.tracking_id}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="textSecondary">
                Filename:
              </Typography>
              <Typography variant="body1">
                {analysisData.filename}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="textSecondary">
                Region:
              </Typography>
              <Typography variant="body1">
                {analysisData.region}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="textSecondary">
                Upload Date:
              </Typography>
              <Typography variant="body1">
                {new Date(analysisData.uploaded_at).toLocaleDateString()}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysisData.analysis && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Deepfake Detection Results
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} sm={4}>
                <Box textAlign="center" p={2}>
                  <Chip
                    icon={getClassificationIcon(analysisData.analysis.classification)}
                    label={analysisData.analysis.classification.toUpperCase()}
                    color={getClassificationColor(analysisData.analysis.classification)}
                    size="large"
                    sx={{ fontSize: '1.1rem', p: 1 }}
                  />
                </Box>
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <Box textAlign="center" p={2}>
                  <Typography variant="h4" color="primary">
                    {(analysisData.analysis.confidence * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Confidence Score
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} sm={4}>
                <Box textAlign="center" p={2}>
                  <Typography variant="h4" color="secondary">
                    {(analysisData.analysis.deepfake_score * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Deepfake Probability
                  </Typography>
                </Box>
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Processing Time:
                </Typography>
                <Typography variant="body1">
                  {analysisData.analysis.processing_time.toFixed(2)} seconds
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Model Version:
                </Typography>
                <Typography variant="body1">
                  {analysisData.analysis.model_version}
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Frames Analyzed:
                </Typography>
                <Typography variant="body1">
                  {analysisData.analysis.heatmap_frames?.length || 0} frames
                </Typography>
              </Grid>
            </Grid>

            {/* Detailed Analysis Indicators */}
            {analysisData.analysis.manipulation_indicators && (
              <Accordion sx={{ mt: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">Detailed Analysis Indicators</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {Object.entries(analysisData.analysis.manipulation_indicators).map(([key, value]) => (
                      <Grid item xs={12} sm={6} key={key}>
                        <Card variant="outlined">
                          <CardContent>
                            <Typography variant="subtitle2" gutterBottom>
                              {key.replace(/_/g, ' ').toUpperCase()}
                            </Typography>
                            {typeof value === 'object' ? (
                              Object.entries(value).map(([subKey, subValue]) => (
                                <Box key={subKey} display="flex" justifyContent="space-between" mb={1}>
                                  <Typography variant="body2" color="textSecondary">
                                    {subKey.replace(/_/g, ' ')}:
                                  </Typography>
                                  <Typography variant="body2">
                                    {typeof subValue === 'number' ? subValue.toFixed(3) : subValue}
                                  </Typography>
                                </Box>
                              ))
                            ) : (
                              <Typography variant="body1">
                                {typeof value === 'number' ? value.toFixed(3) : value}
                              </Typography>
                            )}
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            )}
          </CardContent>
        </Card>
      )}

      {/* Geospatial Verification */}
      {analysisData.geospatial_data && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Geospatial Verification
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <Box textAlign="center" p={2}>
                  <Chip
                    icon={<LocationIcon />}
                    label={analysisData.geospatial_data.location_verification.toUpperCase()}
                    color={getGeospatialColor(analysisData.geospatial_data.location_verification)}
                    size="large"
                    sx={{ fontSize: '1.1rem', p: 1 }}
                  />
                </Box>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Box textAlign="center" p={2}>
                  <Typography variant="h4" color="primary">
                    {analysisData.geospatial_data.verification_confidence ? 
                      (analysisData.geospatial_data.verification_confidence * 100).toFixed(1) : 'N/A'}%
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Verification Confidence
                  </Typography>
                </Box>
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Latitude:
                </Typography>
                <Typography variant="body1">
                  {analysisData.geospatial_data.latitude?.toFixed(6) || 'N/A'}
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Longitude:
                </Typography>
                <Typography variant="body1">
                  {analysisData.geospatial_data.longitude?.toFixed(6) || 'N/A'}
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Altitude:
                </Typography>
                <Typography variant="body1">
                  {analysisData.geospatial_data.altitude ? 
                    `${analysisData.geospatial_data.altitude.toFixed(1)}m` : 'N/A'}
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Location Accuracy:
                </Typography>
                <Typography variant="body1">
                  {analysisData.geospatial_data.location_accuracy ? 
                    `±${analysisData.geospatial_data.location_accuracy.toFixed(1)}m` : 'N/A'}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Status */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Analysis Status
          </Typography>
          <Box display="flex" alignItems="center">
            <Chip
              label={analysisData.status}
              color={analysisData.status === 'completed' ? 'success' : 'warning'}
              sx={{ mr: 2 }}
            />
            <Typography variant="body2" color="textSecondary">
              {analysisData.status === 'completed' ? 
                'Analysis completed successfully' : 
                'Analysis in progress or failed'}
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}

export default VideoAnalysis;
