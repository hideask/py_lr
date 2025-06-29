# -*- coding: utf-8 -*-

import json
import logging
import requests



logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# 获取一个日志器
logger = logging.getLogger(__name__)


# 模拟API调用的函数
def api_call(query, AppConversationID, userID):
    url = 'http://10.163.21.201:32300/api/proxy/api/v1/chat_query'
    data = {
        'Apikey': 'd138prfsbfv9olu4a700',
        "Query": query,
        "AppConversationID": AppConversationID,
        "ResponseMode": "blocking",
        "UserID": userID
    }

    headers = {
        'Content-Type': 'application/json',
        'Apikey': 'd138prfsbfv9olu4a700',
    }

    response = requests.post(url, json=data, headers=headers)

    introduce = '无'

    if response.status_code == 200:
        start = response.text.index('{')
        result = json.loads(response.text[start:-1]).get("answer")
        result = result.encode('ISO_8859_1').decode('utf-8')
        try:
            if result != '':
                logging.info(f'{result}')
            else:
                error = json.loads(result[result.index('{'):result.index('}') + 1]).get('error')
                logging.error(f'error:{error}')
        except Exception as e:
            logging.error(f'数据解析失败:{e}')
    else:
        logging.error(f'Failed to post data:{response.text}')


def getApplicationId(threadName):
    url = 'http://10.163.21.201:32300/api/proxy/api/v1/create_conversation'
    data1 = {
        'Apikey': 'd138prfsbfv9olu4a700',
        "Inputs": {
            "var": "variable"
        },
        "UserID": threadName
    }

    headers = {
        'Content-Type': 'application/json',
        'Apikey': 'd138prfsbfv9olu4a700'
    }

    response1 = requests.post(url, json=data1, headers=headers)

    if response1.status_code == 200:
        AppConversationID = response1.json().get("Conversation").get('AppConversationID')
    else:
        AppConversationID = ''
        print('Failed to post data:', response1.status_code)
    return AppConversationID


