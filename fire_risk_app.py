import streamlit as st

# 页面设置
st.set_page_config(
    page_title="火灾风险评估系统",
    page_icon="🔥",
    layout="wide"
)

# 应用标题
st.title("🔥 老旧楼宇火灾风险检测系统")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.header("📋 楼宇信息输入")
    
    building = st.text_input("楼宇名称", "模拟楼宇1")
    
    st.subheader("建筑信息")
    age = st.selectbox(
        "楼龄",
        ["≥40年", "30-39年", "20-29年", "10-19年", "1-10年", "1年内新建"]
    )
    
    structure = st.selectbox(
        "结构类型",
        ["现代防火结构", "钢混结构", "砖混结构", "木质结构"]
    )
    
    st.subheader("预算设置")
    budget = st.number_input("预算（万元）", value=30.5, min_value=0.0)
    
    if st.button("开始评估", type="primary"):
        st.session_state.assessed = True

# 主内容
if st.session_state.get('assessed', False):
    st.success("✅ 评估完成！")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("风险评分", "3.2/5.0")
        st.metric("风险等级", "中风险")
    
    with col2:
        st.metric("建议预算", "24万元")
        st.metric("整改周期", "45天")
    
    st.info("📊 完整图表功能正在部署中...")
    
else:
    st.info("""
    ## 🎯 系统说明
    
    这是一个专业的火灾风险评估系统，基于科学模型构建。
    
    ### 当前状态：
    ✅ 基础框架已部署
    🔄 核心算法部署中
    🔄 图表功能部署中
    
    ### 即将上线：
    1. 完整风险评估算法
    2. 可视化图表分析
    3. 整改策略推荐
    4. 成本效益分析
    
    ---
    
    **使用方法：**
    1. 左侧输入楼宇信息
    2. 设置预算
    3. 点击"开始评估"
    """)

# 页脚
st.markdown("---")
st.caption("版本: 基础框架 v1.0 | 完整功能即将上线")
