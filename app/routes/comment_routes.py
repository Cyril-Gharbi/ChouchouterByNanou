from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Comment


def init_routes(app):
    comment_bp = Blueprint("comment", __name__)

    # Add a new comment (POST only), requires user to be logged in
    @comment_bp.route("/add_comment", methods=["POST"], endpoint="add_comment")
    @login_required
    def add_comment():
        content = request.form.get("content", "").strip()
        if not content:
            flash("Le commentaire ne peut pas être vide.")
            return redirect(url_for("comment.my_comments"))

        comment = Comment(
            content=content, user=current_user, username_at_time=current_user.username
        )
        db.session.add(comment)
        db.session.commit()

        flash("Merci pour votre commentaire !")
        return redirect(url_for("comment.my_comments"))

    @comment_bp.route("/delete_comment", methods=["POST"], endpoint="delete_comment")
    @login_required
    def delete_comment():
        comment_id = request.form.get("comment_id")

        if not comment_id:
            flash("Tous les champs sont requis.", "danger")
            return redirect(url_for("comment.my_comments"))

        comment = Comment.query.get(comment_id)

        if not comment:
            flash("Commentaire introuvable.", "danger")
            return redirect(url_for("main.comments"))

        if comment.user_id != current_user.id:
            flash("Action non autorisée", "danger")
            return redirect(url_for("main.comments"))

        db.session.delete(comment)
        db.session.commit()

        flash("Commentaire supprimé avec succès.", "success")
        return redirect(url_for("comment.my_comments"))

    @comment_bp.route("/my_comments", endpoint="my_comments")
    @login_required
    def my_comments():
        comments = current_user.comments
        return render_template("account_user/my_comments.html", comments=comments)

    @comment_bp.route("/edit_comment", methods=["POST"], endpoint="edit_comment")
    @login_required
    def edit_comment():
        comment_id = request.form.get("comment_id")
        content = request.form.get("content", "").strip()

        if not comment_id or not content:
            flash("Le commentaire ne peut pas être vide.", "danger")
            return redirect(url_for("comment.my_comments"))

        comment = Comment.query.get(comment_id)
        if not comment:
            flash("Commentaire introuvable.", "danger")
            return redirect(url_for("comment.my_comments"))

        if comment.user_id != current_user.id:
            flash("Action non autorisée.", "danger")
            return redirect(url_for("comment.my_comments"))

        comment.content = content
        db.session.commit()
        flash("Commentaire modifié avec succès.", "success")
        return redirect(url_for("comment.my_comments"))

    return comment_bp
