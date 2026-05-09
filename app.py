#!/usr/bin/env python3
"""
🎨 Danbooru 词条匹配器
功能：
- 输入中文 → AI 匹配 Danbooru 英文词条
- 显示最多 5 个匹配结果
- 用户投稿词条映射
- 投票排序
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime
import json
import urllib.request
from keyword_mapping import parse_input

app = Flask(__name__)
# 数据库路径：Vercel/HF Space 使用临时目录，本地使用当前目录
DB_PATH = os.environ.get('DB_PATH', os.path.join(os.path.dirname(__file__), 'danbooru_tags.db'))
# Vercel 使用 /tmp 目录
if os.environ.get('VERCEL'):
    DB_PATH = '/tmp/danbooru_tags.db'

# AI API 配置（第三方 API - uglycat.cc）
AI_API_KEY = 'sk-B9LzZVnN5h0IGpGIOcONOJagimqPNKDZ8fh1722AzU3PVQo5'
AI_API_URL = 'https://api.uglycat.cc/v1/chat/completions'
AI_MODEL = 'qwen-3-235b-a22b-instruct-2507'

# 内置常用 Danbooru 词条库（英文 - 中文）
BUILTIN_TAGS = [
    ("red eyes", "红眼睛"),
    ("blue eyes", "蓝眼睛"),
    ("green eyes", "绿眼睛"),
    ("yellow eyes", "黄眼睛"),
    ("purple eyes", "紫眼睛"),
    ("pink eyes", "粉眼睛"),
    ("orange eyes", "橙眼睛"),
    ("black eyes", "黑眼睛"),
    ("white eyes", "白眼睛"),
    ("heterochromia", "异色瞳"),
    ("two side up", "小揪揪"),
    ("short ponytail", "短马尾"),
    ("long hair", "长发"),
    ("short hair", "短发"),
    ("twin tails", "双马尾"),
    ("ponytail", "马尾"),
    ("braid", "辫子"),
    ("bob cut", "波波头"),
    ("blonde hair", "金发"),
    ("black hair", "黑发"),
    ("brown hair", "棕发"),
    ("silver hair", "银发"),
    ("blue hair", "蓝发"),
    ("pink hair", "粉发"),
    ("green hair", "绿发"),
    ("purple hair", "紫发"),
    ("red hair", "红发"),
    ("white hair", "白发"),
    ("smile", "微笑"),
    ("frown", "皱眉"),
    ("angry", "生气"),
    ("crying", "哭泣"),
    ("blush", "脸红"),
    ("laugh", "大笑"),
    ("serious", "严肃"),
    ("surprised", "惊讶"),
    ("school uniform", "校服"),
    ("casual clothes", "便服"),
    ("dress", "连衣裙"),
    ("skirt", "短裙"),
    ("shirt", "衬衫"),
    ("jacket", "夹克"),
    ("coat", "外套"),
    ("sweater", "毛衣"),
    ("hoodie", "连帽衫"),
    ("jeans", "牛仔裤"),
    ("shorts", "短裤"),
    ("glasses", "眼镜"),
    ("hair ornament", "发饰"),
    ("ribbon", "丝带"),
    ("bow", "蝴蝶结"),
    ("hat", "帽子"),
    ("cat ears", "猫耳"),
    ("dog ears", "狗耳"),
    ("fox ears", "狐耳"),
    ("animal ears", "兽耳"),
    ("wings", "翅膀"),
    ("halo", "光环"),
    ("horns", "角"),
    ("tail", "尾巴"),
    ("mechanical wings", "机械翅膀"),
    ("feather wings", "羽毛翅膀"),
    ("demon wings", "恶魔翅膀"),
    ("angel wings", "天使翅膀"),
    ("standing", "站立"),
    ("sitting", "坐着"),
    ("lying", "躺着"),
    ("running", "跑步"),
    ("jumping", "跳跃"),
    ("dancing", "跳舞"),
    ("fighting", "战斗"),
    ("eating", "吃"),
    ("drinking", "喝"),
    ("sleeping", "睡觉"),
    ("reading", "阅读"),
    ("outdoors", "户外"),
    ("indoors", "室内"),
    ("classroom", "教室"),
    ("bedroom", "卧室"),
    ("garden", "花园"),
    ("park", "公园"),
    ("street", "街道"),
    ("school", "学校"),
    ("city", "城市"),
    ("nature", "自然"),
    ("sky", "天空"),
    ("clouds", "云"),
    ("sun", "太阳"),
    ("moon", "月亮"),
    ("stars", "星星"),
    ("night", "夜晚"),
    ("day", "白天"),
    ("sunset", "日落"),
    ("sunrise", "日出"),
    ("rain", "雨"),
    ("snow", "雪"),
    ("fire", "火"),
    ("water", "水"),
    ("ice", "冰"),
    ("lightning", "闪电"),
    ("magic", "魔法"),
    ("weapon", "武器"),
    ("sword", "剑"),
    ("gun", "枪"),
    ("bow", "弓"),
    ("staff", "法杖"),
    ("shield", "盾"),
    ("armor", "盔甲"),
    ("cape", "披风"),
    ("kimono", "和服"),
    ("yukata", "浴衣"),
    ("maid dress", "女仆装"),
    ("swimsuit", "泳装"),
    ("bikini", "比基尼"),
    ("pajamas", "睡衣"),
    ("mask", "面具"),
    ("scar", "伤疤"),
    ("bandage", "绷带"),
    ("flower", "花"),
    ("rose", "玫瑰"),
    ("cherry blossom", "樱花"),
    ("butterfly", "蝴蝶"),
    ("cat", "猫"),
    ("dog", "狗"),
    ("rabbit", "兔子"),
    ("fox", "狐狸"),
    ("dragon", "龙"),
    ("phoenix", "凤凰"),
    ("unicorn", "独角兽"),
    ("mermaid", "美人鱼"),
    ("fairy", "精灵"),
    ("witch", "魔女"),
    ("wizard", "巫师"),
    ("knight", "骑士"),
    ("princess", "公主"),
    ("prince", "王子"),
    ("angel", "天使"),
    ("demon", "恶魔"),
    ("robot", "机器人"),
    ("cyborg", "生化人"),
    ("mecha", "机甲"),
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english TEXT NOT NULL UNIQUE,
            chinese TEXT NOT NULL,
            category TEXT DEFAULT 'builtin',
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chinese_input TEXT NOT NULL,
            english_tag TEXT NOT NULL,
            chinese_translation TEXT NOT NULL,
            votes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (chinese_input, english_tag)
        )
    ''')
    
    for english, chinese in BUILTIN_TAGS:
        try:
            cursor.execute('INSERT OR IGNORE INTO tags (english, chinese) VALUES (?, ?)', (english, chinese))
        except:
            pass
    
    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化完成，内置 {len(BUILTIN_TAGS)} 个词条")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/match', methods=['POST'])
def match_tags():
    data = request.json
    chinese_input = data.get('input', '').strip()
    
    if not chinese_input:
        return jsonify({'error': '请输入中文内容'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. 智能关键词拆解（优先！）
    parsed_keywords, remaining = parse_input(chinese_input)
    
    if parsed_keywords:
        results = [
            {'english': kw['english'], 'chinese': kw['keyword'], 'votes': 0, 'source': '关键词匹配'}
            for kw in parsed_keywords
        ]
        conn.close()
        return jsonify({'results': results[:5], 'source': '关键词匹配'})
    
    # 2. 查找用户投稿
    cursor.execute('''
        SELECT english_tag, chinese_translation, votes
        FROM submissions
        WHERE LOWER(chinese_input) = LOWER(?)
        ORDER BY votes DESC
        LIMIT 5
    ''', (chinese_input,))
    existing = cursor.fetchall()
    
    if existing:
        results = [
            {'english': row['english_tag'], 'chinese': row['chinese_translation'], 'votes': row['votes'], 'source': '用户投稿'}
            for row in existing
        ]
        conn.close()
        return jsonify({'results': results, 'source': 'database'})
    
    # 3. 从 Danbooru 词库模糊匹配
    cursor.execute('''
        SELECT english, chinese, usage_count
        FROM tags
        WHERE chinese LIKE ? OR english LIKE ?
        ORDER BY usage_count DESC
        LIMIT 10
    ''', (f'%{chinese_input}%', f'%{chinese_input}%'))
    db_matches = cursor.fetchall()
    
    if db_matches:
        results = [
            {'english': row['english'], 'chinese': row['chinese'], 'votes': row['usage_count'], 'source': 'Danbooru 词库'}
            for row in db_matches[:5]
        ]
        conn.close()
        return jsonify({'results': results, 'source': 'database'})
    
    conn.close()
    
    # 4. AI 匹配（实在找不到时）
    if not AI_API_KEY:
        return jsonify({'error': '未配置 AI API Key（请在 HF Space 设置中添加 QWEN_API_KEY 或 DEEPSEEK_API_KEY）', 'demo_mode': True, 'results': []}), 500
    
    prompt = f"""Danbooru 词条匹配助手。

