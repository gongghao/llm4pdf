import streamlit as st
import os
from pdf_utils import extract_text, extract_large_images
from llm_api import get_summary, ask_question, find_image_by_number, setup_llm_api
import re

st.set_page_config(page_title="PDF智能解读", layout="wide")

def highlight_text(text, keywords):
    """高亮显示关键词"""
    highlighted = text
    for keyword in keywords:
        if keyword in text:
            highlighted = highlighted.replace(keyword, f"**{keyword}**")
    return highlighted

def main():
    # 这里填写你的API类型和密钥
    # setup_llm_api("deepseek", "sk-2766c2e985dc4b568207f647a0056052")
    st.title("📚 PDF文档智能解读系统")
    
    # 侧边栏：PDF上传
    with st.sidebar:
        st.header("📄 上传PDF")
        uploaded_file = st.file_uploader("选择PDF文件", type=['pdf'])
        
        if uploaded_file:
            st.success(f"已上传: {uploaded_file.name}")
    
    # 主界面
    if uploaded_file:
        # 保存PDF文件
        pdf_path = f"temp_{uploaded_file.name}"
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # 解析PDF
        with st.spinner("正在解析PDF..."):
            text= extract_text(pdf_path)
            st.session_state['pdf_text'] = text
            figures = extract_large_images(pdf_path)
            st.session_state['figures'] = figures
        
        # 显示文献总结
        st.header("📋 文献总结")
        if st.button("生成总结"):
            with st.spinner("正在生成总结..."):
                summary = get_summary(st.session_state['pdf_text'])
                st.write(summary)
        
        # 显示PDF图片
        if st.session_state.get('figures'):
            st.header("🖼️ PDF图片")
            cols = st.columns(3)
            for i, fig in enumerate(st.session_state['figures']):
                with cols[i % 3]:
                    st.image(fig['img_path'], caption=f"图片 {i+1}")
        
        # 问答界面
        st.header("💬 智能问答")
        
        # 示例问题
        st.subheader("💡 示例问题")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("本文实验在哪些数据集上完成？"):
                st.session_state['example_question'] = "本文实验在哪些数据集上完成？"
        with col2:
            if st.button("全文的第2张图片描述了什么内容？"):
                st.session_state['example_question'] = "全文的第2张图片描述了什么内容？"
        with col3:
            if st.button("总结本文的核心创新点"):
                st.session_state['example_question'] = "总结本文的核心创新点"
        
        # 问题输入
        question = st.text_input(
            "请输入你的问题：", 
            value=st.session_state.get('example_question', ''),
            placeholder="例如：本文实验在哪些数据集上完成？"
        )
        
        if question:
            if st.button("提交问题"):
                with st.spinner("正在思考..."):
                    answer, evidence = ask_question(st.session_state['pdf_text'], question)
                    
                    # 检查问题是否涉及"第X张图片"
                    match = re.search(r'第(\d+)张图片', question)
                    if match and st.session_state.get('figures'):
                        fig_num = int(match.group(1))
                        if(1 <= fig_num <= len(st.session_state['figures'])):
                            img = st.session_state['figures'][fig_num-1]['img_path']
                            st.subheader(f"🖼️ 第{fig_num}张图片")
                            st.image(img, caption=f"图片 {fig_num}")
                    
                    # 显示答案和原文依据
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.subheader("🤖 答案")
                        st.write(answer)
                    with col2:
                        st.subheader("📖 原文依据")
                        
                        # 高亮显示关键词
                        keywords = ['数据集', 'dataset', '实验', 'experiment', '方法', 'method', 
                                   '结果', 'result', '创新', 'contribution', '图片', 'figure']
                        highlighted_evidence = highlight_text(evidence, keywords)
                        
                        st.markdown(highlighted_evidence)
                        
                        # 显示原文长度信息
                        st.info(f"原文片段长度: {len(evidence)} 字符")
        
        # 清理临时文件
        os.remove(pdf_path)

if __name__ == "__main__":
    main()
