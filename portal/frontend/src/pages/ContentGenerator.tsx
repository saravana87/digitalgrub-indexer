import React, { useState } from 'react';
import { 
  Card, Input, Button, Select, Space, List, Tag, Divider, message, 
  Tabs, Row, Col, Typography, Spin, Empty, Modal 
} from 'antd';
import { 
  CopyOutlined, SaveOutlined, ReloadOutlined, FileTextOutlined,
  ShareAltOutlined, EditOutlined 
} from '@ant-design/icons';
import { useQuery, useMutation } from '@tanstack/react-query';
import { contentApi } from '../api/client';

const { Option } = Select;
const { Title, Paragraph, Text } = Typography;

const ContentGenerator: React.FC = () => {
  const [activeTab, setActiveTab] = useState('titles');
  
  // Common state
  const [sourceType, setSourceType] = useState<'jobs' | 'news'>('jobs');
  const [sector, setSector] = useState<string | undefined>(undefined);
  const [category, setCategory] = useState<string | undefined>(undefined);
  const [source, setSource] = useState<string | undefined>(undefined);
  
  // Titles state
  const [titleCount, setTitleCount] = useState(5);
  const [generatedTitles, setGeneratedTitles] = useState<string[]>([]);
  
  // Social content state
  const [socialTitle, setSocialTitle] = useState('');
  const [socialTone, setSocialTone] = useState('professional');
  const [generatedSocial, setGeneratedSocial] = useState('');
  
  // Blog state
  const [blogTitle, setBlogTitle] = useState('');
  const [blogTone, setBlogTone] = useState('professional');
  const [blogLength, setBlogLength] = useState('medium');
  const [generatedBlog, setGeneratedBlog] = useState<any>(null);
  
  // Modal state
  const [previewModal, setPreviewModal] = useState(false);
  const [previewContent, setPreviewContent] = useState('');

  // Fetch filter options
  const { data: filterOptions, isLoading: filtersLoading } = useQuery({
    queryKey: ['filters'],
    queryFn: async () => {
      const response = await contentApi.getFilters();
      return response.data;
    },
  });

  // Fetch saved titles
  const { data: savedTitles, refetch: refetchTitles } = useQuery({
    queryKey: ['titles'],
    queryFn: async () => {
      const response = await contentApi.listTitles({
        source_type: sourceType,
        filter_sector: sector,
        filter_category: category,
        filter_source: source,
        limit: 50,
      });
      return response.data;
    },
    enabled: activeTab === 'titles',
    refetchOnWindowFocus: false,
  });

  // Fetch saved social content
  const { data: savedSocial, refetch: refetchSocial } = useQuery({
    queryKey: ['social'],
    queryFn: async () => {
      const response = await contentApi.listSocial({
        source_type: sourceType,
        filter_sector: sector,
        filter_category: category,
        filter_source: source,
        limit: 50,
      });
      return response.data;
    },
    enabled: activeTab === 'social',
    refetchOnWindowFocus: false,
  });

  // Fetch saved blogs
  const { data: savedBlogs, refetch: refetchBlogs } = useQuery({
    queryKey: ['blogs'],
    queryFn: async () => {
      const response = await contentApi.listBlogs({
        source_type: sourceType,
        filter_sector: sector,
        filter_category: category,
        filter_source: source,
        limit: 50,
      });
      return response.data;
    },
    enabled: activeTab === 'blog',
    refetchOnWindowFocus: false,
  });

  // Generate titles mutation
  const generateTitlesMutation = useMutation({
    mutationFn: (data: any) => contentApi.generateTitles(data),
    onSuccess: (response) => {
      setGeneratedTitles(response.data.titles);
      message.success(`${response.data.titles.length} titles generated and saved!`);
      
      // Auto-save all generated titles
      const savePromises = response.data.titles.map((title: string) => 
        contentApi.saveTitle({
          source_type: sourceType,
          topic: '',
          title,
          filter_sector: sourceType === 'jobs' ? sector : undefined,
          filter_category: sourceType === 'news' ? category : undefined,
          filter_source: sourceType === 'news' ? source : undefined,
        })
      );
      
      Promise.all(savePromises).then(() => {
        refetchTitles();
      });
    },
    onError: () => {
      message.error('Failed to generate titles');
    },
  });

  // Save title mutation
  const saveTitleMutation = useMutation({
    mutationFn: (data: any) => contentApi.saveTitle(data),
    onSuccess: () => {
      message.success('Title saved!');
      refetchTitles();
    },
    onError: () => {
      message.error('Failed to save title');
    },
  });

  // Generate social mutation
  const generateSocialMutation = useMutation({
    mutationFn: (data: any) => contentApi.generateSocial(data),
    onSuccess: (response) => {
      setGeneratedSocial(response.data.content);
      message.success('Content generated successfully!');
      // Auto-save
      saveSocialMutation.mutate({
        source_type: sourceType,
        topic: '',
        title: socialTitle,
        content: response.data.content,
        tone: socialTone,
        filter_sector: sourceType === 'jobs' ? sector : undefined,
        filter_category: sourceType === 'news' ? category : undefined,
        filter_source: sourceType === 'news' ? source : undefined,
      });
    },
    onError: () => {
      message.error('Failed to generate content');
    },
  });

  // Save social mutation
  const saveSocialMutation = useMutation({
    mutationFn: (data: any) => contentApi.generateSocial(data),
    onSuccess: () => {
      refetchSocial();
    },
  });

  // Generate blog mutation
  const generateBlogMutation = useMutation({
    mutationFn: (data: any) => contentApi.generateBlog(data),
    onSuccess: (response) => {
      setGeneratedBlog(response.data);
      message.success('Blog generated successfully!');
      refetchBlogs();
    },
    onError: () => {
      message.error('Failed to generate blog');
    },
  });

  const handleSourceTypeChange = (newType: 'jobs' | 'news') => {
    setSourceType(newType);
    setSector(undefined);
    setCategory(undefined);
    setSource(undefined);
  };

  const handleGenerateTitles = () => {
    generateTitlesMutation.mutate({
      source_type: sourceType,
      count: titleCount,
      sector: sourceType === 'jobs' ? sector : undefined,
      category: sourceType === 'news' ? category : undefined,
      source: sourceType === 'news' ? source : undefined,
    });
  };

  const handleSaveTitle = (title: string) => {
    saveTitleMutation.mutate({
      source_type: sourceType,
      topic: '',
      title,
      filter_sector: sourceType === 'jobs' ? sector : undefined,
      filter_category: sourceType === 'news' ? category : undefined,
      filter_source: sourceType === 'news' ? source : undefined,
    });
  };

  const handleGenerateSocial = () => {
    if (!socialTitle.trim()) {
      message.warning('Please enter a title');
      return;
    }

    generateSocialMutation.mutate({
      title: socialTitle,
      topic: '',
      source_type: sourceType,
      tone: socialTone,
      filter_sector: sourceType === 'jobs' ? sector : undefined,
      filter_category: sourceType === 'news' ? category : undefined,
      filter_source: sourceType === 'news' ? source : undefined,
    });
  };

  const handleGenerateBlog = () => {
    if (!blogTitle.trim()) {
      message.warning('Please enter a title');
      return;
    }

    generateBlogMutation.mutate({
      title: blogTitle,
      topic: '',
      source_type: sourceType,
      tone: blogTone,
      length: blogLength,
      filter_sector: sourceType === 'jobs' ? sector : undefined,
      filter_category: sourceType === 'news' ? category : undefined,
      filter_source: sourceType === 'news' ? source : undefined,
    });
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    message.success('Copied to clipboard!');
  };

  const showPreview = (content: string) => {
    setPreviewContent(content);
    setPreviewModal(true);
  };

  // Common filter component
  const FilterSection = () => (
    <Card size="small" style={{ marginBottom: 16 }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        <div>
          <Text strong>Source Type:</Text>
          <Select
            value={sourceType}
            onChange={handleSourceTypeChange}
            style={{ width: '100%', marginTop: 8 }}
          >
            <Option value="jobs">Jobs</Option>
            <Option value="news">News</Option>
          </Select>
        </div>

        {filtersLoading ? (
          <Spin size="small" />
        ) : (
          <>
            {sourceType === 'jobs' && (
              <div>
                <Text strong>Sector:</Text>
                <Select
                  placeholder="Select Sector (optional)"
                  value={sector}
                  onChange={setSector}
                  allowClear
                  style={{ width: '100%', marginTop: 8 }}
                >
                  {filterOptions?.job_sectors?.map((s: string) => (
                    <Option key={s} value={s}>{s}</Option>
                  ))}
                </Select>
              </div>
            )}

            {sourceType === 'news' && (
              <>
                <div>
                  <Text strong>Category:</Text>
                  <Select
                    placeholder="Select Category (optional)"
                    value={category}
                    onChange={setCategory}
                    allowClear
                    style={{ width: '100%', marginTop: 8 }}
                  >
                    {filterOptions?.news_categories?.map((c: string) => (
                      <Option key={c} value={c}>{c}</Option>
                    ))}
                  </Select>
                </div>
                <div>
                  <Text strong>Source:</Text>
                  <Select
                    placeholder="Select Source (optional)"
                    value={source}
                    onChange={setSource}
                    allowClear
                    style={{ width: '100%', marginTop: 8 }}
                  >
                    {filterOptions?.news_sources?.map((s: string) => (
                      <Option key={s} value={s}>{s}</Option>
                    ))}
                  </Select>
                </div>
              </>
            )}
          </>
        )}
      </Space>
    </Card>
  );

  // Titles Tab
  const TitlesTab = () => (
    <Row gutter={16}>
      <Col span={12}>
        <Card title="Generate Titles" extra={<FileTextOutlined />}>
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <FilterSection />

            <div>
              <Text strong>Number of Titles:</Text>
              <Select
                value={titleCount}
                onChange={setTitleCount}
                style={{ width: '100%', marginTop: 8 }}
              >
                {[3, 5, 7, 10].map((num) => (
                  <Option key={num} value={num}>{num}</Option>
                ))}
              </Select>
            </div>

            <Button
              type="primary"
              onClick={handleGenerateTitles}
              loading={generateTitlesMutation.isPending}
              icon={<ReloadOutlined />}
              block
            >
              Generate Titles
            </Button>

            {generatedTitles.length > 0 && (
              <div>
                <Divider>Generated Titles</Divider>
                <List
                  size="small"
                  bordered
                  dataSource={generatedTitles}
                  renderItem={(title, index) => (
                    <List.Item
                      actions={[
                        <Button
                          key="copy"
                          size="small"
                          icon={<CopyOutlined />}
                          onClick={() => copyToClipboard(title)}
                        />,
                        <Button
                          key="save"
                          size="small"
                          type="primary"
                          icon={<SaveOutlined />}
                          onClick={() => handleSaveTitle(title)}
                        />,
                      ]}
                    >
                      <Text>{index + 1}. {title}</Text>
                    </List.Item>
                  )}
                />
              </div>
            )}
          </Space>
        </Card>
      </Col>

      <Col span={12}>
        <Card title="Saved Titles Library" extra={<Tag color="blue">{savedTitles?.length || 0} titles</Tag>}>
          {!savedTitles || savedTitles.length === 0 ? (
            <Empty description="No saved titles yet" />
          ) : (
            <List
              size="small"
              dataSource={savedTitles}
              renderItem={(item: any) => (
                <List.Item
                  actions={[
                    <Button
                      key="copy"
                      size="small"
                      icon={<CopyOutlined />}
                      onClick={() => copyToClipboard(item.title)}
                    />,
                    <Button
                      key="social"
                      size="small"
                      onClick={() => {
                        setSocialTitle(item.title);
                        setActiveTab('social');
                        message.info('Title loaded to Social Media tab');
                      }}
                    >
                      Use for Social
                    </Button>,
                    <Button
                      key="blog"
                      size="small"
                      onClick={() => {
                        setBlogTitle(item.title);
                        setActiveTab('blog');
                        message.info('Title loaded to Blog tab');
                      }}
                    >
                      Use for Blog
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    title={item.title}
                    description={
                      <Space size="small">
                        <Tag>{item.source_type}</Tag>
                        {item.filter_sector && <Tag color="green">{item.filter_sector}</Tag>}
                        {item.filter_category && <Tag color="blue">{item.filter_category}</Tag>}
                        <Text type="secondary" style={{ fontSize: 11 }}>
                          {new Date(item.created_at).toLocaleDateString()}
                        </Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </Card>
      </Col>
    </Row>
  );

  // Social Media Tab
  const SocialTab = () => (
    <Row gutter={16}>
      <Col span={12}>
        <Card title="Generate Content" extra={<ShareAltOutlined />}>
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <FilterSection />
            
            <div>
              <Text strong>Title:</Text>
              <Input
                placeholder="Enter title"
                value={socialTitle}
                onChange={(e) => setSocialTitle(e.target.value)}
                style={{ marginTop: 8 }}
              />
            </div>

            <div>
              <Text strong>Tone:</Text>
              <Select
                value={socialTone}
                onChange={setSocialTone}
                style={{ width: '100%', marginTop: 8 }}
              >
                <Option value="professional">Professional</Option>
                <Option value="casual">Casual</Option>
                <Option value="enthusiastic">Enthusiastic</Option>
                <Option value="informative">Informative</Option>
              </Select>
            </div>

            <Button
              type="primary"
              onClick={handleGenerateSocial}
              loading={generateSocialMutation.isPending}
              icon={<ReloadOutlined />}
              block
            >
              Generate Content
            </Button>

            {generatedSocial && (
              <div>
                <Divider>Generated Content</Divider>
                <Card size="small">
                  <Paragraph>{generatedSocial}</Paragraph>
                  <Button
                    size="small"
                    icon={<CopyOutlined />}
                    onClick={() => copyToClipboard(generatedSocial)}
                  >
                    Copy
                  </Button>
                </Card>
              </div>
            )}
          </Space>
        </Card>
      </Col>

      <Col span={12}>
        <Card title="Content Library" extra={<Tag color="green">{savedSocial?.length || 0} items</Tag>}>
          {!savedSocial || savedSocial.length === 0 ? (
            <Empty description="No saved content yet" />
          ) : (
            <List
              size="small"
              dataSource={savedSocial}
              renderItem={(item: any) => (
                <List.Item
                  actions={[
                    <Button
                      key="copy"
                      size="small"
                      icon={<CopyOutlined />}
                      onClick={() => copyToClipboard(item.content)}
                    />,
                  ]}
                >
                  <List.Item.Meta
                    title={item.title || 'Untitled'}
                    description={
                      <>
                        <Paragraph ellipsis={{ rows: 2 }}>{item.content}</Paragraph>
                        <Space size="small">
                          <Tag>{item.tone}</Tag>
                          <Tag>{item.source_type}</Tag>
                          <Text type="secondary" style={{ fontSize: 11 }}>
                            {new Date(item.created_at).toLocaleDateString()}
                          </Text>
                        </Space>
                      </>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </Card>
      </Col>
    </Row>
  );

  // Blog Tab
  const BlogTab = () => (
    <Row gutter={16}>
      <Col span={12}>
        <Card title="Generate Blog" extra={<EditOutlined />}>
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            <FilterSection />
            
            <div>
              <Text strong>Title:</Text>
              <Input
                placeholder="Enter blog title"
                value={blogTitle}
                onChange={(e) => setBlogTitle(e.target.value)}
                style={{ marginTop: 8 }}
              />
            </div>

            <div>
              <Text strong>Tone:</Text>
              <Select
                value={blogTone}
                onChange={setBlogTone}
                style={{ width: '100%', marginTop: 8 }}
              >
                <Option value="professional">Professional</Option>
                <Option value="casual">Casual</Option>
                <Option value="technical">Technical</Option>
                <Option value="conversational">Conversational</Option>
              </Select>
            </div>

            <div>
              <Text strong>Length:</Text>
              <Select
                value={blogLength}
                onChange={setBlogLength}
                style={{ width: '100%', marginTop: 8 }}
              >
                <Option value="short">Short (~500 words)</Option>
                <Option value="medium">Medium (~1000 words)</Option>
                <Option value="long">Long (~1500 words)</Option>
              </Select>
            </div>

            <Button
              type="primary"
              onClick={handleGenerateBlog}
              loading={generateBlogMutation.isPending}
              icon={<ReloadOutlined />}
              block
            >
              Generate Blog
            </Button>

            {generatedBlog && (
              <div>
                <Divider>Generated Blog</Divider>
                <Card size="small">
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Text strong>Summary:</Text>
                    <Paragraph>{generatedBlog.summary}</Paragraph>
                    <Space>
                      <Tag>Words: {generatedBlog.word_count}</Tag>
                      <Button
                        size="small"
                        onClick={() => showPreview(generatedBlog.content)}
                      >
                        Preview Full
                      </Button>
                      <Button
                        size="small"
                        icon={<CopyOutlined />}
                        onClick={() => copyToClipboard(generatedBlog.content)}
                      >
                        Copy
                      </Button>
                    </Space>
                  </Space>
                </Card>
              </div>
            )}
          </Space>
        </Card>
      </Col>

      <Col span={12}>
        <Card title="Blog Library" extra={<Tag color="purple">{savedBlogs?.length || 0} blogs</Tag>}>
          {!savedBlogs || savedBlogs.length === 0 ? (
            <Empty description="No saved blogs yet" />
          ) : (
            <List
              size="small"
              dataSource={savedBlogs}
              renderItem={(item: any) => (
                <List.Item
                  actions={[
                    <Button
                      key="view"
                      size="small"
                      onClick={() => showPreview(item.content)}
                    >
                      View
                    </Button>,
                    <Button
                      key="copy"
                      size="small"
                      icon={<CopyOutlined />}
                      onClick={() => copyToClipboard(item.content)}
                    />,
                  ]}
                >
                  <List.Item.Meta
                    title={item.title}
                    description={
                      <>
                        <Paragraph ellipsis={{ rows: 2 }}>{item.summary}</Paragraph>
                        <Space size="small">
                          <Tag>{item.word_count} words</Tag>
                          <Tag>{item.tone}</Tag>
                          <Tag>{item.source_type}</Tag>
                          <Text type="secondary" style={{ fontSize: 11 }}>
                            {new Date(item.created_at).toLocaleDateString()}
                          </Text>
                        </Space>
                      </>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </Card>
      </Col>
    </Row>
  );

  return (
    <div style={{ padding: 24 }}>
      <Title level={2}>Content Generator</Title>
      <Paragraph>
        Generate and manage titles, social media content, and blogs with AI-powered insights
      </Paragraph>

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        destroyInactiveTabPane={false}
        items={[
          {
            key: 'titles',
            label: 'Titles',
            children: <TitlesTab />,
          },
          {
            key: 'social',
            label: 'Social Media',
            children: <SocialTab />,
          },
          {
            key: 'blog',
            label: 'Blogs',
            children: <BlogTab />,
          },
        ]}
      />

      <Modal
        title="Content Preview"
        open={previewModal}
        onCancel={() => setPreviewModal(false)}
        footer={[
          <Button key="copy" icon={<CopyOutlined />} onClick={() => copyToClipboard(previewContent)}>
            Copy
          </Button>,
          <Button key="close" onClick={() => setPreviewModal(false)}>
            Close
          </Button>,
        ]}
        width={800}
      >
        <div style={{ maxHeight: 500, overflow: 'auto' }}>
          <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
            {previewContent}
          </pre>
        </div>
      </Modal>
    </div>
  );
};

export default ContentGenerator;
