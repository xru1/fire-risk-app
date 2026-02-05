import streamlit as st

# ==================== 页面配置 ====================
st.set_page_config(
    page_title='老旧楼宇火灾风险检测系统',
    page_icon='🔥',
    layout='wide'
)

# ==================== 完整的风险评估模型 ====================
def calculate_comprehensive_risk(building_data):
    """
    完整的风险评估模型
    基于提供的权重和评分标准计算综合风险分
    building_data: 字典，包含所有9项指标的选择值
    """
    
    # 1. 定义评分标准字典（0-5分）
    scoring_criteria = {
        # 建筑老化风险
        '楼龄': {
            '≥40年': 5, '30-39年': 4, '20-29年': 3, 
            '10-19年': 2, '1-10年': 1, '1年内新建': 0
        },
        '结构类型与材料': {
            '木质/易燃外搭结构': 5, '砖混+易燃建材': 4, '砖混结构': 3,
            '钢混+部分老化': 2, '钢混结构良好': 1, '现代防火结构': 0
        },
        '使用性质与密度风险': {
            '"下店上宅"+群租+培训机构': 5, '两种高风险业态': 4,
            '一种高风险业态': 3, '普通住宅但拥挤': 2,
            '正常居住密度': 1, '低密度规范使用': 0
        },
        '住户高龄化程度': {
            '（60岁及以上人口占比）>50%': 5, '40-50%': 4,
            '30-40%': 3, '20-30%': 2, '10-20%': 1, '<10%': 0
        },
        # 消防能力缺失
        '火灾报警系统有效性': {
            '无报警系统或完全失效': 5, '主要区域失效': 4,
            '部分探测器故障': 3, '系统老旧响应慢': 2,
            '小范围问题': 1, '全覆盖且正常': 0
        },
        '消防通道与疏散通道状况': {
            '无消防通道+疏散通道被占': 5, '通道严重狭窄或被占（≥40%）': 4,
            '部分通道不畅（10%-40%）': 3, '基本通畅但有隐患（不畅通道＜10%）': 2,
            '通畅但标识不清': 1, '完全规范': 0
        },
        '消防设备完好率': {
            '系统瘫痪/无水/严重锈蚀': 5, '多设备失效': 4,
            '部分设备故障': 3, '设备老旧但可用': 2,
            '轻微问题': 1, '全部完好有效': 0
        },
        # 电气线路隐患
        '电气线路老化程度': {
            '普遍老化+绝缘破损': 5, '多处线路老化': 4,
            '部分线路老化': 3, '线路轻微老化': 2,
            '基本完好但超期': 1, '新装/合规线路': 0
        },
        '违规用电情况': {
            '普遍飞线充电（≥3处）或强电私拉乱接': 5,
            '存在有1-2处明显的飞线充电/插排串联、过载': 4,
            '存在临时飞线/弱电乱接': 3,
            '无私拉乱接现象，但存在充电设施不足/个别插排过载': 2,
            '住户用电基本安全，仅存在个别非关键性问题': 1,
            '完全符合规范': 0
        }
    }
    
    # 2. 计算各项得分
    indicator_scores = {}
    for indicator, value in building_data.items():
        if indicator in scoring_criteria and value in scoring_criteria[indicator]:
            indicator_scores[indicator] = scoring_criteria[indicator][value]
        else:
            indicator_scores[indicator] = 0  # 默认值
    
    # 3. 计算核心变量得分（加权平均）
    # 建筑老化风险 (权重: 0.47)
    building_aging_indicators = ['楼龄', '结构类型与材料', '使用性质与密度风险', '住户高龄化程度']
    building_aging_weights = [0.3, 0.35, 0.15, 0.2]
    building_aging_score = sum(indicator_scores[ind] * weight 
                              for ind, weight in zip(building_aging_indicators, building_aging_weights))
    
    # 消防能力缺失 (权重: 0.29)
    fire_safety_indicators = ['火灾报警系统有效性', '消防通道与疏散通道状况', '消防设备完好率']
    fire_safety_weights = [0.25, 0.4, 0.35]
    fire_safety_score = sum(indicator_scores[ind] * weight 
                           for ind, weight in zip(fire_safety_indicators, fire_safety_weights))
    
    # 电气线路隐患 (权重: 0.24)
    electrical_indicators = ['电气线路老化程度', '违规用电情况']
    electrical_weights = [0.6, 0.4]
    electrical_score = sum(indicator_scores[ind] * weight 
                          for ind, weight in zip(electrical_indicators, electrical_weights))
    
    # 4. 计算综合风险总分
    core_weights = [0.47, 0.29, 0.24]
    core_scores = [building_aging_score, fire_safety_score, electrical_score]
    
    total_score = sum(score * weight for score, weight in zip(core_scores, core_weights))
    
    # 5. 确定风险等级
    if total_score >= 4.0:
        risk_level = '极高风险'
        recommendation = '①立即响应整改 ②采取强制措施 ③限期挂牌督办'
        color = 'red'
    elif total_score >= 3.0:
        risk_level = '高风险'
        recommendation = '限期整改：7日内下达整改通知'
        color = 'orange'
    elif total_score >= 2.0:
        risk_level = '中风险'
        recommendation = '①常规计划整改 ②定期检查 ③采取宣传警示'
        color = 'yellow'
    elif total_score >= 1.0:
        risk_level = '低风险'
        recommendation = '①日常维护 ②常规监测 ③教育预防'
        color = 'green'
    else:
        risk_level = '极低风险'
        recommendation = '继续保持：保持现有管理水平和设备状态'
        color = 'blue'
    
    # 6. 估算整改成本（简化模型）
    estimated_cost = total_score * 8  # 万元
    
    return {
        'total_score': round(total_score, 2),
        'risk_level': risk_level,
        'recommendation': recommendation,
        'color': color,
        'estimated_cost': round(estimated_cost, 1),
        'indicator_scores': indicator_scores,
        'core_scores': {
            '建筑老化风险': round(building_aging_score, 2),
            '消防能力缺失': round(fire_safety_score, 2),
            '电气线路隐患': round(electrical_score, 2)
        }
    }

