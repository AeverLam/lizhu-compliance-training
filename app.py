from flask import Flask, send_file, request, jsonify, render_template_string
import os, json, random, hashlib, time
from functools import wraps
from datetime import datetime

app = Flask(__name__)

# ========== 配置 ==========
ADMIN_PASSWORD = "livzon2026"  # 后台管理密码
DATA_DIR = "data"
EXAM_FILE = os.path.join(DATA_DIR, "exams.json")
QUESTIONS_FILE = os.path.join(DATA_DIR, "questions.json")

os.makedirs(DATA_DIR, exist_ok=True)

# ========== 题库（从微课内容提取） ==========
QUESTION_BANK = [
    {
        "id": 1,
        "type": "single",
        "question": "本次合规速训微课的课时要求是？",
        "options": ["A. 45分钟", "B. 30分钟", "C. 15分钟", "D. 60分钟"],
        "answer": 1,
        "section": "课程信息"
    },
    {
        "id": 2,
        "type": "single",
        "question": "本次考核的合格分数线是多少？",
        "options": ["A. 60分", "B. 70分", "C. 80分", "D. 90分"],
        "answer": 2,
        "section": "课程信息"
    },
    {
        "id": 3,
        "type": "single",
        "question": "本次课程的完成要求是什么？",
        "options": ["A. 80%覆盖率 + 60分合格", "B. 90%覆盖率 + 70分合格", "C. 100%覆盖率 + 80分合格", "D. 100%覆盖率 + 90分合格"],
        "answer": 2,
        "section": "课程信息"
    },
    {
        "id": 4,
        "type": "single",
        "question": "医药反腐集中整治工作是从什么时候开始的？",
        "options": ["A. 2022年1月", "B. 2023年7月", "C. 2024年3月", "D. 2025年1月"],
        "answer": 1,
        "section": "当下的形势"
    },
    {
        "id": 5,
        "type": "single",
        "question": "医药代表拜访前必须完成什么？",
        "options": ["A. 出差申请", "B. 医药代表备案", "C. 产品培训", "D. 销售目标确认"],
        "answer": 1,
        "section": "行为红线"
    },
    {
        "id": 6,
        "type": "multiple",
        "question": "以下哪些属于商业贿赂的红线行为？（多选）",
        "options": ["A. 向医生支付现金回扣", "B. 赠送购物卡给医生", "C. 通过CSO变相输送利益", "D. 带医生参加公司组织的学术会议"],
        "answer": [0, 1, 2],
        "section": "行为红线"
    },
    {
        "id": 7,
        "type": "single",
        "question": "关于讲课费，以下说法正确的是？",
        "options": ["A. 只要有医生签名就算合规", "B. 必须对应真实的讲课行为", "C. 可以先支付后补讲课", "D. 讲课费标准可以自行决定"],
        "answer": 1,
        "section": "案例警示"
    },
    {
        "id": 8,
        "type": "multiple",
        "question": "以下哪些属于虚假学术活动的表现？（多选）",
        "options": ["A. 以学术会议为名组织旅游", "B. 虚构参会人员名单", "C. 组织有真实学术内容的科室会", "D. 以讲课费名义支付回扣"],
        "answer": [0, 1, 3],
        "section": "行为红线"
    },
    {
        "id": 9,
        "type": "single",
        "question": "根据课程内容，反腐进入什么阶段？",
        "options": ["A. 初期排查阶段", "B. 深水区阶段", "C. 收尾阶段", "D. 暂停阶段"],
        "answer": 1,
        "section": "当下的形势"
    },
    {
        "id": 10,
        "type": "single",
        "question": "关于学术活动地点选择，以下哪个是正确的？",
        "options": ["A. 任何城市都可以", "B. 必须选择旅游度假城市", "C. 应选择有合理学术理由的地点", "D. 由医生决定地点"],
        "answer": 2,
        "section": "实操指南"
    },
    {
        "id": 11,
        "type": "single",
        "question": "遇到不确定是否合规的场景，首先应该？",
        "options": ["A. 先做了再说", "B. 问同事", "C. 停下来，问上级或合规部", "D. 自行判断"],
        "answer": 2,
        "section": "实操指南"
    },
    {
        "id": 12,
        "type": "multiple",
        "question": "以下哪些情况需要立即上报？（多选）",
        "options": ["A. 上级要求配合做虚假报销", "B. 医生主动索要回扣", "C. 发现有同事疑似违规", "D. 收到监管部门调查通知"],
        "answer": [0, 1, 2, 3],
        "section": "实操指南"
    },
    {
        "id": 13,
        "type": "single",
        "question": "关于在微信/短信/邮件中讨论费用和利益，正确的做法是？",
        "options": ["A. 可以在私人微信中讨论", "B. 可以在加密邮件中讨论", "C. 不做此类活动，也不在这些渠道讨论", "D. 只要不留下文字记录就可以"],
        "answer": 2,
        "section": "案例警示"
    },
    {
        "id": 14,
        "type": "single",
        "question": "课程强调的合规关键判断标准是什么？",
        "options": ["A. 金额是否超过500元", "B. 是否能向纪检/检察院/媒体解释正当关系", "C. 是否经过领导批准", "D. 是否在公开场合进行"],
        "answer": 1,
        "section": "行为红线"
    },
    {
        "id": 15,
        "type": "single",
        "question": "医生主动要回扣时，正确的做法是？",
        "options": ["A. 答应以维护客户关系", "B. 私下给，不做记录", "C. 明确拒绝，做好记录，立即上报", "D. 让医生通过第三方拿"],
        "answer": 2,
        "section": "实操指南"
    },
    {
        "id": 16,
        "type": "single",
        "question": "关于费用报销，以下哪个是正确的？",
        "options": ["A. 可以用个人账户代收代付", "B. 可以借用他人身份信息报销", "C. 每一笔报销必须基于真实发生的业务活动", "D. 只要领导签字就可以报销"],
        "answer": 2,
        "section": "行为红线"
    },
    {
        "id": 17,
        "type": "single",
        "question": "关于科室会请客吃饭，正确的是？",
        "options": ["A. 可以安排任何档次的餐饮", "B. 可以安排会议简餐，须审批且不超标准", "C. 不能有任何形式的用餐安排", "D. 由医生自行安排后报销"],
        "answer": 1,
        "section": "实操指南"
    },
    {
        "id": 18,
        "type": "single",
        "question": "医药反腐的监管覆盖范围是？",
        "options": ["A. 仅限医院", "B. 仅限药企", "C. 医药购销全链条", "D. 仅限销售代表"],
        "answer": 2,
        "section": "当下的形势"
    },
    {
        "id": 19,
        "type": "multiple",
        "question": "五条行为红线包括哪些？（多选）",
        "options": ["A. 商业贿赂", "B. 虚假学术活动", "C. 违规拜访和推广", "D. 费用造假和套现", "E. 信息安全和数据合规"],
        "answer": [0, 1, 2, 3, 4],
        "section": "行为红线"
    },
    {
        "id": 20,
        "type": "single",
        "question": "课程提到反腐的长期趋势是什么？",
        "options": ["A. 一轮整治后会放松", "B. 不会过去，只会更严", "C. 只针对外资企业", "D. 两年后会结束"],
        "answer": 1,
        "section": "总结与承诺"
    },
    {
        "id": 21,
        "type": "single",
        "question": "关于CSO合作，以下说法正确的是？",
        "options": ["A. CSO可以作为利益输送的通道", "B. 可以用CSO变相给医生回扣", "C. 与CSO合作必须确保真实业务能力和服务交付", "D. CSO不需要有实际业务能力"],
        "answer": 2,
        "section": "案例警示"
    },
    {
        "id": 22,
        "type": "single",
        "question": "学术活动合规检查清单不包括以下哪项？",
        "options": ["A. 活动目的是否与学术推广相关", "B. 讲者是否具备相应资质", "C. 能否带来最高销售额", "D. 费用预算是否与活动规模匹配"],
        "answer": 2,
        "section": "实操指南"
    },
    {
        "id": 23,
        "type": "multiple",
        "question": "以下哪些渠道适合上报违规行为？（多选）",
        "options": ["A. 公司合规部热线", "B. 营销市场总部合规联系人", "C. 匿名举报邮箱", "D. 朋友圈发帖"],
        "answer": [0, 1, 2],
        "section": "实操指南"
    },
    {
        "id": 24,
        "type": "single",
        "question": "案例四中，代表在微信群里发了什么内容导致被判刑？",
        "options": ["A. 产品推广广告", "B. 竞品负面信息", "C. 带金销售返利信息", "D. 客户隐私数据"],
        "answer": 2,
        "section": "案例警示"
    },
    {
        "id": 25,
        "type": "single",
        "question": "课程提出'五句话记住今天'，以下哪句不在其中？",
        "options": ["A. 反腐不是一阵风", "B. 合规是保护自己", "C. 回扣是行业惯例", "D. 不确定就问"],
        "answer": 2,
        "section": "总结与承诺"
    },
    {
        "id": 26,
        "type": "single",
        "question": "关于医生拜访，以下做法正确的是？",
        "options": ["A. 在任何时间都可以拜访", "B. 不用预约，直接去医院", "C. 确认备案后通过医院平台预约", "D. 可以带竞品对比资料去推广"],
        "answer": 2,
        "section": "实操指南"
    },
    {
        "id": 27,
        "type": "single",
        "question": "超适应症推广属于哪条红线？",
        "options": ["A. 商业贿赂", "B. 虚假学术活动", "C. 违规拜访和推广", "D. 费用造假"],
        "answer": 2,
        "section": "行为红线"
    },
    {
        "id": 28,
        "type": "single",
        "question": "本次培训的课程性质是什么？",
        "options": ["A. 例行年度合规培训", "B. 新员工入职培训", "C. 应对医药反腐深水区的紧急必修课", "D. 自愿参加的选修课"],
        "answer": 2,
        "section": "课程信息"
    },
    {
        "id": 29,
        "type": "single",
        "question": "关于'红线标准'中讲课费的判断方法，正确的是？",
        "options": ["A. 只要有人讲课就算合规", "B. 去掉讲课费后还有动力组织才算真实", "C. 讲课费金额越大越合规", "D. 只要医生签字就可以"],
        "answer": 1,
        "section": "案例警示"
    },
    {
        "id": 30,
        "type": "single",
        "question": "遇到'不确定'场景的处理原则是？",
        "options": ["A. 先做后问 → 事后补报", "B. 停下来 → 问一句 → 留记录", "C. 自己做主 → 出问题再说", "D. 问同事 → 大家说行就行"],
        "answer": 1,
        "section": "实操指南"
    },
]


