import { useState, useEffect } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import Sidebar from './components/Sidebar/Sidebar';
import Header from './components/Header/Header';
import QueryGenerator from './components/QueryGenerator/QueryGenerator';
import DatabaseConnectionModal from './components/DatabaseConnectionModal/DatabaseConnectionModal';
import { queryService } from './api/services';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [showConnectionModal, setShowConnectionModal] = useState(false);
  const [isChecking, setIsChecking] = useState(true); // Check connection status on load

  // Check if backend is already connected on page load
  useEffect(() => {
    const checkDatabaseConnection = async () => {
      try {
        const response = await queryService.getDatabaseStatus();
        
        if (response.connected) {
          // Backend is already connected - no need to show modal
          setIsConnected(true);
          setShowConnectionModal(false);
        } else {
          // Backend not connected - show modal
          setIsConnected(false);
          setShowConnectionModal(true);
        }
      } catch (error) {
        console.error('Failed to check database status:', error);
        // On error, show connection modal
        setIsConnected(false);
        setShowConnectionModal(true);
      } finally {
        setIsChecking(false);
      }
    };

    checkDatabaseConnection();
  }, []);

  // Show loading state while checking connection
  if (isChecking) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          backgroundColor: '#f5f5f5',
          gap: 2,
        }}
      >
        <CircularProgress size={50} />
        <Typography variant="body1" color="text.secondary">
          Checking database connection...
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <Sidebar />
      
      <Box
        sx={{
          marginLeft: '220px',
          width: 'calc(100% - 220px)',
          minHeight: '100vh',
        }}
      >
        <Header />
        
        <Box
          sx={{
            marginTop: '60px',
            padding: 0,
          }}
        >
          {isConnected ? (
            <QueryGenerator />
          ) : (
            <Box
              sx={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: 'calc(100vh - 60px)',
                gap: 2,
              }}
            >
              <Typography variant="h6" color="text.secondary">
                Please connect to a database to continue
              </Typography>
            </Box>
          )}
        </Box>
      </Box>

      {/* Database Connection Modal */}
      <DatabaseConnectionModal
        open={showConnectionModal}
        onClose={() => {
          // Allow closing if already connected (shouldn't happen in normal flow)
          if (isConnected) {
            setShowConnectionModal(false);
          }
        }}
        onConnect={() => {
          setIsConnected(true);
          setShowConnectionModal(false);
        }}
      />
    </Box>
  );
}

export default App;