任务：根据中文描述匹配最相关的 Danbooru 英文词条，返回最多 5 个。
格式：JSON 数组，每个元素包含 english 和 chinese 字段。

输入：{chinese_input}

返回 JSON 数组即可。"""

    try:
        req_data = json.dumps({
            'model': AI_MODEL,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': 0.3,
            'max_tokens': 500
        }).encode('utf-8')
        
        req = urllib.request.Request(
            AI_API_URL,
            data=req_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {AI_API_KEY}',
                'User-Agent': 'Mozilla/5.0 (compatible; DanbooruMatcher/1.0)'
            },
            method='POST'
        )
        
        import ssl
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(req, timeout=30, context=context) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
        
        import re
        json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
        if json_match:
            ai_response = json_match.group()
        
        matches = json.loads(ai_response)
        results = [
            {'english': m.get('english', ''), 'chinese': m.get('chinese', ''), 'votes': 0, 'source': 'AI 匹配'}
            for m in matches[:5]
        ]
        
        return jsonify({'results': results, 'source': 'ai'})
        
    except Exception as e:
        return jsonify({'error': f'AI 匹配失败：{str(e)}'}), 500

@app.route('/api/submit', methods=['POST'])
def submit_tag():
    data = request.json
    chinese_input = data.get('chinese_input', '').strip()
    english_tag = data.get('english_tag', '').strip()
    chinese_translation = data.get('chinese_translation', '').strip()
    
    if not all([chinese_input, english_tag, chinese_translation]):
        return jsonify({'error': '请填写完整信息'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO submissions (chinese_input, english_tag, chinese_translation, votes)
            VALUES (?, ?, ?, 1)
            ON CONFLICT (chinese_input, english_tag) DO UPDATE SET
                votes = votes + 1,
                chinese_translation = excluded.chinese_translation
        ''', (chinese_input, english_tag, chinese_translation))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': '投稿成功！'})
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT chinese_input, english_tag, chinese_translation, votes, created_at
        FROM submissions
        ORDER BY votes DESC, created_at DESC
        LIMIT 50
    ''')
    submissions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(submissions)

# 启动时初始化数据库
# Vercel 使用 /tmp 目录
if os.environ.get('VERCEL'):
    DB_PATH = '/tmp/danbooru_tags.db'
    os.makedirs('/tmp/templates', exist_ok=True)
    # 复制模板到临时目录
    import shutil
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if os.path.exists(templates_dir):
        for f in os.listdir(templates_dir):
            src = os.path.join(templates_dir, f)
            dst = os.path.join('/tmp/templates', f)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
    app.template_folder = '/tmp/templates'

os.makedirs('templates', exist_ok=True)
init_db()

# Vercel 部署：导出 app 对象即可
# 本地运行
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--host', type=str, default='0.0.0.0')
    args = parser.parse_args()
    
    # 自动检测运行环境
    if os.environ.get('HF_SPACE_ID'):
        port = 7860
        env_name = "HF Space"
    elif os.environ.get('VERCEL'):
        port = 8080
        env_name = "Vercel"
    else:
        port = args.port
        env_name = "本地"
    
    print(f"\n🎨 Danbooru 词条匹配器启动中... [{env_name}] http://{args.host}:{port}")
    app.run(host=args.host, port=port, debug=False)
