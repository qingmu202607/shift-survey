import time
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import streamlit as st

# ========== 页面基础设置（必须放在最前面） ==========
st.set_page_config(
    page_title="排班意愿与工作反馈",
    page_icon="📋",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# ========== 隐藏 Streamlit 默认菜单和页脚 ==========
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ========== 页面标题 ==========
st.title("📋 排班意愿与工作反馈")
st.markdown("请根据您的实际需求填写，我会结合大家的意愿尽量协调下个月排班。")


# ========== 邮件发送函数 ==========
def send_email(form_data):
    """将问卷内容通过 QQ 邮箱 SMTP 发送给管理员。"""
    sender_email = st.secrets["email"]["sender"]
    sender_password = st.secrets["email"]["password"]

    receiver_emails = st.secrets["email"]["receiver"]
    if isinstance(receiver_emails, str):
        receiver_emails = [addr.strip()
                           for addr in receiver_emails.split(",")]

    submission_time = form_data['time']
    subject = (
        f"排班反馈 - {form_data['name']}"
        f"({form_data['id']}) - {submission_time}"
    )

    body = f"""
    提交时间：{submission_time}
    姓名：{form_data['name']}
    工号/编号：{form_data['id']}
    ----------------------------------------
    【排班与休息意愿】
    🥇 首选班次：{form_data['preferred_shift']}
    🥈 备选班次：{form_data['second_choice_shift']}
    📅 周末休息偏好：{form_data['weekend_preference']}
    📝 本月请假需求：{form_data['leave_request']}
    ⛔ 必须避开的时间：{form_data['unavailable_dates']}
    其他备注：{form_data['shift_note']}
    ----------------------------------------
    【工作问题与建议】
    近期遇到的问题或困难：{form_data['problem']}
    其他想说的话：{form_data['other_note']}
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ", ".join(receiver_emails)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_emails, msg.as_string())
        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)


# ========== 选项定义 ==========
shift_options = [
    "请选择",
    "08:00-18:00",
    "09:00-19:00",
    "10:00-20:00",
    "14:00-24:00",
    "16:00-02:00",
    "18:00-04:00",
    "20:00-06:00",
    "21:00-07:00",
    "22:00-08:00",
    "弹性/其他",
]

weekend_options = [
    "请选择",
    "希望周六休息",
    "希望周日休息",
    "都可以，服从安排",
]


# ========== 主表单 ==========
with st.form("survey_form"):
    st.subheader("👤 基本信息")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(
            "姓名 *", max_chars=50, placeholder="请输入您的姓名"
        )
    with col2:
        employee_id = st.text_input(
            "工号/编号", max_chars=20, placeholder="方便核对，可不填"
        )

    st.divider()

    st.subheader("🗓️ 下个月排班意愿")
    preferred_shift = st.selectbox("🥇 首选班次 *", shift_options)
    second_choice_shift = st.selectbox(
        "🥈 备选班次（如果首选安排不了）", shift_options
    )
    weekend_preference = st.selectbox(
        "📅 周末休息偏好 *", weekend_options
    )
    leave_request = st.text_input(
        "📝 当月请假需求",
        placeholder="例：7月15日请假一天 / 暂时没有请假计划",
    )
    unavailable_dates = st.text_input(
        "⛔ 必须避开的时间",
        placeholder="例：每周三晚上不行，或者某个特定日期",
    )
    shift_note = st.text_input(
        "其他排班备注",
        placeholder="例如：希望能跟某某同事上同个班次",
    )

    st.divider()

    st.subheader("💡 工作中遇到的困难（操作/流程/工具）")
    problem = st.text_area(
        "请描述您近期遇到的流程卡点、系统不便或操作困难 *",
        placeholder=(
            "例如：打卡系统常崩溃 / 客户信息查询步骤太繁琐 "
            "/ 缺少某个常用工具……说清楚问题，我好尽快帮您解决。"
        ),
    )
    other_note = st.text_area("其他想对管理员说的话（非必填）")

    st.divider()
    submitted = st.form_submit_button("✅ 提交反馈")

    # ========== 提交逻辑 ==========
    if submitted:
        errors = []
        if not name:
            errors.append("请填写姓名")
        if preferred_shift == "请选择":
            errors.append("请选择您的首选班次")
        if weekend_preference == "请选择":
            errors.append("请选择周末休息偏好")
        if not problem:
            errors.append("请简要描述您遇到的问题，这对我改进工作很重要")

        if errors:
            for err in errors:
                st.error(err)
        else:
            submission_data = {
                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "id": employee_id,
                "name": name,
                "preferred_shift": preferred_shift,
                "second_choice_shift": second_choice_shift,
                "weekend_preference": weekend_preference,
                "leave_request": leave_request,
                "unavailable_dates": unavailable_dates,
                "shift_note": shift_note,
                "problem": problem,
                "other_note": other_note,
            }

            success, error_msg = send_email(submission_data)
            if success:
                st.success(
                    "提交成功！感谢您的反馈，我会结合大家意愿统筹排班。"
                )
                st.balloons()
                time.sleep(1)
                st.rerun()
            else:
                st.error(
                    "邮件发送失败，请稍后重试或直接联系管理员。"
                    f"错误信息：{error_msg}"
                )
