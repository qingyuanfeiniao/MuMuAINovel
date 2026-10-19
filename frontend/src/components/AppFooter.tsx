import { Typography, Space, Divider, Grid, theme } from 'antd';
import { ClockCircleOutlined } from '@ant-design/icons';
import { VERSION_INFO, getVersionString } from '../config/version';

const { Text } = Typography;
const { useBreakpoint } = Grid;

interface AppFooterProps {
  sidebarWidth?: number;
}

export default function AppFooter({ sidebarWidth = 0 }: AppFooterProps) {
  const screens = useBreakpoint();
  const isMobile = !screens.md;
  const { token } = theme.useToken();
  const alphaColor = (color: string, alpha: number) => `color-mix(in srgb, ${color} ${(alpha * 100).toFixed(0)}%, transparent)`;

  return (
    <footer
      style={{
        position: 'fixed',
        bottom: 0,
        left: isMobile ? 0 : sidebarWidth,
        right: 0,
        backdropFilter: 'blur(20px) saturate(180%)',
        WebkitBackdropFilter: 'blur(20px) saturate(180%)',
        borderTop: `1px solid ${token.colorBorder}`,
        padding: isMobile ? '8px 12px' : '10px 16px',
        zIndex: 100,
        boxShadow: `0 -2px 16px ${alphaColor(token.colorText, 0.08)}`,
        backgroundColor: alphaColor(token.colorBgContainer, 0.82),
        transition: 'left 0.3s ease',
        textAlign: 'center',
      }}
    >
      <Space
        size={isMobile ? 8 : 12}
        split={<Divider type="vertical" style={{ borderColor: token.colorBorder }} />}
        wrap
      >
        <Text style={{ fontSize: isMobile ? 11 : 12, color: token.colorTextSecondary }}>
          <strong style={{ color: token.colorText }}>{VERSION_INFO.projectName}</strong>
          {' '}{getVersionString()}
        </Text>
        <Text style={{ fontSize: isMobile ? 10 : 12, color: token.colorTextTertiary }}>
          <ClockCircleOutlined style={{ marginRight: 4 }} />
          {VERSION_INFO.buildTime}
        </Text>
      </Space>
    </footer>
  );
}
