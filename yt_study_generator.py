#!/usr/bin/env python3
"""
YouTube 播放清單學習網頁生成器（離線版）
需要 Python 3

使用方法：
    python3 yt_study_generator.py "播放清單網址" [-o 輸出檔名] [-n 課程名稱]
"""

import sys
import re
import json
import urllib.request
import urllib.parse
import urllib.error
import argparse
import os

# 顏色配置
COLORS = [
    ('00d9ff', '00ff88', '藍綠'),
    ('ff6b6b', 'feca57', '橙黃'),
    ('a29bfe', 'fd79a8', '紫粉'),
    ('00b894', '00cec9', '青色'),
    ('e17055', 'fdcb6e', '橘色'),
]

def get_playlist_videos(playlist_url):
    """從 YouTube 播放清單獲取影片列表"""
    print("正在獲取播放清單...")
    
    # 提取 playlist ID
    match = re.search(r'[?&]list=([a-zA-Z0-9_-]+)', playlist_url)
    if not match:
        print("錯誤：無法解析播放清單 ID")
        return None, None
    
    playlist_id = match.group(1)
    print(f"播放清單 ID: {playlist_id}")
    
    # 使用 Invidious API
    instances = [
        'https://invidious.jingl.xyz',
        'https://invidious.privacydev.net', 
        'https://invidious.snopyta.org',
        'https://yewtu.be',
        'https://invidious.projectsegfau.lt',
    ]
    
    videos = None
    playlist_title = None
    
    for instance in instances:
        try:
            url = f"{instance}/api/v1/playlists/{playlist_id}"
            print(f"嘗試: {instance}...")
            
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if 'videos' in data:
                videos = []
                for i, v in enumerate(data['videos']):
                    title = v.get('title', f'影片 {i+1}')
                    # 嘗試提取章節編號
                    chapter = ''
                    title_match = re.match(r'^[\d\-\.]+\s*(.+)', title)
                    if title_match:
                        chapter = title_match.group(1).strip()
                    
                    videos.append({
                        'id': v['videoId'],
                        'title': title,
                        'chapter': chapter
                    })
                
                playlist_title = data.get('title', '')
                print(f"成功！找到 {len(videos)} 部影片")
                return videos, playlist_title
                
        except Exception as e:
            print(f"  失敗: {str(e)[:50]}")
            continue
    
    # 如果 Invidious 都失敗，使用備用方法
    print("嘗試備用方法...")
    videos = fetch_via_curl(playlist_id)
    
    if videos:
        return videos, "課程"
    
    return None, None

