# VedioS - 自然语言视频检索与智能学习平台

基于Whisper、FAISS和FFmpeg的视频片段自然语言检索与智能学习平台，支持视频内容分析、智能检索、学习测试和个性化AI导师互动。

## 🎯 核心功能

### 视频处理与索引
- **视频上传**：支持多种视频格式（mp4、avi、mov、mkv、flv、wmv）
- **自动转录**：使用Whisper将视频音频转换为文本
- **智能分块**：将转录文本按时间段分割成可管理的块（默认30秒）
- **向量索引**：使用FAISS对文本块进行向量索引，支持高效相似度搜索
- **语言支持**：自动检测或手动指定转录语言

### 智能检索
- **自然语言查询**：支持中文自然语言查询，检索相关视频片段
- **精准匹配**：基于余弦相似度的精确匹配算法
- **结果排序**：按匹配度排序的搜索结果
- **片段定位**：精确到秒的视频片段定位

### 内容生成
- **标题摘要**：自动生成去标题党的真实标题和结构清晰的文字概要
- **思维导图**：生成Markdown格式的可视化思维导图
- **智能习题**：基于视频内容生成3-5道单选题，包含难度系数和详细解析

### 学习测试
- **多关卡测试**：基于视频内容的互动式学习测试
- **自动评分**：实时计算得分并提供详细解析
- **错题分析**：针对错误题目提供针对性指导
- **毕业证书**：生成个性化学习毕业证书

### 百变大师
- **个性化AI导师**：根据视频内容生成专属大师形象（如历史学家、科学家、艺术家等）
- **幽默互动**：大师性格设定为幽默风趣，善于引导思考
- **学习分析**：根据用户答题情况调整回答方式
- **实时对话**：支持与大师实时对话，解答学习问题

## 🛠️ 技术栈

### 后端
- **Python 3.10+**：主要开发语言
- **FastAPI**：现代、快速的Web框架
- **Whisper**：音频转录模型
- **FAISS**：高效的向量索引库
- **FFmpeg**：视频和音频处理工具
- **aiohttp**：异步HTTP客户端
- **dotenv**：环境变量管理
- **Pydantic**：数据验证和设置管理

### 前端
- **HTML5**：页面结构
- **CSS3**：样式设计
- **JavaScript (ES6+)**：交互逻辑
- **Markmap**：思维导图可视化
- **D3.js**：数据驱动的文档可视化

### 机器学习
- **OpenAI Whisper**：语音识别和转录
- **FAISS**：相似性搜索和向量索引
- **大语言模型**：内容生成和对话增强

## 📦 安装与配置

### 环境要求
- **操作系统**：Windows 10+ / Linux / macOS
- **Python**：3.10+（推荐使用虚拟环境）
- **FFmpeg**：需要系统中安装FFmpeg

### 安装步骤

1. **克隆或下载项目**
   ```bash
   cd c:\Users\Lenovo\OneDrive\桌面\vedioS
   ```

2. **创建并激活虚拟环境**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/macOS
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **安装FFmpeg**
   - **Windows**：下载二进制文件并添加到系统环境变量
   - **Linux**：`sudo apt update && sudo apt install ffmpeg`
   - **macOS**：`brew install ffmpeg`

5. **配置环境变量**
   创建`.env`文件并配置必要的环境变量：
   ```env
   # LLM配置
   LLM_API_KEY=your_api_key
   LLM_BASE_URL=https://api.example.com/v1
   LLM_MODEL=gpt-4

   # 视频搜索配置
   WHISPER_MODEL=base  # 可选: tiny, base, small, medium, large
   EMBEDDING_DIMENSION=1024
   INDEX_FILE=video_index.faiss
   CHUNK_DURATION=30.0

   # 嵌入API密钥（如果使用SiliconFlow）
   siliconflow_api_key=your_siliconflow_api_key
   ```

## 🚀 快速开始

### 启动后端服务
```bash
uvicorn main:app --host 0.0.0.0 --port 8567 --reload
```

### 启动前端服务
```bash
python -m http.server 8000
```

### 访问应用
打开浏览器，访问：http://localhost:8000

## 📖 使用指南

### 1. 上传视频
- 点击"选择视频文件"按钮，选择要上传的视频
- 等待视频上传并自动处理完成
- 视频将被转录、分块并建立索引

