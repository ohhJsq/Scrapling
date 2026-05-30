"""
获取小红书评论
"""

import json
import re
from scrapling.fetchers import StealthyFetcher

def get_xiaohongshu_comments(url):
    """获取小红书评论"""
    print(f"正在访问: {url}")
    
    try:
        page = StealthyFetcher.fetch(url, headless=True)
        print(f"页面标题: {page.css('title::text').get()}")
        
        scripts = page.css('script[type="application/ld+json"]').getall()
        for script in scripts:
            print(f"JSON-LD: {script.get()[:500]}")
        
        scripts = page.css('script::text').getall()
        note_data = None
        for script in scripts:
            if 'noteDetailMap' in script or '"id"' in script:
                match = re.search(r'"noteId"\s*:\s*"([^"]+)"', script)
                if match:
                    note_id = match.group(1)
                    print(f"\n找到笔记ID: {note_id}")
                    note_data = script
                    break
        
        if not note_data:
            for script in scripts:
                if 'window.__INITIAL_STATE__' in script or 'window.__INIT_SSR_STATE__' in script:
                    match = re.search(r'= ({".*})\s*</script>', script, re.DOTALL)
                    if match:
                        try:
                            data = json.loads(match.group(1))
                            print("\n找到初始状态数据")
                        except:
                            pass
        
        comment_elements = page.css('.comment-item, .note-comment-item, [class*="comment"]')
        print(f"\n找到 {len(comment_elements)} 个可能包含评论的元素")
        
        return None
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    url = "https://www.xiaohongshu.com/explore/69faf2f500000000200389f5"
    get_xiaohongshu_comments(url)
