from flask import render_template, request, redirect, url_for, session, flash
from app import app, db
from ..models import Comment, User



# Display all comments, ordered by most recent
@app.route('/comments')
def comments():
    all_comments = Comment.query.order_by(Comment.date.desc()).all()
    return render_template('comments.html', comments=all_comments)

# Add a new comment (POST only), requires user to be logged in
@app.route('/add_comment', methods=['POST'])
def add_comment():
    if 'user_id' not in session:
        flash("Vous devez Ãªtre connectÃ© pour laisser un commentaire.")
        return redirect(url_for('connection'))
    
    content = request.form.get('content', '').strip()
    if not content:
        flash("Le commentaire ne peut pas Ãªtre vide.")
        return redirect(url_for('comments'))

    user = User.query.get(session['user_id'])
    if not user:
        flash("Utilisateur non trouvÃ©.")
        return redirect(url_for('connection'))

    comment = Comment(content=content, user=user)
    db.session.add(comment)
    db.session.commit()

    flash("Merci pour votre commentaire !")
    return redirect(url_for('comments'))