### 2. 智能检索
- 输入自然语言查询，如："Transformer的核心原理"
- 点击"开始搜索"
- 查看搜索结果，点击"播放片段"观看匹配的视频片段

### 3. 内容生成
- 上传视频后，系统自动生成标题、概要和思维导图
- 可以查看详细的视频内容分析

### 4. 学习测试
- 完成基于视频内容的选择题
- 查看测试结果和详细解析
- 生成个性化毕业证书

### 5. 百变大师
- 完成学习测试后，"百变大师"功能自动解锁
- 向大师提问关于视频内容的问题
- 大师根据你的学习情况进行个性化指导

## 📚 API文档

### 主要API端点

#### 视频处理
- `POST /upload` - 上传视频并自动处理索引
- `GET /search` - 基于自然语言查询检索视频片段
- `GET /video/{filename}` - 获取上传的视频文件
- `GET /index-info` - 获取索引信息
- `POST /extract-segment` - 提取视频片段

#### 内容生成
- `POST /generate-content` - 生成视频内容（标题、概要、思维导图、习题）

#### 学习功能
- `POST /submit-quiz` - 提交答题结果
- `POST /generate-certificate` - 生成毕业证书

#### 百变大师
- `POST /master-agent/identity` - 生成大师身份
- `POST /master-agent/chat` - 与大师对话

### API文档访问
启动后端服务后，访问：http://localhost:8567/docs 查看完整的API文档

## 📁 项目结构

```
vedioS/
├── certificates/               # 生成的毕业证书
├── generated_content/          # 生成的视频内容
├── transcripts/                # 视频转录文本
├── uploaded_videos/            # 上传的视频文件
├── .vscode/                    # VS Code配置
├── .gitignore                  # Git忽略文件
├── README.md                   # 项目说明文档
├── certificate_generator.py    # 证书生成模块
├── configuration.py            # 配置管理
├── content_generator.py        # 内容生成模块
├── embedding.py                # 嵌入模型
├── index.html                  # 前端页面
├── indexer.py                  # 向量索引模块
├── llm_conversation.py         # LLM对话模块
├── main.py                     # FastAPI主应用
├── master_agent.py             # 百变大师模块
├── requirements.txt            # 依赖列表
├── test_video_search.py        # 测试脚本
├── transcriber.py              # 音频转录模块
├── transcript_storage.py       # 转录文本存储
├── video_index.faiss           # FAISS索引文件
├── video_index_metadata.pkl    # 索引元数据
├── video_processor.py          # 视频处理模块
└── video_search_tool.py        # 视频搜索工具
```

## 🔧 主要模块

### VideoProcessor
- 使用FFmpeg处理视频文件
- 提取音频、获取视频时长、提取片段

### Transcriber
- 使用Whisper进行音频转录
- 支持多种语言和模型大小
- 将转录结果分块处理

### VideoIndexer
- 使用FAISS进行向量索引
- 支持持久化存储索引
- 基于余弦相似度进行搜索

### ContentGenerator
- 生成视频标题和概要
- 生成思维导图
- 生成学习测试习题

### MasterAgent
- 生成个性化AI学习导师
- 与用户进行实时对话
- 根据学习情况调整回答方式

### CertificateGenerator
- 生成个性化毕业证书
- 支持自定义证书内容和样式

## 🧪 测试

运行测试脚本：
```bash
python test_video_search.py
```

## ⚠️ 注意事项

1. **模型大小**：Whisper模型大小影响准确性和速度，可根据需要选择（tiny、base、small、medium、large）
2. **内存使用**：大视频文件可能需要较多内存
3. **索引持久化**：索引会自动保存到磁盘，可重复使用
4. **API密钥**：需要正确配置LLM API密钥才能使用所有功能
5. **网络连接**：需要网络连接才能使用Whisper和LLM功能
6. **文件大小限制**：单个视频文件最大支持500MB

## 🚀 扩展功能

- [ ] 支持多语言转录和检索
- [ ] 实时视频流处理
- [ ] 高级搜索过滤器
- [ ] 结果可视化增强
- [ ] 支持更多视频格式
- [ ] 移动端适配

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 项目地址：https://github.com/yourusername/vedioS
- 电子邮件：your.email@example.com

---

**VedioS** - 让视频学习更简单、更智能！ 🎬🤖✨
