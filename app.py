import streamlit as st
import qrcode
import os
from datetime import datetime
import json
from base64 import b64encode
from io import BytesIO
import pandas as pd
from PIL import Image

# 数据存储文件
DATA_FILE = 'plant_data.json'
IMAGE_DIR = 'uploaded_images'
os.makedirs(IMAGE_DIR, exist_ok=True)


# 初始化数据结构
@st.cache_resource
def load_data():
    if not os.path.exists(DATA_FILE):
        initial_data = {
            "records": [],
            "last_updated": str(datetime.now())
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(initial_data, f)

    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def save_data(data):
    data['last_updated'] = str(datetime.now())
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)


# 主应用
def main():
    st.set_page_config(page_title="植物数据跟踪", layout="wide")
    st.title("🌱 植物数据跟踪系统")

    # 加载数据
    data = load_data()

    st.write(f"**最后更新:** {data['last_updated']}")

    # 创建两列布局
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("添加新记录")
        with st.form("new_record_form"):
            date = st.date_input("日期", datetime.now())
            height = st.number_input("株高 (cm)", min_value=0.0, step=0.1)
            chlorophyll = st.text_input("叶绿素 (mg/g)")
            nitrogen = st.text_input("氮含量 (%)")
            thermal_image = st.file_uploader("热成像图片", type=["png", "jpg", "jpeg"])
            visible_image = st.file_uploader("可见光图片", type=["png", "jpg", "jpeg"])

            submitted = st.form_submit_button("提交")

            if submitted:
                if not (height and chlorophyll and nitrogen):
                    st.error("请填写所有必填字段")
                else:
                    thermal_image_data = None
                    visible_image_data = None
                    date_str = date.strftime("%Y%m%d")

                    if thermal_image:
                        thermal_image_bytes = thermal_image.getvalue()
                        thermal_image_data = f"data:image/{thermal_image.type.split('/')[-1]};base64,{b64encode(thermal_image_bytes).decode('utf-8')}"

                        # 保存文件到本地（用于持久化）
                        if not os.path.exists(IMAGE_DIR):
                            os.makedirs(IMAGE_DIR)
                        filename = f"thermal_{date_str}.{thermal_image.type.split('/')[-1]}"
                        with open(os.path.join(IMAGE_DIR, filename), 'wb') as f:
                            f.write(thermal_image_bytes)

                    if visible_image:
                        visible_image_bytes = visible_image.getvalue()
                        visible_image_data = f"data:image/{visible_image.type.split('/')[-1]};base64,{b64encode(visible_image_bytes).decode('utf-8')}"

                        # 保存文件到本地（用于持久化）
                        if not os.path.exists(IMAGE_DIR):
                            os.makedirs(IMAGE_DIR)
                        filename = f"visible_{date_str}.{visible_image.type.split('/')[-1]}"
                        with open(os.path.join(IMAGE_DIR, filename), 'wb') as f:
                            f.write(visible_image_bytes)

                    new_record = {
                        "timestamp": date.strftime("%Y-%m-%d"),
                        "thermal_image": thermal_image_data,
                        "visible_image": visible_image_data,
                        "chlorophyll": chlorophyll,
                        "nitrogen": nitrogen,
                        "height": str(height)
                    }

                    data['records'].append(new_record)
                    save_data(data)
                    st.success("数据已成功添加!")
                    st.experimental_rerun()

    with col2:
        st.header("记录列表")
        if not data['records']:
            st.info("暂无记录，请添加新的植物数据。")
        else:
            # 按日期倒序排列记录
            sorted_records = sorted(data['records'], key=lambda x: x['timestamp'], reverse=True)

            for i, record in enumerate(sorted_records):
                with st.expander(f"记录 {record['timestamp']}"):
                    col_a, col_b = st.columns(2)

                    with col_a:
                        if record['thermal_image']:
                            st.markdown("**热成像:**")
                            st.markdown(f"<img src='{record['thermal_image']}' width='250'>", unsafe_allow_html=True)

                        if record['visible_image']:
                            st.markdown("**可见光:**")
                            st.markdown(f"<img src='{record['visible_image']}' width='250'>", unsafe_allow_html=True)

                    with col_b:
                        st.markdown(f"**叶绿素:** {record['chlorophyll']} mg/g")
                        st.markdown(f"**氮含量:** {record['nitrogen']} %")
                        st.markdown(f"**株高:** {record['height']} cm")

    # 添加数据导出功能
    st.sidebar.header("数据管理")
    if st.sidebar.button("导出为CSV"):
        if data['records']:
            df = pd.DataFrame([
                {
                    "日期": r["timestamp"],
                    "株高(cm)": r["height"],
                    "叶绿素(mg/g)": r["chlorophyll"],
                    "氮含量(%)": r["nitrogen"]
                } for r in data['records']
            ])

            csv = df.to_csv(index=False)
            st.sidebar.download_button(
                "下载CSV文件",
                csv,
                "plant_data.csv",
                "text/csv",
                key='download-csv'
            )
        else:
            st.sidebar.info("暂无数据可导出")


if __name__ == "__main__":
    main()
