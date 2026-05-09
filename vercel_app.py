#!/usr/bin/env python3
"""
🎨 Danbooru 词条匹配器 - Vercel 入口
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime
import json
import urllib.request
from keyword_mapping import parse_input

app = Flask(__name__)

# Vercel 使用 /tmp 目录
DB_PATH = '/tmp/danbooru_tags.db'

# AI API 配置（从环境变量读取）
AI_API_KEY = os.environ.get('QWEN_API_KEY', 'sk-B9LzZVnN5h0IGpGIOcONOJagimqPNKDZ8fh1722AzU3PVQo5')
AI_API_URL = os.environ.get('QWEN_API_URL', 'https://api.uglycat.cc/v1/chat/completions')
AI_MODEL = os.environ.get('QWEN_MODEL', 'qwen-3-235b-a22b-instruct-2507')

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
    ("blunt bangs", "齐刘海"),
    ("forehead", "露额头"),
    ("hair between eyes", "眼间发"),
    ("ahoge", "呆毛"),
    ("white hair", "白发"),
    ("black hair", "黑发"),
    ("blonde hair", "金发"),
    ("brown hair", "棕发"),
    ("blue hair", "蓝发"),
    ("pink hair", "粉发"),
    ("purple hair", "紫发"),
    ("green hair", "绿发"),
    ("red hair", "红发"),
    ("grey hair", "灰发"),
    ("orange hair", "橙发"),
    ("silver hair", "银发"),
    ("light blue hair", "浅蓝发"),
    ("dark blue hair", "深蓝发"),
    ("light brown hair", "浅棕发"),
    ("dark brown hair", "深棕发"),
    ("light pink hair", "浅粉发"),
    ("dark pink hair", "深粉发"),
    ("platinum blonde", "铂金发"),
    ("ash blonde", "灰金色"),
    ("strawberry blonde", "草莓金"),
    ("aqua hair", "水色发"),
    ("teal hair", "青绿发"),
    ("lavender hair", "薰衣草发"),
    ("multicolored hair", "多色发"),
    ("gradient hair", "渐变发"),
    ("colored inner hair", "内层染发"),
    ("streaked hair", "挑染"),
    ("blue eyes", "蓝瞳"),
    ("red eyes", "红瞳"),
    ("green eyes", "绿瞳"),
    ("purple eyes", "紫瞳"),
    ("pink eyes", "粉瞳"),
    ("yellow eyes", "金瞳"),
    ("orange eyes", "橙瞳"),
    ("black eyes", "黑瞳"),
    ("brown eyes", "棕瞳"),
    ("grey eyes", "灰瞳"),
    ("white eyes", "白瞳"),
    ("aqua eyes", "水色瞳"),
    ("teal eyes", "青绿瞳"),
    ("lavender eyes", "薰衣草瞳"),
    ("heterochromia", "异色瞳"),
    ("red and blue eyes", "红蓝异色"),
    ("red and green eyes", "红绿异色"),
    ("blue and green eyes", "蓝绿异色"),
    ("blue and yellow eyes", "蓝黄异色"),
    ("purple and blue eyes", "紫蓝异色"),
    ("pink and blue eyes", "粉蓝异色"),
    ("one eye covered", "单眼遮盖"),
    ("closed eyes", "闭眼"),
    ("half-closed eyes", "半闭眼"),
    ("eye reflection", "眼反光"),
    ("glowing eyes", "发光眼"),
    ("empty eyes", "空洞眼"),
    ("heart-shaped eyes", "爱心眼"),
    ("star-shaped eyes", "星星眼"),
    ("x-shaped eyes", "X 形眼"),
    ("dollar-shaped eyes", "金钱眼"),
    ("spiral eyes", "螺旋眼"),
    ("button eyes", "纽扣眼"),
    ("no eyes", "无眼"),
    ("extra eyes", "多眼"),
    ("no visible eyes", "不可见眼"),
]

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建词条映射表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tag_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chinese_input TEXT NOT NULL,
            english_tag TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usage_count INTEGER DEFAULT 0
        )
    ''')
    
    # 创建投票表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mapping_id INTEGER NOT NULL,
            ip_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mapping_id) REFERENCES tag_mappings(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/api/match', methods=['POST'])
def match_tags():
    """匹配词条"""
    data = request.get_json()
    chinese_input = data.get('input', '')
    
    if not chinese_input:
        return jsonify({'error': '请输入内容'}), 400
    
    # 1. 先从数据库查询用户投稿
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT english_tag, chinese_input, usage_count 
        FROM tag_mappings 
        WHERE chinese_input LIKE ? 
        ORDER BY usage_count DESC, votes DESC
        LIMIT 5
    ''', (f'%{chinese_input}%',))
    db_results = cursor.fetchall()
    conn.close()
    
    results = []
    matched_keywords = set()
    
    # 添加数据库结果
    for row in db_results:
        results.append({
            'tag': row['english_tag'],
            'translation': row['chinese_input'],
            'source': '用户投稿',
            'votes': row['usage_count']
        })
        matched_keywords.add(row['english_tag'])
    
    # 2. 如果数据库结果不足，使用关键词拆解
    if len(results) < 5:
        parsed = parse_input(chinese_input)
        for keyword, tag in parsed:
            if tag not in matched_keywords:
                # 检查是否在内置词库中
                for builtin_tag, builtin_cn in BUILTIN_TAGS:
                    if keyword in builtin_cn or builtin_tag == tag:
                        results.append({
                            'tag': tag,
                            'translation': builtin_cn,
                            'source': '词库匹配',
                            'votes': 0
                        })
                        matched_keywords.add(tag)
                        break
    
    # 3. 如果还是不足，使用 AI 匹配
    if len(results) < 5:
        try:
            ai_results = query_ai(chinese_input)
            for tag, translation in ai_results:
                if tag not in matched_keywords:
                    results.append({
                        'tag': tag,
                        'translation': translation,
                        'source': 'AI 匹配',
                        'votes': 0
                    })
                    matched_keywords.add(tag)
                    if len(results) >= 5:
                        break
        except Exception as e:
            pass
    
    return jsonify({'results': results[:5]})

def query_ai(chinese_input):
    """查询 AI 匹配"""
    prompt = f"""请将以下中文描述转换为 Danbooru 风格的英文标签。
