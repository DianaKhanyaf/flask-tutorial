# flask tutorial, Blog Blueprint, https://flask.palletsprojects.com/en/3.0.x/tutorial/blog/
#were created:
#flaskr/templates/blog/index.html
#flaskr/templates/blog/create.html
#flaskr/templates/blog/update.html
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
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
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

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

# Add the new route for song search
@bp.route('/search', methods=('GET', 'POST'))
@login_required
def search():
    if request.method == 'POST':
        keyword = request.form['keyword']
        query = "SELECT lyrics FROM song WHERE lyrics LIKE ?"
        print("Query:", query)
        print("Values:", (f"%{keyword}%",))
        lyrics = get_db().execute(query, (f"%{keyword}%",)).fetchall()
        return render_template('blog/search_results.html', lyrics=lyrics, keyword=keyword)

    return render_template('blog/search.html')

# blog.py





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

def translate_text(text, target_language="en" or "ru", source_language="de"):
    translator = Translator(to_lang=target_language, from_lang = source_language)
    translation = translator.translate(text)
    return translation

