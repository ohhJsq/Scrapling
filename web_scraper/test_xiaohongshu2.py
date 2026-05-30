"""
获取小红书评论 - 多种尝试
"""

import json
import re
from scrapling.fetchers import Fetcher, DynamicFetcher

def try_http_fetch(url):
    """尝试 HTTP 方式获取"""
    print(f"\n{'='*60}")
    print("方式 1: HTTP 快速请求")
    print(f"{'='*60}")
    
    try:
        page = Fetcher.get(url, impersonate='chrome')
        print(f"状态码: {page.status}")
        print(f"标题: {page.css('title::text').get()}")
        
        scripts = page.css('script::text').getall()
        for script in scripts[:5]:
            if 'note' in script.lower() or 'comment' in script.lower():
                print(f"\n找到相关脚本: {script[:300]}...")
                break
        
        return True
    except Exception as e:
        print(f"错误: {e}")
        return False

def try_dynamic_fetch(url):
    """尝试动态渲染方式"""
    print(f"\n{'='*60}")
    print("方式 2: 浏览器动态渲染")
    print(f"{'='*60}")
    
    try:
        with DynamicFetcher() as fetcher:
            page = fetcher.fetch(url, headless=True, network_idle=True)
            print(f"标题: {page.css('title::text').get()}")
            
            html = page.get()
            print(f"HTML 长度: {len(html)}")
            
            if 'comment' in html.lower():
                print("页面包含评论相关内容")
            
            comment_selectors = [
                '.comment-item',
                '[class*="comment"]',
                '.note-comment',
                '.interact-wrapper'
            ]
            
            for selector in comment_selectors:
                elements = page.css(selector)
                if elements:
                    print(f"找到 {len(elements)} 个元素: {selector}")
            
            return True
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_api():
    """分析小红书可能的 API"""
    print(f"\n{'='*60}")
    print("小红书 API 分析")
    print(f"{'='*60}")
    
    note_id = "69faf2f500000000200389f5"
    
    apis = [
        f"https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id={note_id}&cursor=&top_comment_id=&image_formats=jpg,webp,avif&need_num=10&list_type=root",
        f"https://www.xiaohongshu.com/api/sns/web/v2/comment/page?note_id={note_id}&cursor=&top_comment_id=&image_formats=jpg,webp,avif&need_num=10&list_type=root"
    ]
    
    for api in apis:
        print(f"\n尝试 API: {api}")
        try:
            page = Fetcher.get(api, impersonate='chrome')
            print(f"状态: {page.status}")
            print(f"响应: {page.text[:500]}")
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    url = "https://www.xiaohongshu.com/explore/69faf2f500000000200389f5"
    
    print("🔍 小红书评论获取工具")
    print(f"目标链接: {url}")
    
    try_http_fetch(url)
    try_dynamic_fetch(url)
    analyze_api()
    
    print("\n" + "="*60)
    print("⚠️  小红书评论获取限制说明")
    print("="*60)
    print("""
1. 小红书评论需要用户登录态才能访问
2. 网站有严格的反爬虫检测机制
3. 链接可能已过期或内容已下架

💡 替代方案:
   - 使用 Cookie 模拟登录态
   - 使用 Selenium + 手动登录
   - 通过小红书官方 API（如有开发者权限）
   - 直接在浏览器中打开链接查看
""")
