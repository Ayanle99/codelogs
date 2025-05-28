from flask import Flask, render_template, flash, url_for, redirect, request
from app.users import bp
from app.models import *
from .forms import  *

from flask_login import login_required, current_user
from difflib import unified_diff


@bp.route('/user/<string:username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    return render_template('users/user.html', title=f"{user.username} Profile",user=user)


@bp.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, body=form.body.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.index'))
    return render_template('users/create_post.html', form=form)



@bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)

    form = EditPostForm(obj=post)

    if form.validate_on_submit():
        # Store old content
        old_title = post.title or ""
        old_body = post.body or ""

        new_title = form.title.data
        new_body = form.body.data

        # Only save if there's a change
        if old_title != new_title or old_body != new_body:
            # Update post content
            post.title = new_title
            post.body = new_body
            post.last_edited_by = current_user
            post.updated_at = datetime.utcnow()

            # Compute diffs
            title_diff = '\n'.join(unified_diff(
                old_title.splitlines(),
                new_title.splitlines(),
                fromfile='title_old',
                tofile='title_new',
                lineterm=''
            ))

            body_diff = '\n'.join(unified_diff(
                old_body.splitlines(),
                new_body.splitlines(),
                fromfile='body_old',
                tofile='body_new',
                lineterm=''
            ))

            combined_diff = f"--- Title Diff ---\n{title_diff}\n\n--- Body Diff ---\n{body_diff}"

            # Create EditHistory record with explicit IDs
            edit_record = EditHistory(
                post_id=post.id,
                editor_id=current_user.id,
                diff=combined_diff
            )

            db.session.add(edit_record)

        db.session.commit()

        flash('Your post has been updated!', 'success')
        return redirect(url_for('main.index'))

    return render_template('users/edit_post.html', form=form, post=post)


@bp.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    form = EmptyForm()
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)

    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully.', 'success')
        return  redirect(url_for('main.index'))
    return render_template('users/delete_post.html', title="Delete Post", form=form, post=post)


@bp.route('/edit_post_history/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post_history(post_id):
    post = Post.query.get_or_404(post_id)

    edit_histories = post.edit_histories.order_by(EditHistory.timestamp.desc()).all()

    return render_template(
        'users/edit_post_history.html',
        title="Edit Post History",
        post=post,
        edit_histories=edit_histories
    )
