import streamlit as st
# from dotenv import load_dotenv
from http import HTTPStatus
import dashscope
import os
# import weave


st.title("视频分析应用")

# 用户输入阿里云Qwen API key
api_key = st.text_input("请输入阿里云Qwen API Key", type="password")
if api_key:
    dashscope.api_key = api_key

# # 添加Weave API key配置选项
# use_weave = st.checkbox("使用Weave进行实验管理")
# if use_weave:
#     weave_api_key = st.text_input("请输入Weave API Key", type="password")
#     if weave_api_key:
#         os.environ["WANDB_API_KEY"] = weave_api_key
#         weave.init('OT-analysis')

# 用户输入问题
input_prompt = st.text_input("请输入分析问题", value="分析视频内容，若工人操作时未进行个人防护，请发出警告，并给出建议。")

# @weave.op()
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

def analyze_all_videos():
    """Analyze all videos in the 'videos' folder."""
    results = []
    videos_folder = 'videos'  # 修改为相对路径
    for video_file in os.listdir(videos_folder):
        if video_file.endswith(('.mp4', '.avi', '.mov')):
            video_path = os.path.join(videos_folder, video_file)
            result = analyze_video(video_path)
            results.append(result)
    return results

if st.button("开始分析"):
    if not api_key:
        st.error("请先输入API Key")
    # elif use_weave and not weave_api_key:
    #     st.error("您选择了使用Weave，请输入Weave API Key")
    else:
        with st.spinner("正在分析视频..."):
            results = analyze_all_videos()
        
        for result in results:
            st.subheader(f"视频分析结果")
            st.write(f"问题: {result['prompt']}")
            st.write(f"回答: {result['response']}")
            st.divider()

# st.sidebar.info("注意：请确保'videos'文件夹中包含要分析的视频文件。")