import streamlit as st
from http import HTTPStatus
import dashscope
import os
import weave

st.title("视频分析应用")

# 获取视频列表
videos_folder = 'videos'
video_files = [f for f in os.listdir(videos_folder) if f.endswith(('.mp4', '.avi', '.mov'))]

# 让用户选择视频
selected_video = st.selectbox("选择要分析的视频", video_files)

# 展示选中的视频
if selected_video:
    video_path = os.path.join(videos_folder, selected_video)
    st.video(video_path)

# 用户输入阿里云Qwen API key
api_key = st.text_input("请输入阿里云Qwen API Key", type="password")
if api_key:
    dashscope.api_key = api_key

# 添加Weave API key配置选项
use_weave = st.checkbox("使用Weave进行实验管理")
if use_weave:
    weave_api_key = st.text_input("请输入Weave API Key", type="password")
    if weave_api_key:
        os.environ["WANDB_API_KEY"] = weave_api_key
        weave.init('OT-analysis')

# 用户输入问题
input_prompt = st.text_input("请输入分析问题", value="分析视频内容，若工人操作时未进行个人防护，请发出警告，并给出建议。")

@weave.op()
def analyze_video(video_path):
    """Analyze a single video using the multimodal conversation model."""
    messages = [
        {
            "role": "user",
            "content": [
                {"video": video_path},
                {"text": input_prompt}
            ]
        }
    ]
    response = dashscope.MultiModalConversation.call(
        model='qwen-vl-max-0809',
        messages=messages
    )
    if response.status_code == HTTPStatus.OK:
        result = response.output.choices[0].message.content[0]['text']
    else:
        result = f"Error: {response.message}"
    return {"prompt": input_prompt, "response": result}

if st.button("开始分析"):
    if not api_key:
        st.error("请先输入阿里云Qwen API Key")
    elif use_weave and not weave_api_key:
        st.error("您选择了使用Weave，请输入Weave API Key")
    elif not selected_video:
        st.error("请选择要分析的视频")
    else:
        with st.spinner("正在分析视频..."):
            video_path = os.path.join(videos_folder, selected_video)
            result = analyze_video(video_path)
        
        st.subheader("视频分析结果")
        st.write(f"问题: {result['prompt']}")
        st.write(f"回答: {result['response']}")

st.sidebar.info("注意：请确保'videos'文件夹中包含要分析的视频文件。")