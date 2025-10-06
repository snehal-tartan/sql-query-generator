import { Box, Typography } from '@mui/material';
import { 
  TbWand, 
  TbSparkles, 
  TbFileText,
  TbInfinity,
  TbChecklist,
  TbDatabase,
  TbUsers,
  TbChartBar,
  TbFileStack,
  TbHelp
} from 'react-icons/tb';

interface NavItem {
  icon: React.ReactNode;
  label: string;
  badge?: string;
  isActive?: boolean;
}

const Sidebar = () => {
  const navItems: NavItem[] = [
    { icon: <TbWand size={12} />, label: 'PolyCraft' },
    { icon: <TbSparkles size={12} />, label: 'PolyGPT', badge: 'NEW' },
    { icon: <TbFileText size={12} />, label: 'Policies' },
    { icon: <TbInfinity size={12} />, label: 'RuleSenseAI' },
    { icon: <TbChecklist size={12} />, label: 'Approvals' },
    { icon: <TbDatabase size={12} />, label: 'QueryGen', isActive: true },
    { icon: <TbUsers size={12} />, label: 'User Management' },
    { icon: <TbChartBar size={12} />, label: 'Assessments' },
    { icon: <TbFileStack size={12} />, label: 'Reports' },
    { icon: <TbHelp size={12} />, label: 'FAQ' },
  ];

  return (
    <Box
      sx={{
        width: 220,
        height: '100vh',
        backgroundColor: '#ffffff',
        borderRight: '1px solid #e0e0e0',
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        left: 0,
        top: 0,
      }}
    >
      {/* Navigation Items */}
      <Box
        sx={{
          flex: 1,
          padding: '8px',
          marginTop: '60px', // Account for header height
          overflowY: 'auto',
        }}
      >
        {navItems.map((item, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              padding: '10px 16px',
              marginBottom: '2px',
              borderRadius: '8px',
              cursor: 'pointer',
              backgroundColor: item.isActive ? '#EEF2FF' : 'transparent',
              color: item.isActive ? '#4F46E5' : '#1a1a1a',
              transition: 'all 0.2s',
              '&:hover': {
                backgroundColor: item.isActive ? '#EEF2FF' : '#f5f5f5',
              },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', color: 'inherit' }}>
              {item.icon}
            </Box>
            <Typography
              sx={{
                fontSize: '12px',
                fontWeight: item.isActive ? 650 : 600,
                color: 'inherit',
                flex: 1,
              }}
            >
              {item.label}
            </Typography>
            {item.badge && (
              <Box
                sx={{
                  backgroundColor: '#f0f0f0',
                  color: '#666',
                  fontSize: '8px',
                  fontWeight: 600,
                  padding: '2px 2px',
                  borderRadius: '4px',
                }}
              >
                {item.badge}
              </Box>
            )}
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default Sidebar;

