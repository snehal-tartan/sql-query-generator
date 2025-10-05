import { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  IconButton,
} from '@mui/material';
import { MdDownload } from 'react-icons/md';
import { queryService } from '../../api/services';

interface QueryExecutorProps {
  sqlQuery: string;
  onExecute?: (execute: () => Promise<void>) => void;
  onResultsChange?: (hasResults: boolean) => void;
}

const QueryExecutor = ({ sqlQuery, onExecute, onResultsChange }: QueryExecutorProps) => {
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [downloading, setDownloading] = useState(false);

  const handleExecuteSQL = async () => {
    if (!sqlQuery.trim()) {
      setError('No SQL query to execute');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await queryService.executeSQL(sqlQuery);

      if (response.error) {
        setError(response.error);
        setResults(null);
        if (onResultsChange) onResultsChange(false);
      } else if (response.results) {
        setResults(response.results);
        if (onResultsChange) onResultsChange(response.results.length > 0);
      } else {
        setError('No results returned');
        setResults(null);
        if (onResultsChange) onResultsChange(false);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to execute SQL query. Please try again.');
      setResults(null);
      if (onResultsChange) onResultsChange(false);
    } finally {
      setLoading(false);
    }
  };

  // Expose the execute function to parent component
  useEffect(() => {
    if (onExecute) {
      onExecute(handleExecuteSQL);
    }
  }, [sqlQuery, onExecute]);

  const handleDownloadCSV = async () => {
    if (!sqlQuery.trim() || !results) {
      return;
    }

    setDownloading(true);
    try {
      const blob = await queryService.downloadCSV(sqlQuery);
      
      // Create a download link
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'query_results.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to download CSV');
    } finally {
      setDownloading(false);
    }
  };

  const renderTable = () => {
    if (!results || results.length === 0) {
      return (
        <Box sx={{ padding: 3, textAlign: 'center', color: '#999' }}>
          <Typography>No data to display</Typography>
        </Box>
      );
    }

    const columns = Object.keys(results[0]);

    return (
      <TableContainer>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              {/* S.No. Column Header */}
              <TableCell
                sx={{
                  backgroundColor: '#f8f9fa',
                  fontWeight: 600,
                  fontSize: '13px',
                  color: '#1a1a1a',
                  borderBottom: '2px solid #e0e0e0',
                  width: '80px',
                }}
              >
                S.No.
              </TableCell>
              {columns.map((column) => (
                <TableCell
                  key={column}
                  sx={{
                    backgroundColor: '#f8f9fa',
                    fontWeight: 600,
                    fontSize: '13px',
                    color: '#1a1a1a',
                    borderBottom: '2px solid #e0e0e0',
                  }}
                >
                  {column}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {results.map((row: any, rowIndex: number) => (
              <TableRow
                key={rowIndex}
                sx={{
                  '&:hover': {
                    backgroundColor: '#f5f5f5',
                  },
                  '&:nth-of-type(even)': {
                    backgroundColor: '#fafafa',
                  },
                }}
              >
                {/* S.No. Column Data */}
                <TableCell
                  sx={{
                    fontSize: '13px',
                    color: '#666',
                    padding: '12px 16px',
                    fontWeight: 500,
                  }}
                >
                  {rowIndex + 1}
                </TableCell>
                {columns.map((column) => (
                  <TableCell
                    key={column}
                    sx={{
                      fontSize: '13px',
                      color: '#333',
                      padding: '12px 16px',
                    }}
                  >
                    {row[column] !== null && row[column] !== undefined
                      ? String(row[column])
                      : '-'}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    );
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
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 2,
          flexShrink: 0,
        }}
      >
        <Typography
          sx={{
            fontWeight: 550,
            color: '#1a1a1a',
            fontSize: '16px',
          }}
        >
          Query Results
        </Typography>

        {results && (
          <IconButton
            onClick={handleDownloadCSV}
            disabled={downloading || !results}
            sx={{
              color: '#2F78EE',
              '&:hover': {
                backgroundColor: '#F0F7FF',
              },
              '&:disabled': {
                color: '#ccc',
              },
            }}
          >
            {downloading ? <CircularProgress size={24} /> : <MdDownload size={24} />}
          </IconButton>
        )}
      </Box>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ marginBottom: 2, flexShrink: 0 }}>
          {error}
        </Alert>
      )}

      {/* Results Section */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Paper
          elevation={0}
          sx={{
            flex: 1,
            border: '1px solid #e0e0e0',
            borderRadius: '8px',
            overflow: 'auto',
            backgroundColor: '#ffffff',
            maxHeight: 300,
          }}
        >
          {loading ? (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                minHeight: 200,
              }}
            >
              <CircularProgress />
            </Box>
          ) : results ? (
            renderTable()
          ) : (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                minHeight: 200,
                color: '#999',
              }}
            >
              <Typography sx={{ fontSize: '14px' }}>
                Execute a query to see results here...
              </Typography>
            </Box>
          )}
        </Paper>
      </Box>
    </Paper>
  );
};

export default QueryExecutor;

