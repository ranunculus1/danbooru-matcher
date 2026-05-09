#!/usr/bin/env python3
"""
📥 导入 Danbooru CSV 词条到数据库
"""

import sqlite3
import csv
import os

DB_PATH = '/home/node/.openclaw/workspace/danbooru-matcher/danbooru_tags.db'
CSV_PATH = '/home/node/.openclaw/media/inbound/9b4466f6-0f4e-4bad-adc5-437d4fd21d36.csv'

def main():
    if not os.path.exists(CSV_PATH):
        print(f"❌ CSV 文件不存在：{CSV_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 确保 tags 表存在
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english TEXT NOT NULL UNIQUE,
            chinese TEXT NOT NULL,
            category TEXT DEFAULT 'danbooru',
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 读取 CSV 并导入
    count = 0
    duplicate = 0
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            english = row.get('标签名', '').strip()
            chinese = row.get('中文翻译', '').strip()
            usage_count = int(row.get('使用次数', 0) or 0)
            category = row.get('分类', 'danbooru')
            
            if not english or not chinese:
                continue
            
            try:
                cursor.execute('''
                    INSERT INTO tags (english, chinese, category, usage_count)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT (english) DO UPDATE SET
                        chinese = excluded.chinese,
                        usage_count = excluded.usage_count
                ''', (english, chinese, category, usage_count))
                count += 1
            except sqlite3.IntegrityError:
                duplicate += 1
    
    conn.commit()
    
    # 统计
    cursor.execute('SELECT COUNT(*) FROM tags')
    total = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✅ 导入完成！")
    print(f"   成功：{count} 个")
    print(f"   重复：{duplicate} 个")
    print(f"   数据库总计：{total} 个词条")

if __name__ == '__main__':
    main()
