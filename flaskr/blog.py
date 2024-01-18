# flask tutorial, Blog Blueprint, https://flask.palletsprojects.com/en/3.0.x/tutorial/blog/
#were created:
#flaskr/templates/blog/index.html
#flaskr/templates/blog/create.html
#flaskr/templates/blog/update.html
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

from translate import Translator

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    default_title = f"{g.user['username']}'s Job {get_user_job_count() + 1}"

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()

            # Retrieve the ID of the newly created post
            post_id = db.execute(
                'SELECT id FROM post WHERE title = ? AND author_id = ?',
                (title, g.user['id'])
            ).fetchone()['id']

            # Redirect to the edit page for the newly created post
            return redirect(url_for('blog.update', id=post_id))

    return render_template('blog/create.html', default_title=default_title)

def get_user_job_count():
    db = get_db()
    count = db.execute(
        'SELECT COUNT(id) FROM post WHERE author_id = ?',
        (g.user['id'],)
    ).fetchone()[0]
    return count



def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))



    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
# flask tutorial, end of Blog Blueprint, https://flask.palletsprojects.com/en/3.0.x/tutorial/blog/

#TRANSLATION function, on the page with all jobs (what we did)
@bp.route('/<int:id>/translate', methods=['GET', 'POST'])
@login_required
def translate_post(id):
    post = get_post(id)

    if request.method == 'GET':
        # Display translation form
        return render_template('blog/translate_post.html', post=post)
    elif request.method == 'POST':
        # Handle translation submission
        language = request.form.get('language')

        # Translate post content using the translate library
        translated_text = translate_text(post['body'], language)

        db = get_db()
        db.execute(
            'UPDATE post SET body = ? WHERE id = ?',
            (post['body'] + '\n' + translated_text, id)
        )
        db.commit()

        return render_template('blog/translated_post.html', post=post, translated_text=translated_text)

def translate_text(text, target_language="en" or "ru" or "it", source_language="de"):
    translator = Translator(to_lang=target_language, from_lang = source_language)
    translation = translator.translate(text)
    return translation

#COMMENTING function, on the page with all jobs (what we did)
@bp.route('/<int:id>/comments', methods=['GET', 'POST'])
def comments(id):
    post = get_post(id, check_author=False)

    if request.method == 'POST':
        content = request.form['content']
        error = None

        if not content:
            error = 'Content is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO comment (post_id, author_id, content)'
                ' VALUES (?, ?, ?)',
                (id, g.user['id'], content)
            )
            db.commit()

    comments = get_comments(id)

    return render_template('blog/comments.html', post=post, comments=comments)

def get_comments(id):
    return get_db().execute(
        'SELECT c.id, content, created, author_id, username'
        ' FROM comment c JOIN user u ON c.author_id = u.id'
        ' WHERE c.post_id = ?'
        ' ORDER BY created DESC',
        (id,)
    ).fetchall()