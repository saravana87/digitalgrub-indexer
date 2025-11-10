import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Layout, Menu } from 'antd';
import { DashboardOutlined, FileTextOutlined, FolderOpenOutlined } from '@ant-design/icons';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from './pages/Dashboard';
import ContentGenerator from './pages/ContentGenerator';
import ContentLibrary from './pages/ContentLibrary';

const { Header, Content, Sider } = Layout;

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout style={{ minHeight: '100vh' }}>
          <Header style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
            <div style={{ color: 'white', fontSize: 20, fontWeight: 'bold' }}>
              DigitalGrub Portal
            </div>
          </Header>
          <Layout>
            <Sider width={200} theme="light">
              <Menu
                mode="inline"
                defaultSelectedKeys={['dashboard']}
                style={{ height: '100%', borderRight: 0 }}
              >
                <Menu.Item key="dashboard" icon={<DashboardOutlined />}>
                  <Link to="/">Dashboard</Link>
                </Menu.Item>
                <Menu.Item key="content" icon={<FileTextOutlined />}>
                  <Link to="/content">Content Generator</Link>
                </Menu.Item>
                <Menu.Item key="library" icon={<FolderOpenOutlined />}>
                  <Link to="/library">Content Library</Link>
                </Menu.Item>
              </Menu>
            </Sider>
            <Layout style={{ padding: '0 24px 24px' }}>
              <Content
                style={{
                  padding: 24,
                  margin: 0,
                  minHeight: 280,
                  background: '#fff',
                }}
              >
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/content" element={<ContentGenerator />} />
                  <Route path="/library" element={<ContentLibrary />} />
                </Routes>
              </Content>
            </Layout>
          </Layout>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
