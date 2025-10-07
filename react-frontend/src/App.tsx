import { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import Sidebar from './components/Sidebar/Sidebar';
import Header from './components/Header/Header';
import QueryGenerator from './components/QueryGenerator/QueryGenerator';
import DatabaseConnectionModal from './components/DatabaseConnectionModal/DatabaseConnectionModal';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [showConnectionModal, setShowConnectionModal] = useState(true); // Always show modal initially

  // Always show modal on page load/refresh
  useEffect(() => {
    // Reset connection state and show modal every time
    setIsConnected(false);
    setShowConnectionModal(true);
  }, []);

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
          // Never allow closing - user must connect to proceed
          // Modal can only be closed after successful connection
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
