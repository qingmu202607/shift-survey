import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime  # 只导入 datetime 类，避免引入 date 造成混淆

st.set_page_config(page_title="排班意愿与工作反馈", page_icon="📋")
st.title("📋 排班意愿与工作反馈")
st.markdown("请根据您的实际需求填写，我会结合大家的意愿尽量协调下个月排班。")


def send_email(form_data):
    """
    发送邮件，form_data 是字典，包含所有反馈信息。
    注意：参数和内部变量都避免使用 'date' 一词，防止隐藏外部作用域名称。
    """
    sender_email = st.secrets["email"]["sender"]
    sender_password = st.secrets["email"]["password"]

    # 处理接收人：支持逗号分隔字符串或列表
    receiver_emails = st.secrets["email"]["receiver"]
    if isinstance(receiver_emails, str):
        receiver_emails = [addr.strip() for addr in receiver_emails.split(",")]

    # 构造主题和正文，这里使用 'submission_time' 而不是 'date'
    submission_time = form_data['time']  # 已经是字符串 'YYYY-MM-DD HH:MM:SS'
    subject = f"排班反馈 - {form_data['name']}({form_data['id']}) - {submission_time}"

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
        server = smtplib.SMTP_SSL('smtp.163.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_emails, msg.as_string())
        server.quit()
        return True, None
    except Exception as e:
        return False, str(e)


# 班次选项
shift_options = [
    "", "08:00-18:00", "09:00-19:00", "10:00-20:00",
    "16:00-02:00", "18:00-04:00", "20:00-06:00",
    "21:00-07:00", "22:00-08:00", "弹性/其他"
]

# 不使用 clear_on_submit，提交成功后手动清空
with st.form("survey_form"):
    st.subheader("👤 基本信息")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("姓名 *", max_chars=50, placeholder="请输入您的姓名")
    with col2:
        employee_id = st.text_input("工号/编号", max_chars=20, placeholder="方便核对，可不填")

    st.divider()

    st.subheader("🗓️ 下个月排班意愿")
    preferred_shift = st.selectbox("🥇 首选班次 *", shift_options)
    second_choice_shift = st.selectbox("🥈 备选班次（如果首选安排不了）", shift_options)
    weekend_preference = st.selectbox(
        "📅 周末休息偏好 *",
        ["", "希望周六休息", "希望周日休息", "都可以，服从安排"]
    )
    leave_request = st.text_input("📝 当月请假需求", placeholder="例：7月15日请假一天 / 暂时没有请假计划")
    unavailable_dates = st.text_input("⛔ 必须避开的时间", placeholder="例：每周三晚上不行，或者某个特定日期")
    shift_note = st.text_input("其他排班备注", placeholder="例如：希望能跟某某同事上同个班次")

    st.divider()

    st.subheader("💡 工作中遇到的问题")
    problem = st.text_area(
        "请描述您近期遇到的困难或需要帮忙的事情 *",
        placeholder="说清楚问题，我好尽快帮您协调解决。"
    )
    other_note = st.text_area("其他想对管理员说的话（非必填）")

    st.divider()
    submitted = st.form_submit_button("✅ 提交反馈")

    if submitted:
        # 前端校验
        if not name:
            st.error("请填写您的姓名")
        elif not preferred_shift:
            st.error("请选择您的首选班次")
        elif not weekend_preference:
            st.error("请选择您的周末休息偏好，方便排班")
        elif not problem:
            st.error("为了帮您解决问题，请简要描述您遇到的问题")
        else:
            # 构造数据（注意：这里变量名叫 submission_data，不是 date）
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
                "other_note": other_note
            }

            success, error_msg = send_email(submission_data)
            if success:
                st.success("提交成功！感谢您的反馈，我会结合大家意愿统筹排班。")
                st.balloons()
                # 延迟后刷新页面清空表单
                import time

                time.sleep(1)
                st.rerun()
            else:
                st.error(f"邮件发送失败，请稍后重试或直接联系管理员。错误信息：{error_msg}")
