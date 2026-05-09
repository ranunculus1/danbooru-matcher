# 🚀 Vercel 部署指南

## 📋 部署步骤

### 步骤 1: 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名：`danbooru-matcher`
3. 设为公开仓库（Public）
4. 点击 "Create repository"

### 步骤 2: 上传代码到 GitHub

**方法 A: 使用 GitHub 网页上传（最简单）**

1. 打开刚创建的仓库
2. 点击 "uploading an existing file"
3. 把以下文件拖进去：
   - `app.py`
   - `keyword_mapping.py`
   - `requirements.txt`
   - `vercel.json`
   - `.vercelignore`
   - `README.md`
   - `templates/index.html`
4. 点击 "Commit changes"

**方法 B: 使用 Git 命令**

```bash
cd /home/node/.openclaw/workspace/danbooru-matcher
git remote add origin https://github.com/你的用户名/danbooru-matcher.git
git branch -M main
git push -u origin main
```

### 步骤 3: 在 Vercel 部署

1. 访问 https://vercel.com
2. 用 GitHub 账号登录
3. 点击 "Add New Project"
4. 选择 `danbooru-matcher` 仓库
5. 点击 "Import"

### 步骤 4: 配置环境变量

在 Vercel 项目设置页面，添加以下环境变量：

| Variable | Value |
|----------|-------|
| `QWEN_API_KEY` | `sk-B9LzZVnN5h0IGpGIOcONOJagimqPNKDZ8fh1722AzU3PVQo5` |
| `QWEN_API_URL` | `https://api.uglycat.cc/v1/chat/completions` |
| `QWEN_MODEL` | `qwen-3-235b-a22b-instruct-2507` |

### 步骤 5: 完成部署！

点击 "Deploy"，等待约 1-2 分钟，获得固定域名：
```
https://danbooru-matcher-xxx.vercel.app
```

---

## ⏱️ 免费额度能用多久？

### 每月重置的免费额度

| 资源 | 免费额度 | 个人使用 | 结论 |
|------|---------|---------|------|
| **带宽** | 100 GB/月 | 约 1-5 GB/月 | ✅ 一直免费 |
| **函数调用** | 1000 万次/月 | 约 10-50 万次 | ✅ 一直免费 |
| **构建时长** | 6000 分钟/月 | 约 30-60 分钟 | ✅ 一直免费 |

**对于个人使用，Vercel 免费额度完全够用，可以一直免费使用！**

---

## 🔧 更新代码

**每次修改代码后：**

1. 提交到 GitHub
2. Vercel 自动检测并重新部署（约 1-2 分钟）
3. 域名不变，自动更新

---

## 📝 注意事项

1. **API Key 安全** - 使用 Vercel 环境变量，不要硬编码到代码
2. **数据库持久化** - Vercel 是无服务器架构，SQLite 数据会丢失，建议使用外部数据库
3. **域名固定** - `xxx.vercel.app` 域名永久固定，除非删除项目

---

## 🆘 遇到问题？

**常见错误：**

1. **构建失败** - 检查 `requirements.txt` 和 `vercel.json`
2. **500 错误** - 检查环境变量是否配置正确
3. **404 错误** - 检查 `templates/index.html` 是否存在

---

_最后更新：2026-05-09_
