#!/usr/bin/env python3
"""
YouTube 播放清單學習網頁生成器
用法: python3 generate_study_page.py <YouTube_Playlist_URL> [輸出檔名]
"""

import sys
import re
import subprocess
import json

def get_video_ids_and_titles(playlist_url):
    """取得播放清單中的所有影片 ID 和標題"""
    print(f"正在獲取播放清單: {playlist_url}")
    
    # 使用 curl 取得頁面內容
    cmd = f'curl -s "{playlist_url}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    html = result.stdout
    
    # 提取影片 ID
    video_ids = re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', html)
    video_ids = list(dict.fromkeys(video_ids))  # 去重
    
    print(f"找到 {len(video_ids)} 部影片")
    
    # 取得每個影片的標題
    videos = []
    for i, vid in enumerate(video_ids):
        print(f"  處理影片 {i+1}/{len(video_ids)}: {vid}")
        cmd = f'curl -s "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        try:
            data = json.loads(result.stdout)
            title = data.get('title', f'影片 {i+1}')
        except:
            title = f'影片 {i+1}'
        
        videos.append({'id': vid, 'title': title})
    
    return videos

def generate_html(videos, playlist_name, output_file):
    """生成學習網頁 HTML"""
    
    # 顏色配置
    colors = [
        ('#00d9ff', '#00ff88'),  # 藍綠
        ('#ff6b6b', '#feca57'),  # 橙黃
        ('#a29bfe', '#fd79a8'),  # 紫粉
        ('#00b894', '#00cec9'),  # 青色
        ('#e17055', '#fdcb6e'),  # 橘色
    ]
    
    color = colors[hash(playlist_name) % len(colors)]
    
    html = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{playlist_name}｜郭春林 - 學習中心</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft JhengHei", sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); min-height: 100vh; color: #fff; line-height: 1.6; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        header {{ text-align: center; padding: 40px 20px; background: rgba(255,255,255,0.05); border-radius: 20px; margin-bottom: 30px; backdrop-filter: blur(10px); }}
        h1 {{ font-size: 2.2em; margin-bottom: 10px; background: linear-gradient(90deg, {color[0]}, {color[1]}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
        .subtitle {{ font-size: 1.1em; color: #aaa; margin-bottom: 20px; }}
        .stats {{ display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; margin-top: 20px; }}
        .stat-item {{ text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: {color[0]}; }}
        .stat-label {{ font-size: 0.9em; color: #888; }}
        .progress-section {{ background: rgba(255,255,255,0.05); border-radius: 15px; padding: 20px; margin-bottom: 30px; }}
        .progress-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }}
        .progress-bar {{ height: 10px; background: rgba(255,255,255,0.1); border-radius: 5px; overflow: hidden; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, {color[0]}, {color[1]}); border-radius: 5px; transition: width 0.3s ease; }}
        .video-list {{ display: grid; gap: 15px; }}
        .video-item {{ background: rgba(255,255,255,0.08); border-radius: 12px; padding: 15px 20px; display: flex; align-items: center; gap: 15px; transition: all 0.3s ease; cursor: pointer; border: 2px solid transparent; }}
        .video-item:hover {{ background: rgba(255,255,255,0.12); transform: translateX(5px); }}
        .video-item.completed {{ border-color: {color[1]}; background: rgba({color[1].replace('#','').replace('ff','255,').replace('a',',').replace('b',',').replace('c',',').replace('d',',').replace('e',',')},0.1); }}
        .video-item.completed .video-number {{ background: {color[1]}; color: #1a1a2e; }}
        .video-number {{ width: 35px; height: 35px; background: rgba(255,255,255,0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0; }}
        .video-info {{ flex: 1; }}
        .video-title {{ font-size: 1em; margin-bottom: 5px; color: #fff; }}
        .video-chapter {{ font-size: 0.8em; color: #888; }}
        .video-link {{ color: {color[0]}; text-decoration: none; padding: 8px 15px; background: rgba(255,255,255,0.1); border-radius: 20px; font-size: 0.85em; transition: all 0.3s ease; white-space: nowrap; }}
        .video-link:hover {{ background: rgba(255,255,255,0.2); }}
        .check-btn {{ width: 28px; height: 28px; border: 2px solid #555; border-radius: 50%; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
        .check-btn:hover {{ border-color: {color[1]}; }}
        .video-item.completed .check-btn {{ background: {color[1]}; border-color: {color[1]}; }}
        .check-btn::after {{ content: "✓"; color: #1a1a2e; font-weight: bold; display: none; }}
        .video-item.completed .check-btn::after {{ display: block; }}
        footer {{ text-align: center; padding: 30px; color: #666; font-size: 0.9em; }}
        .reset-btn {{ background: rgba(255,100,100,0.2); border: 1px solid #ff6464; color: #ff6464; padding: 10px 20px; border-radius: 20px; cursor: pointer; font-size: 0.9em; transition: all 0.3s ease; margin-top: 20px; }}
        .reset-btn:hover {{ background: rgba(255,100,100,0.4); }}
        @media (max-width: 600px) {{ h1 {{ font-size: 1.6em; }} .stats {{ gap: 20px; }} .video-item {{ flex-wrap: wrap; }} .video-link {{ margin-top: 10px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 {playlist_name}</h1>
            <p class="subtitle">郭春林 | {len(videos)}堂必修課</p>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number" id="totalVideos">{len(videos)}</div>
                    <div class="stat-label">總影片數</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="completedCount">0</div>
                    <div class="stat-label">已完成</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="progressPercent">0%</div>
                    <div class="stat-label">學習進度</div>
                </div>
            </div>
        </header>

        <div class="progress-section">
            <div class="progress-header">
                <span>學習進度</span>
                <span id="progressText">0 / {len(videos)}</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill" style="width: 0%"></div>
            </div>
        </div>

        <div class="video-list" id="videoList"></div>

        <footer>
            <p>點擊影片標題可跳轉到 YouTube 觀看</p>
            <p>點擊圓圈可標記已完成</p>
            <button class="reset-btn" onclick="resetProgress()">重置進度</button>
        </footer>
    </div>

    <script>
        const videos = {json.dumps(videos, ensure_ascii=False)};
        
        const STORAGE_KEY = 'gcl-{slug}-completed';
        
        let completedVideos = JSON.parse(localStorage.getItem(STORAGE_KEY.replace('{slug}', '{slug}')) || '[]');

        function saveProgress() {{
            localStorage.setItem(STORAGE_KEY.replace('{slug}', '{slug}'), JSON.stringify(completedVideos));
            updateStats();
        }}

        function toggleComplete(index) {{
            const videoId = videos[index].id;
            if (completedVideos.includes(videoId)) {{
                completedVideos = completedVideos.filter(id => id !== videoId);
            }} else {{
                completedVideos.push(videoId);
            }}
            saveProgress();
            renderList();
        }}

        function updateStats() {{
            document.getElementById('completedCount').textContent = completedVideos.length;
            document.getElementById('progressText').textContent = `${{completedVideos.length}} / ${{videos.length}}`;
            const percent = Math.round((completedVideos.length / videos.length) * 100);
            document.getElementById('progressPercent').textContent = `${{percent}}%`;
            document.getElementById('progressFill').style.width = `${{percent}}%`;
        }}

        function renderList() {{
            const list = document.getElementById('videoList');
            list.innerHTML = videos.map((video, index) => `
                <div class="video-item ${{completedVideos.includes(video.id) ? 'completed' : ''}}" onclick="toggleComplete(${{index}})">
                    <div class="video-number">${{index + 1}}</div>
                    <div class="video-info">
                        <div class="video-title">${{video.title}}</div>
                        <div class="video-chapter">${{video.chapter || ''}}</div>
                    </div>
                    <a href="https://youtu.be/${{video.id}}" target="_blank" class="video-link" onclick="event.stopPropagation()">
                        ▶ 看影片
                    </a>
                    <div class="check-btn"></div>
                </div>
            `).join('');
            updateStats();
        }}

        function resetProgress() {{
            if (confirm('確定要重置所有進度嗎？')) {{
                completedVideos = [];
                saveProgress();
                renderList();
            }}
        }}

        renderList();
    </script>
</body>
</html>'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"已生成網頁: {output_file}")

def main():
    if len(sys.argv) < 2:
        print("用法: python3 generate_study_page.py <YouTube_Playlist_URL> [輸出檔名]")
        sys.exit(1)
    
    playlist_url = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "study_page.html"
    
    # 從 URL 提取播放清單名稱
    playlist_name = "課程學習"
    
    videos = get_video_ids_and_titles(playlist_url)
    
    if not videos:
        print("無法取得影片列表")
        sys.exit(1)
    
    generate_html(videos, playlist_name, output_file)
    print("完成！")

if __name__ == "__main__":
    main()
