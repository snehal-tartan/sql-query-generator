import { Box } from '@mui/material';
import Sidebar from './components/Sidebar/Sidebar';
import Header from './components/Header/Header';
import QueryGenerator from './components/QueryGenerator/QueryGenerator';

function App() {


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
          <QueryGenerator />
        </Box>
      </Box>
    </Box>
  );
}

export default App;
