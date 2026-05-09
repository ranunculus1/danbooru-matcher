---
title: Danbooru 词条匹配器
emoji: 🎨
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
license: mit
---

# 🎨 Danbooru 词条匹配器

输入中文描述，自动匹配 Danbooru 英文词条！

## 功能

- 🔍 **AI 智能匹配** - 输入中文，输出最相关的 Danbooru 英文词条
- 📊 **最多 5 个结果** - 按匹配度排序显示
- 📝 **用户投稿** - 提交自己的中文→英文映射
- 🏆 **投票排序** - 投稿多的词条优先显示
- 📖 **中文翻译** - 每个词条下方显示中文翻译

## 使用示例

| 中文输入 | 匹配结果 |
|---------|---------|
| 红色眼睛 | red eyes（红眼睛） |
| 小揪揪 | two side up（两边小辫子） |
| 猫耳朵 | cat ears（猫耳） |
| 异色瞳 | heterochromia（异色瞳） |
| 机械翅膀 | mechanical wings（机械翅膀） |

## 部署

### 本地运行

```bash
pip3 install flask
python3 app.py --port 5000
```

### Hugging Face Spaces

已配置自动部署，推送到 main 分支即可。

## 环境变量

- `DEEPSEEK_API_KEY` - DeepSeek API Key（可选，用于 AI 匹配）
- `DEEPSEEK_MODEL` - 模型名称（默认：deepseek-chat）

## 技术栈

- **后端**: Flask + SQLite
- **前端**: HTML + CSS + JavaScript
- **AI**: DeepSeek API

## 内置词条

包含 150+ 常用 Danbooru 词条，涵盖：
- 外貌特征（眼睛颜色、发型等）
- 服装配饰
- 动作表情
- 场景环境
- 角色属性

## License

MIT
