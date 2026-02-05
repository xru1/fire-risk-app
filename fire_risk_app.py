import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

# 设置页面配置
st.set_page_config(
    page_title="老旧楼宇火灾风险检测与整改策略分析系统",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #111827;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #374151;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }
    .metric-card:hover {
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .risk-high { color: #EF4444; font-weight: 700; }
    .risk-medium { color: #F97316; font-weight: 600; }
    .risk-low { color: #10B981; font-weight: 600; }
    .stButton>button {
        background-color: #EF4444;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #DC2626;
    }
</style>
""", unsafe_allow_html=True)

# 定义风险评估模型类
class FireRiskAssessmentModel:
    def __init__(self):
        # 核心变量权重
        self.core_weights = {
            '建筑老化风险': 0.47,
            '消防能力缺失': 0.29,
            '电气线路隐患': 0.24
        }
        
        # 子指标权重和评分标准
        self.indicators = {
            '建筑老化风险': {
                '楼龄': {
                    'weight': 0.3,
                    'criteria': {
                        '≥40年': 5,
                        '30-39年': 4,
                        '20-29年': 3,
                        '10-19年': 2,
                        '1-10年': 1,
                        '1年内新建': 0
                    }
                },
                '结构类型与材料': {
                    'weight': 0.35,
                    'criteria': {
                        '木质/易燃外搭结构': 5,
                        '砖混+易燃建材': 4,
                        '砖混结构': 3,
                        '钢混+部分老化': 2,
                        '钢混结构良好': 1,
                        '现代防火结构': 0
                    }
                },
                '使用性质与密度风险': {
                    'weight': 0.15,
                    'criteria': {
                        '"下店上宅"+群租+培训机构': 5,
                        '两种高风险业态': 4,
                        '一种高风险业态': 3,
                        '普通住宅但拥挤': 2,
                        '正常居住密度': 1,
                        '低密度规范使用': 0
                    }
                },
                '住户高龄化程度': {
                    'weight': 0.2,
                    'criteria': {
                        '（60岁及以上人口占比）>50%': 5,
                        '40-50%': 4,
                        '30-40%': 3,
                        '20-30%': 2,
                        '10-20%': 1,
                        '<10%': 0
                    }
                }
            },
            '消防能力缺失': {
                '火灾报警系统有效性': {
                    'weight': 0.25,
                    'criteria': {
                        '无报警系统或完全失效': 5,
                        '主要区域失效': 4,
                        '部分探测器故障': 3,
                        '系统老旧响应慢': 2,
                        '小范围问题': 1,
                        '全覆盖且正常': 0
                    }
                },
                '消防通道与疏散通道状况': {
                    'weight': 0.4,
                    'criteria': {
                        '无消防通道+疏散通道被占': 5,
                        '通道严重狭窄或被占（≥40%）': 4,
                        '部分通道不畅（10%-40%）': 3,
                        '基本通畅但有隐患（不畅通道＜10%）': 2,
                        '通畅但标识不清': 1,
                        '完全规范': 0
                    }
                },
                '消防设备完好率': {
                    'weight': 0.35,
                    'criteria': {
                        '系统瘫痪/无水/严重锈蚀': 5,
                        '多设备失效': 4,
                        '部分设备故障': 3,
                        '设备老旧但可用': 2,
                        '轻微问题': 1,
                        '全部完好有效': 0
                    }
                }
            },
            '电气线路隐患': {
                '电气线路老化程度': {
                    'weight': 0.6,
                    'criteria': {
                        '普遍老化+绝缘破损': 5,
                        '多处线路老化': 4,
                        '部分线路老化': 3,
                        '线路轻微老化': 2,
                        '基本完好但超期': 1,
                        '新装/合规线路': 0
                    }
                },
                '违规用电情况': {
                    'weight': 0.4,
                    'criteria': {
                        '普遍飞线充电（≥3处）或强电私拉乱接': 5,
                        '存在有1-2处明显的飞线充电/插排串联、过载': 4,
                        '存在临时飞线/弱电乱接': 3,
                        '无私拉乱接现象，但存在充电设施不足/个别插排过载': 2,
                        '住户用电基本安全，仅存在个别非关键性问题': 1,
                        '完全符合规范': 0
                    }
                }
            }
        }
        
        # 风险等级划分标准
        self.risk_levels = {
            '极高风险': (4.0, 5.0),
            '高风险': (3.0, 3.9),
            '中风险': (2.0, 2.9),
            '低风险': (1.0, 1.9),
            '极低风险': (0, 0.9)
        }
        
        # 整改建议
        self.recommendations = {
            '极高风险': [
                '立即响应整改：24小时内下达《重大隐患整改通知书》',
                '采取强制措施：根据隐患性质，立即采取局部停用、清空住户、断电等临时管控措施',
                '限期挂牌督办：由街道/乡镇政府挂牌，主要责任人牵头，限期（≤15天）完成整改'
            ],
            '高风险': [
                '限期整改：7日内下达整改通知，明确整改责任人、措施和时限（通常≤30天）'
            ],
            '中风险': [
                '常规计划整改：15日内制定书面整改计划，明确时间表、路线图，整改周期不宜超过90天',
                '定期检查：纳入月度重点检查清单，每月核查整改进展',
                '采取宣传警示：在楼栋公示风险点，对相关住户进行针对性安全提醒'
            ],
            '低风险': [
                '日常维护：由物业或产权单位按常规维保计划进行维护，确保现状不恶化',
                '常规监测：纳入季度巡查范围，每季度检查一次',
                '教育预防：通过社区宣传栏、微信群等进行常规安全知识普及'
            ],
            '极低风险': [
                '继续保持：保持现有管理水平和设备状态，可视为安全标杆'
            ]
        }

    def calculate_score(self, indicator, value):
        """计算单个指标的评分"""
        for core_var in self.indicators:
            if indicator in self.indicators[core_var]:
                criteria = self.indicators[core_var][indicator]['criteria']
                if value in criteria:
                    return criteria[value]
        return 0

    def calculate_risk_score(self, building_data):
        """计算楼宇的综合风险评分"""
        scores = {}
        core_scores = {}
        
        # 计算每个核心变量的得分
        for core_var, indicators_dict in self.indicators.items():
            var_score = 0
            var_weight_sum = 0
            
            for indicator, config in indicators_dict.items():
                if indicator in building_data:
                    weight = config['weight']
                    score = self.calculate_score(indicator, building_data[indicator])
                    var_score += weight * score
                    var_weight_sum += weight
                    scores[indicator] = score
            
            # 归一化处理
            if var_weight_sum > 0:
                core_scores[core_var] = var_score / var_weight_sum * 5  # 归一化到0-5分
        
        # 计算综合风险总分
        total_score = 0
        for core_var, score in core_scores.items():
            total_score += self.core_weights[core_var] * score
        
        return total_score, scores, core_scores

    def get_risk_level(self, score):
        """根据评分获取风险等级"""
        for level, (min_score, max_score) in self.risk_levels.items():
            if min_score <= score <= max_score:
                return level
        return '未知风险'

    def get_recommendations(self, risk_level):
        """获取对应风险等级的整改建议"""
        return self.recommendations.get(risk_level, [])

    def estimate_improvement(self, building_data, improvement_level=2):
        """估算整改后的风险评分"""
        improved_data = building_data.copy()
        # 假设整改后每个指标降低2个等级
        for indicator in improved_data:
            for core_var in self.indicators:
                if indicator in self.indicators[core_var]:
                    current_value = improved_data[indicator]
                    criteria = list(self.indicators[core_var][indicator]['criteria'].keys())
                    if current_value in criteria:
                        current_index = criteria.index(current_value)
                        new_index = max(0, current_index - improvement_level)
                        improved_data[indicator] = criteria[new_index]
                    break
        
        improved_score, _, _ = self.calculate_risk_score(improved_data)
        return improved_score

# 初始化模型
model = FireRiskAssessmentModel()

# 应用标题
st.markdown('<h1 class="main-header">🔥 老旧楼宇火灾风险检测与整改策略分析系统</h1>', unsafe_allow_html=True)

# 侧边栏 - 楼宇信息输入
with st.sidebar:
    st.markdown('<h3 class="sub-header">📋 楼宇信息输入</h3>', unsafe_allow_html=True)
    
    building_name = st.text_input("楼宇名称", "模拟楼宇1")
    
    # 建筑老化风险指标
    st.markdown("**建筑老化风险指标**")
    building_age = st.selectbox(
        "楼龄",
        list(model.indicators['建筑老化风险']['楼龄']['criteria'].keys())
    )
    
    structure_type = st.selectbox(
        "结构类型与材料",
        list(model.indicators['建筑老化风险']['结构类型与材料']['criteria'].keys())
    )
    
    usage_density = st.selectbox(
        "使用性质与密度风险",
        list(model.indicators['建筑老化风险']['使用性质与密度风险']['criteria'].keys())
    )
    
    elderly_ratio = st.selectbox(
        "住户高龄化程度",
        list(model.indicators['建筑老化风险']['住户高龄化程度']['criteria'].keys())
    )
    
    # 消防能力缺失指标
    st.markdown("**消防能力缺失指标**")
    alarm_system = st.selectbox(
        "火灾报警系统有效性",
        list(model.indicators['消防能力缺失']['火灾报警系统有效性']['criteria'].keys())
    )
    
    evacuation_passage = st.selectbox(
        "消防通道与疏散通道状况",
        list(model.indicators['消防能力缺失']['消防通道与疏散通道状况']['criteria'].keys())
    )
    
    fire_equipment = st.selectbox(
        "消防设备完好率",
        list(model.indicators['消防能力缺失']['消防设备完好率']['criteria'].keys())
    )
    
    # 电气线路隐患指标
    st.markdown("**电气线路隐患指标**")
    wiring_condition = st.selectbox(
        "电气线路老化程度",
        list(model.indicators['电气线路隐患']['电气线路老化程度']['criteria'].keys())
    )
    
    electricity_violation = st.selectbox(
        "违规用电情况",
        list(model.indicators['电气线路隐患']['违规用电情况']['criteria'].keys())
    )
    
    # 预算设置
    st.markdown("**预算设置**")
    available_budget = st.number_input("可用预算（万元）", min_value=0.0, value=30.5, step=0.1)
    
    calculate_button = st.button("开始风险评估")

# 主内容区域
if calculate_button:
    # 收集楼宇数据
    building_data = {
        '楼龄': building_age,
        '结构类型与材料': structure_type,
        '使用性质与密度风险': usage_density,
        '住户高龄化程度': elderly_ratio,
        '火灾报警系统有效性': alarm_system,
        '消防通道与疏散通道状况': evacuation_passage,
        '消防设备完好率': fire_equipment,
        '电气线路老化程度': wiring_condition,
        '违规用电情况': electricity_violation
    }
    
    # 计算风险评分
    total_score, indicator_scores, core_scores = model.calculate_risk_score(building_data)
    risk_level = model.get_risk_level(total_score)
    
    # 估算整改后评分
    improved_score = model.estimate_improvement(building_data)
    risk_reduction = total_score - improved_score
    
    # 估算整改成本（基于风险等级和楼宇情况）
    # 这里使用简化的成本估算模型，实际情况应更复杂
    cost_multiplier = {
        '极高风险': 14,
        '高风险': 10,
        '中风险': 6,
        '低风险': 4,
        '极低风险': 2
    }
    estimated_cost = cost_multiplier.get(risk_level, 10)  # 万元
    
    # 单位成本效益
    cost_benefit = risk_reduction / estimated_cost if estimated_cost > 0 else 0
    
    # 创建三列布局
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="综合风险总分",
            value=f"{total_score:.2f}",
            delta=f"{risk_level}"
        )
        
        # 根据风险等级设置颜色
        if risk_level == '极高风险':
            st.markdown('<p class="risk-high">🔥 极高风险 - 需要立即整改</p>', unsafe_allow_html=True)
        elif risk_level == '高风险':
            st.markdown('<p class="risk-high">⚠️ 高风险 - 需要限期整改</p>', unsafe_allow_html=True)
        elif risk_level == '中风险':
            st.markdown('<p class="risk-medium">⚠️ 中风险 - 建议计划整改</p>', unsafe_allow_html=True)
        elif risk_level in ['低风险', '极低风险']:
            st.markdown('<p class="risk-low">✓ 低风险 - 保持监测</p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="风险降低潜力",
            value=f"{risk_reduction:.2f}",
            delta=f"整改后预估: {improved_score:.2f}"
        )
        st.progress(min(risk_reduction / 5, 1.0))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(
            label="估算整改成本",
            value=f"{estimated_cost:.1f} 万元",
            delta=f"单位效益: {cost_benefit:.3f}/万元"
        )
        
        if estimated_cost <= available_budget:
            st.success(f"✅ 在预算范围内 (可用预算: {available_budget}万元)")
        else:
            st.warning(f"⚠️ 超出预算 {estimated_cost - available_budget:.1f}万元")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 风险详细分析
    st.markdown('<h3 class="sub-header">📊 风险详细分析</h3>', unsafe_allow_html=True)
    
    # 创建两列用于图表
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # 核心风险变量雷达图
        fig1 = go.Figure()
        
        categories = list(core_scores.keys())
        values = list(core_scores.values())
        
        fig1.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='风险评分',
            line_color='#EF4444'
        ))
        
        fig1.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )),
            showlegend=False,
            title="核心风险变量评分雷达图",
            height=400
        )
        
        st.plotly_chart(fig1, use_container_width=True)
    
    with col_chart2:
        # 指标评分条形图
        fig2 = go.Figure()
        
        indicators = list(indicator_scores.keys())
        scores = list(indicator_scores.values())
        
        # 根据分数设置颜色
        colors = ['#EF4444' if s >= 4 else '#F97316' if s >= 2 else '#10B981' for s in scores]
        
        fig2.add_trace(go.Bar(
            x=indicators,
            y=scores,
            marker_color=colors,
            text=[f"{s:.1f}" for s in scores],
            textposition='auto',
        ))
        
        fig2.update_layout(
            title="各指标风险评分",
            xaxis_tickangle=-45,
            yaxis_range=[0, 5],
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    # 整改策略建议
    st.markdown('<h3 class="sub-header">🎯 整改策略建议</h3>', unsafe_allow_html=True)
    
    recommendations = model.get_recommendations(risk_level)
    
    recommendation_card = '<div class="metric-card">'
    for i, rec in enumerate(recommendations, 1):
        recommendation_card += f'<p><strong>{i}. {rec}</strong></p>'
    recommendation_card += '</div>'
    
    st.markdown(recommendation_card, unsafe_allow_html=True)
    
    # 优先级排序（如果是多楼宇评估）
    st.markdown('<h3 class="sub-header">📈 成本效益分析</h3>', unsafe_allow_html=True)
    
    # 创建成本效益分析数据
    analysis_data = {
        '指标': ['综合风险评分', '风险降低值', '估算成本', '单位成本效益'],
        '数值': [total_score, risk_reduction, estimated_cost, cost_benefit],
        '单位': ['分', '分', '万元', '分/万元']
    }
    
    df_analysis = pd.DataFrame(analysis_data)
    
    col_analysis1, col_analysis2 = st.columns(2)
    
    with col_analysis1:
        st.dataframe(df_analysis, use_container_width=True, hide_index=True)
    
    with col_analysis2:
        # 成本效益散点图示意
        fig3 = go.Figure()
        
        # 这里可以扩展为多楼宇比较
        fig3.add_trace(go.Scatter(
            x=[estimated_cost],
            y=[risk_reduction],
            mode='markers+text',
            marker=dict(size=20, color='#EF4444'),
            text=[building_name],
            textposition="top center",
            name='当前楼宇'
        ))
        
        # 添加参考线
        max_cost = max(available_budget, estimated_cost) * 1.2
        fig3.add_shape(
            type="line",
            x0=0, y0=0,
            x1=max_cost, y1=max_cost * 0.15,  # 假设每万元降低0.15分
            line=dict(color="#9CA3AF", width=2, dash="dash"),
        )
        
        fig3.update_layout(
            title="成本效益分析",
            xaxis_title="整改成本 (万元)",
            yaxis_title="风险降低值 (分)",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    # 详细指标解释
    with st.expander("📖 查看详细指标解释和评分标准"):
        st.markdown("""
        ### 评分标准解释
        
        **5分（极高风险）**：对应案例中直接导致重大伤亡或严重财产损失的隐患状态。
        
        **3-4分（中高风险）**：对应案例中显著加重火情或影响疏散的隐患状态。
        
        **1-2分（低风险）**：存在隐患但尚未在案例中直接引发严重后果，或引发后果较轻。
        
        **0分（无风险）**：完全符合现行消防及建筑规范的最佳实践状态。
        
        ### 权重说明
        
        系统采用三级权重体系：
        1. **核心变量权重**：建筑老化风险(47%)、消防能力缺失(29%)、电气线路隐患(24%)
        2. **子指标权重**：每个核心变量下的具体指标权重
        3. **综合计算**：加权求和得到最终风险评分
        """)
        
        # 显示权重表格
        weights_data = []
        for core_var, weight in model.core_weights.items():
            weights_data.append({
                '层级': '核心变量',
                '名称': core_var,
                '权重': f"{weight*100:.1f}%"
            })
            
            for indicator, config in model.indicators[core_var].items():
                weights_data.append({
                    '层级': '子指标',
                    '名称': f"  └─ {indicator}",
                    '权重': f"{config['weight']*100:.1f}%"
                })
        
        st.table(pd.DataFrame(weights_data))
    
    # 生成报告按钮
    if st.button("📄 生成详细评估报告"):
        report_data = {
            '楼宇名称': building_name,
            '评估时间': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            '综合风险评分': total_score,
            '风险等级': risk_level,
            '整改后预估评分': improved_score,
            '风险降低值': risk_reduction,
            '估算整改成本': f"{estimated_cost}万元",
            '单位成本效益': cost_benefit,
            '各项指标评分': indicator_scores,
            '核心变量评分': core_scores
        }
        
        # 转换为JSON格式
        report_json = json.dumps(report_data, ensure_ascii=False, indent=2)
        
        # 提供下载
        st.download_button(
            label="下载评估报告 (JSON)",
            data=report_json,
            file_name=f"火灾风险评估报告_{building_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

else:
    # 默认显示界面 - 应用介绍和功能说明
    st.markdown("""
    <div class="metric-card">
    <h3>欢迎使用老旧楼宇火灾风险检测与整改策略分析系统</h3>
    
    <p>本系统基于科学的风险评估模型，帮助您：</p>
    
    <ul>
    <li><strong>量化评估</strong>：将楼宇火灾风险转化为可计算的数值指标</li>
    <li><strong>智能分析</strong>：自动识别高风险环节和薄弱点</li>
    <li><strong>策略优化</strong>：在有限预算下提供最优整改方案</li>
    <li><strong>可视化展示</strong>：直观呈现风险分布和改进效果</li>
    </ul>
    
    <h4>使用方法：</h4>
    <ol>
    <li>在左侧边栏输入楼宇的各项指标信息</li>
    <li>设置可用预算（可选）</li>
    <li>点击"开始风险评估"按钮</li>
    <li>查看详细的风险分析和整改建议</li>
    </ol>
    
    <p><strong>系统特点：</strong></p>
    <ul>
    <li>🎯 <strong>科学量化</strong>：基于实际火灾案例分析构建评分体系</li>
    <li>⚡ <strong>实时计算</strong>：输入即得结果，快速响应决策需求</li>
    <li>📊 <strong>数据驱动</strong>：可视化展示，支持多维度分析</li>
    <li>💰 <strong>成本优化</strong>：考虑预算约束，最大化安全效益</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 显示示例数据
    with st.expander("👀 查看示例楼宇评估"):
        st.info("以下为系统内置的模拟楼宇数据示例，您可以在侧边栏修改这些值进行自定义评估")
        
        example_cols = st.columns(4)
        
        with example_cols[0]:
            st.markdown("""
            **模拟楼宇1**
            - 楼龄: 42年
            - 风险总分: 2.91
            - 等级: 高风险
            """)
        
        with example_cols[1]:
            st.markdown("""
            **模拟楼宇6**
            - 楼龄: 44年
            - 风险总分: 3.58
            - 等级: 极高风险
            """)
        
        with example_cols[2]:
            st.markdown("""
            **模拟楼宇4**
            - 楼龄: 5年
            - 风险总分: 0.52
            - 等级: 低风险
            """)
        
        with example_cols[3]:
            st.markdown("""
            **模拟楼宇8**
            - 楼龄: 21年
            - 风险总分: 1.96
            - 等级: 中风险
            """)

# 页脚信息
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #9CA3AF; font-size: 0.9rem;">
<p>🔥 老旧楼宇火灾风险检测与整改策略分析系统 | 基于科学评估模型与优化算法</p>
<p>⚠️ 本系统评估结果仅供参考，实际整改需结合现场具体情况和专业意见</p>
</div>
""", unsafe_allow_html=True)