# ==================== 侧边栏：用户输入界面 ====================
with st.sidebar:
    st.title('📋 楼宇信息输入')
    
    building_info = {}
    
    st.subheader('🏗️ 建筑老化风险')
    building_info['楼龄'] = st.selectbox(
        '楼龄',
        ['≥40年', '30-39年', '20-29年', '10-19年', '1-10年', '1年内新建']
    )
    building_info['结构类型与材料'] = st.selectbox(
        '结构类型与材料',
        ['木质/易燃外搭结构', '砖混+易燃建材', '砖混结构', 
         '钢混+部分老化', '钢混结构良好', '现代防火结构']
    )
    building_info['使用性质与密度风险'] = st.selectbox(
        '使用性质与密度风险',
        ['"下店上宅"+群租+培训机构', '两种高风险业态', '一种高风险业态',
         '普通住宅但拥挤', '正常居住密度', '低密度规范使用']
    )
    building_info['住户高龄化程度'] = st.selectbox(
        '住户高龄化程度',
        ['（60岁及以上人口占比）>50%', '40-50%', '30-40%',
         '20-30%', '10-20%', '<10%']
    )
    
    st.subheader('🚒 消防能力缺失')
    building_info['火灾报警系统有效性'] = st.selectbox(
        '火灾报警系统有效性',
        ['无报警系统或完全失效', '主要区域失效', '部分探测器故障',
         '系统老旧响应慢', '小范围问题', '全覆盖且正常']
    )
    building_info['消防通道与疏散通道状况'] = st.selectbox(
        '消防通道与疏散通道状况',
        ['无消防通道+疏散通道被占', '通道严重狭窄或被占（≥40%）',
         '部分通道不畅（10%-40%）', '基本通畅但有隐患（不畅通道＜10%）',
         '通畅但标识不清', '完全规范']
    )
    building_info['消防设备完好率'] = st.selectbox(
        '消防设备完好率',
        ['系统瘫痪/无水/严重锈蚀', '多设备失效', '部分设备故障',
         '设备老旧但可用', '轻微问题', '全部完好有效']
    )
    
    st.subheader('⚡ 电气线路隐患')
    building_info['电气线路老化程度'] = st.selectbox(
        '电气线路老化程度',
        ['普遍老化+绝缘破损', '多处线路老化', '部分线路老化',
         '线路轻微老化', '基本完好但超期', '新装/合规线路']
    )
    building_info['违规用电情况'] = st.selectbox(
        '违规用电情况',
        ['普遍飞线充电（≥3处）或强电私拉乱接',
         '存在有1-2处明显的飞线充电/插排串联、过载',
         '存在临时飞线/弱电乱接',
         '无私拉乱接现象，但存在充电设施不足/个别插排过载',
         '住户用电基本安全，仅存在个别非关键性问题',
         '完全符合规范']
    )
    
    st.subheader('💰 预算设置')
    available_budget = st.number_input(
        '可用预算（万元）',
        min_value=0.0,
        value=30.5,
        step=1.0
    )
    
    if st.button('开始风险评估', type='primary', use_container_width=True):
        st.session_state['building_info'] = building_info
        st.session_state['available_budget'] = available_budget
        st.session_state['result'] = calculate_comprehensive_risk(building_info)
        st.session_state['assessed'] = True

