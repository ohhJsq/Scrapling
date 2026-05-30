"""
Web Scraper - 基于 Scrapling 的在线爬虫工具
"""

import json
import re
import traceback
from flask import Flask, render_template, request, jsonify
from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher

app = Flask(__name__)
app.secret_key = 'web-scraper-secret-key-change-in-production'

FETCHER_MODES = {
    'fast': {'class': Fetcher, 'name': '快速模式 (HTTP)'},
    'stealth': {'class': StealthyFetcher, 'name': '隐身模式 (绕过反爬)'},
    'dynamic': {'class': DynamicFetcher, 'name': '动态模式 (浏览器渲染)'}
}


def parse_selector(selector_str: str) -> dict:
    """解析选择器字符串，返回类型和选择器"""
    selector_str = selector_str.strip()
    
    if selector_str.startswith('//') or selector_str.startswith('(//'):
        return {'type': 'xpath', 'selector': selector_str}
    elif selector_str.startswith('text:'):
        return {'type': 'text', 'selector': selector_str[5:].strip()}
    elif selector_str.startswith('attr:'):
        parts = selector_str[5:].split('::', 1)
        if len(parts) == 2:
            return {'type': 'attr', 'selector': parts[0], 'attr': parts[1]}
        return {'type': 'css', 'selector': selector_str[5:]}
    else:
        return {'type': 'css', 'selector': selector_str}


def apply_selector(page, selector_info: dict):
    """应用选择器并提取数据"""
    selector_type = selector_info['type']
    selector = selector_info['selector']
    
    if selector_type == 'css':
        elements = page.css(selector)
        return [e.get() for e in elements]
    elif selector_type == 'xpath':
        elements = page.xpath(selector)
        return [e.get() for e in elements]
    elif selector_type == 'text':
        elements = page.find_by_text(selector)
        return [e.get() for e in elements]
    elif selector_type == 'attr':
        elements = page.css(selector)
        attr = selector_info.get('attr', 'href')
        return [e.attrib.get(attr, '') for e in elements]
    return []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        selectors = data.get('selectors', [])
        mode = data.get('mode', 'fast')
        options = data.get('options', {})
        
        if not url:
            return jsonify({'success': False, 'error': '请输入网址'}), 400
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        if not selectors or not selectors[0].strip():
            return jsonify({'success': False, 'error': '请输入选择器或需求描述'}), 400
        
        fetcher_info = FETCHER_MODES.get(mode, FETCHER_MODES['fast'])
        fetcher_class = fetcher_info['class']
        
        fetch_options = {}
        if mode == 'stealth':
            fetch_options['headless'] = options.get('headless', True)
            fetch_options['solve_cloudflare'] = options.get('solve_cloudflare', False)
        elif mode == 'dynamic':
            fetch_options['headless'] = options.get('headless', True)
            fetch_options['network_idle'] = options.get('network_idle', True)
        
        page = fetcher_class.fetch(url, **fetch_options)
        
        results = {}
        for i, selector_str in enumerate(selectors):
            if not selector_str.strip():
                continue
            
            parsed = parse_selector(selector_str)
            data = apply_selector(page, parsed)
            
            key = f"result_{i+1}" if len(selectors) > 1 else 'data'
            results[key] = {
                'selector': selector_str,
                'type': parsed['type'],
                'count': len(data),
                'data': data[:100]
            }
        
        return jsonify({
            'success': True,
            'url': url,
            'mode': fetcher_info['name'],
            'title': page.css('title::text').get() or 'N/A',
            'results': results,
            'message': f'成功获取 {sum(r["count"] for r in results.values())} 条数据'
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'爬取失败: {str(e)}'
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """分析网页结构，返回可用选择器"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        mode = data.get('mode', 'stealth')
        
        if not url:
            return jsonify({'success': False, 'error': '请输入网址'}), 400
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        fetcher_class = FETCHER_MODES.get(mode, FETCHER_MODES['stealth'])
        page = fetcher_class.fetch(url, headless=True)
        
        elements = []
        for elem in page.css('a, img, div, span, p, h1, h2, h3')[:50]:
            tag = elem.tag
            elem_class = elem.attrib.get('class', '')
            elem_id = elem.attrib.get('id', '')
            text = elem.get().strip()[:100] if elem.get() else ''
            
            if text or elem_class or elem_id:
                css_selector = f"{tag}"
                if elem_class:
                    css_selector += f".{elem_class.split()[0]}"
                if elem_id:
                    css_selector = f"{tag}#{elem_id}"
                
                elements.append({
                    'tag': tag,
                    'class': elem_class[:50],
                    'id': elem_id,
                    'text': text[:80],
                    'suggested_selector': css_selector
                })
        
        return jsonify({
            'success': True,
            'title': page.css('title::text').get() or 'N/A',
            'elements': elements
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'分析失败: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🕷️  Web Scraper 启动成功!")
    print("=" * 60)
    print("请访问: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
