import { Box, Avatar, Typography } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';

const Header = () => {
  return (
    <Box
      sx={{
        height: 60,
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #e0e0e0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px 0 0',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100,
      }}
    >
      {/* Left side - Tartan Logo and Title */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          width: 220,
          height: '100%',
          borderRight: '1px solid #e0e0e0',
          paddingLeft: '24px',
        }}
      >
        {/* Tartan Logo */}
        <Box
          component="img"
          src="/assets/TartanLogo.png"
          alt="Tartan"
          sx={{
            height: 40,
            width: 'auto',
            objectFit: 'contain',
          }}
        />
      </Box>

      {/* Right side - User info */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          cursor: 'pointer',
          paddingRight: '24px',
        }}
      >
        <Box sx={{ textAlign: 'right' }}>
          <Typography sx={{ fontSize: '14px', fontWeight: 500, color: '#1a1a1a' }}>
            Policy Manager
          </Typography>
          <Typography sx={{ fontSize: '12px', color: '#666' }}>
            User (user@example.com)
          </Typography>
        </Box>
        <Avatar sx={{ width: 36, height: 36, backgroundColor: '#black' }}>
          <AccountCircleIcon />
        </Avatar>
      </Box>
    </Box>
  );
};

export default Header;