# ========== 工具函数 ==========
def load_exams():
    if not os.path.exists(EXAM_FILE):
        return []
    with open(EXAM_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_exams(exams):
    with open(EXAM_FILE, 'w', encoding='utf-8') as f:
        json.dump(exams, f, ensure_ascii=False, indent=2)

def generate_exam(n=20):
    """从题库随机抽取 n 道题生成试卷"""
    bank = QUESTION_BANK.copy()
    random.shuffle(bank)
    selected = bank[:n]
    # 重新编号
    for i, q in enumerate(selected):
        q = q.copy()
        q["exam_order"] = i + 1
        selected[i] = q
    return selected

def calculate_score(answers, questions):
    """根据答案计算得分，每题5分"""
    total = len(questions)
    correct = 0
    details = []
    for i, q in enumerate(questions):
        user_ans = answers.get(str(i), None)
        correct_ans = q["answer"]
        is_correct = False
        
        if q["type"] == "multiple":
            if isinstance(user_ans, list) and isinstance(correct_ans, list):
                is_correct = set(user_ans) == set(correct_ans)
            elif isinstance(user_ans, str):
                try:
                    user_list = json.loads(user_ans)
                    is_correct = set(user_list) == set(correct_ans)
                except:
                    is_correct = False
        else:
            try:
                is_correct = int(user_ans) == correct_ans
            except:
                is_correct = False
        
        if is_correct:
            correct += 1
        
        details.append({
            "question_id": q["id"],
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct
        })
    
    score = int((correct / total) * 100)
    return score, correct, total, details


# ========== 页面路由 ==========
@app.route('/')
def index():
    return send_file('index.html')

@app.route('/exam')
def exam_page():
    return send_file('exam.html')

@app.route('/admin')
def admin_page():
    return send_file('admin.html')

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'compliance-training'}

