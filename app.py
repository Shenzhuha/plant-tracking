import streamlit as st
import qrcode
from datetime import datetime
import json
from base64 import b64encode
from io import BytesIO
import pandas as pd

DATA_FILE = 'plant_data.json'

@st.cache_resource
def load_data():
    if not os.path.exists(DATA_FILE):
        initial_data = {"records": [], "last_updated": str(datetime.now())}
        with open(DATA_FILE, 'w') as f:
            json.dump(initial_data, f)
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    data['last_updated'] = str(datetime.now())
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def generate_qr_code(record_id, base_url="https://your-app.onrender.com"):  # 部署后替换为 Render URL
    qr_url = f"{base_url}/?record_id={record_id}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill='black', back_color='white')
    buf = BytesIO()
    qr_img.save(buf, format="PNG")
    return buf.getvalue()

def main():
    st.set_page_config(page_title="植物数据跟踪", layout="wide")
    data = load_data()
    # 其余代码保持不变，详见之前完整版本
    st.title("🌱 植物数据跟踪系统")
    # ... 添加记录和显示列表的逻辑 ...

if __name__ == "__main__":
    main()
