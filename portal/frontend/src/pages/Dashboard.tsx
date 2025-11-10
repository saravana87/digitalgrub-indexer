import React from 'react';
import { Card, Row, Col, Statistic, Progress, Table } from 'antd';
import { FileTextOutlined, DatabaseOutlined, CheckCircleOutlined, SyncOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { indexingApi } from '../api/client';

const Dashboard: React.FC = () => {
  const { data: dashboardData, isLoading: dashboardLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await indexingApi.getDashboard();
      return response.data;
    },
  });

  const { data: statsData, isLoading: statsLoading } = useQuery({
    queryKey: ['indexing-stats'],
    queryFn: async () => {
      const response = await indexingApi.getStats();
      return response.data;
    },
  });

  const statsList = statsData?.stats ? Object.values(statsData.stats) : [];

  const columns = [
    {
      title: 'Table',
      dataIndex: 'table_name',
      key: 'table_name',
      render: (text: string) => text.toUpperCase(),
    },
    {
      title: 'Total Records',
      dataIndex: 'total_records',
      key: 'total_records',
    },
    {
      title: 'Indexed',
      dataIndex: 'indexed_records',
      key: 'indexed_records',
    },
    {
      title: 'Progress',
      key: 'progress',
      render: (_: any, record: any) => (
        <Progress
          percent={record.index_percentage}
          size="small"
          status={record.index_percentage === 100 ? 'success' : 'active'}
        />
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <h1>Dashboard</h1>
      
      {/* Stats Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card loading={dashboardLoading}>
            <Statistic
              title="Total Jobs"
              value={dashboardData?.total_jobs || 0}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={dashboardLoading}>
            <Statistic
              title="Total News"
              value={dashboardData?.total_news || 0}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={dashboardLoading}>
            <Statistic
              title="Indexed Today"
              value={dashboardData?.indexed_today || 0}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={dashboardLoading}>
            <Statistic
              title="Success Rate"
              value={dashboardData?.indexing_success_rate || 0}
              suffix="%"
              prefix={<SyncOutlined spin={dashboardData?.indexing_success_rate < 100} />}
            />
          </Card>
        </Col>
      </Row>

      {/* Indexing Status Table */}
      <Card title="Indexing Status" style={{ marginBottom: 24 }}>
        <Table
          columns={columns}
          dataSource={statsList}
          loading={statsLoading}
          rowKey="table_name"
          pagination={false}
        />
      </Card>

      {/* Overall Progress */}
      <Card title="Overall Progress">
        <Statistic
          title="Total Records Indexed"
          value={statsData?.total_indexed || 0}
          suffix={`/ ${statsData?.total_records || 0}`}
        />
        <Progress
          percent={statsData?.overall_percentage || 0}
          status={statsData?.overall_percentage === 100 ? 'success' : 'active'}
          style={{ marginTop: 16 }}
        />
      </Card>
    </div>
  );
};

export default Dashboard;
