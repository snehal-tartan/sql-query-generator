import { Paper, Typography, Box } from '@mui/material';
import { TbBulb } from 'react-icons/tb';

interface KeyInsightsProps {
  insights: string;
}

const KeyInsights = ({ insights }: KeyInsightsProps) => {
  if (!insights) {
    return null;
  }

  return (
    <Paper
      elevation={0}
      sx={{
        padding: 2.5,
        backgroundColor: '#F0F7FF',
        border: '1px solid #2F78EE',
        borderRadius: '8px',
        display: 'flex',
        flexDirection: 'column',
        gap: 1.5,
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        <TbBulb size={20} color="#2F78EE" />
        <Typography
          sx={{
            fontSize: '15px',
            fontWeight: 600,
            color: '#2F78EE',
          }}
        >
          Key Insights
        </Typography>
      </Box>

      {/* Insights Content */}
      <Typography
        sx={{
          fontSize: '13px',
          color: '#1a1a1a',
          whiteSpace: 'pre-wrap',
          lineHeight: 1.7,
          '& ul': {
            margin: 0,
            paddingLeft: '20px',
          },
          '& li': {
            marginBottom: '8px',
          },
        }}
      >
        {insights}
      </Typography>
    </Paper>
  );
};

export default KeyInsights;
