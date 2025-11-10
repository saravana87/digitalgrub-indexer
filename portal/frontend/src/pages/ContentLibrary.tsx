import React, { useState } from 'react';
import { 
  Card, Table, Tag, Button, Space, message, Tabs, Modal, Typography,
  Select
} from 'antd';
import { 
  EyeOutlined, CopyOutlined,
  CheckCircleOutlined, CloseCircleOutlined, GlobalOutlined 
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { contentApi } from '../api/client';
import type { ColumnsType } from 'antd/es/table';

const { Title, Paragraph } = Typography;
const { Option } = Select;

interface TitleRecord {
  id: number;
  source_type: string;
  topic: string;
  title: string;
  filter_sector?: string;
  filter_category?: string;
  filter_source?: string;
  is_used: boolean;
  used_count: number;
  created_at: string;
}

interface SocialRecord {
  id: number;
  source_type: string;
  topic?: string;
  title?: string;
  content: string;
  tone?: string;
  filter_sector?: string;
  filter_category?: string;
  filter_source?: string;
  is_published: boolean;
  published_at?: string;
  created_at: string;
}

interface BlogRecord {
  id: number;
  source_type: string;
  title: string;
  content: string;
  summary?: string;
  word_count?: number;
  tone?: string;
  length?: string;
  filter_sector?: string;
  filter_category?: string;
  filter_source?: string;
  is_published: boolean;
  published_at?: string;
  published_url?: string;
  created_at: string;
}

const ContentLibrary: React.FC = () => {
  const [activeTab, setActiveTab] = useState('titles');
  const [previewModal, setPreviewModal] = useState(false);
  const [previewContent, setPreviewContent] = useState<any>(null);
  
  // Filters
  const [titleFilters, setTitleFilters] = useState({ source_type: undefined, is_used: undefined });
  const [socialFilters, setSocialFilters] = useState({ source_type: undefined, is_published: undefined });
  const [blogFilters, setBlogFilters] = useState({ source_type: undefined, is_published: undefined });

  // Fetch saved titles
  const { data: titlesData, isLoading: titlesLoading } = useQuery({
    queryKey: ['savedTitles', titleFilters],
    queryFn: () => contentApi.listTitles(titleFilters),
    enabled: activeTab === 'titles',
  });

  // Fetch saved social content
  const { data: socialData, isLoading: socialLoading } = useQuery({
    queryKey: ['savedSocial', socialFilters],
    queryFn: () => contentApi.listSocial(socialFilters),
    enabled: activeTab === 'social',
  });

  // Fetch saved blogs
  const { data: blogsData, isLoading: blogsLoading } = useQuery({
    queryKey: ['savedBlogs', blogFilters],
    queryFn: () => contentApi.listBlogs(blogFilters),
    enabled: activeTab === 'blogs',
  });

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    message.success('Copied to clipboard!');
  };

  const showPreview = (content: any, type: string) => {
    setPreviewContent({ ...content, type });
    setPreviewModal(true);
  };

  // Titles Table Columns
  const titleColumns: ColumnsType<TitleRecord> = [
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      width: '40%',
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: 'Source',
      dataIndex: 'source_type',
      key: 'source_type',
      render: (type) => <Tag color={type === 'jobs' ? 'blue' : 'green'}>{type}</Tag>,
    },
    {
      title: 'Filters',
      key: 'filters',
      render: (_, record) => (
        <Space direction="vertical" size="small">
          {record.filter_sector && <Tag>Sector: {record.filter_sector}</Tag>}
          {record.filter_category && <Tag>Category: {record.filter_category}</Tag>}
          {record.filter_source && <Tag>Source: {record.filter_source}</Tag>}
        </Space>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'is_used',
      key: 'is_used',
      render: (used, record) => (
        <Space>
          {used ? (
            <Tag icon={<CheckCircleOutlined />} color="success">
              Used ({record.used_count}x)
            </Tag>
          ) : (
            <Tag icon={<CloseCircleOutlined />} color="default">
              Unused
            </Tag>
          )}
        </Space>
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<CopyOutlined />}
            onClick={() => copyToClipboard(record.title)}
          />
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => showPreview(record, 'title')}
          />
        </Space>
      ),
    },
  ];

  // Social Content Table Columns
  const socialColumns: ColumnsType<SocialRecord> = [
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      width: '25%',
    },
    {
      title: 'Content Preview',
      dataIndex: 'content',
      key: 'content',
      width: '30%',
      render: (text) => (
        <Paragraph ellipsis={{ rows: 2 }} style={{ marginBottom: 0 }}>
          {text}
        </Paragraph>
      ),
    },
    {
      title: 'Source',
      dataIndex: 'source_type',
      key: 'source_type',
      render: (type) => <Tag color={type === 'jobs' ? 'blue' : 'green'}>{type}</Tag>,
    },
    {
      title: 'Tone',
      dataIndex: 'tone',
      key: 'tone',
      render: (tone) => <Tag>{tone}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'is_published',
      key: 'is_published',
      render: (published) => (
        published ? (
          <Tag icon={<GlobalOutlined />} color="success">
            Published
          </Tag>
        ) : (
          <Tag color="default">Draft</Tag>
        )
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<CopyOutlined />}
            onClick={() => copyToClipboard(record.content)}
          />
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => showPreview(record, 'social')}
          />
        </Space>
      ),
    },
  ];

  // Blog Table Columns
  const blogColumns: ColumnsType<BlogRecord> = [
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      width: '30%',
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: 'Summary',
      dataIndex: 'summary',
      key: 'summary',
      width: '30%',
      render: (text) => (
        <Paragraph ellipsis={{ rows: 2 }} style={{ marginBottom: 0 }}>
          {text}
        </Paragraph>
      ),
    },
    {
      title: 'Source',
      dataIndex: 'source_type',
      key: 'source_type',
      render: (type) => <Tag color={type === 'jobs' ? 'blue' : 'green'}>{type}</Tag>,
    },
    {
      title: 'Details',
      key: 'details',
      render: (_, record) => (
        <Space direction="vertical" size="small">
          {record.word_count && <Tag>{record.word_count} words</Tag>}
          {record.tone && <Tag>{record.tone}</Tag>}
          {record.length && <Tag>{record.length}</Tag>}
        </Space>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'is_published',
      key: 'is_published',
      render: (published) => (
        published ? (
          <Tag icon={<GlobalOutlined />} color="success">
            Published
          </Tag>
        ) : (
          <Tag color="default">Draft</Tag>
        )
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => showPreview(record, 'blog')}
          />
          <Button
            type="link"
            icon={<CopyOutlined />}
            onClick={() => copyToClipboard(record.content)}
          />
        </Space>
      ),
    },
  ];

  const TitlesTab = () => (
    <Card>
      <Space style={{ marginBottom: 16 }}>
        <Select
          placeholder="Source Type"
          style={{ width: 150 }}
          allowClear
          onChange={(value) => setTitleFilters({ ...titleFilters, source_type: value })}
        >
          <Option value="jobs">Jobs</Option>
          <Option value="news">News</Option>
        </Select>
        <Select
          placeholder="Status"
          style={{ width: 150 }}
          allowClear
          onChange={(value) => setTitleFilters({ ...titleFilters, is_used: value })}
        >
          <Option value={false}>Unused</Option>
          <Option value={true}>Used</Option>
        </Select>
      </Space>
      <Table
        columns={titleColumns}
        dataSource={titlesData?.data || []}
        loading={titlesLoading}
        rowKey="id"
        pagination={{ pageSize: 20 }}
      />
    </Card>
  );

  const SocialTab = () => (
    <Card>
      <Space style={{ marginBottom: 16 }}>
        <Select
          placeholder="Source Type"
          style={{ width: 150 }}
          allowClear
          onChange={(value) => setSocialFilters({ ...socialFilters, source_type: value })}
        >
          <Option value="jobs">Jobs</Option>
          <Option value="news">News</Option>
        </Select>
        <Select
          placeholder="Status"
          style={{ width: 150 }}
          allowClear
          onChange={(value) => setSocialFilters({ ...socialFilters, is_published: value })}
        >
          <Option value={false}>Draft</Option>
          <Option value={true}>Published</Option>
        </Select>
      </Space>
      <Table
        columns={socialColumns}
        dataSource={socialData?.data || []}
        loading={socialLoading}
        rowKey="id"
        pagination={{ pageSize: 20 }}
      />
    </Card>
  );

  const BlogsTab = () => (
    <Card>
      <Space style={{ marginBottom: 16 }}>
        <Select
          placeholder="Source Type"
          style={{ width: 150 }}
          allowClear
          onChange={(value) => setBlogFilters({ ...blogFilters, source_type: value })}
        >
          <Option value="jobs">Jobs</Option>
          <Option value="news">News</Option>
        </Select>
        <Select
          placeholder="Status"
          style={{ width: 150 }}
          allowClear
          onChange={(value) => setBlogFilters({ ...blogFilters, is_published: value })}
        >
          <Option value={false}>Draft</Option>
          <Option value={true}>Published</Option>
        </Select>
      </Space>
      <Table
        columns={blogColumns}
        dataSource={blogsData?.data || []}
        loading={blogsLoading}
        rowKey="id"
        pagination={{ pageSize: 20 }}
      />
    </Card>
  );

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>Content Library</Title>
      <Paragraph>View and manage all your generated content</Paragraph>

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          {
            key: 'titles',
            label: 'Saved Titles',
            children: <TitlesTab />,
          },
          {
            key: 'social',
            label: 'Social Media',
            children: <SocialTab />,
          },
          {
            key: 'blogs',
            label: 'Blog Posts',
            children: <BlogsTab />,
          },
        ]}
      />

      <Modal
        title={previewContent?.type === 'blog' ? 'Blog Preview' : previewContent?.type === 'social' ? 'Social Media Preview' : 'Title Preview'}
        open={previewModal}
        onCancel={() => setPreviewModal(false)}
        width={800}
        footer={[
          <Button key="copy" icon={<CopyOutlined />} onClick={() => {
            if (previewContent?.type === 'blog') {
              copyToClipboard(previewContent.content);
            } else if (previewContent?.type === 'social') {
              copyToClipboard(previewContent.content);
            } else {
              copyToClipboard(previewContent.title);
            }
          }}>
            Copy
          </Button>,
          <Button key="close" onClick={() => setPreviewModal(false)}>
            Close
          </Button>,
        ]}
      >
        {previewContent?.type === 'title' && (
          <div>
            <Title level={4}>{previewContent.title}</Title>
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <strong>Source:</strong> <Tag color={previewContent.source_type === 'jobs' ? 'blue' : 'green'}>{previewContent.source_type}</Tag>
              </div>
              {previewContent.filter_sector && <div><strong>Sector:</strong> {previewContent.filter_sector}</div>}
              {previewContent.filter_category && <div><strong>Category:</strong> {previewContent.filter_category}</div>}
              {previewContent.filter_source && <div><strong>Source:</strong> {previewContent.filter_source}</div>}
              <div><strong>Used:</strong> {previewContent.is_used ? `Yes (${previewContent.used_count}x)` : 'No'}</div>
              <div><strong>Created:</strong> {new Date(previewContent.created_at).toLocaleString()}</div>
            </Space>
          </div>
        )}
        {previewContent?.type === 'social' && (
          <div>
            {previewContent.title && <Title level={4}>{previewContent.title}</Title>}
            <Paragraph>{previewContent.content}</Paragraph>
            <Space direction="vertical" style={{ width: '100%', marginTop: 16 }}>
              <div>
                <strong>Source:</strong> <Tag color={previewContent.source_type === 'jobs' ? 'blue' : 'green'}>{previewContent.source_type}</Tag>
              </div>
              {previewContent.tone && <div><strong>Tone:</strong> {previewContent.tone}</div>}
              <div><strong>Status:</strong> {previewContent.is_published ? 'Published' : 'Draft'}</div>
              <div><strong>Created:</strong> {new Date(previewContent.created_at).toLocaleString()}</div>
            </Space>
          </div>
        )}
        {previewContent?.type === 'blog' && (
          <div>
            <Title level={4}>{previewContent.title}</Title>
            {previewContent.summary && (
              <Paragraph strong style={{ color: '#666' }}>
                {previewContent.summary}
              </Paragraph>
            )}
            <Paragraph style={{ whiteSpace: 'pre-wrap', maxHeight: '400px', overflow: 'auto' }}>
              {previewContent.content}
            </Paragraph>
            <Space direction="vertical" style={{ width: '100%', marginTop: 16 }}>
              <div>
                <strong>Source:</strong> <Tag color={previewContent.source_type === 'jobs' ? 'blue' : 'green'}>{previewContent.source_type}</Tag>
              </div>
              {previewContent.word_count && <div><strong>Word Count:</strong> {previewContent.word_count}</div>}
              {previewContent.tone && <div><strong>Tone:</strong> {previewContent.tone}</div>}
              {previewContent.length && <div><strong>Length:</strong> {previewContent.length}</div>}
              <div><strong>Status:</strong> {previewContent.is_published ? 'Published' : 'Draft'}</div>
              {previewContent.published_url && <div><strong>URL:</strong> <a href={previewContent.published_url} target="_blank" rel="noopener noreferrer">{previewContent.published_url}</a></div>}
              <div><strong>Created:</strong> {new Date(previewContent.created_at).toLocaleString()}</div>
            </Space>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ContentLibrary;