# ========== API 路由 ==========
@app.route('/api/exam/generate', methods=['GET'])
def api_generate_exam():
    """生成一套试题（不返回正确答案）"""
    exam_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:12]
    questions = generate_exam(20)
    
    # 保存到临时存储，不含答案
    safe_questions = []
    for q in questions:
        sq = {
            "exam_order": q["exam_order"],
            "id": q["id"],
            "type": q["type"],
            "question": q["question"],
            "options": q["options"],
            "section": q["section"]
        }
        safe_questions.append(sq)
    
    # 内存中缓存正确答案（考试ID -> 试题）
    if not hasattr(app, 'exam_cache'):
        app.exam_cache = {}
    app.exam_cache[exam_id] = questions
    
    return jsonify({
        "exam_id": exam_id,
        "total": len(safe_questions),
        "time_limit": 30,  # 30分钟
        "questions": safe_questions
    })

@app.route('/api/exam/submit', methods=['POST'])
def api_exam_submit():
    """提交答案并评分"""
    data = request.json
    exam_id = data.get("exam_id")
    user_info = data.get("user_info", {})
    answers = data.get("answers", {})
    
    if not hasattr(app, 'exam_cache') or exam_id not in app.exam_cache:
        return jsonify({"error": "试卷已过期，请重新生成"}), 400
    
    questions = app.exam_cache[exam_id]
    score, correct, total, details = calculate_score(answers, questions)
    passed = score >= 80
    
    # 只保留答题详情中需要的信息
    result_details = []
    for d, q in zip(details, questions):
        result_details.append({
            "question": q["question"],
            "user_answer": d["user_answer"],
            "correct_answer": d["correct_answer"],
            "is_correct": d["is_correct"],
            "section": q["section"]
        })
    
    # 保存考试记录
    exam_record = {
        "exam_id": exam_id,
        "user_name": user_info.get("name", ""),
        "user_dept": user_info.get("dept", ""),
        "user_phone": user_info.get("phone", ""),
        "score": score,
        "correct": correct,
        "total": total,
        "passed": passed,
        "submit_time": datetime.now().isoformat(),
        "details": result_details
    }
    
    exams = load_exams()
    exams.append(exam_record)
    save_exams(exams)
    
    # 清除缓存
    del app.exam_cache[exam_id]
    
    return jsonify({
        "score": score,
        "correct": correct,
        "total": total,
        "passed": passed,
        "message": "合格" if passed else "不合格，请重新学习后再考",
        "details": result_details
    })