# 主函数
def main():
    userId = '123'
    AppConversationID = getApplicationId(userId)
    query = '{"user": {"name": "刘先生", "genderLabel": "男", "email": "", "age": 36, "ageLabel": "36岁", "maxEducationLabel": "本科", "workYears": 14, "workYearsLabel": "14年", "cityLabel": "现居深圳 南山区", "phone": "176****5122"}, "resume": {"skillTags": ["web前端", "虚拟机/jvm", "android移动开发", "vue.js框架", "ios移动开发", "小程序开发", "typescript", "yarn", "规则引擎", "日志分析"], "educationExperiences": [{"schoolName": "北京大学", "beginTime": 1485878400000, "endTime": 1580486400000, "educationTimeLabel": "2017.02 - 2020.02", "major": "信息管理与信息系统", "educationLabel": "本科"}, {"schoolName": "江西旅游商贸职业学院", "beginTime": 1220198400000, "endTime": 1309449600000, "educationTimeLabel": "2008.09 - 2011.07", "major": "计算机及应用", "educationLabel": "大专"}], "workExperiences": [{"orgName": "美的集团战略合作事业部（外包项目）", "description": "核心职责：参与美的集团AI创新业务线（AIGC）的边缘系统开发与工具链优化，随着边缘系统开发的深入有的涉及到核心数据及应用，因此需要调整岗位，重新找一些 非核心岗位 边缘系统开发项目。目前的项目基于 Vue3 + TypeScript 技术栈完成低代码模块化组件封装，推动内部研发效能提升 20%（通过代码复用率评估）\n关键成果：\n数字人智能陪练系统：独立负责交互层功能迭代，完成动态表单配置器开发与 API 数据流重构，支撑日均 5000+ 用户会话稳定运行（TPS ≤50ms）\nAIGC 门户站点工程化升级：采用 Composition API 重构核心模块，通过 AI 驱动的 ESLint 规则引擎实现代码质量自动化管控，减少人工 Code Review 耗时 40%\n敏捷交付能力：参与 2 个以上微前端子应用开发，100% 达成版本里程碑目标", "jobTitle": "web前端工程师", "timeLabel": "2025.02 - 2025.04 (2个月)", "workSkillTags": [{"name": "AIGC门户"}, {"name": "TypeScript"}, {"name": "Vue"}, {"name": "React"}, {"name": "Node.js"}]}, {"orgName": "深圳市问渠科技有限公司", "description": "1.鸿蒙跨端架构设计：基于HarmonyOS FA模型与Uniapp+Vue2技术栈，主导搭建多端融合框架，实现iOS/Android/HarmonyOS三端代码复用率提升至85%，通过动态模块加载与ArkUI组件适配，解决鸿蒙特有手势操作（如边缘滑动、多指触控）的兼容性问题。\n\n2.HarmonyOS原生能力整合：深度集成HarmonyOS原子化服务（FA），实现与原生模块（权限管理、分布式数据管理、设备协同）的无缝通信；开发鸿蒙调试日志分析工具，基于HiLogKit实现运行时异常监控，提升故障定位效率40%。\n\n3.性能优化与工程化：采用Monorepo架构管理企业级组件库，结合Yarn Workspaces与Lerna实现跨项目模块共享；搭建基于Docker的CI/CD流水线，部署阶段化构建策略（增量编译+按需打包），降低鸿蒙FA应用构建耗时30%。\n\n核心业务系统研发：\n1.主导健康分小程序与鸿蒙FA商城双端开发，基于ArkUI实现自适应布局与跨设备协同（手机/平板/智慧屏），支持分布式购物车同步；\n\n2.设计千人千面营养测评系统，整合HarmonyOS传感器数据（健康Kit）与大数据埋点，实现用户行为漏斗分析，推动复购率提升22%；\n\n3.研发支付分期与一键复购服务，通过HarmonyOS安全子系统（身份认证+可信执行环境）保障交易安全，降低首单获客成本18%。", "jobTitle": "web前端开发工程师", "timeLabel": "2024.02 - 2024.12 (10个月)", "workSkillTags": [{"name": "鸿蒙项目"}, {"name": "TypeScript"}, {"name": "Vue"}, {"name": "uni-app"}, {"name": "Node.js"}]}, {"orgName": "上海镜心智能科技有限公司", "description": "工作内容：\n1. AI智能体做即时聊天系统\n2. 做内部数据采集系统，对数据进行分析并反馈结果。\n3. 通过自定义采集器，使用APP或者浏览器对目标网站进行数据采集并入库。\n4. 在 GitLab 平台上，主导研发和生产两套解决方案的搭建，实时监控上下游竞品价格和库存变动。\n业绩:\n 1. TTS研发及在项目初期，全程参与了大部分站点的功能设计和实现，包括SOCKET即使消息、mongodb数据库入库、用户群组、AI交互Stream流等，确保项目AI从HTTP的字节模式转到长文本输出模式。\n2. 成功实现内部 ERP 系统的对接，实现竞品和上下游价格和库存数据的实时同步，以及订单数据的无缝传输，确保了企业运营的精准与高效。\n3.参与数据分析系统的接口开发与优化，帮助企业建立起强大的数据分析体系，实现精准多维度分析，有效提升企业决策科学性。", "jobTitle": "前端开发工程师", "timeLabel": "2023.02 - 2024.01 (11个月)", "workSkillTags": [{"name": "HTML5"}, {"name": "CSS"}, {"name": "JavaScript"}, {"name": "即时聊天"}, {"name": "uni-app"}, {"name": "Vue"}, {"name": "Node.js"}, {"name": "Echarts"}, {"name": "Three.js"}]}, {"orgName": "深圳市普森斯科技有限公司", "description": "内容:\n1. 以大疆官网为竞品分析,针对性能和品牌调性 根据原型制作官网和品牌独立站和优化\n2. 根据原型设计主导外贸独立站研发,包括多页引用的 SEO优化、品牌站界面落地\n3. 针对订阅和支付进行对接及促销优惠券的使用和 ERP 打通\n业绩:\n1. 参与 主导前期企业布局全球8个国家的外贸独立站。\n2. 参与 独立站性能优化,和缓存优化。\n3. 全球各个国家打开独立站的网速是不一样的,而内容制作和商城打开需要优化的地方也不一样,主要实现了 独立站从浏览到购买全流程和用户中心及优惠券核销之类的业务逻辑。", "jobTitle": "web前端工程师", "timeLabel": "2022.02 - 2022.12 (10个月)", "workSkillTags": [{"name": "HTML5"}, {"name": "Node.js"}, {"name": "jQuery"}, {"name": "JavaScript"}, {"name": "TypeScript"}]}, {"orgName": "深圳中集智能科技有限公司", "description": "内容:\n 1. 分析 CIMC 监控平台和 TOS 系统的需求及根据船舶计划、堆场北斗实时数据、堆场闸口事件、GIS 可视化等系统数据信息交互\n信息前端展示和预研\n2. 数字孪生项目可行性预研及 Three.js 可视化管理 重构\n3. 针对 WIFI 网络和蜂窝网络，CAN 和串口或蓝牙相关物联网设备数据软硬件数据采集可视化\n4.小程序冷箱卫士前端开发、冷箱数据采集平台 WEB 管理系统前端开发\n业绩:\n 1. 研发冷箱卫士小程序\n2. 研发 WEB 冷箱数据采集平台系统\n3. 前期数字孪生堆场可行性预研", "jobTitle": "Web前端工程师", "timeLabel": "2021.02 - 2021.12 (10个月)", "workSkillTags": [{"name": "ES6"}, {"name": "HTML5"}, {"name": "ElementUI"}, {"name": "Web前端"}, {"name": "小程序"}, {"name": "Vue"}, {"name": "Node.js"}, {"name": "Canvas"}]}, {"orgName": "深圳市合纵动力软件科技有限公司", "description": "内容:\n1. 负责项目的需求收集和分析以及针对竞品进行交互优化提供方案 提供建议\n2. 主导前端3-5个人小组相关工作\n2. 负责对研发项目进行拆解和颗粒度划分以及交互落地\n3. 负责协调后端研发人员对齐颗粒度进行敏捷成果交付、前端框架选型\n4. 负责项目开发文档编写和项目总结\n5. 负责前端页面的功能开发包括：\n● POS 收银结算系统进行前端界面开发和交互\n● POS 点单系统进行前端界面开发和交互，包括自定义触摸键盘、菜品多级分类快速筛选\n● POS 会员系统进行前端界面开发和交互\n● 负责公共组件的 WEB 端异形屏幕适配，包括分页优化，列表展示优化和快速批量编辑优化实现\n● 负责胡桃里酒吧小程序前端点餐页面的功能开发即点餐、会员卡、礼品卡、充值等\n业绩:\n 1. 成功推动POS收银、点单、会员系统在实际业务中落地应用，提升了公司的运营效率和客户满意度。\n 2. 成功实现了小程序会员、点单及线上支付的落地，为公司拓展了新的业务渠道，并提高了会员的消费体验。", "jobTitle": "Senior front-end engineer", "timeLabel": "2019.04 - 2021.01 (1年 9个月)", "workSkillTags": [{"name": "Vue"}, {"name": "VueX"}, {"name": "CSS3"}, {"name": "ES6"}, {"name": "ES5"}, {"name": "Canvas"}, {"name": "Javascript"}, {"name": "MVVM"}]}, {"orgName": "深圳市组创微电子有限公司", "description": "内容:\n1.负责H5开发微信公众号，原生 ES 6小程序产品前端开发实现, 内部应用管理软件开发。\n2.角色分析,流程分析, 绘制产品原型,逻辑思维导图,模块化的 JAVASCRIPT 代码开发\n实现及团队前端开发文档标准编写,物联网智能产品(软件硬件结合)的产品上线。\n3.根据调研数据,明确产品定位,分析产品特点,管理产品功能模块,实现界面设计与视觉效果\n的统一,协调资源和软件开发与硬件的产品功能 。\n4.通过H5开发及指令编码封装对接 实现移动设备 WIFI 联网、蓝牙联网、声波配网等技术，\n并实现对设备进行控制和云资源协调共享。\n儿童产品符合儿童的品味，让用户有良好的产品交互使用体\n业绩:\n1. 参与机顶盒设备及电视 APP 前端 和界面广告打通，儿童安全座椅、点读笔、故事机等研发\n2. 参与 实现了物联网新方案的 声波配网、AIRKISS 配网、蓝牙配网相关工作\n3. 构建了企业内部烧录管理系统 针对 BOM 物料进行管理和成本核算", "jobTitle": "web前端", "timeLabel": "2017.02 - 2019.02 (2年)", "workSkillTags": [{"name": "JavaScript"}]}, {"orgName": "北大光电研究院", "description": "内容:\n从业公司为东莞中石创半导体有限公司属于电子方案解决供应商，其中石创属于北大光电研究院旗下子公司，属于主导研发灯控台灯 AIOT 项目，全程参与物联网项目全流程相关工作：\n1. 设备通讯协议制定和产品需求分析- 流程分析, 绘制产品原型,逻辑思维导图, 微信小程序和公众号的相关代码开发及实现设备配网，实现及团队前端开发文档标准编写,物联网智能产品(软件硬件结合)的产品上线。\n2.根据调研数据,明确产品定位,分析产品特点,管理产品功能模块,实现界面设计与视觉效果\n的统一,协调资源和软件开发与硬件的产品功能 。\n业绩:\n1.落地从零到1实现了一款物联网植物台灯。\n2.开发符合儿童心理预期的交互界面。\n3.开发前期的设备管理后台对协议和设备绑定及配网进行落地。", "jobTitle": "物联网产品经理", "timeLabel": "2016.08 - 2017.02 (6个月)", "workSkillTags": [{"name": "物联网"}]}, {"orgName": "东莞市嘉荣超市有限公司", "description": "内容:\n1. 主要负责电商平台运维和二次开发,使用高负载高并发的 LINUX 系统运维技术,配合营销活动.根据咨询相关营销企业,明确系统产\n品定位,实现传统零售企业的信息化转型,从办公 OA 电子会员到 ERP 促销优惠券 并通过多个第三方开发商对接把项目落地并实现\n验收。\n2. 参与构建 ESB 服务总线实现内外网防火墙和堡垒机部署项目跟进和私有云前期搭建。\n3. 管理项目团队协调跨公司多方团队实现 嘉荣超市 POS 设备的支付宝和微信支付升级和对 ERP 系统的打通以及十多个系统的部\n分参与招标及相关内部峰会和新品软件发布会。\n4. 对现有系统进行维护和升级项目对接管控- 前端开发 JQUERY,DIV \\HTML \\CSS AJAX等 及后端 PHP 代码的调整，LINUX 运维\n及常用的 SHELL 命令。\n5.落地了 ERP 系统购物积分系统，用户可以通过线下办理会员后，消费获取积分并通过活动使用积分进行兑换礼品支撑营销部活\n动系统体系搭建。\n业绩:\n● 13年 当年喜伴啦啦网年营收破100万大关。\n● 14年落地了会员积分兑换系统 实现了微信会员破百万，会员转化率提升了30%。\n● 15年落地了 POS 相关微信和支付宝 系统，经过压测后在当年双十二无纸币交易量表现抢眼。", "jobTitle": "信息系统主管", "timeLabel": "2013.10 - 2016.05 (2年 7个月)", "workSkillTags": [{"name": "零售电商"}, {"name": "食品电商"}, {"name": "母婴电商"}]}, {"orgName": "东莞房产网", "description": "www.0769fcw.com   [CLOSED]\n服务器:IIS  开发语言:  数据库: MSSQL", "jobTitle": ".net软件工程师", "timeLabel": "2010.09 - 2012.09 (2年)", "workSkillTags": [{"name": "C#"}]}], "projectExperiences": [{"name": "会员服务与支付系统（HarmonyOS安全子系统 + 微服务架构）", "beginTime": 1706716800000, "endTime": 1732982400000, "timeLabel": "2024.02 - 2024.12 (10个月)", "description": "技术实现：\n\n基于HarmonyOS TEE可信执行环境开发支付安全模块，集成指纹/3D人脸双因子认证，保障分期付款交易安全性；\n\n采用ArkTS声明式编程重构会员中心，实现动态权益展示（包月/包年/试用会员的差异化UI渲染）。\n核心功能：\n\n设计「营养方案-会员等级」智能匹配算法，结合问卷数据自动推荐会员套餐（转化率提升32%）；\n\n开发跨平台支付中间件，支持微信/支付宝/华为Pay多通道无缝切换，支付成功率提升至99.6%。\n商业价值：\n\n会员体系上线；\n通过分期付款功能降低首单门槛，新客转化成本下降。", "responsibility": ""}, {"name": "个性化问卷与营养定制系统（HarmonyOS传感器融合 + AI推理）", "beginTime": 1706716800000, "endTime": 1732982400000, "timeLabel": "2024.02 - 2024.12 (10个月)", "description": "技术创新：\n\n1. 整合HarmonyOS健康传感器（心率、睡眠监测）与问卷数据，生成个性化营养报告；\n\n2. 采用Stage模型开发问卷编辑器，支持动态题型配置（矩阵题/滑动评分/图片选择），组件复用率达90%。\n\n系统效能：\n1. 问卷加载速度优化至1.2秒（较竞品快300%）；\n2. 营养方案匹配准确率达95%。", "responsibility": ""}, {"name": "鸿蒙FA营养商城系统（HarmonyOS FA + 跨端开发）", "beginTime": 1706716800000, "endTime": 1732982400000, "timeLabel": "2024.02 - 2024.12 (10个月)", "description": "技术架构：基于HarmonyOS FA原子化服务模型，采用ArkUI开发自适应布局，集成Deveco Studio调试工具链，实现手机/平板双端自适应；通过UniApp插件机制对接HarmonyOS原生权限管理（如相机、地理位置、健康数据授权）。\n\n核心职责：\n1.主导鸿蒙FA模块开发，实现「一键唤起鸿蒙服务卡片」功能，通过Intent参数化路由打通商城与问卷系统；\n\n2.设计分布式数据同步方案，利用HarmonyOS分布式数据库（RelationalStore）实现跨设备购物车状态实时同步；\n\n3.开发鸿蒙调试日志分析工具，基于HiLogKit实现运行时异常监控，定位手势冲突问题（如多指触控与侧边返回事件竞争），优化响应延迟至50ms以内。\n\n创新点：\n1.首创「FA+小程序」混合开发模式，通过Native API封装解决鸿蒙与微信支付SDK兼容性问题；\n2.采用HiAI Engine加速商品推荐模型推理，实现千人千面商品展示（响应时间≤800ms）。\n\n业绩：\n1.完成华为应用市场首发上线；\n2.商城核心页面FPS稳定60帧，启动耗时优化35%。", "responsibility": ""}, {"name": "智慧营养大数据埋点系统（HarmonyOS元服务 + 数据分析）", "beginTime": 1706716800000, "endTime": 1732982400000, "timeLabel": "2024.02 - 2024.12 (10个月)", "description": "技术方案：基于HarmonyOS元服务框架构建端侧埋点SDK，通过HiChain实现数据加密上报；结合华为云Data Lake构建用户行为漏斗模型，实时分析界面停留时长、点击热区等20+维度指标。\n核心突破：\n\n1.设计「事件优先级队列」机制，解决鸿蒙FA应用与埋点SDK的资源抢占问题，数据丢失率降至0.2%以下；\n\n2.开发可视化埋点配置平台，支持动态更新埋点策略（A/B测试覆盖率提升40%）。\n\n数据驱动成果：\n\n1. 精准识别高转化率页面模块，优化广告投放ROI至1:8.5；\n2. 通过用户行为路径分析，推动「一键复购」功能上线。", "responsibility": ""}, {"name": "外贸独立站", "beginTime": 1643644800000, "endTime": 1669824000000, "timeLabel": "2022.02 - 2022.12 (10个月)", "description": "内容:\n项目环境：linux\\php\\MSSQL\n工作角色：前端工程师\n工作内容：\n 1. 针对美国、英国、德国、法国、加拿大、日本、意大利、西班牙、波兰等多个核心市场，进行了精准而独特的风格设计，打造出\n各具特色的独立电商网站，显著提升用户体验和品牌形象。\n2. 深入分析各目标市场的文化差异和用户需求，确保每个站点都能与当地消费者产生深度共鸣，从而增强用户粘性和转化率。\n3. 高效参与 CI/CD 流程的搭建，确保代码提交、测试、部署等流程自动化，大幅提升团队研发效率。\n4. 在 GitLab 平台上，主导研发和生产两套解决方案的搭建，为需求管理提供了强大的创新支持，确保项目快速迭代和高质量交付。\n\n业绩:\n1. wordpress 插件研发及在项目初期，全程参与了大部分站点的功能设计和实现，包括但不限于主体定制、优惠券发放、用户订阅、客服交互等核心功能，确保项目从概念到落地的完美呈现。\n2. 成功实现领星 ERP 系统的对接，实现价格和库存数据的实时同步，以及订单数据的无缝传输，确保了企业运营的精准与高效。\n3.深度参与邮件订阅系统的开发与优化，帮助企业建立起强大的营销体系，实现精准触达目标客户，有效提升客户忠诚度和复购率。\n4. 参与企业 AI 客服前端可行性开发试验，实现内网TTS 交流工具接入本地AI模型。\n5. 通过内部制作插件抓取竞品数据给到运营平台及时做竞争态势调整。", "responsibility": ""}, {"name": "中集集团-堆场相关边缘项目", "beginTime": 1612108800000, "endTime": 1635696000000, "timeLabel": "2021.02 - 2021.11 (9个月)", "description": "内容:\n项目目标：数字化同步采集冷箱温湿度及地理位置管控系统\n项目环境：Linux \\ nginx \\ mssql \\ java spring\n工作角色：前端工程师\n工作内容：\n1. 引用 谷歌地图+腾讯地图+高德地图实现全球历史轨迹可视化，自定义 gps 围场警告范围。\n2. 使用 Websocket 实时数据通讯，实现对集装箱的数据显示和交互。\n3. 定制时间插件控制，对于堆场的温湿度以及产品是否在运输中和空闲可装配状态进行第三方可控上下架处理。\n4. 通过标签或集装箱搜索 集装箱，并添加和解绑 并 实现数字化采集及可视化、数据查询。\n5. 通过 UUID 进行分享和限制7天分享可用，再分享无效。\n业绩:\n1. 设备信息采集对堆场进行有效预警和客户可以实际知晓产品货物相关状态和具体位置。\n2. CIMC 监控平台系统 前端相关开发。\n3. 冷箱卫士小程序开发，数字化采集前馈网络数据展示及冷箱事件行为管控。\n4. 堆场数字孪生前期项目unity3d和threejs预研。", "responsibility": ""}, {"name": "POS及小程序点单、收银、会员系统", "beginTime": 1564588800000, "endTime": 1609430400000, "timeLabel": "2019.08 - 2021.01 (1年 5个月)", "description": "内容:\n项目环境：IIS 开发语言：.NET CORE 3.0 C# 数据库： MSSQL\n前端框架： QUASER 、Element 基于 VUE, WEBPACK 原生 ES 6开发\n职责角色：HTML 5开发工程师 - 工程部\n项目目标：实现公众号、小程序前端点餐功能和后端 POS 收银、POS 点单功能管理，支持1000+人在线点单。\n工作内容：\n1. 前端界面开发和交互\n2. 自定义前端组件开发如：触摸键盘、菜品多级分类快速筛选\n3. 会员营销系统前端界面开发和交互\n4. 负责公共组件的 WEB 端异形屏幕适配，优化\n业绩:\n 1. 小程序扫码点单\n2. 收银系统前端开发和适配\n3. 点单系统前端开发和适配\n4. 会员系统和小程序会员 前端开发和适配\n5. 咨客系统界面开发和适配", "responsibility": ""}, {"name": "消费类电子-宝宝故事机方案", "beginTime": 1485878400000, "endTime": 1548950400000, "timeLabel": "2017.02 - 2019.02 (2年)", "description": "内容:\n 2017.02-2019.02\n公司是一家提供智能消费类电子方案的企业，研发了一款可以和父母语音通话的宝宝故事机产品，既能解决儿童学习问题也能随时\n保持和父母的沟通 加深亲子关系。\n项目环境：Windows IIS 和.NETframework 及 MSSQL\n工作角色：前端工程师\n项目目标：研发实现任何类似儿童消费类电子整套物联网解决方案\n工作内容：\n1. 负责前端技术微信 AIRKISS 实现 WIFI 配网、声波配网和蓝牙配网\n2. 开发适合宝宝使用习惯的操作界面，针对第三方企业对小程序将那些界面定制化开发\n3. 完成设备绑定及语音对聊及各种云端资源整合\n4. 针对购买解决方案的企业提供前端到后端的软件等定制化服务\n业绩:\n1. 研发内部企业 BOM 管理系统，帮助企业降本增效\n2. 实现 EXCEL 在线批量导入硬件设备元器件方便快速核算成本，并且针对芯片烧录进行数据统计\n3.参与落地 宝宝故事机方案、儿童蓝牙安全座椅方案、点读笔物联网方案前端相关工作。", "responsibility": ""}, {"name": "物联网果果飞船", "beginTime": 1469980800000, "endTime": 1512057600000, "timeLabel": "2016.08 - 2017.12 (1年 4个月)", "description": "内容:\n项目环境：windows 服务器 IIS 开发语言：ASP.NET C# 数据库： MSSQL\n职责角色：物联网开发工程师 工程部- 负责H5开发微信公众号，原生 ES 6小程序产品前端开发实现, 内部应用管理软件开发。- 通过H5开发及指令编码封装对接 实现移动设备 WIFI 联网、蓝牙联网、声波配网等技术，\n并实现对设备进行控制和云资源协调共享。\n儿童产品符合儿童的品味，让用户有良好的产品交互使用体验.\n业绩:\n1. 落地实现简单的界面操控物联网设备\n2. 落地实现了物联网设备从协议到网络测试等全流程硬件设计和出样及生产制造\n3. 全流程参与 从模型、选材、控制板、网络信号测试、指令集、生产打样", "responsibility": ""}, {"name": "东莞嘉荣喜伴啦啦网", "beginTime": 1380556800000, "endTime": 1462032000000, "timeLabel": "2013.10 - 2016.05 (2年 7个月)", "description": "内容:\n项目环境：Linux apache 开发语言：PHP 数据库： MySQL \\ Oracle\n工作角色：信息系统主管 信息部\n工作内容：\n1. 搭建企业本地网上零售系统，通过对 Linux 进行集群与分布式、高负载运维和相关信息系统项目管理及第三方开发商对接验收，协商跟进开发。\n2. 使用 PHP 编程语言对电商网站进行二次开发，前端多页应用开发 JQuery, DIV \\HTML \\CSS 和 AJAX等 及后端 PHP 代码的接口授权调整，数据库 读写分离及 ERP 对接。\n3. 全程参与并 信息系统项目管理 需求\\目标\\计划\\过程管理, 实施的系统有电子微会员/微商城开发/卡券系统/POS 设备的支付宝及微信支付等 ,以及十多个系统的部分参与招标及峰会.\n 4. 参与构建营销部营销系统体系，为适应用户消费行为习惯的转变从 WEB 端转向移动端，需要粉丝积累达到微营销的效果，负责该公司的微信日常活动。微信公众号配合H5进行开发达到营销活动让用户参与的目的 而开发的系列小应用，如 刮卡，抽奖，评选等\n\n业绩:\n1. 实现多服务器的负载均衡和高可用高并发处理。\n2. 实现电商在线平台购物，当年销售额突破百万大关。", "responsibility": ""}, {"name": "东莞房产网", "beginTime": 1314806400000, "endTime": 1346428800000, "timeLabel": "2011.09 - 2012.09 (1年)", "description": "内容:\n项目环境：WINDOWS 服务器 IIS 开发语言：ASP 数据库： MSSQL\n工作角色：项目经理 - 软件中心\n工作内容：竞品分析、门户网站开发 ,角色分析,流程分析, 绘制产品原型,逻辑思维导图,存粹的 HTML及 JAVASCRIPT 代码开发实现\n及 ASP 后端开发和开发文档编写\n业绩:\n实现门户网站多系统接入 广告系统，租赁系统和楼盘展示系统在一个域名下运作。\n楼盘内容中心, 中介监管平台开发，搜索中心，广告中心 ，聊天系统和在线问答系统。\n内容中心负责搜集各种楼盘信息，搜索中心用于给用户便利的搜索交互，广告中心用于部\n署互联网平台广告矩阵，实现广告与外网交互 。\n\n实现了三项收入：\n1. 广告收入 -首页全屏广告 配合房产商做活动促销，引入大量房企的营销经费\n2.租赁中介收入 - 类似于微信公众号需要年检费用，引入大量中介开户和年检按年收费\n3.私域活动收入 - 针对购买房子的意向用户进行拉群对家居产品进行促销", "responsibility": ""}], "languageSkills": [{"name": "汉语", "readWriteSkill": "精通", "hearSpeakSkill": "精通"}, {"name": "英语", "readWriteSkill": "良好", "hearSpeakSkill": "良好"}], "certificates": [{"name": "鸿蒙开发高级理论认证"}, {"name": "鸿蒙初级认证"}], "purposes": [{"industryLabel": "不限行业", "jobTypeLabel": "PHP", "jobNatureLabel": "全职", "location": "广东", "salaryLabel": "3.5万-7万/月"}, {"industryLabel": "不限行业", "jobTypeLabel": "前端开发", "jobNatureLabel": "全职", "location": "成都", "salaryLabel": "1万-2万/月"}, {"industryLabel": "不限行业", "jobTypeLabel": "架构师", "jobNatureLabel": "全职", "location": "成都", "salaryLabel": "24万-25万/月"}]}, "id": 2}'
    api_call(query, AppConversationID, userId)


# 调用主函数
if __name__ == "__main__":
    main()
