
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

def text_chunking(markdown_text):
    # 先用markdown拆分器，拆分内容
    headers_to_split_on = [("#", "h1"), ("##", "h2"), ("###", "h3"), ("####", "h4")]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers = False)
    md_header_splits = markdown_splitter.split_text(markdown_text)

    # 再次对拆分后的内容进行二次拆分
    chunk_size = 200
    chunk_overleap = 10
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overleap)
    splits = text_splitter.split_documents(md_header_splits)

    return splits