# ==================== 主页面：标题和说明 ====================
st.title('🔥 老旧楼宇火灾风险检测与整改策略分析系统')
st.markdown('---')

if not st.session_state.get('assessed', False):
    # 未评估时的介绍页面
    st.info('''
    ### 🎯 系统说明
    本系统基于多指标加权评估模型，对老旧楼宇火灾风险进行科学量化分析。
    
    **评估流程：**
    1. 在左侧输入楼宇的各项指标信息
    2. 设置可用的整改预算
    3. 点击"开始风险评估"按钮
    4. 查看详细的风险分析和整改建议
    
    **三大核心风险变量：**
    - 🏗️ 建筑老化风险（权重47%）
    - 🚒 消防能力缺失（权重29%）
    - ⚡ 电气线路隐患（权重24%）
    ''')
    
    # 显示评估指标说明
    with st.expander('📖 查看详细评估指标说明', expanded=False):
        st.markdown('''
        **评分标准：**
        - **5分（极高风险）**：对应案例中直接导致重大伤亡的隐患状态
        - **3-4分（中高风险）**：对应案例中显著加重火情或影响疏散的隐患状态
        - **1-2分（低风险）**：存在隐患但尚未直接引发严重后果
        - **0分（无风险）**：完全符合现行规范的最佳实践状态
        
        **权重体系：**
        - 采用三级权重体系，确保评估科学性
        - 所有指标均基于实际火灾案例分析构建
        ''')
    
    st.markdown('---')
    st.caption('请输入楼宇信息并点击"开始风险评估"按钮')

