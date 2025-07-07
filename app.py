import streamlit as st
import os
from ppstructure_utils import PDFParser
from llm_api import get_summary, ask_question, setup_llm_api
from Img_util import save_imgs, is_meaningless_img, clear_imgs
import re
import gc
from text_util import text_chunking

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
        if st.session_state.get('pdf_file_name') != uploaded_file.name:
            # 清理 session_state
            st.session_state['pdf_text'] = None
            st.session_state['figures'] = None

            with st.spinner("正在使用PPStructure提取PDF内容,时间较长请稍候（约半分钟）..."):
                pdf_parser = PDFParser(pdf_path)
                pdf_parser.parse()
                st.session_state['pdf_text'] = pdf_parser.markdown_texts
                st.session_state['figures'] = pdf_parser.markdown_images
                st.session_state['pdf_file_name'] = uploaded_file.name

                # 清理图片
                clear_imgs();
                # 保存图片
                save_imgs(st.session_state['figures'])

                # 处理文字
                st.session_state['processed_text'] = text_chunking(st.session_state['pdf_text'])

                del pdf_parser
                gc.collect()
        
        if st.session_state.get('pdf_text') or st.session_state.get('figures'):
            # 显示PDF图片
            # if st.session_state.get('figures'):
            #     st.header("🖼️ PDF图片")
            #     cols = st.columns(3)
            #     img_count = 0
            #     for page_dict in st.session_state['figures']:
            #         if isinstance(page_dict, dict) and page_dict:
            #             for path, image in page_dict.items():
            #                 if not is_meaningless_img(image):
            #                     col = cols[img_count % 3]
            #                     with col:
            #                         st.image(image, caption=path)
            #                     img_count += 1
        
            
        
        

            # 显示文献总结
            st.header("📋 文献总结")
            if st.button("生成总结"):
                with st.spinner("正在生成总结..."):
                    summary = get_summary(st.session_state['pdf_text'])
                    st.write(summary)
        

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
                            if(1 <= fig_num <= len(os.listdir("./pics"))):
                                st.subheader(f"🖼️ 第{fig_num}张图片")
                                img_file = f"./pics/img_{fig_num}.png"
                                st.image(img_file, caption=f"图片 {fig_num}")
                        
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

if __name__ == "__main__":
    main()
