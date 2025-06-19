from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import FileField
from wtforms.validators import DataRequired
import hashlib
import os
import secrets
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SIGNATURE_FOLDER'] = 'signatures'
app.config['SECRET_KEY'] = secrets.token_hex(16)  # Random secret key for CSRF and session
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SIGNATURE_FOLDER'], exist_ok=True)

class UploadForm(FlaskForm):
    file = FileField('file', validators=[DataRequired()])

def sign_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            file_data = f.read()
        return hashlib.sha256(file_data + app.config['SECRET_KEY'].encode()).hexdigest()
    except Exception as e:
        return None

@app.route('/')
def index():
    return redirect(url_for('send_file'))

@app.route('/send', methods=['GET', 'POST'])
def send_file():
    form = UploadForm()
    if request.method == 'POST' and form.validate_on_submit():
        file = form.file.data
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(filepath)
                signature = sign_file(filepath)
                if not signature:
                    flash("Lỗi khi tạo chữ ký cho file.", "error")
                    return render_template('send.html', form=form)

                sig_path = os.path.join(app.config['SIGNATURE_FOLDER'], filename + '.sig')
                with open(sig_path, 'w') as f:
                    f.write(signature)

                flash(f"Tải file '{filename}' thành công!", "success")
                return render_template('send.html', form=form, filename=filename)
            except Exception as e:
                flash(f"Lỗi khi lưu file: {str(e)}", "error")
                return render_template('send.html', form=form)
        else:
            flash("Vui lòng chọn một file hợp lệ.", "error")
    return render_template('send.html', form=form)

@app.route('/receive', methods=['GET'])
def receive_file():
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
    except Exception:
        files = []
        flash("Lỗi khi truy cập thư mục file.", "error")
    return render_template('receive.html', files=files)

@app.route('/download/<filename>')
def download(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception:
        flash("File không tồn tại.", "error")
        return redirect(url_for('receive_file'))

@app.route('/verify/<filename>')
def verify(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    sig_path = os.path.join(app.config['SIGNATURE_FOLDER'], filename + '.sig')

    if not os.path.exists(filepath) or not os.path.exists(sig_path):
        flash("File hoặc chữ ký không tồn tại.", "error")
        return redirect(url_for('receive_file'))

    actual_sig = sign_file(filepath)
    if not actual_sig:
        flash("Lỗi khi xác minh chữ ký.", "error")
        return redirect(url_for('receive_file'))

    try:
        with open(sig_path, 'r') as f:
            saved_sig = f.read()
    except Exception:
        flash("Lỗi khi đọc chữ ký.", "error")
        return redirect(url_for('receive_file'))

    if actual_sig == saved_sig:
        flash(f'✅ Chữ ký hợp lệ cho file: {filename}', "success")
    else:
        flash(f'❌ Chữ ký không hợp lệ cho file: {filename}', "error")
    return redirect(url_for('receive_file'))

if __name__ == '__main__':
    app.run(debug=True)