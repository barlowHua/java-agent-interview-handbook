#!/usr/bin/env python3
"""Generate the eight Agent chapter diagrams; does not rebuild the reader.

Only stdlib + the shared svgkit. Run from any directory. Geometry checks are
conservative estimates; browser text measurement remains a separate QA step.
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from svgkit import Diagram

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "modules" / "assets"
C = (25, 277, 529)
W = 226


def node(d, key, col, row, lines, color='blue', height=72):
    d.node(key, C[col], 85 + row * 100, W, height, lines, color)


def link(d, source, target, side='right', target_side=None, color='gray', dashed=False):
    d.edge(source, target, side, target_side, color, dashed)
    # Explicit ownership lets downstream QA inspect source/target clearance.
    d.connectors[-1] = d.connectors[-1].replace('data-connector="true"',
        f'data-connector="true" data-from="{source}" data-to="{target}"')


def path(d, command, source, target, color='gray', dashed=False):
    d.path(command, color, dashed)
    d.connectors[-1] = d.connectors[-1].replace('data-connector="true"',
        f'data-connector="true" data-from="{source}" data-to="{target}"')


def save(d, name):
    d.save(OUT / name)


def attention():
    d = Diagram('从 token 到下一个 token：因果注意力做了什么', height=410,
        desc='编号经过嵌入和各层投影形成 Q、K、V。因果掩码挡住未来位置，权重加权 V，最终通过词表预测下一个 token。',
        subtitle='蓝色是输入，紫色是模型计算；矩阵仅表示可见性，不表示实际注意力分数')
    node(d, 'tokens', 0, 0, ['文本 → tokenizer → 编号', '示意：t₁、t₂、t₃、t₄', '一个 token 不等于一个汉字'])
    node(d, 'embedding', 1, 0, ['token 嵌入与位置信息', '每个位置得到隐藏表示 X', '不是检索用的句向量'])
    node(d, 'qkv', 2, 0, ['各层的可学习线性投影', 'Q = XWQ；K = XWK', 'V = XWV'], 'purple')
    node(d, 'scores', 2, 1, ['缩放得分 + 因果掩码', 'A = softmax(QKᵀ/√dₖ + M)', 'M 把未来位置设为负无穷'], 'purple')
    node(d, 'aggregate', 1, 1, ['按注意力权重汇总 A V', '多头合并、前馈与残差', '堆叠多层得到上下文表示'], 'purple')
    node(d, 'output', 1, 2, ['最终隐藏表示 → 词表 logits', '转为概率并选择或采样', '得到下一个 token 编号'], 'green')
    node(d, 'append', 2, 2, ['未触发停止条件时', '把新 token 作为后续输入', '继续预测，直到结束'], 'green')
    d.group('causal-mask', 25, 185, 226, 172, '因果可见性：行 i 只能看 j ≤ i')
    d.text(145, 216, '列 j：已有位置', 10, '#64748b')
    for j in range(4): d.text(130 + j * 25, 237, str(j + 1), 10, '#64748b')
    for i in range(4):
        d.text(86, 258 + i * 25, '行 ' + str(i + 1), 10, '#64748b')
        for j in range(4):
            x, y = 119 + j * 25, 244 + i * 25
            fill = '#d1fae5' if j <= i else '#fce7f3'
            d.foreground.append(f'<rect data-cell="mask-{i}-{j}" x="{x}" y="{y}" width="22" height="22" rx="3" fill="{fill}"/>')
            d.text(x + 11, y + 14, '可' if j <= i else '×', 10, '#166534' if j <= i else '#9d174d')
    link(d, 'tokens', 'embedding', color='blue')
    link(d, 'embedding', 'qkv', color='purple')
    link(d, 'qkv', 'scores', 'bottom', color='purple')
    link(d, 'scores', 'aggregate', 'left', color='purple')
    link(d, 'aggregate', 'output', 'bottom', color='green')
    link(d, 'output', 'append', color='green')
    d.footer(['这里只画解码器自注意力的教学主干；省略归一化、具体位置编码与架构变体。',
              '注意力权重是信息混合系数，不是“事实正确率”；训练目标与业务验证是不同层。'])
    save(d, '15-token-attention.svg')


def inference():
    d = Diagram('Prefill、首 token 与 Decode：缓存复用的位置', height=430,
        desc='Prefill 处理已有输入，并由末位结果预测首个新 token。后续 decode 读取历史 KV 和最近生成的 token，追加新 KV 并预测下一个 token。',
        subtitle='单序列、标准自回归推理示意；首 token 可以由 prefill 的末位输出产生')
    node(d, 'prompt', 0, 0, ['输入上下文 t₁…tₙ', '指令、历史、工具、证据', '先给输出预留 token 预算'])
    node(d, 'prefill', 1, 0, ['Prefill：计算输入各位置', '因果约束内可并行处理', '产生各层 KV 与末位 logits'], 'purple')
    node(d, 'first', 2, 0, ['选择首个新 token tₙ₊₁', '此时可返回首段内容', 'TTFT 还包含排队与网络'], 'green')
    node(d, 'cache', 0, 1, ['KV cache：各层历史 K/V', '缓存已处理的位置', '后续追加，不重算全部前缀'], 'orange')
    node(d, 'decode', 1, 1, ['Decode：输入刚生成的 token', '读取已有 KV，计算新 KV', '完成当前一步注意力与预测'], 'purple')
    node(d, 'next', 2, 1, ['预测下一个 token', '检查结束符、长度与预算', '未结束则进入下一步'], 'green')
    node(d, 'memory', 0, 2, ['KV 显存的粗略量级', '2 × L × T × Hkv × dh × b', '不含模型权重与其他激活'], 'gray')
    link(d, 'prompt', 'prefill', color='blue')
    link(d, 'prefill', 'first', color='green')
    path(d, 'M 390,162 C 390,168 138,168 138,174', 'prefill', 'cache', 'orange')
    # Enter decode away from the prefill→cache branch so the two flows do not
    # visually join. Selecting a token does not itself append its K/V.
    path(d, 'M 642,162 C 642,168 430,168 430,174', 'first', 'decode', 'green')
    link(d, 'cache', 'decode', color='orange')
    path(d, 'M 272,242 L 262,242', 'decode', 'cache', 'orange', True)
    link(d, 'decode', 'next', color='green')
    # Return arc is outside all boxes and arrives upward at decode's bottom.
    path(d, 'M 642,262 C 642,321 390,321 390,268', 'next', 'decode', 'purple', True)
    d.text(516, 337, '下一步：新 token 成为输入', 11, '#6b21a8')
    d.text(516, 359, '新 KV 在解码步骤中追加到缓存', 10, '#64748b')
    d.footer(['L=层数，T=缓存位置数，Hkv=KV 头数，dh=每头维度，b=每元素字节数。',
              '前缀缓存命中可以减少部分输入计算；不是答案缓存，也不消除后续 decode。'])
    save(d, '15-prefill-decode.svg')


def rag_pipeline():
    d = Diagram('RAG 双链路：建库更新与带权限的在线回答', height=425,
        desc='上排为离线解析建库，下两排为在线查询与生成。可信身份约束召回，原文权限和生效版本在重排与生成前检查。',
        subtitle='索引保存可检索表示；权威原文、文档版本和权限来源必须可追溯')
    node(d, 'source', 0, 0, ['离线：受控源文档', '内容、版本、生效时间', '授权范围与来源定位'])
    node(d, 'chunks', 1, 0, ['解析、去重、结构化分块', '保留 docId / chunkId / ACL', '词法字段 + embedding'], 'orange')
    node(d, 'index', 2, 0, ['倒排索引 + 向量索引', '关联原文库及权限版本', '更新时清理旧块和墓碑'], 'green')
    node(d, 'request', 0, 1, ['在线：问题 + 已认证用户', '先识别意图与必要条件', '余额/库存转权威业务 API'])
    node(d, 'scope', 1, 1, ['可信身份 → 检索范围', '租户、ACL、生效范围', '查询改写不能扩大权限'], 'pink')
    node(d, 'retrieve', 2, 1, ['词法 + 向量候选召回', '执行可信范围过滤', '读取原文时重新检查授权'], 'orange')
    node(d, 'rerank', 2, 2, ['去重、融合、重排', '只处理已经授权的候选', '重排不能补回漏召回文档'], 'purple')
    node(d, 'context', 1, 2, ['证据装配与输出前策略', '版本、引用位置、token 预算', '缺失必要条件则澄清/拒答'], 'orange')
    node(d, 'answer', 0, 2, ['生成回答并验证逐条引用', '事实是否被证据支持？', '业务所需条件是否完整？'], 'green')
    for a,b in [('source','chunks'),('chunks','index'),('request','scope'),('scope','retrieve')]: link(d,a,b)
    link(d,'index','retrieve','bottom',color='green')
    link(d,'retrieve','rerank','bottom',color='orange')
    link(d,'rerank','context','left',color='purple')
    link(d,'context','answer','left',color='green')
    d.footer(['离线权限元数据可能滞后：定义撤销时限、校验点和缓存失效策略，不能只信索引标签。',
              '知识问答主路径示意；省略查询规划和无答案分支的具体实现，但它们必须有显式行为。'])
    save(d, '16-rag-pipeline.svg')


def rag_metrics():
    d = Diagram('检索命中、断言支持与业务成功：三个不同分母', height=410,
        desc='教学例子需要文档 A、B，实际召回 A、C、D。四个断言中三个有依据，但遗漏 B 的必要条件，业务仍然失败。',
        subtitle='同一任务可以检索命中、部分断言有依据，同时业务失败')
    node(d,'retrieval',0,0,['需要的证据：A、B','前 3 个结果：A、C、D','唯一相关命中 A，排名 1'])
    node(d,'claims',1,0,['回答含 4 条可核验断言','其中 3 条由上下文支持','另 1 条没有证据支持'],'purple')
    node(d,'goal',2,0,['业务要求：满足全部条件','必须说明 B 中的例外','权限与副作用也要合格'],'orange')
    node(d,'retrieval-score',0,1,['Recall@3 = 1/2','Hit@3 = 1；RR@3 = 1','只回答“有没有找到证据”'],'green')
    node(d,'claim-score',1,1,['Groundedness = 3/4','不保证资料真实或最新','也不证明被允许读取'],'green')
    node(d,'task-score',2,1,['本任务：业务失败','缺少 B 的必要限制条件','不能用别的高分抵消'],'pink')
    for a,b in [('retrieval','retrieval-score'),('claims','claim-score'),('goal','task-score')]: link(d,a,b,'bottom')
    d.node('denominators',25,285,730,72,[
        '检索按文档/块标注；生成按可核验断言；业务按任务与不变量判定',
        '无相关证据题单独统计拒答；无可核验断言记 N/A 并报告数量',
        '先约定权限、生效时间、标注粒度与宏/微平均，才能比较两个版本'
    ],'gray')
    d.footer(['RR 是单题倒数排名；MRR 是多题 RR 的平均值。图中数字均为教学样例。',
              '评测不要把“给出空回答”自动算作满分；也不要把最终答案包含关键词视为业务完成。'])
    save(d,'16-rag-evaluation.svg')


def agent_loop():
    d = Diagram('Agent 工具循环：模型提议，运行时执行与记账',height=495,
        desc='上面六个节点构成工具循环，状态持久化后重建上下文。下面区分对话、长期记忆和外部资料，所有输入按来源和权限治理。',
        subtitle='沿顺时针阅读；只有可信执行层可以把提议变成业务动作')
    node(d,'context',0,0,['上下文装配','当前输入 + 已授权事实','保留来源与 token 预算'])
    node(d,'model',1,0,['模型调用','回答候选或工具调用提议','模型不能授予业务权限'],'purple')
    node(d,'gate',2,0,['可信执行门禁','schema、对象授权、业务条件','预算/审批；先落库动作意图'],'pink')
    node(d,'tool',2,1,['业务工具或 MCP 适配','身份由服务端注入','限时执行；写入使用幂等键'],'orange')
    node(d,'observe',1,1,['观察结果与终止判断','校验业务真实状态','继续 / 完成 / 等待 / 失败'],'green')
    node(d,'state',0,1,['持久化运行状态','意图、结果、版本、预算','恢复不能仅依赖聊天摘要'],'green')
    for a,b in [('context','model'),('model','gate')]:link(d,a,b)
    link(d,'gate','tool','bottom',color='pink')
    link(d,'tool','observe','left',color='orange')
    link(d,'observe','state','left',color='green')
    link(d,'state','context','top',color='blue')
    d.text(390,289,'装配层按任务读取的三类资料：不能混成同一可信事实库',11,'#64748b')
    for col,key,lines,color in [
        (0,'conversation',['对话历史','保留近期信息与原始引用','可压缩，但不是交易账本'],'blue'),
        (1,'memory',['长期记忆','来源、时效与用户隔离','事实确认后才能写入'],'green'),
        (2,'external',['外部资料与工具返回','检索文本可以携带恶意指令','只作为数据，不替用户授权'],'pink')]:
        d.node(key,C[col],315,W,90,lines,color)
    d.footer(['下排是数据治理分类，不是新增执行步骤；运行状态与长期记忆分别存储和管理。',
              '副作用的动作意图必须在工具执行前落库；图中的状态节点还负责后续结果记录与恢复。',
              '只读查询同样需要对象权限；停止循环依据预算和外部可验证结果，而非模型自称完成。'])
    save(d,'17-agent-loop-memory.svg')


def recovery():
    d = Diagram('副作用结果不确定：UNKNOWN 不是 FAILED',height=445,
        desc='已授权且意图持久化后提交。明确成功可落为 SUCCEEDED；超时进入 UNKNOWN，按稳定业务键查流水。未查到不自动代表没有执行。',
        subtitle='上排是正常提交；中排是超时恢复；下排是查询结果的三种处理规则')
    node(d,'ready',0,0,['READY：已具备执行条件','身份与具体参数已授权','动作意图已持久化'],'blue')
    node(d,'sending',1,0,['SUBMITTING：已发送','稳定 intentId + 参数指纹','不是每次重试生成新键'],'orange')
    node(d,'success',2,0,['SUCCEEDED：确认成功','收到可核验的业务凭证','持久化业务 ID 与结果'],'green')
    node(d,'intent',0,1,['持久化动作记录','intentId / payload / version','崩溃后重读，防并发推进'],'gray')
    node(d,'unknown',1,1,['UNKNOWN：响应超时/丢失','可能未执行，也可能已成功','保留原意图；不直接重做'],'pink')
    node(d,'query',2,1,['按业务键查询 / 对账','重新检查身份与授权','结合服务端幂等记录判断'],'orange')
    node(d,'retry',0,2,['权威确认未执行','满足幂等/重试契约后','以原意图、原键受控重试'],'blue')
    node(d,'wait',1,2,['仍无法确认结果','保持 UNKNOWN 并退避','预算耗尽后转人工处理'],'pink')
    node(d,'restore',2,2,['确认动作已经完成','补记结果为 SUCCEEDED','不得再次触发相同副作用'],'green')
    link(d,'ready','sending')
    link(d,'sending','success',color='green')
    link(d,'intent','ready','top',color='blue',dashed=True)
    link(d,'sending','unknown','bottom',color='pink')
    link(d,'unknown','query',color='orange')
    # Fan-out lives entirely in the 28px gap. Arrow tangents end downward.
    for key,center in [('retry',138),('wait',390),('restore',642)]:
        path(d,f'M 642,262 C 642,268 {center},268 {center},274','query',key,'orange')
    d.footer(['下排列出互斥处理条件，不表示无条件自动重试；明确拒绝可落 FAILED，不能把所有超时归失败。',
              '“暂时未查到”可能来自异步受理或最终一致查询；必须按服务契约判断，不能据此重做。',
              'Checkpoint 只恢复运行过程；外部效果仍需要业务服务的幂等、流水与对账机制。'])
    save(d,'17-tool-recovery.svg')


def eval_cost():
    d=Diagram('评测数据流：从固定任务到发布门禁与成本',height=445,
        desc='固定任务输入与标签，用冻结版本执行并记录 trace，分别评估组件、业务不变量和成本时延，再做发布门禁。',
        subtitle='评分器独立于被测系统；平均高分不能抵消越权、重复动作等关键失败')
    node(d,'dataset',0,0,['固定任务与环境快照','问题、用户、证据、金标准','开发集与独立测试集分开'])
    node(d,'run',1,0,['冻结配置运行','模型/prompt/schema/索引','重复运行以观察输出波动'],'purple')
    node(d,'trace',2,0,['可回放 trace 与业务结果','路由、文档 ID、工具凭证','阶段耗时、usage、错误'],'green')
    node(d,'components',0,1,['组件与开放回答评分','Recall、参数、断言支持','规则优先；模型裁判需校准'],'blue')
    node(d,'business',1,1,['任务与安全不变量','正确对象？真实状态完成？','重复动作/越权分别统计'],'pink')
    node(d,'resources',2,1,['运行资源与交付效率','关键路径、p50/p95/p99','调用+重试+工具+人工成本'],'orange')
    link(d,'dataset','run');link(d,'run','trace',color='green')
    for key,center in [('components',138),('business',390),('resources',642)]:
        path(d,f'M 642,162 C 642,168 {center},168 {center},174','trace',key,'green')
    d.node('release',25,285,730,72,[
        '发布门禁：按任务分桶对比基线 → 小流量验证 → 持续收集失败 → 可回滚配置',
        '每成功任务成本 = 同一窗口内所有尝试的总成本 ÷ 完成业务目标的任务数',
        '成功数为 0 时该比值不可计算；不能排除失败与重试成本后宣布“更便宜”'
    ],'gray')
    for key,center in [('components',138),('business',390),('resources',642)]:
        path(d,f'M {center},262 L {center},274',key,'release','gray')
    d.footer(['指标需固定分母、时间窗口和版本；影子评测不能再次执行真实写入副作用。',
              '延迟取实际端到端分布；不能将不同阶段各自的 p95 相加当作任务 p95。',
              '示意图没有给出企业通用上线阈值，门禁应由业务风险与 SLO 决定。'])
    save(d,'18-evaluation-cost.svg')


def trust():
    d=Diagram('Agent 信任边界：外部文本不能直接获得执行权',height=485,
        desc='外部资料经过模型变成候选动作，动作必须跨过可信执行门禁。凭据仅在可信层使用，业务服务限制对象、幂等与出站目标。',
        subtitle='来源标签和提示词是辅助；真正限制副作用的是服务端身份、政策与隔离')
    d.group('untrusted',25,80,350,322,'非授权来源：只产生数据或动作提议')
    d.group('trusted',405,80,350,322,'可信执行层：授权、凭据和业务规则')
    for key,x,y,lines,color in [
        ('data',40,110,['网页 / 文档 / 邮件 / 工具文本','可能包含“忽略规则、导出密钥”等指令','不能把检索内容当作用户授权'],'pink'),
        ('model',40,210,['模型理解与生成','可以被不可信内容误导','不持有支付凭据，不拥有最终批准权'],'purple'),
        ('proposal',40,310,['候选动作：工具名 + 参数','读取与写入能力分开','身份与 tenantId 不由模型声明'],'orange'),
        ('identity',420,110,['认证后的身份与授权上下文','对象范围、操作类型、有效期','短期凭据留在服务端使用'],'blue'),
        ('gate',420,210,['执行门禁：校验具体对象与参数','允许的工具、业务条件、预算与审批','拒绝 / 等待补充 / 放行'],'pink'),
        ('service',420,310,['业务服务与出站控制','幂等、交易约束、流水查询、目标白名单','返回最小必要结果并脱敏'],'green')]:
        d.node(key,x,y,320,72,lines,color)
    link(d,'data','model','bottom',color='pink')
    link(d,'model','proposal','bottom',color='purple')
    link(d,'identity','gate','bottom',color='blue')
    link(d,'gate','service','bottom',color='green')
    path(d,'M 365,346 C 390,346 384,246 409,246','proposal','gate','orange')
    d.footer(['左侧内容不能绕过门禁访问右侧业务服务；凭据不能通过模型上下文转发给任意目标。',
              '只读也会泄露数据，工具结果仍作为数据回到循环；来源可信不等于其文字可以提升权限。',
              '这些控制用于降低风险，并不承诺消除所有 prompt injection 或运行环境漏洞。'])
    save(d,'18-trust-boundary.svg')


def verify():
    ns={'s':'http://www.w3.org/2000/svg'}
    files=sorted(p for p in OUT.glob('*.svg') if re.match(r'1[5-8]-',p.name))
    for file in files:
        root=ET.parse(file).getroot()
        vb=[float(x) for x in root.attrib['viewBox'].split()]
        boxes={}
        for rect in root.findall('.//s:rect[@data-node]',ns):
            b=tuple(float(rect.attrib[k]) for k in ('x','y','width','height'))
            boxes[rect.attrib['data-node']]=b
            assert b[0]>=20 and b[1]>=65 and b[0]+b[2]<=vb[2]-20 and b[1]+b[3]<=vb[3]-20,(file,b)
        for key,b in boxes.items():
            for other,c in boxes.items():
                if key>=other:continue
                overlap_x=min(b[0]+b[2],c[0]+c[2])-max(b[0],c[0])
                overlap_y=min(b[1]+b[3],c[1]+c[3])-max(b[1],c[1])
                assert not(overlap_x>0 and overlap_y>0),(file,key,other,'overlap')
                if overlap_x>0:assert -overlap_y>=25,(file,key,other,'vertical gap')
                if overlap_y>0:assert -overlap_x>=25,(file,key,other,'horizontal gap')
        for text in root.findall('.//s:text',ns):
            size=float(text.attrib.get('font-size',12)); x=float(text.attrib['x']);y=float(text.attrib['y'])
            content=''.join(text.itertext())
            estimate=sum(size if ord(ch)>255 else size*.57 for ch in content)
            anchor=text.attrib.get('text-anchor','start')
            left=x-estimate/2 if anchor=='middle' else (x-estimate if anchor=='end' else x)
            right=left+estimate
            assert left>=5 and right<=vb[2]-5 and y-size>=5 and y+size*.3<=vb[3]-5,(file,content,'viewBox')
            if 'data-owner' in text.attrib:
                bx,by,bw,bh=boxes[text.attrib['data-owner']]
                assert left>=bx+6 and right<=bx+bw-6,(file,content,'node text width')
                assert y-size>=by+8 and y+size*.3<=by+bh-8,(file,content,'node text height')
        for marker in root.findall('.//s:marker',ns):
            assert marker.attrib['markerUnits']=='userSpaceOnUse'
        assert 'Noto Sans CJK SC' in file.read_text()
        print(f'OK {file.name}: XML / node spacing / estimated text / markers')
    assert len(files)==8, f'expected 8 diagrams, found {len(files)}'


if __name__=='__main__':
    for draw in (attention,inference,rag_pipeline,rag_metrics,agent_loop,recovery,eval_cost,trust):draw()
    verify()