else:
    # ==================== 结果显示页面 ====================
    result = st.session_state['result']
    building_info = st.session_state['building_info']
    
    # 1. 综合风险评估结果（三列布局）
    st.subheader('📊 综合风险评估结果')
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label='综合风险总分',
            value=f"{result['total_score']}/5.0",
            delta=result['risk_level'],
            delta_color='inverse'
        )
    
    with col2:
        # 根据风险等级显示不同的表情和颜色
        risk_emoji = {'极高风险': '🔴', '高风险': '🟠', '中风险': '🟡', '低风险': '🟢', '极低风险': '🔵'}
        st.metric(
            label='风险等级',
            value=f"{risk_emoji.get(result['risk_level'], '⚪')} {result['risk_level']}"
        )
    
    with col3:
        cost_diff = result['estimated_cost'] - st.session_state['available_budget']
        st.metric(
            label='估算整改成本',
            value=f"{result['estimated_cost']} 万元",
            delta=f"{'超支' if cost_diff > 0 else '充足'} {abs(cost_diff):.1f}万元",
            delta_color='inverse' if cost_diff > 0 else 'normal'
        )
    
    # 2. 核心风险变量分析
    st.subheader('🎯 核心风险变量分析')
    core_cols = st.columns(3)
    core_vars = list(result['core_scores'].keys())
    core_colors = ['#FF6B6B', '#FFA726', '#42A5F5']  # 红，橙，蓝
    
    for idx, (col, var) in enumerate(zip(core_cols, core_vars)):
        with col:
            score = result['core_scores'][var]
            # 创建简单的进度条可视化
            progress = min(score / 5.0, 1.0)
            col.progress(progress, text=f'{var}: {score}/5.0')
    
    # 3. 详细指标评分（可展开）
    with st.expander('📋 查看详细指标评分', expanded=True):
        # 按三大风险变量分组显示
        indicator_groups = {
            '建筑老化风险': ['楼龄', '结构类型与材料', '使用性质与密度风险', '住户高龄化程度'],
            '消防能力缺失': ['火灾报警系统有效性', '消防通道与疏散通道状况', '消防设备完好率'],
            '电气线路隐患': ['电气线路老化程度', '违规用电情况']
        }
        
        for group_name, indicators in indicator_groups.items():
            st.write(f'**{group_name}**')
            group_cols = st.columns(len(indicators))
            for col, indicator in zip(group_cols, indicators):
                with col:
                    score = result['indicator_scores'][indicator]
                    selected_value = building_info[indicator]
                    # 显示评分和选择值
                    st.markdown(f'''
                    **{indicator}**  
                    📊 评分: `{score}/5`  
                    📝 状态: {selected_value[:15]}...
                    ''')
            st.write('---')
    
    # 4. 整改策略建议
    st.subheader('🛠️ 整改策略建议')
    
    # 根据风险等级显示不同颜色的提示框
    if result['risk_level'] == '极高风险':
        st.error(f"**立即行动建议：** {result['recommendation']}")
    elif result['risk_level'] == '高风险':
        st.warning(f"**限期整改建议：** {result['recommendation']}")
    elif result['risk_level'] == '中风险':
        st.info(f"**计划整改建议：** {result['recommendation']}")
    else:
        st.success(f"**维护建议：** {result['recommendation']}")
    
    # 预算匹配建议
    st.info(f'''
    **💰 预算匹配分析：**
    - 估算所需成本：**{result['estimated_cost']}万元**
    - 您设置的预算：**{st.session_state['available_budget']}万元**
    - 预算状态：**{'充足 ✅' if result['estimated_cost'] <= st.session_state['available_budget'] else '不足 ⚠️'}**
    
    **建议：** {'预算充足，可按计划推进整改。' if result['estimated_cost'] <= st.session_state['available_budget'] else '建议申请额外预算或优先整改高风险项目。'}
    ''')
    
    # 5. 简单数据可视化（使用Streamlit原生图表）
    st.subheader('📈 风险评分可视化')
    
    # 创建核心变量分数柱状图数据
    core_data = {
        '核心变量': list(result['core_scores'].keys()),
        '风险评分': list(result['core_scores'].values())
    }
    
    # 使用Streamlit原生柱状图
    st.bar_chart(
        data=core_data,
        x='核心变量',
        y='风险评分',
        color='#EF4444'  # 消防红色
    )
    
    # 6. 底部操作按钮
    st.markdown('---')
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button('🔄 重新评估', use_container_width=True):
            st.session_state.clear()
            st.rerun()

# ==================== 页脚信息 ====================
st.markdown('---')
st.caption('''
🔥 老旧楼宇火灾风险检测系统 | 基于多指标加权评估模型 | 版本: 完整功能版 v1.0  
⚠️ 评估结果仅供参考，实际整改需结合现场专业意见
''')
