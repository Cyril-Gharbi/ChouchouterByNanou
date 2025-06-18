from flask import render_template, request, redirect, url_for, session, flash
from app import app, db
from ..models import Comment, User
from flask_login import login_required, current_user


# Add a new comment (POST only), requires user to be logged in
@app.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
    content = request.form.get('content', '').strip()
    if not content:
        flash("Le commentaire ne peut pas être vide.")
        return redirect(url_for('my_comments'))

    comment = Comment(
        content=content,
        user=current_user,
        username_at_time=current_user.username
    )
    db.session.add(comment)
    db.session.commit()

    flash("Merci pour votre commentaire !")
    return redirect(url_for('my_comments'))

@app.route('/delete_comment', methods=['POST'])
@login_required
def delete_comment():
    comment_id = request.form.get("comment_id")

    if not comment_id:
        flash("Tous les champs sont requis.", "danger")
        return redirect(url_for("my_comments"))

    comment = Comment.query.get(comment_id)

    if not comment:
        flash("Commentaire introuvable.", "danger")
        return redirect(url_for("comments"))

    if comment.user_id != current_user.id:
        flash("Action non autorisée", "danger")
        return redirect(url_for("comments"))
    
    db.session.delete(comment)
    db.session.commit()

    flash("Commentaire supprimé avec succès.", "success")
    return redirect(url_for("my_comments"))


@app.route('/my_comments')
@login_required
def my_comments():
    comments = current_user.comments
    return render_template("account_user/my_comments.html", comments=comments)


@app.route('/edit_comment', methods=['POST'])
@login_required
def edit_comment():
    comment_id = request.form.get('comment_id')
    content = request.form.get('content', '').strip()

    if not comment_id or not content:
        flash("Le commentaire ne peut pas être vide.", "danger")
        return redirect(url_for('my_comments'))

    comment = Comment.query.get(comment_id)
    if not comment:
        flash("Commentaire introuvable.", "danger")
        return redirect(url_for('my_comments'))

    if comment.user_id != current_user.id:
        flash("Action non autorisée.", "danger")
        return redirect(url_for('my_comments'))

    comment.content = content
    db.session.commit()
    flash("Commentaire modifié avec succès.", "success")
    return redirect(url_for('my_comments'))