@app.route('/api/admin/login', methods=['POST'])
def api_admin_login():
    """管理后台登录"""
    data = request.json
    password = data.get("password", "")
    if password == ADMIN_PASSWORD:
        return jsonify({"success": True, "token": hashlib.md5(ADMIN_PASSWORD.encode()).hexdigest()})
    return jsonify({"success": False, "message": "密码错误"}), 401

@app.route('/api/admin/exams', methods=['GET'])
def api_admin_exams():
    """获取所有考试记录"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    expected = hashlib.md5(ADMIN_PASSWORD.encode()).hexdigest()
    if token != expected:
        return jsonify({"error": "未授权"}), 401
    
    exams = load_exams()
    # 按时间倒序
    exams.sort(key=lambda x: x.get("submit_time", ""), reverse=True)
    
    # 统计
    total = len(exams)
    passed_count = sum(1 for e in exams if e.get("passed"))
    avg_score = sum(e["score"] for e in exams) / total if total > 0 else 0
    
    # 返回时不包含答案详情以减小数据量（详情可单独获取）
    summary = []
    for e in exams:
        summary.append({
            "exam_id": e.get("exam_id"),
            "user_name": e.get("user_name"),
            "user_dept": e.get("user_dept"),
            "user_phone": e.get("user_phone"),
            "score": e.get("score"),
            "correct": e.get("correct"),
            "total": e.get("total"),
            "passed": e.get("passed"),
            "submit_time": e.get("submit_time")
        })
    
    return jsonify({
        "stats": {
            "total": total,
            "passed": passed_count,
            "failed": total - passed_count,
            "pass_rate": round(passed_count / total * 100, 1) if total > 0 else 0,
            "avg_score": round(avg_score, 1)
        },
        "records": summary
    })

@app.route('/api/admin/exam/<exam_id>', methods=['GET'])
def api_admin_exam_detail(exam_id):
    """获取单次考试详细记录"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    expected = hashlib.md5(ADMIN_PASSWORD.encode()).hexdigest()
    if token != expected:
        return jsonify({"error": "未授权"}), 401
    
    exams = load_exams()
    for e in exams:
        if e.get("exam_id") == exam_id:
            return jsonify(e)
    return jsonify({"error": "未找到记录"}), 404

@app.route('/api/admin/export', methods=['GET'])
def api_admin_export():
    """导出考试数据为CSV"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    expected = hashlib.md5(ADMIN_PASSWORD.encode()).hexdigest()
    if token != expected:
        return jsonify({"error": "未授权"}), 401
    
    exams = load_exams()
    exams.sort(key=lambda x: x.get("submit_time", ""), reverse=True)
    
    csv_lines = ["姓名,部门,电话,分数,正确数,总题数,是否合格,提交时间"]
    for e in exams:
        csv_lines.append(f'{e.get("user_name","")},{e.get("user_dept","")},{e.get("user_phone","")},{e.get("score")},{e.get("correct")},{e.get("total")},{"是" if e.get("passed") else "否"},{e.get("submit_time","")}')
    
    return "\n".join(csv_lines), 200, {'Content-Type': 'text/csv; charset=utf-8', 'Content-Disposition': 'attachment; filename=exam_result.csv'}


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
