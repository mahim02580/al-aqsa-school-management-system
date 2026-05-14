from flask import redirect, url_for
from bijoy2unicode.converter import Unicode, conversionMap


def redirect_dashboard(role):
    if role == "Admin":
        return redirect(url_for('admin_dashboard'))
    elif role == "Service Admin":
        return redirect(url_for('service_admin_dashboard'))
    elif role == "Teacher":
        return redirect(url_for('teacher_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))


def convert_bangla_text(text):
    converter = Unicode()

    if not text:
        return ""

    text = str(text).strip()

    try:
        converted = converter.convertBijoyToUnicode(text)

        return converted

    except Exception:
        return text
