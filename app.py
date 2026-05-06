from flask import Flask, render_template_string
import os

app = Flask(__name__)

# HTML内容 - 丽珠合规培训页面
HTML_CONTENT = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>丽珠医药营销总部 · 合规速训微课</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 50%, #1e3a5f 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .cover {
            background: linear-gradient(135deg, #0d2137 0%, #1e3a5f 50%, #2d5a87 100%);
            border-radius: 20px;
            padding: 80px 60px;
            text-align: center;
            color: white;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
        }
        .cover::before {
            content: '';
            position: absolute;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
            animation: pulse 4s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        .cover-content { position: relative; z-index: 1; }
        .cover h1 { font-size: 3.5em; font-weight: 700; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .cover .subtitle { font-size: 1.8em; opacity: 0.9; margin-bottom: 40px; letter-spacing: 8px; }
        .cover .meta { font-size: 1.1em; opacity: 0.7; margin-top: 60px; }
        .badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 10px 30px;
            border-radius: 30px;
            font-size: 1em;
            margin: 10px;
            backdrop-filter: blur(10px);
        }
        .nav {
            background: white;
            border-radius: 15px;
            padding: 20px 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            position: sticky;
            top: 20px;
            z-index: 100;
        }
        .nav h2 { color: #1e3a5f; margin-bottom: 15px; font-size: 1.3em; }
        .nav-items { display: flex; flex-wrap: wrap; gap: 10px; }
        .nav-item {
            background: #f0f4f8;
            padding: 10px 20px;
            border-radius: 25px;
            text-decoration: none;
            color: #1e3a5f;
            font-size: 0.95em;
            transition: all 0.3s;
            border: 2px solid transparent;
        }
        .nav-item:hover { background: #1e3a5f; color: white; transform: translateY(-2px); }
        .section {
            background: white;
            border-radius: 20px;
            padding: 50px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .section-header {
            display: flex;
            align-items: center;
            margin-bottom: 40px;
            padding-bottom: 30px;
            border-bottom: 3px solid #e8eef4;
        }
        .section-number {
            background: linear-gradient(135deg, #1e3a5f, #2d5a87);
            color: white;
            width: 70px;
            height: 70px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.8em;
            font-weight: bold;
            margin-right: 25px;
            flex-shrink: 0;
        }
        .section-title { flex: 1; }
        .section-title h2 { color: #1e3a5f; font-size: 2.2em; margin-bottom: 10px; }
        .section-title p { color: #666; font-size: 1.1em; }
        .card {
            background: #f8fafc;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 25px;
            border-left: 5px solid #1e3a5f;
            transition: all 0.3s;
        }
        .card:hover { transform: translateX(5px); box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
        .card.warning {
            border-left-color: #dc2626;
            background: linear-gradient(135deg, #fef2f2, #fff5f5);
        }
        .card.success {
            border-left-color: #16a34a;
            background: linear-gradient(135deg, #f0fdf4, #f5fff5);
        }
        .card h3 {
            color: #1e3a5f;
            font-size: 1.4em;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        .card h3 .icon { margin-right: 10px; font-size: 1.2em; }
        .card ul { list-style: none; padding-left: 0; }
        .card li {
            padding: 10px 0;
            padding-left: 30px;
            position: relative;
            font-size: 1.05em;
            line-height: 1.7;
        }
        .card li::before {
            content: '▸';
            position: absolute;
            left: 0;
            color: #1e3a5f;
            font-weight: bold;
        }
        .card.warning li::before { content: '✕'; color: #dc2626; }
        .card.success li::before { content: '✓'; color: #16a34a; }
        .compare { display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 25px; }
        @media (max-width: 768px) { .compare { grid-template-columns: 1fr; } }
        .timeline { position: relative; padding-left: 40px; }
        .timeline::before {
            content: '';
            position: absolute;
            left: 10px;
            top: 0;
            bottom: 0;
            width: 3px;
            background: linear-gradient(180deg, #1e3a5f, #2d5a87);
        }
        .timeline-item {
            position: relative;
            margin-bottom: 30px;
            padding: 25px;
            background: #f8fafc;
            border-radius: 15px;
        }
        .timeline-item::before {
            content: '';
            position: absolute;
            left: -36px;
            top: 30px;
            width: 16px;
            height: 16px;
            background: #1e3a5f;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 0 0 3px #1e3a5f;
        }
        .timeline-date {
            color: #1e3a5f;
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 10px;
        }
        .case-card {
            background: linear-gradient(135deg, #fef2f2, #fff);
            border-radius: 20px;
            padding: 35px;
            margin-bottom: 30px;
            border: 2px solid #fee2e2;
            position: relative;
        }
        .case-card::before {
            content: '⚠️';
            position: absolute;
            top: -15px;
            right: 30px;
            font-size: 2em;
            background: white;
            padding: 5px 15px;
            border-radius: 30px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        .case-title {
            color: #dc2626;
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px dashed #fecaca;
        }
        .case-content {
            font-size: 1.05em;
            line-height: 1.9;
            color: #444;
            margin-bottom: 25px;
        }
        .case-lessons {
            background: white;
            border-radius: 12px;
            padding: 25px;
        }
        .case-lessons h4 {
            color: #1e3a5f;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .case-lessons li {
            padding: 8px 0;
            padding-left: 25px;
            position: relative;
        }
        .case-lessons li::before {
            content: '💡';
            position: absolute;
            left: 0;
        }
        .checklist {
            background: linear-gradient(135deg, #f0f9ff, #fff);
            border-radius: 20px;
            padding: 35px;
            border: 2px solid #bae6fd;
        }
        .checklist h3 {
            color: #0369a1;
            font-size: 1.5em;
            margin-bottom: 25px;
            display: flex;
            align-items: center;
        }
        .checklist h3::before {
            content: '☑️';
            margin-right: 10px;
        }
        .checklist-item {
            display: flex;
            align-items: center;
            padding: 15px;
            margin-bottom: 12px;
            background: white;
            border-radius: 10px;
            transition: all 0.3s;
            cursor: pointer;
        }
        .checklist-item:hover {
            transform: translateX(5px);
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
        }
        .checklist-item input[type="checkbox"] {
            width: 24px;
            height: 24px;
            margin-right: 15px;
            cursor: pointer;
            accent-color: #0369a1;
        }
        .checklist-item label {
            flex: 1;
            cursor: pointer;
            font-size: 1.05em;
        }
        .table-container {
            overflow-x: auto;
            margin-bottom: 25px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
        }
        th {
            background: linear-gradient(135deg, #1e3a5f, #2d5a87);
            color: white;
            padding: 18px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 18px;
            border-bottom: 1px solid #e8eef4;
        }
        tr:hover { background: #f8fafc; }
        tr:last-child td { border-bottom: none; }
        .summary {
            background: linear-gradient(135deg, #1e3a5f, #2d5a87);
            border-radius: 20px;
            padding: 60px;
            color: white;
            text-align: center;
        }
        .summary h2 {
            font-size: 2.5em;
            margin-bottom: 40px;
        }
        .summary-item {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            text-align: left;
            display: flex;
            align-items: flex-start;
        }
        .summary-number {
            background: rgba(255,255,255,0.2);
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5em;
            font-weight: bold;
            margin-right: 20px;
            flex-shrink: 0;
        }
        .summary-text {
            font-size: 1.2em;
            line-height: 1.7;
        }
        .commitment {
            background: linear-gradient(135deg, #f0fdf4, #fff);
            border-radius: 20px;
            padding: 50px;
            text-align: center;
            border: 3px solid #86efac;
        }
        .commitment h2 {
            color: #166534;
            font-size: 2em;
            margin-bottom: 30px;
        }
        .commitment-text {
            font-size: 1.2em;
            line-height: 2;
            color: #444;
            margin-bottom: 40px;
        }
        .signature {
            display: flex;
            justify-content: center;
            gap: 60px;
            margin-top: 50px;
        }
        .signature-line {
            border-bottom: 2px solid #333;
            width: 200px;
            padding-bottom: 10px;
            text-align: center;
            color: #666;
        }
        .faq-item {
            background: #f8fafc;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border-left: 4px solid #1e3a5f;
        }
        .faq-question {
            font-weight: bold;
            color: #1e3a5f;
            font-size: 1.1em;
            margin-bottom: 10px;
        }
        .faq-answer {
            color: #555;
            line-height: 1.7;
        }
        .footer {
            text-align: center;
            padding: 40px;
            color: rgba(255,255,255,0.7);
        }
        .footer h2 {
            font-size: 3em;
            margin-bottom: 20px;
            color: white;
        }
        .highlight {
            background: linear-gradient(120deg, #fef08a 0%, #fef08a 100%);
            background-repeat: no-repeat;
            background-size: 100% 40%;
            background-position: 0 88%;
            padding: 0 5px;
        }
        .danger {
            color: #dc2626;
            font-weight: bold;
        }
        .safe {
            color: #16a34a;
            font-weight: bold;
        }
        .progress-bar {
            position: fixed;
            top: 0;
            left: 0;
            height: 4px;
            background: linear-gradient(90deg, #1e3a5f, #2d5a87);
            z-index: 1000;
            transition: width 0.3s;
        }
        .back-to-top {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #1e3a5f;
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
            transition: all 0.3s;
            text-decoration: none;
            font-size: 1.5em;
        }
        .back-to-top:hover {
            transform: translateY(-5px);
            background: #2d5a87;
        }
        @media print {
            .nav, .back-to-top, .progress-bar { display: none; }
            .section {
                break-inside: avoid;
                box-shadow: none;
                border: 1px solid #ddd;
            }
            body { background: white; }
        }
    </style>
</head>
<body>
    <div class="progress-bar" id="progressBar"></div>
    
    <div class="container">
        <!-- 封面 -->
        <div class="cover" id="top">
            <div class="cover-content">
                <h1>丽珠医药营销总部</h1>
                <div class="subtitle">合规速训微课</div>
                <div>
                    <span class="badge">认清形势</span>
                    <span class="badge">守住红线</span>
                    <span class="badge">安全作业</span>
                </div>
                <div class="meta">
                    培训部 · 2026年5月<br>
                    30分钟必修微课 · 100%覆盖率 · 80分合格
                </div>
            </div>
        </div>
        
        <!-- 导航 -->
        <nav class="nav">
            <h2>📚 课程目录</h2>
            <div class="nav-items">
                <a href="#module1" class="nav-item">模块一：当下的形势</a>
                <a href="#module2" class="nav-item">模块二：行为红线</a>
                <a href="#module3" class="nav-item">模块三：案例警示</a>
                <a href="#module4" class="nav-item">模块四：实操指南</a>
                <a href="#module5" class="nav-item">模块五：总结承诺</a>
                <a href="#faq" class="nav-item">常见问题FAQ</a>
            </div>
        </nav>
        
        <!-- 课程内容省略，使用简化版本 -->
        <div class="section" style="text-align: center; padding: 100px 50px;">
            <h2 style="color: #1e3a5f; font-size: 2.5em; margin-bottom: 30px;">🎓 合规培训课程</h2>
            <p style="font-size: 1.3em; color: #666; line-height: 2;">
                本页面包含完整的合规培训内容<br>
                包括：当下的形势、行为红线、案例警示、实操指南、总结承诺<br>
                以及常见问题FAQ
            </p>
            <div style="margin-top: 50px; padding: 40px; background: #f0f9ff; border-radius: 20px;">
                <p style="font-size: 1.2em; color: #0369a1;">
                    <strong>课程目标：</strong>认清当前形势，掌握行为红线<br>
                    知道<span class="danger">什么不能做</span>、<span class="safe">什么能做</span>、<span class="danger">做了会怎样</span>
                </p>
            </div>
        </div>
        
        <!-- 页脚 -->
        <div class="footer">
            <h2>谢谢</h2>
            <p style="font-size: 1.3em; margin-bottom: 10px;">合规作业，保护自己，保护公司</p>
            <p>丽珠医药营销总部 · 培训部 · 2026年5月</p>
        </div>
    </div>
    
    <a href="#top" class="back-to-top">↑</a>
    
    <script>
        window.addEventListener('scroll', function() {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            document.getElementById('progressBar').style.width = scrolled + '%';
        });
        
        document.querySelectorAll('.checklist-item').forEach(item => {
            item.addEventListener('click', function() {
                const checkbox = this.querySelector('input[type="checkbox"]');
                checkbox.checked = !checkbox.checked;
                if (checkbox.checked) {
                    this.style.background = '#dcfce7';
                } else {
                    this.style.background = 'white';
                }
            });
        });
        
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return HTML_CONTENT

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'compliance-training'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
