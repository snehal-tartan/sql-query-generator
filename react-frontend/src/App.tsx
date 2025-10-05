import { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import Sidebar from './components/Sidebar/Sidebar';
import Header from './components/Header/Header';
import QueryGenerator from './components/QueryGenerator/QueryGenerator';
import DatabaseConnectionModal from './components/DatabaseConnectionModal/DatabaseConnectionModal';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [showConnectionModal, setShowConnectionModal] = useState(true); // Show by default

  // Check connection status on mount
  useEffect(() => {
    checkConnectionStatus();
  }, []);

  const checkConnectionStatus = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/database_status');
      const data = await response.json();
      console.log('Database status:', data);
      if (data.connected) {
        setIsConnected(true);
        setShowConnectionModal(false);
      } else {
        setIsConnected(false);
        setShowConnectionModal(true);
      }
    } catch (error) {
      console.error('Failed to check connection status:', error);
      setIsConnected(false);
      setShowConnectionModal(true);
    }
  };

  const handleConnect = () => {
    setIsConnected(true);
  };

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
                alignItems: 'center',
                justifyContent: 'center',
                height: 'calc(100vh - 60px)',
              }}
            >
              {/* Placeholder while checking connection */}
            </Box>
          )}
        </Box>
      </Box>

      {/* Database Connection Modal */}
      <DatabaseConnectionModal
        open={showConnectionModal}
        onClose={() => {
          // Don't allow closing if not connected
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
