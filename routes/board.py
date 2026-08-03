from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import Post
from extensions import db
from functools import wraps

board_bp = Blueprint('board', __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            flash('로그인이 필요합니다.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@board_bp.route('/')
def board_list():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('board_list.html', posts=posts)

@board_bp.route('/write', methods=['GET', 'POST'])
@login_required
def board_write():
    if request.method == 'GET':
        return render_template('board_write.html')

    title = request.form.get('title', '').strip()
    content = request.form.get('content', '')

    if not title or not content:
        flash('제목과 내용을 모두 입력해주세요.')
        return redirect(url_for('board.board_write'))

    new_post = Post(title=title, content=content, author=session.get('username'))
    db.session.add(new_post)
    db.session.commit()

    flash('게시글이 등록되었습니다.')
    return redirect(url_for('board.board_list'))

@board_bp.route('/<int:post_id>')
def board_view(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('board_view.html', post=post)

@board_bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def board_edit(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'GET':
        return render_template('board_write.html', post=post)

    post.title = request.form.get('title', post.title)
    post.content = request.form.get('content', post.content)
    db.session.commit()

    flash('게시글이 수정되었습니다.')
    return redirect(url_for('board.board_view', post_id=post.id))

@board_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def board_delete(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()

    flash('게시글이 삭제되었습니다.')
    return redirect(url_for('board.board_list'))