# ルーティングとビューの定義
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from app.models import User, Lesson, Enrollment, Payment, Survey, AnalysisReport
from werkzeug.security import generate_password_hash, check_password_hash
from app.analysis import analyze_data_with_gpt
import stripe

# Stripe APIキーの設定
stripe.api_key = os.getenv('STRIPE_API_KEY')

# ログインユーザーのロード
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ホームページのルート
@app.route('/')
def home():
    return render_template('home.html')

# ログインページのルート
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your email and password.')
    return render_template('login.html')
# ダッシュボードのルート
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# テンプレート選択ページのルート
@app.route('/select_template', methods=['GET', 'POST'])
@login_required
def select_template():
    if request.method == 'POST':
        selected_template = request.form.get('template')
        current_user.selected_template = selected_template  # ユーザーごとに選択されたテンプレートを保存
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('select_template.html')

# 選択されたテンプレートに基づいてUIを表示するルート
@app.route('/view_ui')
@login_required
def view_ui():
    template = current_user.selected_template or 'template1'
    return render_template(f'ui_templates/{template}.html')
# 提案と分析のルート
@app.route('/proposals')
@login_required
def proposals():
    proposal, chart = analyze_data_with_gpt(current_user.id)
    return render_template('proposals.html', proposal=proposal, chart=chart)

# ログアウトのルート
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
# レッスンのキャンセルと返金のルート
@app.route('/cancel-lesson/<int:lesson_id>', methods=['POST'])
@login_required
def cancel_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    enrollment = Enrollment.query.filter_by(lesson_id=lesson_id, student_id=current_user.id).first_or_404()

    # キャンセル期限を確認し、期限内なら返金処理を行う
    if datetime.utcnow() <= lesson.cancel_deadline:
        try:
            payment = Payment.query.filter_by(enrollment_id=enrollment.id).first()
            if payment and payment.status == 'paid':
                refund = stripe.Refund.create(payment_intent=payment.payment_intent)
                payment.status = 'refunded'
                db.session.commit()
                flash('レッスンをキャンセルしました。返金が処理されます。', 'success')
            else:
                flash('このレッスンには返金を行えません。', 'danger')
        except Exception as e:
            flash(f'返金処理中にエラーが発生しました: {str(e)}', 'danger')
    else:
        flash('キャンセル期限を過ぎています。インストラクターに直接連絡してください。', 'warning')

    return redirect(url_for('dashboard'))

# インストラクターによる返金のルート（キャンセル期限後）
@app.route('/refund/<int:enrollment_id>', methods=['POST'])
@login_required
def refund_student(enrollment_id):
    if current_user.role != 'instructor':
        flash('この操作を行う権限がありません。', 'danger')
        return redirect(url_for('dashboard'))

    enrollment = Enrollment.query.get_or_404(enrollment_id)
    payment = Payment.query.filter_by(enrollment_id=enrollment.id).first()

    if payment and payment.status == 'paid':
        try:
            refund = stripe.Refund.create(payment_intent=payment.payment_intent)
            payment.status = 'refunded'
            db.session.commit()
            flash('返金処理が完了しました。', 'success')
        except Exception as e:
            flash(f'返金処理中にエラーが発生しました: {str(e)}', 'danger')
    else:
        flash('このレッスンには返金を行えません。', 'danger')

    return redirect(url_for('dashboard'))
