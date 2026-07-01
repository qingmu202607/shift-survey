import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

st.set_page_config(page_title="排班意愿调查", page_icon="📋")
st.title("📋 排班意愿调查")
st.markdown("请填写以下信息，提交后管理员将收到邮件通知。")

def send_email(data):
    sender_email = st.secrets["email"]["sender"]
    sender_password = st.secrets["email"]["password"]
    receiver_email = st.secrets["email"]["receiver"]

    subject = f"排班意愿 - {data['name']} - {data['time']}"
    body = f"""
    提交时间：{data['time']}
    姓名/工号：{data['name']}
    希望的班次：{data['shift']}
    每周最大工作时长：{data['max_hours']} 小时
    完全不考虑的时间段：{data['unavailable']}
    其他建议：{data['comment']}
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP_SSL('smtp.163.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email.split(','), msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"邮件发送失败：{e}")
        return False

with st.form("survey_form", clear_on_submit=True):
    name = st.text_input("姓名/工号 *", max_chars=50, placeholder="请输入姓名或工号")
    shift = st.selectbox(
        "希望的班次类型 *",
        ["", "早班 (8:00-16:00)", "中班 (16:00-24:00)", 
         "晚班 (0:00-8:00)", "行政白班 (9:00-18:00)", "弹性工作"]
    )
    max_hours = st.number_input(
        "每周最大可接受工作时长（小时）", 
        min_value=0, max_value=80, value=40, step=1
    )
    unavailable = st.text_input(
        "完全不考虑的时间段", 
        placeholder="例：周一上午, 周末全天"
    )
    comment = st.text_area("其他建议或特殊需求")

    submitted = st.form_submit_button("✅ 提交问卷")

    if submitted:
        if not name:
            st.error("请填写姓名/工号")
        elif not shift:
            st.error("请选择希望的班次类型")
        else:
            data = {
                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "name": name,
                "shift": shift,
                "max_hours": max_hours,
                "unavailable": unavailable,
                "comment": comment
            }
            if send_email(data):
                st.success("提交成功！感谢您的反馈。")
            else:
                st.warning("提交失败，请稍后重试或直接联系管理员。")