def fetch_via_curl(playlist_id):
    """使用 curl 獲取影片列表"""
    import subprocess
    
    try:
        cmd = f'curl -s "https://www.youtube.com/playlist?list={playlist_id}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        html = result.stdout
        
        # 提取影片 ID
        video_ids = re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', html)
        video_ids = list(dict.fromkeys(video_ids))
        
        if not video_ids:
            return None
        
        print(f"找到 {len(video_ids)} 部影片，正在獲取標題...")
        
        videos = []
        for i, vid in enumerate(video_ids):
            print(f"  處理 {i+1}/{len(video_ids)}...")
            
            # 嘗試獲取標題
            try:
                req = urllib.request.Request(
                    f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json',
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    title = data.get('title', f'影片 {i+1}')
            except:
                title = f'影片 {i+1}'
            
            videos.append({
                'id': vid,
                'title': title,
                'chapter': ''
            })
        
        return videos
        
    except Exception as e:
        print(f"備用方法失敗: {e}")
        return None

def generate_html(videos, course_name, subtitle, color_index=0):
    """生成學習網頁 HTML"""
    
    c1, c2, _ = COLORS[color_index % len(COLORS)]
    slug = re.sub(r'[^a-zA-Z0-9]', '-', course_name.lower())[:20]
    
    html = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{course_name}｜學習中心</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft JhengHei", sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); min-height: 100vh; color: #fff; line-height: 1.6; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        header {{ text-align: center; padding: 40px 20px; background: rgba(255,255,255,0.05); border-radius: 20px; margin-bottom: 30px; backdrop-filter: blur(10px); }}
        h1 {{ font-size: 2.2em; margin-bottom: 10px; background: linear-gradient(90deg, #{c1}, #{c2}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .subtitle {{ font-size: 1.1em; color: #aaa; margin-bottom: 20px; }}
        .stats {{ display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; margin-top: 20px; }}
        .stat-item {{ text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #{c1}; }}
        .stat-label {{ font-size: 0.9em; color: #888; }}
        .progress-section {{ background: rgba(255,255,255,0.05); border-radius: 15px; padding: 20px; margin-bottom: 30px; }}
        .progress-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
        .progress-bar {{ height: 10px; background: rgba(255,255,255,0.1); border-radius: 5px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #{c1}, #{c2}); border-radius: 5px; transition: width 0.3s ease; }}
        .video-list {{ display: grid; gap: 15px; }}
        .video-item {{ background: rgba(255,255,255,0.08); border-radius: 12px; padding: 15px 20px; display: flex; align-items: center; gap: 15px; transition: all 0.3s ease; cursor: pointer; border: 2px solid transparent; }}
        .video-item:hover {{ background: rgba(255,255,255,0.12); transform: translateX(5px); }}
        .video-item.completed {{ border-color: #{c2}; background: rgba(255,255,255,0.1); }}
        .video-item.completed .video-number {{ background: #{c2}; color: #1a1a2e; }}
        .video-number {{ width: 35px; height: 35px; background: rgba(255,255,255,0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0; }}
        .video-info {{ flex: 1; }}
        .video-title {{ font-size: 1em; margin-bottom: 5px; color: #fff; }}
        .video-chapter {{ font-size: 0.8em; color: #888; }}
        .video-link {{ color: #{c1}; text-decoration: none; padding: 8px 15px; background: rgba(255,255,255,0.1); border-radius: 20px; font-size: 0.85em; transition: all 0.3s ease; white-space: nowrap; }}
        .video-link:hover {{ background: rgba(255,255,255,0.2); }}
        .check-btn {{ width: 28px; height: 28px; border: 2px solid #555; border-radius: 50%; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
        .check-btn:hover {{ border-color: #{c2}; }}
        .video-item.completed .check-btn {{ background: #{c2}; border-color: #{c2}; }}
        .check-btn::after {{ content: "✓"; color: #1a1a2e; font-weight: bold; display: none; }}
        .video-item.completed .check-btn::after {{ display: block; }}
        footer {{ text-align: center; padding: 30px; color: #666; font-size: 0.9em; }}
        .reset-btn {{ background: rgba(255,100,100,0.2); border: 1px solid #ff6464; color: #ff6464; padding: 10px 20px; border-radius: 20px; cursor: pointer; font-size: 0.9em; margin-top: 20px; }}
        @media (max-width: 600px) {{ h1 {{ font-size: 1.6em; }} .stats {{ gap: 20px; }} .video-item {{ flex-wrap: wrap; }} .video-link {{ margin-top: 10px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{course_name}</h1>
            <p class="subtitle">{subtitle}</p>
            <div class="stats">
                <div class="stat-item"><div class="stat-number" id="totalVideos">{len(videos)}</div><div class="stat-label">總影片數</div></div>
                <div class="stat-item"><div class="stat-number" id="completedCount">0</div><div class="stat-label">已完成</div></div>
                <div class="stat-item"><div class="stat-number" id="progressPercent">0%</div><div class="stat-label">學習進度</div></div>
            </div>
        </header>
        <div class="progress-section">
            <div class="progress-header"><span>學習進度</span><span id="progressText">0 / {len(videos)}</span></div>
            <div class="progress-bar"><div class="progress-fill" id="progressFill" style="width: 0%"></div></div>
        </div>
        <div class="video-list" id="videoList"></div>
        <footer>
            <p>點擊圓圈可標記已完成</p>
            <button class="reset-btn" onclick="resetProgress()">重置進度</button>
        </footer>
    </div>
    <script>
        const videos = {json.dumps(videos, ensure_ascii=False)};
        const STORAGE_KEY = 'gcl-{slug}-completed';
        let completedVideos = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        
        function saveProgress() {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(completedVideos)); updateStats(); }}
        function toggleComplete(index) {{ const id = videos[index].id; completedVideos.includes(id) ? completedVideos = completedVideos.filter(x => x !== id) : completedVideos.push(id); saveProgress(); renderList(); }}
        function updateStats() {{ document.getElementById('completedCount').textContent = completedVideos.length; document.getElementById('progressText').textContent = completedVideos.length + ' / ' + videos.length; const p = Math.round(completedVideos.length / videos.length * 100); document.getElementById('progressPercent').textContent = p + '%'; document.getElementById('progressFill').style.width = p + '%'; }}
        function renderList() {{ document.getElementById('videoList').innerHTML = videos.map((v, i) => '<div class="video-item ' + (completedVideos.includes(v.id) ? 'completed' : '') + '" onclick="toggleComplete(' + i + ')"><div class="video-number">' + (i+1) + '</div><div class="video-info"><div class="video-title">' + v.title.replace(/'/g, "\\'") + '</div><div class="video-chapter">' + (v.chapter || '') + '</div></div><a href="https://youtu.be/' + v.id + '" target="_blank" class="video-link" onclick="event.stopPropagation()">▶ 看影片</a><div class="check-btn"></div></div>').join(''); updateStats(); }}
        function resetProgress() {{ if(confirm('確定重置？')) {{ completedVideos = []; saveProgress(); renderList(); }} }}
        renderList();
    </script>
</body>
</html>'''
    
    return html

def main():
    parser = argparse.ArgumentParser(
        description='YouTube 播放清單學習網頁生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
    python3 yt_study_generator.py "https://youtube.com/playlist?list=PLxxx"
    python3 yt_study_generator.py "https://youtube.com/playlist?list=PLxxx" -o mycourse.html
    python3 yt_study_generator.py "https://youtube.com/playlist?list=PLxxx" -n "我的課程" -c 2
        '''
    )
    
    parser.add_argument('playlist_url', help='YouTube 播放清單網址')
    parser.add_argument('-o', '--output', default=None, help='輸出檔名（預設：課程名稱.html）')
    parser.add_argument('-n', '--name', default=None, help='課程名稱（預設：從播放清單自動取得）')
    parser.add_argument('-s', '--subtitle', default='', help='課程副標題')
    parser.add_argument('-c', '--color', type=int, default=0, help='顏色主題編號 (0-4)')
    
    args = parser.parse_args()
    
    # 獲取影片列表
    videos, playlist_title = get_playlist_videos(args.playlist_url)
    
    if not videos:
        print("\n無法獲取播放清單！")
        print("請確認：")
        print("1. 播放清單網址是否正確")
        print("2. 播放清單是否為公開")
        print("3. 網路連線是否正常")
        print("\n或者可以手動輸入影片 ID 清單")
        sys.exit(1)
    
    # 設定課程名稱
    course_name = args.name
    if not course_name:
        if playlist_title:
            # 清理標題
            course_name = re.split(r'[｜|\|]', playlist_title)[0].strip()
        else:
            course_name = "課程學習"
    
    # 設定輸出檔名
    output_file = args.output
    if not output_file:
        safe_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '-', course_name)
        output_file = f"{safe_name}.html"
    
    # 生成 HTML
    print(f"\n正在生成網頁...")
    subtitle = args.subtitle or f"{len(videos)}部影片"
    html = generate_html(videos, course_name, subtitle, args.color)
    
    # 儲存檔案
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ 成功！")
    print(f"   課程名稱: {course_name}")
    print(f"   影片數量: {len(videos)} 部")
    print(f"   輸出檔案: {output_file}")
    print(f"\n用瀏覽器打開 {output_file} 即可使用！")

if __name__ == '__main__':
    main()
