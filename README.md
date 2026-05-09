# 🎨 Danbooru 词条匹配器

智能匹配中文描述到 Danbooru 英文词条的工具。

## 功能特点

- ✨ **智能关键词拆解** - 自动识别"白发蓝瞳美少女"→`white hair`, `blue eyes`, `1girl`
- 📚 **完整模糊匹配** - 支持 100+ 种发色/瞳色/发型等关键词变体
- 📝 **用户投稿系统** - 投票排序，社区共建
- 🤖 **AI 备用匹配** - 实在找不到时才用 AI
- 📋 **点击复制** - 点击词条卡片自动复制英文词条

## 部署到 Vercel

### 1. Fork 本仓库

点击右上角 Fork 按钮

### 2. 在 Vercel 导入项目

1. 访问 https://vercel.com
2. 点击 "Add New Project"
3. 选择 GitHub 仓库
4. 点击 "Import"

### 3. 配置环境变量

在 Vercel 项目设置中添加：

| Variable | Value |
|----------|-------|
| `QWEN_API_KEY` | `sk-xxxxx`（你的千问 API Key） |
| `QWEN_API_URL` | `https://api.uglycat.cc/v1/chat/completions` |
| `QWEN_MODEL` | `qwen-3-235b-a22b-instruct-2507` |

### 4. 部署完成！

Vercel 会自动构建并部署，获得固定域名：
```
https://your-project.vercel.app
```

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python app.py --port 8888
```

## 技术栈

- **前端**: HTML/CSS/JavaScript
- **后端**: Flask + Python
- **数据库**: SQLite
- **部署**: Vercel

## License

MIT
