
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'
headers_to_split_on = [("#", "h1"), ("##", "h2"), ("###", "h3")]
markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
with open("./output/temp_反事实-Yang 等 - 2023 - Counterfactual Learning on Heterogeneous Graphs wi.md", "r", encoding="utf-8") as f:
    text = f.read()
chunks = markdown_splitter.split_text(text)

with open("test.md", "w", encoding="utf-8") as f:
    for chunk in chunks:
        f.write(chunk.page_content)
        f.write("\n")
        f.write(str(chunk.metadata))
        f.write("\n")
        f.write("=" * 40)
        f.write("\n")

embeddings = HuggingFaceEmbeddings(model_name="shibing624/text2vec-base-multilingual")
vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory="./chroma_db")
print("vectordb:", vectorstore._collection.count())
vectorstore.persist() # 向量持久化