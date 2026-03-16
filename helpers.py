from flask import redirect, url_for

def redirect_dashboard(role):
    if role == "Admin":
        return redirect(url_for('admin_dashboard'))
    elif role == "Service Admin":
        return redirect(url_for('service_admin_dashboard'))
    elif role == "Teacher":
        return redirect(url_for('teacher_dashboard'))
    else:
        return redirect(url_for('guardian_dashboard'))
