import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
} from '@mui/material';
import CustomButton from '../common/CustomButton';
import KeyInsights from '../KeyInsights/KeyInsights';
import { queryService } from '../../api/services';

interface GraphGeneratorProps {
  sqlQuery: string;
  hasResults: boolean;
}

const GraphGenerator = ({ sqlQuery, hasResults }: GraphGeneratorProps) => {
  const [chartType, setChartType] = useState('bar');
  const [graphImage, setGraphImage] = useState('');
  const [insights, setInsights] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerateGraph = async () => {
    if (!sqlQuery.trim()) {
      setError('No SQL query available');
      return;
    }

    setLoading(true);
    setError('');
    setGraphImage('');
    setInsights('');

    try {
      const response = await queryService.generateGraph(
        sqlQuery,
        chartType
      );

      if (response.error) {
        setError(response.error);
      } else if (response.image_base64) {
        setGraphImage(response.image_base64);
        setInsights(response.insights || '');
      } else {
        setError('Failed to generate graph');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate graph. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper
      elevation={0}
      sx={{
        padding: 3,
        backgroundColor: '#ffffff',
        border: '1px solid #e0e0e0',
        borderRadius: '12px',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
      }}
    >
      <Typography
        sx={{
          fontWeight: 550,
          color: '#1a1a1a',
          marginBottom: 3,
          fontSize: '16px',
          flexShrink: 0,
        }}
      >
        Graph Visualization
      </Typography>

      {/* Chart Options */}
      <Box
        sx={{
          display: 'flex',
          gap: 2,
          marginBottom: 2,
          flexShrink: 0,
        }}
      >
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <InputLabel>Chart Type</InputLabel>
          <Select
            value={chartType}
            label="Chart Type"
            onChange={(e) => setChartType(e.target.value)}
            disabled={!hasResults}
          >
            <MenuItem value="bar">Bar Chart</MenuItem>
            <MenuItem value="line">Line Chart</MenuItem>
            <MenuItem value="pie">Pie Chart</MenuItem>
            <MenuItem value="scatter">Scatter Plot</MenuItem>
          </Select>
        </FormControl>

        <CustomButton
          variant="primary"
          onClick={handleGenerateGraph}
          disabled={!hasResults || loading}
          loading={loading}
        >
          Generate Graph
        </CustomButton>
      </Box>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ marginBottom: 2, flexShrink: 0 }}>
          {error}
        </Alert>
      )}

      {/* Graph Display and Insights */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        {/* Graph Image */}
        <Box
          sx={{
            flex: 1,
            overflow: 'auto',
            border: '1px solid #e0e0e0',
            borderRadius: '8px',
            backgroundColor: '#ffffff',
            padding: 2,
          }}
        >
          {loading ? (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                minHeight: 300,
              }}
            >
              <CircularProgress />
            </Box>
          ) : graphImage ? (
            <Box
              component="img"
              src={`data:image/png;base64,${graphImage}`}
              alt="Generated Graph"
              sx={{
                width: '100%',
                height: 'auto',
                display: 'block',
                objectFit: 'contain',
              }}
            />
          ) : (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                minHeight: 300,
                color: '#999',
              }}
            >
              <Typography sx={{ fontSize: '14px', textAlign: 'center', padding: 2 }}>
                {hasResults
                  ? 'Select chart type and click "Generate Graph" to visualize data'
                  : 'Execute a query first to generate graphs'}
              </Typography>
            </Box>
          )}
        </Box>

        {/* Key Insights Component */}
        {insights && <KeyInsights insights={insights} />}
      </Box>
    </Paper>
  );
};

export default GraphGenerator;

