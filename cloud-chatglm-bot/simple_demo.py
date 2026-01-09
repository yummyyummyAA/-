# simple_demo.py - 单文件快速演示
from transformers import AutoTokenizer, AutoModelForCausalLM
import streamlit as st

@st.cache_resource
def load_model():
    return AutoTokenizer.from_pretrained("THUDM/chatglm3-6b", trust_remote_code=True), \
           AutoModelForCausalLM.from_pretrained("THUDM/chatglm3-6b", trust_remote_code=True).cpu()

tokenizer, model = load_model()

st.title("🧠 本地 ChatGLM3-6B 聊天机器人（课程设计演示）")

if "history" not in st.session_state:
    st.session_state.history = []

for h in st.session_state.history:
    st.chat_message("user").write(h[0])
    st.chat_message("assistant").write(h[1])

if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("生成中..."):
            inp = tokenizer(prompt, return_tensors="pt")
            output = model.generate(**inp, max_new_tokens=128)
            response = tokenizer.decode(output[0], skip_special_tokens=True)
            st.write(response)
            st.session_state.history.append((prompt, response))
