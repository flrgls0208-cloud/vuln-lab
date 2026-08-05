import os
from uuid import uuid4
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory, abort
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from extensions import db
from models import Dsboard, Comment, User

board_bp = Blueprint('board', __name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, 'static', 'uploads')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            flash('로그인이 필요합니다.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def can_manage_post(post):
    if session.get('user_id') == post.user_id:
        return True
    return session.get('role') == 'admin'


def save_uploaded_file():
    uploaded_file = request.files.get('attachment') or request.files.get('image')
    if not uploaded_file or uploaded_file.filename == '':
        return None

    filename = secure_filename(uploaded_file.filename)
    if not filename:
        flash('올바른 파일명만 업로드할 수 있습니다.')
        return None

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(filename)[1]
    saved_name = f"{uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_DIR, saved_name)
    uploaded_file.save(save_path)
    return os.path.join('uploads', saved_name)


def delete_uploaded_file(image_path):
    if not image_path:
        return

    normalized = image_path.replace('\\', '/').lstrip('/')
    full_path = os.path.join(BASE_DIR, 'static', normalized)
    if os.path.exists(full_path):
        os.remove(full_path)


@board_bp.route('/')
def board_list():
    search_query = request.args.get('q', '').strip()
    filter_type = request.args.get('filter', 'all')

    query = Dsboard.query

    if search_query:
        like_query = f"%{search_query}%"
        if filter_type == 'title':
            query = query.filter(Dsboard.title.like(like_query))
        elif filter_type == 'content':
            query = query.filter(Dsboard.content.like(like_query))
        elif filter_type == 'author':
            query = query.join(Dsboard.user).filter(User.username.like(like_query))
        else:
            query = query.filter(
                or_(
                    Dsboard.title.like(like_query),
                    Dsboard.content.like(like_query),
                )
            )

    posts = query.order_by(Dsboard.id.desc()).all()
    return render_template('board_list.html', posts=posts, search_query=search_query, filter_type=filter_type)


@board_bp.route('/write', methods=['GET', 'POST'])
@login_required
def board_write():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '')

        if not title or not content:
            flash('제목과 내용을 모두 입력해주세요.')
            return redirect(url_for('board.board_write'))

        image_path = save_uploaded_file()
        new_post = Dsboard(
            user_id=session.get('user_id'),
            title=title,
            content=content,
            image_path=image_path,
        )
        db.session.add(new_post)
        db.session.commit()

        flash('게시글이 등록되었습니다.')
        return redirect(url_for('board.board_list'))

    return render_template('board_write.html')


@board_bp.route('/<int:post_id>', methods=['GET', 'POST'])
def board_view(post_id):
    post = Dsboard.query.get_or_404(post_id)

    if request.method == 'POST' and session.get('user_id'):
        content = request.form.get('comment', '').strip()
        if content:
            comment = Comment(post_id=post.id, user_id=session.get('user_id'), content=content)
            db.session.add(comment)
            db.session.commit()
            flash('댓글이 등록되었습니다.')
            return redirect(url_for('board.board_view', post_id=post.id))
        flash('댓글 내용을 입력해주세요.')
        return redirect(url_for('board.board_view', post_id=post.id))

    return render_template('board_view.html', post=post)


@board_bp.route('/<int:post_id>/download')
def board_download(post_id):
    post = Dsboard.query.get_or_404(post_id)
    if not post.image_path:
        flash('첨부파일이 없습니다.')
        return redirect(url_for('board.board_view', post_id=post.id))

    normalized = post.image_path.replace('\\', '/').lstrip('/')
    full_path = os.path.join(BASE_DIR, 'static', normalized)
    if not os.path.exists(full_path):
        abort(404)

    return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path), as_attachment=True)


@board_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def board_edit(post_id):
    post = Dsboard.query.get_or_404(post_id)
    if not can_manage_post(post):
        flash('수정 권한이 없습니다.')
        return redirect(url_for('board.board_view', post_id=post.id))

    if request.method == 'GET':
        return render_template('board_write.html', post=post)

    post.title = request.form.get('title', post.title)
    post.content = request.form.get('content', post.content)

    new_file = save_uploaded_file()
    if new_file is not None:
        if post.image_path:
            delete_uploaded_file(post.image_path)
        post.image_path = new_file

    db.session.commit()

    flash('게시글이 수정되었습니다.')
    return redirect(url_for('board.board_view', post_id=post.id))


@board_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def board_delete(post_id):
    post = Dsboard.query.get_or_404(post_id)
    is_author = (post.user_id == session.get('user_id'))
    is_admin = (session.get('role') == 'admin')

    if not (is_author or is_admin):
        flash('삭제 권한이 없습니다.')
        return redirect(url_for('board.board_view', post_id=post.id))

    if post.image_path:
        delete_uploaded_file(post.image_path)

    db.session.delete(post)
    db.session.commit()

    flash('게시글이 삭제되었습니다.')
    return redirect(url_for('board.board_list'))