只返回标签列表，每行一个标签，格式：英文标签，中文翻译

输入：{chinese_input}

示例：
输入：白发红瞳
输出：
white hair，白发
red eyes，红瞳

现在请转换："""
    
    req = urllib.request.Request(
        AI_API_URL,
        data=json.dumps({
            'model': AI_MODEL,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.3,
            'max_tokens': 500
        }).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {AI_API_KEY}',
            'Content-Type': 'application/json'
        },
        method='POST'
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        results = []
        for line in content.strip().split('\n'):
            if '，' in line:
                parts = line.split(',')
                if len(parts) >= 2:
                    tag = parts[0].strip()
                    translation = ','.join(parts[1:]).strip()
                    results.append((tag, translation))
        
        return results

@app.route('/api/submit', methods=['POST'])
def submit_mapping():
    """投稿词条"""
    data = request.get_json()
    chinese = data.get('chinese', '')
    english = data.get('english', '')
    
    if not chinese or not english:
        return jsonify({'error': '请填写完整信息'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tag_mappings (chinese_input, english_tag)
        VALUES (?, ?)
    ''', (chinese, english))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/vote', methods=['POST'])
def vote_mapping():
    """投票"""
    data = request.get_json()
    mapping_id = data.get('id')
    
    if not mapping_id:
        return jsonify({'error': '无效 ID'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tag_mappings SET usage_count = usage_count + 1
        WHERE id = ?
    ''', (mapping_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/submissions', methods=['GET'])
def get_submissions():
    """获取投稿列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, chinese_input, english_tag, usage_count, created_at
        FROM tag_mappings
        ORDER BY usage_count DESC, created_at DESC
        LIMIT 50
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    submissions = []
    for row in rows:
        submissions.append({
            'id': row['id'],
            'chinese': row['chinese_input'],
            'english': row['english_tag'],
            'votes': row['usage_count'],
            'created_at': row['created_at']
        })
    
    return jsonify({'submissions': submissions})

# Vercel 需要这个
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)
