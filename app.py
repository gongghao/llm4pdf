import streamlit as st
import os
import fitz
from llm_api import get_summary, ask_question, setup_llm_api, setup_vlm_api
import re
import gc
from text_util import text_chunking
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from pdf_parser import  extract_text_and_images_from_pdf   

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

st.set_page_config(page_title="PDF智能解读", layout="wide")



def highlight_text(text, keywords):
    """高亮显示关键词"""
    highlighted = text
    for keyword in keywords:
        if keyword in text:
            highlighted = highlighted.replace(keyword, f"**{keyword}**")
    return highlighted

def main():
    
    # VLM API密钥配置
    # 这里填写你的API类型和密钥
    if os.environ.get('VLM_API_KEY') is None:
        setup_vlm_api("sk-95e87a0b2dee40e0b5ae7ae8ac2161ca")  # 请替换为你的实际API密钥
        setup_llm_api("deepseek", "sk-2766c2e985dc4b568207f647a0056052")
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

            with st.spinner("正在提取PDF内容"):

                
                # # 提取文本和图片描述
                # combined_content, text_only = extract_text_and_images_from_pdf(pdf_path)
                
                # # 保存到session_state
                # st.session_state['pdf_text'] = text_only
                # st.session_state['pdf_file_name'] = uploaded_file.name
                
                # # 保存完整内容
                # complete_text_path = f'pages/complete_text_with_images.md'
                # os.makedirs('pages', exist_ok=True)
                # with open(complete_text_path, 'w', encoding='utf-8') as f:
                #     f.write(combined_content)
                # st.success(f"已保存完整内容: {complete_text_path}")
                
                # # 文本向量化
                # st.session_state['chunks'] = text_chunking(st.session_state['pdf_text'])
                # embeddings = HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-multilingual")
                # vectorstore = Chroma.from_documents(documents=st.session_state['chunks'], embedding=embeddings, persist_directory="./chroma_db")
                # print("vectordb:", vectorstore._collection.count())    
                # 显示提取的内容
                # st.header("📝 提取的内容（包含图片描述）")
                # with st.expander("查看提取的内容", expanded=False):
                #     st.text_area("PDF内容", combined_content, height=300)
                
                # 显示图片统计
                # from pdf_parser import get_all_image_descriptions
                # images = get_all_image_descriptions(combined_content)
                # if images:
                #     st.info(f"📸 检测到 {len(images)} 张图片")
                #     for img in images:
                #         st.write(f"图片 {img['number']}: {img['description'][:100]}...")
                
                
                with open('./pages/complete_text_with_images.md', 'r', encoding='utf-8') as f:
                    markdown_text = f.read()
                st.session_state['pdf_text'] = markdown_text
                st.session_state['pdf_file_name'] = uploaded_file.name


        if st.session_state.get('pdf_text'):
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
                        with open('./pages/complete_text_with_images.md', 'r', encoding='utf-8') as f:
                            markdown_text = f.read()
                        answer, evidence, is_image_question = ask_question(markdown_text, question)
                        if is_image_question:
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                st.subheader("🤖 答案")
                                st.write(answer)
                            with col2:
                                st.subheader("🖼️ 图片")
                                st.image(evidence)
                        else:
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                st.subheader("🤖 答案")
                                st.write(answer)
                            with col2:
                                st.subheader("📖 原文依据")
                                st.markdown(evidence)
                                # 显示原文长度信息
                                st.info(f"原文片段长度: {len(evidence)} 字符")

if __name__ == "__main__":
    main()
