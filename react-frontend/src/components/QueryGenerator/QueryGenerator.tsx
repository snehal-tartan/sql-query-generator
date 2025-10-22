import { useState, useRef } from 'react';
import { Box, TextField, Paper, Typography, IconButton, Tooltip } from '@mui/material';
import { MdContentCopy } from 'react-icons/md';
import { queryService } from '../../api/services';
import QueryExecutor from '../QueryExecutor/QueryExecutor';
import GraphGenerator from '../GraphGenerator/GraphGenerator';
import CustomButton from '../common/CustomButton';

const QueryGenerator = () => {
  const [prompt, setPrompt] = useState('');
  const [generatedQuery, setGeneratedQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [executingQuery, setExecutingQuery] = useState(false);
  const [hasResults, setHasResults] = useState(false);
  const [copied, setCopied] = useState(false);
  const executeQueryRef = useRef<(() => Promise<void>) | null>(null);

  const handleGenerateQuery = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setLoading(true);
    setError('');
    setGeneratedQuery('');

    try {
      const response = await queryService.generateSQL(prompt);
      
      if (response.error) {
        setError(response.error);
      } else if (response.sql_query) {
        setGeneratedQuery(response.sql_query);
      } else {
        setError('Failed to generate SQL query');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate query. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteQuery = async () => {
    if (executeQueryRef.current) {
      setExecutingQuery(true);
      try {
        await executeQueryRef.current();
      } finally {
        setExecutingQuery(false);
      }
    }
  };

  const handleCopyQuery = () => {
    if (generatedQuery) {
      navigator.clipboard.writeText(generatedQuery);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000); // Reset after 2 seconds
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: 3,
        height: 'calc(100vh - 100px)',
        padding: 3,
        overflow: 'auto',
      }}
    >
      {/* Row 1 - Prompt Input and Generated Query */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 3,
          flexShrink: 0,
        }}
      >
        {/* Left Panel - Input */}
        <Paper
          elevation={0}
          sx={{
            padding: 3,
            backgroundColor: '#ffffff',
            border: '1px solid #e0e0e0',
            borderRadius: '12px',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <Typography
            sx={{
              fontWeight: 550,
              color: '#1a1a1a',
              marginBottom: 2,
              fontSize: '16px',
            }}
          >
            Enter Your Prompt
          </Typography>

        <TextField
          multiline
          rows={5}
          fullWidth
          placeholder="Show me the names of the customers who have bought the most loans."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          sx={{
            flex: 1,
            '& .MuiOutlinedInput-root': {
              backgroundColor: '#f8f9fa',
              fontSize: '14px',
              fontFamily: 'system-ui, sans-serif',
              '& fieldset': {
                borderColor: '#e0e0e0',
              },
              '&:hover fieldset': {
                borderColor: '#2F78EE',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#2F78EE',
              },
            },
          }}
        />

          <Box sx={{ marginTop: 3 }}>
            {/* Buttons will be placed in the right panel */}
          </Box>

          {error && (
            <Typography
              sx={{
                marginTop: 2,
                color: '#ef4444',
                fontSize: '14px',
              }}
            >
              {error}
            </Typography>
          )}
        </Paper>

        {/* Right Panel - Generated Query Preview */}
        <Paper
          elevation={0}
          sx={{
            padding: 3,
            backgroundColor: '#ffffff',
            border: '1px solid #e0e0e0',
            borderRadius: '12px',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: 2,
            }}
          >
            <Typography
              sx={{
                fontWeight: 550,
                color: '#1a1a1a',
                fontSize: '16px',
              }}
            >
              Generated SQL Query
            </Typography>

            {generatedQuery && (
              <Tooltip title={copied ? 'Copied!' : 'Copy SQL Query'} placement="top">
                <IconButton
                  onClick={handleCopyQuery}
                  size="small"
                  sx={{
                    color: copied ? '#4caf50' : '#666',
                    '&:hover': {
                      backgroundColor: '#f5f5f5',
                    },
                  }}
                >
                  <MdContentCopy size={18} />
                </IconButton>
              </Tooltip>
            )}
          </Box>

          <TextField
            multiline
            fullWidth
            rows={6}
            value={generatedQuery}
            onChange={(e) => setGeneratedQuery(e.target.value)}
            placeholder="Generated query appears here... You can edit it before execution."
            sx={{
              marginBottom: 3,
              '& .MuiOutlinedInput-root': {
                backgroundColor: '#f8f9fa',
                fontFamily: 'monospace',
                fontSize: '13px',
                '& fieldset': {
                  borderColor: '#e0e0e0',
                },
                '&:hover fieldset': {
                  borderColor: '#2F78EE',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#2F78EE',
                },
              },
              '& .MuiInputBase-input': {
                fontFamily: 'monospace',
                fontSize: '13px',
              },
            }}
          />

          {/* Action Buttons - Side by Side */}
          <Box
            sx={{
              display: 'flex',
              gap: 2,
            }}
          >
            <CustomButton
              variant="primary"
              fullWidth
              onClick={handleGenerateQuery}
              disabled={loading || executingQuery}
              loading={loading}
            >
              Generate Query
            </CustomButton>

            <CustomButton
              variant="secondary"
              fullWidth
              onClick={handleExecuteQuery}
              disabled={!generatedQuery.trim() || loading || executingQuery}
              loading={executingQuery}
            >
              Execute Query
            </CustomButton>
          </Box>
        </Paper>
      </Box>

      {/* Row 2 - Query Results Table */}
      <Box
        sx={{
          minHeight: 400,
          flexShrink: 0,
        }}
      >
        <QueryExecutor 
          sqlQuery={generatedQuery}
          onExecute={(execute) => {
            executeQueryRef.current = execute;
          }}
          onResultsChange={(hasData) => setHasResults(hasData)}
        />
      </Box>

      {/* Row 3 - Graph Visualization */}
      <Box
        sx={{
          minHeight: 500,
          flexShrink: 0,
        }}
      >
        <GraphGenerator 
          sqlQuery={generatedQuery}
          hasResults={hasResults}
        />
      </Box>
    </Box>
  );
};

export default QueryGenerator;

