import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Paper,
  Grid,
  Chip
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  VideoLibrary as VideoIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const regions = [
  { code: 'NA', name: 'North America' },
  { code: 'EU', name: 'Europe' },
  { code: 'AS', name: 'Asia' },
  { code: 'SA', name: 'South America' },
  { code: 'AF', name: 'Africa' },
  { code: 'OC', name: 'Oceania' }
];

function VideoUpload() {
  const [selectedRegion, setSelectedRegion] = useState('NA');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      
      // Validate file type
      if (!file.type.startsWith('video/')) {
        setError('Please select a valid video file');
        return;
      }
      
      // Validate file size (100MB limit)
      if (file.size > 100 * 1024 * 1024) {
        setError('File size must be less than 100MB');
        return;
      }
      
      setUploadedFile(file);
      setError('');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.wmv', '.flv']
    },
    multiple: false
  });

  const handleUpload = async () => {
    if (!uploadedFile || !selectedRegion) {
      setError('Please select a file and region');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      formData.append('region', selectedRegion);

      const response = await api.post('/video/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadResult(response.data);
      setUploadedFile(null);
      
      // Navigate to analysis page after a short delay
      setTimeout(() => {
        navigate(`/analysis/${response.data.tracking_id}`);
      }, 2000);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = () => {
    if (uploadResult) {
      navigate(`/analysis/${uploadResult.tracking_id}`);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Upload Video for Analysis
      </Typography>
      
      <Typography variant="body1" color="textSecondary" paragraph>
        Upload a video file to analyze for deepfake detection and geospatial verification.
        Supported formats: MP4, AVI, MOV, WMV, FLV (max 100MB)
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          {/* Upload Area */}
          <Card>
            <CardContent>
              <Box
                {...getRootProps()}
                sx={{
                  border: '2px dashed',
                  borderColor: isDragActive ? 'primary.main' : 'grey.300',
                  borderRadius: 2,
                  p: 4,
                  textAlign: 'center',
                  cursor: 'pointer',
                  backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <input {...getInputProps()} />
                <UploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  {isDragActive ? 'Drop the video here' : 'Drag & drop a video file here'}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  or click to select a file
                </Typography>
              </Box>

              {uploadedFile && (
                <Box mt={2} p={2} bgcolor="success.light" borderRadius={1}>
                  <Box display="flex" alignItems="center">
                    <VideoIcon color="success" sx={{ mr: 1 }} />
                    <Typography variant="body2" color="success.dark">
                      {uploadedFile.name} ({Math.round(uploadedFile.size / 1024 / 1024 * 100) / 100} MB)
                    </Typography>
                  </Box>
                </Box>
              )}

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          {/* Region Selection and Upload */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Analysis Settings
              </Typography>
              
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Region</InputLabel>
                <Select
                  value={selectedRegion}
                  label="Region"
                  onChange={(e) => setSelectedRegion(e.target.value)}
                >
                  {regions.map((region) => (
                    <MenuItem key={region.code} value={region.code}>
                      {region.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Button
                variant="contained"
                fullWidth
                size="large"
                onClick={handleUpload}
                disabled={!uploadedFile || uploading}
                startIcon={uploading ? <CircularProgress size={20} /> : <UploadIcon />}
              >
                {uploading ? 'Uploading...' : 'Upload & Analyze'}
              </Button>

              <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                Analysis will begin automatically after upload
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Upload Result */}
      {uploadResult && (
        <Card sx={{ mt: 3, bgcolor: 'success.light' }}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <CheckIcon color="success" sx={{ mr: 1 }} />
              <Typography variant="h6" color="success.dark">
                Upload Successful!
              </Typography>
            </Box>
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Tracking ID:
                </Typography>
                <Typography variant="body1" fontFamily="monospace">
                  {uploadResult.tracking_id}
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Region:
                </Typography>
                <Typography variant="body1">
                  {regions.find(r => r.code === uploadResult.region)?.name}
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Filename:
                </Typography>
                <Typography variant="body1">
                  {uploadResult.filename}
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="textSecondary">
                  Status:
                </Typography>
                <Chip label="Processing" color="warning" size="small" />
              </Grid>
            </Grid>

            <Box mt={2}>
              <Button
                variant="outlined"
                color="success"
                onClick={handleAnalyze}
                startIcon={<VideoIcon />}
              >
                View Analysis
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

export default VideoUpload;
