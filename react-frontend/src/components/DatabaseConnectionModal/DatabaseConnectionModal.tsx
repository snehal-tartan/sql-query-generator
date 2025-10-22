import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Box,
  Typography,
  Alert,
  IconButton,
} from '@mui/material';
import { MdClose, MdStorage } from 'react-icons/md';
import CustomButton from '../common/CustomButton';
import { queryService } from '../../api/services';

interface DatabaseConnectionModalProps {
  open: boolean;
  onClose: () => void;
  onConnect: () => void;
}

const DatabaseConnectionModal = ({
  open,
  onClose,
  onConnect,
}: DatabaseConnectionModalProps) => {
  const [formData, setFormData] = useState({
    host: 'localhost',
    user: '',
    password: '',
    database: '',
    port: 41854,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (field: string, value: string | number) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setError(''); // Clear error when user types
  };

  const handleConnect = async () => {
    // Validation
    if (!formData.user || !formData.password || !formData.database) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await queryService.connectDatabase(
        formData.host,
        formData.user,
        formData.password,
        formData.database,
        formData.port
      );

      if (response.status === 'success') {
        onConnect();
        onClose();
      } else {
        setError(response.message || 'Failed to connect to database');
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'Failed to connect. Please check your credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading) {
      handleConnect();
    }
  };

  return (
    <Dialog
      open={open}
      onClose={() => {}} // Prevent closing by clicking outside or pressing escape
      maxWidth="sm"
      fullWidth
      disableEscapeKeyDown
      PaperProps={{
        sx: {
          borderRadius: '12px',
          padding: 1,
        },
      }}
    >
      {/* Header */}
      <DialogTitle
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingBottom: 1,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <MdStorage size={24} color="#2F78EE" />
          <Typography sx={{ fontSize: '20px', fontWeight: 600, color: '#1a1a1a' }}>
            Database Connection
          </Typography>
        </Box>
        <IconButton
          onClick={() => {}} // Disable close button
          size="small"
          disabled
          sx={{
            color: '#ccc',
            '&:hover': { backgroundColor: 'transparent' },
          }}
        >
          <MdClose size={20} />
        </IconButton>
      </DialogTitle>

      {/* Content */}
      <DialogContent sx={{ paddingTop: 2 }}>
        <Typography
          sx={{
            fontSize: '14px',
            color: '#666',
            marginBottom: 3,
          }}
        >
          Enter your MySQL database credentials to connect
        </Typography>

        {error && (
          <Alert severity="error" sx={{ marginBottom: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
          {/* Host */}
          <TextField
            label="Host"
            value={formData.host}
            onChange={(e) => handleChange('host', e.target.value)}
            onKeyPress={handleKeyPress}
            fullWidth
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '8px',
              },
            }}
          />

          {/* User */}
          <TextField
            label="User *"
            value={formData.user}
            onChange={(e) => handleChange('user', e.target.value)}
            onKeyPress={handleKeyPress}
            fullWidth
            size="small"
            required
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '8px',
              },
            }}
          />

          {/* Password */}
          <TextField
            label="Password *"
            type="password"
            value={formData.password}
            onChange={(e) => handleChange('password', e.target.value)}
            onKeyPress={handleKeyPress}
            fullWidth
            size="small"
            required
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '8px',
              },
            }}
          />

          {/* Database */}
          <TextField
            label="Database *"
            value={formData.database}
            onChange={(e) => handleChange('database', e.target.value)}
            onKeyPress={handleKeyPress}
            fullWidth
            size="small"
            required
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '8px',
              },
            }}
          />

          {/* Port */}
          <TextField
            label="Port"
            type="number"
            value={formData.port}
            onChange={(e) => handleChange('port', parseInt(e.target.value) || 41854)}
            onKeyPress={handleKeyPress}
            fullWidth
            size="small"
            inputProps={{ min: 1, max: 65535 }}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '8px',
              },
            }}
          />
        </Box>
      </DialogContent>

      {/* Actions */}
      <DialogActions sx={{ padding: 3, paddingTop: 2 }}>
        <CustomButton
          variant="secondary"
          onClick={() => {}} // Disable cancel button
          disabled={true}
          sx={{ minWidth: 100 }}
        >
          Cancel
        </CustomButton>
        <CustomButton
          variant="primary"
          onClick={handleConnect}
          loading={loading}
          disabled={loading}
          sx={{ minWidth: 100 }}
        >
          Connect
        </CustomButton>
      </DialogActions>
    </Dialog>
  );
};

export default DatabaseConnectionModal;
