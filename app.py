import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

st.set_page_config(page_title="排班意愿与工作反馈", page_icon="📋")
st.title("📋 排班意愿与工作反馈")
st.markdown("请填写以下信息，提交后管理员将收到邮件通知，以便协调班次和解决问题。")

def send_email(data):
    sender_email = st.secrets["email"]["sender"]
    sender_password = st.secrets["email"]["password"]
    receiver_email = st.secrets["email"]["receiver"]

    subject = f"排班反馈 - {data['name']} - {data['time']}"
    body = f"""
    提交时间：{data['time']}
    姓名/工号：{data['name']}
    ----------------------------------------
    【排班意愿】（将综合首选和备选协调）
    🥇 首选班次：{data['preferred_shift']}
    🥈 备选班次：{data['second_choice_shift']}
    特殊排班备注（如期望休息日等）：{data['shift_note']}
    ----------------------------------------
    【工作问题与建议】
    近期遇到的工作问题或困难：{data['problem']}
    其他想说的话：{data['other_note']}
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
    
    st.markdown("**请选择您的排班意愿（首选必填，备选也尽量填，方便协调）**")
    
    preferred_shift = st.selectbox(
        "🥇 首选班次 *",
        ["", "早班 (08:00-16:00)", "中班 (16:00-24:00)", 
         "晚班 (00:00-08:00)", "白班 (09:00-19:00)", "夜班 (18:00-04:00)", "弹性工作/看情况"]
    )
    
    second_choice_shift = st.selectbox(
        "🥈 备选班次",
        ["", "早班 (08:00-16:00)", "中班 (16:00-24:00)", 
         "晚班 (00:00-08:00)", "白班 (09:00-19:00)", "夜班 (18:00-04:00)", "弹性工作/看情况"]
    )
    
    shift_note = st.text_input(
        "特殊排班备注（非必填）", 
        placeholder="例：下周二想休息一天 / 周一有事不能早到 / 不能上夜班"
    )
    
    st.markdown("---")
    st.subheader("💡 工作中遇到的问题（方便我来解决）")
    problem = st.text_area(
        "近期在工作中遇到的困难、系统问题或需要帮助的事情 *", 
        placeholder="请详细描述一下您遇到的情况，我会尽快协调帮您解决。"
    )
    other_note = st.text_area("其他建议或想对管理员说的话（非必填）")

    submitted = st.form_submit_button("✅ 提交反馈")

    if submitted:
        if not name:
            st.error("请填写姓名/工号")
        elif not preferred_shift:
            st.error("请选择首选班次")
        elif not problem:
            st.error("为了帮您解决问题，请简要描述您遇到的问题")
        else:
            data = {
                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "name": name,
                "preferred_shift": preferred_shift,
                "second_choice_shift": second_choice_shift,
                "shift_note": shift_note,
                "problem": problem,
                "other_note": other_note
            }
            if send_email(data):
                st.success("提交成功！感谢您的反馈，我会结合首选和备选，尽量统筹协调。")
            else:
                st.warning("提交失败，请稍后重试或直接联系管理员。")
