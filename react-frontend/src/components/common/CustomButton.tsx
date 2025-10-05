import { Button, CircularProgress, type SxProps, type Theme } from '@mui/material';
import { type ReactNode } from 'react';

interface CustomButtonProps {
  variant?: 'primary' | 'secondary';
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  children: ReactNode;
  sx?: SxProps<Theme>;
}

const CustomButton = ({
  variant = 'primary',
  onClick,
  disabled = false,
  loading = false,
  fullWidth = false,
  children,
  sx,
}: CustomButtonProps) => {
  const isPrimary = variant === 'primary';

  return (
    <Button
      variant={isPrimary ? 'contained' : 'outlined'}
      onClick={onClick}
      disabled={disabled || loading}
      fullWidth={fullWidth}
      sx={{
        backgroundColor: isPrimary ? '#2F78EE' : '#ffffff',
        color: isPrimary ? '#ffffff' : '#2F78EE',
        border: isPrimary ? 'none' : '1px solid #2F78EE',
        textTransform: 'none',
        fontSize: '16px',
        fontWeight: 500,
        padding: '12px 24px',
        borderRadius: '8px',
        '&:hover': {
          backgroundColor: isPrimary ? '#2563EB' : '#F0F7FF',
          border: isPrimary ? 'none' : '1px solid #2563EB',
          color: isPrimary ? '#ffffff' : '#2563EB',
        },
        '&:disabled': {
          backgroundColor: isPrimary ? '#E0E7FF' : '#ffffff',
          color: '#999',
          border: isPrimary ? 'none' : '1px solid #E0E0E0',
        },
        ...sx,
      }}
    >
      {loading ? <CircularProgress size={24} color="inherit" /> : children}
    </Button>
  );
};

export default CustomButton;

