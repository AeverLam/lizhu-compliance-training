from flask import Flask, send_file, request, jsonify, render_template_string
import os, json, random, hashlib, time
from functools import wraps
from datetime import datetime

app = Flask(__name__)

# ========== 配置 ==========
ADMIN_PASSWORD = "livzon2026"
DATA_DIR = "data"
EXAM_FILE = os.path.join(DATA_DIR, "exams.json")

os.makedirs(DATA_DIR, exist_ok=True)

# ========== 题库 ==========
# 包含知识点题 + 场景题，全部随机抽取
QUESTION_BANK = [
    # ===== 模块一：当下的形势 =====
    {
        "id": 1,
        "type": "single",
        "question": "课程提到医药反腐的监管覆盖范围已扩展到什么程度？",
        "options": ["A. 仅限药品生产企业", "B. 仅限医院和医生", "C. 穿透式监管覆盖医药购销全链条", "D. 仅限销售代表个人"],
        "answer": 2,
        "section": "当下的形势"
    },
    {
        "id": 2,
        "type": "single",
        "question": "课程强调，学术推广活动最核心的合规底线是什么？",
        "options": ["A. 只要不直接给现金就行", "B. 学术内容真实且占主体，费用与活动实质匹配", "C. 经过上级口头同意即可", "D. 只要医生满意就算成功"],
        "answer": 1,
        "section": "行为红线"
    },
    {
        "id": 3,
        "type": "single",
        "question": "全国医药领域腐败问题集中整治工作是从什么时间正式启动的？",
        "options": ["A. 2022年1月", "B. 2023年7月", "C. 2024年3月", "D. 2025年1月"],
        "answer": 1,
        "section": "当下的形势"
    },
    {
        "id": 4,
        "type": "single",
        "question": "当前医药反腐进入了什么阶段？",
        "options": ["A. 初期排查阶段", "B. 收尾总结阶段", "C. 深水区阶段", "D. 试点阶段"],
        "answer": 2,
        "section": "当下的形势"
    },
    {
        "id": 5,
        "type": "multiple",
        "question": "当前医药反腐发出了哪些核心信号？（多选）",
        "options": ["A. 学术会议大面积叫停或缩减", "B. 医药代表备案制严格执行", "C. 讲课费、咨询费严查", "D. 数字化追溯能力提升"],
        "answer": [0, 1, 2, 3],
        "section": "当下的形势"
    },

    # ===== 模块二：行为红线 =====
    {
        "id": 6,
        "type": "multiple",
        "question": "以下哪些行为属于商业贿赂红线？（多选）",
        "options": ["A. 向医生支付现金回扣", "B. 赠送购物卡给医生", "C. 通过CSO变相输送利益", "D. 为医生的子女升学买单"],
        "answer": [0, 1, 2, 3],
        "section": "行为红线"
    },
    {
        "id": 7,
        "type": "single",
        "question": "课程提出的合规关键判断标准是什么？",
        "options": ["A. 金额是否超过500元", "B. 是否能向纪检/检察院/媒体解释正当关系", "C. 是否经过领导批准", "D. 是否在公开场合进行"],
        "answer": 1,
        "section": "行为红线"
    },
    {
        "id": 8,
        "type": "multiple",
        "question": "以下哪些属于虚假学术活动？（多选）",
        "options": ["A. 以学术会议为名组织旅游", "B. 虚构参会人员名单套取会议费用", "C. 学术会议实际内容与报批不符", "D. 以讲课费名义向医生支付回扣"],
        "answer": [0, 1, 2, 3],
        "section": "行为红线"
    },
    {
        "id": 9,
        "type": "single",
        "question": "医药代表拜访医生前，必须完成什么？",
        "options": ["A. 出差申请", "B. 医药代表备案，并通过医院指定平台预约", "C. 产品知识考试", "D. 销售目标确认"],
        "answer": 1,
        "section": "行为红线"
    },
    {
        "id": 10,
        "type": "multiple",
        "question": "以下哪些属于费用造假和套现行为？（多选）",
        "options": ["A. 虚开发票、虚报差旅", "B. 虚构会议费用", "C. 用个人账户代收代付公司业务款", "D. 与CSO签订虚假服务合同套取费用"],
        "answer": [0, 1, 2, 3],
        "section": "行为红线"
    },
    {
        "id": 11,
        "type": "single",
        "question": "关于讲课费，以下说法正确的是？",
        "options": ["A. 只要有医生签名就算合规", "B. 必须对应真实的讲课行为，有真实听众和内容", "C. 可以先支付后补讲课", "D. 讲课费标准可以自行决定"],
        "answer": 1,
        "section": "行为红线"
    },
    {
        "id": 12,
        "type": "single",
        "question": "关于CSO合作，以下说法正确的是？",
        "options": ["A. CSO可以作为利益输送通道", "B. 可以与无实际业务能力的CSO合作", "C. CSO必须有真实的业务能力和服务交付", "D. CSO不需要实际办公场所和员工"],
        "answer": 2,
        "section": "行为红线"
    },

    # ===== 模块三：实操指南 =====
    {
        "id": 13,
        "type": "single",
        "question": "遇到不确定是否合规的场景时，正确的处理原则是？",
        "options": ["A. 先做了再说", "B. 停下来 → 问上级或合规部 → 留记录", "C. 问同事，大家说行就行", "D. 自己判断，出问题再说"],
        "answer": 1,
        "section": "实操指南"
    },
    {
        "id": 14,
        "type": "multiple",
        "question": "以下哪些情况需要立即上报？（多选）",
        "options": ["A. 上级要求你配合做虚假报销", "B. 医生主动索要回扣", "C. 发现同事有疑似违规行为", "D. 收到监管部门调查通知"],
        "answer": [0, 1, 2, 3],
        "section": "实操指南"
    },
    {
        "id": 15,
        "type": "single",
        "question": "关于微信/短信/邮件中讨论费用和利益，正确的做法是？",
        "options": ["A. 不在这些渠道讨论，也不开展涉及费用和利益的活动", "B. 可以在私人微信中讨论", "C. 只要用加密邮件就可以", "D. 只要不留下文字记录就可以"],
        "answer": 0,
        "section": "实操指南"
    },
    {
        "id": 16,
        "type": "single",
        "question": "医生主动索要回扣时，正确的做法是？",
        "options": ["A. 答应以维护客户关系", "B. 私下给，不做记录", "C. 明确拒绝、做好记录、立即上报", "D. 让医生通过第三方拿"],
        "answer": 2,
        "section": "实操指南"
    },
    {
        "id": 17,
        "type": "multiple",
        "question": "学术活动合规检查清单包含哪些内容？（多选）",
        "options": ["A. 活动目的是否与学术推广直接相关", "B. 讲者是否具备相应资质", "C. 活动地点是否合理（非旅游度假城市）", "D. 是否安排了签到拍照等留痕措施", "E. 费用预算是否与活动规模匹配"],
        "answer": [0, 1, 2, 3, 4],
        "section": "实操指南"
    },

    # ===== 场景题（核心能力考核） =====
    {
        "id": 101,
        "type": "single",
        "question": "【场景】你计划组织一场消化道领域的学术研讨会，有同事建议安排在海边度假城市，并预留三天自由活动时间。以下做法正确的是？",
        "options": ["A. 同意，学术会议与休闲结合更好", "B. 拒绝，学术活动地点要有合理性，学术内容占主体，不能出现半天开会三天玩", "C. 把学术内容压缩到半天，其余时间自由活动", "D. 只要医生高兴就行"],
        "answer": 1,
        "section": "场景题"
    },
    {
        "id": 102,
        "type": "single",
        "question": "【场景】一位核心处方医生私下对你说：\"这个月多开点你们的药，每盒给我返30块就行。\"你应该怎么做？",
        "options": ["A. 答应他，毕竟是大客户", "B. 口头答应但不记录", "C. 明确拒绝，做好记录，立即通过合规渠道上报", "D. 让他写个收据就行"],
        "answer": 2,
        "section": "场景题"
    },
    {
        "id": 103,
        "type": "single",
        "question": "【场景】你的上级要求你帮一位医生的个人旅游费用\"走一下学术会议费报销\"，并表示\"大家都这么干\"。你应该怎么做？",
        "options": ["A. 照做，上级的话不能不听", "B. 拒绝并上报，这是虚假报销，属于红线行为", "C. 帮他想办法换成其他名目报销", "D. 私下帮医生付了"],
        "answer": 1,
        "section": "场景题"
    },
    {
        "id": 104,
        "type": "single",
        "question": "【场景】你正在准备一场科室会，科室主任说：\"讲就不用讲了，PPT我签个名，讲课费照给就行。\"你应该怎么做？",
        "options": ["A. 同意，省时省力", "B. 拒绝，讲课费必须对应真实的讲课行为，有真实听众和内容", "C. 让主任象征性讲5分钟", "D. 把讲课费换成其他形式支付"],
        "answer": 1,
        "section": "场景题"
    },
    {
        "id": 105,
        "type": "single",
        "question": "【场景】医生在微信群里@你说：\"你们竞品那边每盒返5块，你们能返多少？\"你应该怎么处理？",
        "options": ["A. 直接在群里回复一个更有竞争力的价格", "B. 加他私聊讨论", "C. 不在微信讨论费用和利益安排，也不开展此类活动", "D. 让医生删掉消息就当没发生过"],
        "answer": 2,
        "section": "场景题"
    },
    {
        "id": 106,
        "type": "single",
        "question": "【场景】你的医药代表备案还没完成，但经理催你这周必须去医院拜访关键医生。你应该怎么做？",
        "options": ["A. 先去拜访，备案补上就行", "B. 先完成备案，再通过医院指定平台预约拜访", "C. 让经理帮你想办法绕过备案", "D. 趁医院不检查时去"],
        "answer": 1,
        "section": "场景题"
    },
    {
        "id": 107,
        "type": "single",
        "question": "【场景】你在组织科室会时，有同事建议：\"参会名单多写几个医生名字，这样费用能多报一些。\"你应该怎么做？",
        "options": ["A. 同意，反正不会有人查", "B. 拒绝，参会名单必须真实，虚构参会人员属于红线行为", "C. 中间折中，只多报一两个", "D. 让同事自己决定"],
        "answer": 1,
        "section": "场景题"
    },
    {
        "id": 108,
        "type": "single",
        "question": "【场景】医生提出要你给他孩子安排夏令营费用，他说\"就当是正常的学术支持费用来走\"。你应该怎么做？",
        "options": ["A. 帮他安排，用学术费用报销", "B. 私下自己掏钱帮他付", "C. 拒绝，为医生个人活动买单是商业贿赂红线行为", "D. 让他找别的代表帮忙"],
        "answer": 2,
        "section": "场景题"
    },
    {
        "id": 109,
        "type": "single",
        "question": "【场景】你发现一个同事在报销时虚报差旅费，金额还不小。你应该怎么做？",
        "options": ["A. 装作不知道，不关我的事", "B. 私下提醒他别这样做了", "C. 通过合规渠道上报，发现疑似违规行为要立即上报", "D. 跟他一起做，反正不会被发现"],
        "answer": 2,
        "section": "场景题"
    },
    {
        "id": 110,
        "type": "single",
        "question": "【场景】竞品公司的代表在给医生回扣，导致你跟进的一位医生也开始暗示要好处。你应该怎么做？",
        "options": ["A. 也跟着给回扣，不然丢客户", "B. 用产品临床价值和专业服务赢得医生，合规体系正在建设中", "C. 向上级申请一笔\"特殊费用\"", "D. 放弃这个医生"],
        "answer": 1,
        "section": "场景题"
    },
    {
        "id": 111,
        "type": "single",
        "question": "【场景】你在非工作时间（周末）接到一位医生电话，说他刚完成一台手术，想让你过去聊聊新产品的用法。以下做法正确的是？",
        "options": ["A. 马上过去，医生要求不能拒绝", "B. 约定在非约定场所见面", "C. 告知医生在工作时间和医院指定平台预约后正式拜访", "D. 在电话里直接进行超适应症推广"],
        "answer": 2,
        "section": "场景题"
    },
    {
        "id": 112,
        "type": "single",
        "question": "【场景】一位老同事告诉你：\"我们这个品种竞争太激烈，不搞点返利根本推不动，你在开科室会的时候可以暗示一下医生用量和费用的关系。\"你应该？",
        "options": ["A. 照做，老同事经验丰富", "B. 拒绝，推广内容严格按产品说明书进行，不能涉及费用/利益", "C. 只在私下场合说", "D. 让同事自己去做"],
        "answer": 1,
        "section": "场景题"
    },
    {
        "id": 113,
        "type": "single",
        "question": "【场景】医生问你：\"你们这个药能不能用于XX适应症（该适应症不在说明书范围内）？如果可以我就多用。\"你应该怎么做？",
        "options": ["A. 告诉医生可以用，已经有很多人这么用了", "B. 引导医生联系医学部处理，不做超适应症推广", "C. 口头告诉医生但不要留下记录", "D. 给医生看竞品的超适应症资料"],
        "answer": 1,
        "section": "场景题"
    },
    {
        "id": 114,
        "type": "single",
        "question": "【场景】一位CSO负责人找到你，提出你们可以签一份\"市场推广服务合同\"，他负责走账，把一部分钱以讲课费名义给到医生。你应该？",
        "options": ["A. 合作，CSO模式很多人都用", "B. 拒绝，这是典型的利用CSO变相输送利益，属于红线行为", "C. 私下口头合作不留合同", "D. 建议他用别的名目"],
        "answer": 1,
        "section": "场景题"
    },
    {
        "id": 115,
        "type": "single",
        "question": "【场景】部门要组织一场学术推广活动，经理说为了节省预算，\"讲者资质不用太严格，找个关系好的医生挂个名就行\"。你应该？",
        "options": ["A. 照做，节省预算很重要", "B. 坚持讲者必须有资质，讲课内容须经过医学部审核", "C. 象征性审核一下", "D. 让经理自己负责"],
        "answer": 1,
        "section": "场景题"
    },
    {
        "id": 116,
        "type": "single",
        "question": "【场景】你刚完成医药代表备案，第一次去医院拜访。进门时发现门诊走廊里挤了很多患者，医生匆匆打了个招呼。以下做法正确的是？",
        "options": ["A. 趁机塞给他一些产品资料和一份小礼物", "B. 只使用公司批准的推广材料，不做超适应症推广，在CRM系统中如实记录", "C. 约医生下班后到附近餐厅详谈", "D. 把资料交给护士让她转交"],
        "answer": 1,
        "section": "场景题"
    },
    {
        "id": 117,
        "type": "single",
        "question": "【场景】有媒体记者联系你，询问公司某产品的推广费用和医生合作情况。你应该？",
        "options": ["A. 如实回答记者的问题", "B. 立即上报，收到媒体询问属于需要立即上报的情况", "C. 让记者发邮件来", "D. 回避并删除联系方式"],
        "answer": 1,
        "section": "场景题"
    },
    {
        "id": 118,
        "type": "single",
        "question": "【场景】一位关键医生要过生日了，他暗示你\"有没有什么表示\"。以下做法合规的是？",
        "options": ["A. 送一张500元的购物卡", "B. 发一个微信红包", "C. 仅限公司统一发放的合规推广物料，金额严格控制在公司标准内", "D. 请他去高档餐厅吃饭"],
        "answer": 2,
        "section": "场景题"
    },

    # ===== 总结与承诺 =====
    {
        "id": 21,
        "type": "single",
        "question": "医药反腐的长期趋势是什么？",
        "options": ["A. 一轮整治后会放松", "B. 不会过去，只会更严", "C. 只针对外资企业", "D. 两年后会结束"],
        "answer": 1,
        "section": "总结与承诺"
    },
    {
        "id": 22,
        "type": "single",
        "question": "课程强调的核心理念是？",
        "options": ["A. 合规是公司在为难你", "B. 合规是保护自己，监管在盯着你", "C. 回扣是行业惯例", "D. 出事了再说"],
        "answer": 1,
        "section": "总结与承诺"
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
    """从题库随机抽取 n 道题生成试卷，保证场景题和知识题比例合理"""
    # 分为知识题和场景题
    knowledge = [q for q in QUESTION_BANK if q["section"] != "场景题"]
    scenario = [q for q in QUESTION_BANK if q["section"] == "场景题"]
    
    random.shuffle(knowledge)
    random.shuffle(scenario)
    
    # 抽取8道场景题 + 12道知识题
    selected_scenario = scenario[:8]
    selected_knowledge = knowledge[:12]
    
    # 如果场景题不够8道，用知识题补
    if len(selected_scenario) < 8:
        extra = knowledge[12:12 + (8 - len(selected_scenario))]
        selected_knowledge = knowledge[:12 + (8 - len(selected_scenario))]
        selected_scenario = scenario + extra[:8 - len(scenario)]
    
    selected = selected_scenario + selected_knowledge
    random.shuffle(selected)
    
    for i, q in enumerate(selected):
        q = q.copy()
        q["exam_order"] = i + 1
        selected[i] = q
    return selected

def calculate_score(answers, questions):
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
    exam_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:12]
    questions = generate_exam(20)
    
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
    
    if not hasattr(app, 'exam_cache'):
        app.exam_cache = {}
    app.exam_cache[exam_id] = questions
    
    return jsonify({
        "exam_id": exam_id,
        "total": len(safe_questions),
        "time_limit": 30,
        "questions": safe_questions
    })

@app.route('/api/exam/submit', methods=['POST'])
def api_exam_submit():
    data = request.json
    exam_id = data.get("exam_id")
    user_info = data.get("user_info", {})
    answers = data.get("answers", {})
    
    if not hasattr(app, 'exam_cache') or exam_id not in app.exam_cache:
        return jsonify({"error": "试卷已过期，请重新生成"}), 400
    
    questions = app.exam_cache[exam_id]
    score, correct, total, details = calculate_score(answers, questions)
    passed = score >= 80
    
    result_details = []
    for d, q in zip(details, questions):
        result_details.append({
            "question": q["question"],
            "user_answer": d["user_answer"],
            "correct_answer": d["correct_answer"],
            "is_correct": d["is_correct"],
            "section": q["section"]
        })
    
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
    data = request.json
    password = data.get("password", "")
    if password == ADMIN_PASSWORD:
        return jsonify({"success": True, "token": hashlib.md5(ADMIN_PASSWORD.encode()).hexdigest()})
    return jsonify({"success": False, "message": "密码错误"}), 401

@app.route('/api/admin/exams', methods=['GET'])
def api_admin_exams():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    expected = hashlib.md5(ADMIN_PASSWORD.encode()).hexdigest()
    if token != expected:
        return jsonify({"error": "未授权"}), 401
    
    exams = load_exams()
    exams.sort(key=lambda x: x.get("submit_time", ""), reverse=True)
    
    total = len(exams)
    passed_count = sum(1 for e in exams if e.get("passed"))
    avg_score = sum(e["score"] for e in exams) / total if total > 0 else 0
    
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
