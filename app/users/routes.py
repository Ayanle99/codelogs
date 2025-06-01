from flask import Flask, render_template, flash, url_for, redirect, request, abort
from flask_login import login_required, current_user
from difflib import unified_diff
from datetime import datetime

from app.users import bp
from app.models import *
from app.users.models import *
from .forms import *
from PIL import Image
import io
import os
from werkzeug.utils import secure_filename
import secrets
from app.models import Post, followers

from flask import jsonify


# --------------------- #
# User Profile & Access #
# --------------------- #


def resize_and_save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext

    # Get path to `app/users/static/thumbnails/`
    folder_path = os.path.join(os.path.dirname(__file__), 'static', 'thumbnails')
    os.makedirs(folder_path, exist_ok=True)

    picture_path = os.path.join(folder_path, picture_fn)

    # Resize image
    output_size = (125, 125)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    img.save(picture_path)

    return picture_fn



@bp.route('/user/<string:username>', methods=["GET", "POST"])
@login_required
def user(username):
    """Display user profile and posts if permitted"""
    form = EmptyForm()
    user = User.query.filter_by(username=username).first_or_404()

    if user.is_private and user != current_user and current_user not in user.allowed_users:
        return redirect(url_for('users.account_is_private', username=username))

    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).paginate(page=page, per_page=5)
    sent_requests = ProfileViewRequest.query.filter_by(requester_id=current_user.id).all()
    received_requests = ProfileViewRequest.query.filter_by(profile_owner_id=current_user.id).all()
    profile_form = ProfilePicForm()
    return render_template('users/user.html',
                           title=f"{user.username} Profile",
                           user=user,
                           posts=posts,
                           form=form,
                           sent_requests=sent_requests,
                           received_requests=received_requests,
                           profile_form=profile_form)


@bp.route('/upload_profile_pic', methods=['GET', 'POST'])
@login_required
def upload_profile_pic():
    form = ProfilePicForm()
    if form.validate_on_submit():
        current_user.thumbnail_url = resize_and_save_picture(form.picture.data)
        db.session.commit()

        flash('Profile picture updated!', 'success')
        return redirect(url_for('users.user', username=current_user.username))

    return redirect(url_for('users.user', username=current_user.username))


@bp.route("/account_is_private/<username>/", methods=["GET", "POST"])
@bp.route("/account_is_private/<username>", methods=["GET", "POST"])
@login_required
def account_is_private(username):
    """Handle access to private accounts"""
    user = User.query.filter_by(username=username).first_or_404()
    form = ProfileViewRequestForm()

    has_requested = ProfileViewRequest.query.filter_by(
        requester_id=current_user.id,
        profile_owner_id=user.id
    ).first() is not None

    empty_form = EmptyForm()
    return render_template('users/account_is_private.html',
                           title="Account Is Private",
                           form=form,
                           user=user,
                           has_requested=has_requested,
                           empty_form=empty_form)


@bp.route("/<username>/set_private", methods=["POST"])
@login_required
def set_account_to_private(username):
    """Set user account as private or public"""
    user = User.query.filter_by(username=username).first_or_404()
    if user != current_user:
        return redirect(url_for('errors.permission_denied'))

    form = EmptyForm()
    if form.validate_on_submit():
        user.is_private = 'is_private' in request.form
        db.session.commit()
        flash("Your account privacy setting has been updated.", "info")

    return redirect(url_for("users.user", username=user.username))


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data

        if form.password.data:
            current_user.set_password(form.password.data)  # Assuming you have a set_password method

        db.session.commit()
        flash("Your profile has been updated!", "success")
        return redirect(url_for('users.edit_profile'))
    return render_template('users/edit_profile.html', title=f"Edit {current_user.username}'s Profile", form=form)


# --------------------------- #
# Profile View Request Routes #
# --------------------------- #

@bp.route("/request_account_permision/<username>/", methods=["GET", "POST"])
@login_required
def request_account_permision(username):
    """Send profile view request"""
    user = User.query.filter_by(username=username).first_or_404()

    existing_request = ProfileViewRequest.query.filter_by(
        requester_id=current_user.id,
        profile_owner_id=user.id
    ).first()

    if existing_request:
        flash("You have already requested permission to view this profile.", "warning")
    else:
        form = ProfileViewRequestForm()
        if form.validate_on_submit():
            pr = ProfileViewRequest(
                requester_id=current_user.id,
                profile_owner_id=user.id
            )
            db.session.add(pr)
            db.session.commit()
            flash("Permission requested!", "success")

    return redirect(url_for('users.user', username=current_user.username))


@bp.route('/users/<username>/cancel_request', methods=['POST'])
@login_required
def cancel_request(username):
    """Cancel a previously sent request"""
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first_or_404()
        permission_request = ProfileViewRequest.query.filter_by(
            requester_id=current_user.id,
            profile_owner_id=user.id
        ).first()

        if permission_request:
            db.session.delete(permission_request)
            db.session.commit()
            flash('Your request has been cancelled.', 'success')
        else:
            flash('No active request found.', 'warning')
        return redirect(url_for('users.user', username=current_user.username))

    flash('Invalid request.', 'danger')
    return redirect(url_for('users.user', username=current_user.username))


@bp.route('/sent_requests/', methods=['GET', 'POST'])
@login_required
def sent_requests():
    """View sent profile view requests"""
    sent_requests = ProfileViewRequest.query.filter_by(requester_id=current_user.id).all()
    form = EmptyForm()
    return render_template('users/sent_requests.html',
                           title=f"{current_user.username}'s Requests",
                           sent_requests=sent_requests,
                           form=form)


@bp.route('/retract_request/', methods=['POST'])
@login_required
def retract_request():
    """Retract a sent request"""
    sent_request = ProfileViewRequest.query.filter_by(requester_id=current_user.id).first()

    if not current_user.id:
        abort(403)

    db.session.delete(sent_request)
    db.session.commit()
    flash('Request retracted successfully.', 'info')
    return redirect(url_for('users.sent_requests'))


@bp.route('/requests_received/', methods=['GET', 'POST'])
@login_required
def requests_received():
    """View requests received by current user"""
    requests_received = ProfileViewRequest.query.filter_by(
        profile_owner_id=current_user.id
    ).order_by(ProfileViewRequest.timestamp.desc()).all()

    form = EmptyForm()
    return render_template('users/received_requests.html',
                           title=f"{current_user.username}'s Requests Received",
                           requests_received=requests_received,
                           form=form)


@bp.route('/approve/<username>', methods=['POST'])
@login_required
def approve_request(username):
    """Approve a profile view request"""
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first_or_404()
        request_sent = ProfileViewRequest.query.filter_by(requester_id=user.id).first()
        request_sent.status = "Approved!"
        request_sent.approved = True
        current_user.allowed_users.append(user)
        db.session.commit()
        flash(f"You approved {username}'s request to view your profile.", "success")
    return redirect(url_for('users.requests_received'))


@bp.route('/reject_request/<username>', methods=["GET", "POST"])
@login_required
def reject_request(username):
    """Reject a profile view request"""
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first_or_404()
        request_sent = ProfileViewRequest.query.filter_by(requester_id=user.id).first()
        request_sent.status = "Rejected!"
        request_sent.approved = False
        db.session.commit()
        flash(f"You rejected {username}'s request to view your profile.", "danger")
    return redirect(url_for('users.requests_received'))


@bp.route('/ignore_request/<username>', methods=["GET", "POST"])
@login_required
def ignore_request(username):
    """Ignore a profile view request (leave pending but not visible)"""
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first_or_404()
        request_sent = ProfileViewRequest.query.filter_by(requester_id=user.id).first()
        request_sent.ignored = True
        db.session.commit()
        flash(f"You have ignored {username}'s request to view your profile.", "danger")
    return redirect(url_for('users.requests_received'))


# ---------------- #
# Post Management  #
# ---------------- #

@bp.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create a new post"""
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
    """Edit an existing post"""
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    form = EditPostForm(obj=post)
    if form.validate_on_submit():
        old_title, old_body = post.title or "", post.body or ""
        new_title, new_body = form.title.data, form.body.data

        if old_title != new_title or old_body != new_body:
            post.title = new_title
            post.body = new_body
            post.last_edited_by = current_user
            post.updated_at = datetime.utcnow()

            title_diff = '\n'.join(unified_diff(old_title.splitlines(), new_title.splitlines(), 'title_old', 'title_new', ''))
            body_diff = '\n'.join(unified_diff(old_body.splitlines(), new_body.splitlines(), 'body_old', 'body_new', ''))

            edit_record = EditHistory(
                post_id=post.id,
                editor_id=current_user.id,
                diff=f"--- Title Diff ---\n{title_diff}\n\n--- Body Diff ---\n{body_diff}"
            )
            db.session.add(edit_record)

        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('main.index'))

    return render_template('users/edit_post.html', form=form, post=post)


@bp.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    """Delete a post"""
    form = EmptyForm()
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)

    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully.', 'success')
        return redirect(url_for('main.index'))

    return render_template('users/delete_post.html', title="Delete Post", form=form, post=post)


@bp.route('/edit_post_history/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post_history(post_id):
    """View edit history of a post"""
    post = Post.query.get_or_404(post_id)
    edit_histories = post.edit_histories.order_by(EditHistory.timestamp.desc()).all()
    return render_template('users/edit_post_history.html',
                           title="Edit Post History",
                           post=post,
                           edit_histories=edit_histories)


# ---------------------------- #
# User Profile Follow/Unfollow #
# ---------------------------- #


@bp.route('/follow/<string:username>/', methods=['POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()


    form = EmptyForm()
    if form.validate_on_submit():
        if current_user.is_following(user):
            current_user.unfollow(user)

            # Record unfollow event
            unfollow_event = FollowEvent(
                follower_id=current_user.id,
                followed_id=user.id,
                action='unfollow'
            )
            db.session.add(unfollow_event)

            db.session.commit()
            flash(f"You have unfollowed {user.username}.", "info")

        else:
            current_user.follow(user)

            # Record follow event
            follow_event = FollowEvent(
                follower_id=current_user.id,
                followed_id=user.id,
                action='follow'
            )
            db.session.add(follow_event)

            db.session.commit()
            flash(f"You are now following {user.username}.", "success")

    return redirect(url_for('users.user', username=current_user.username))


@bp.route('/unfollow/<string:username>/', methods=['GET', 'POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()


    if current_user.is_following(user):
        current_user.unfollow(user)

        # Record unfollow event
        unfollow_event = FollowEvent(
            follower_id=current_user.id,
            followed_id=user.id,
            action='unfollow'
        )
        db.session.add(unfollow_event)

        db.session.commit()
        flash(f"You have unfollowed {user.username}", 'info')
    else:
        flash(f"You are not following {user.username}", 'warning')

    return redirect(url_for('users.user', username=current_user.username))



@bp.route('/followers/<string:username>/', methods=['GET', 'POST'])
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    return render_template(
        'users/followers.html',
        title=f"{user.username}'s Followers",
        user=user,
        form=form
    )


@bp.route('/following/<string:username>/', methods=['GET', 'POST'])
@login_required
def following(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    return render_template(
        'users/following.html',
        title=f"{user.username}'s Following",
        user=user,
        form=form
    )


@bp.route('/search')
@login_required
def search():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({
            'username': user.username,
            'email': user.email,
            'joined_on': user.created_at.strftime('%Y-%m-%d'),
            'profile_url': url_for('users.user', username=user.username),
            'thumbnail_url': url_for('users.static', filename='thumbnails/' + user.thumbnail_url),
            'is_online': user.is_online,
            'edit_profile_url': '/users/edit_profile',
            'following_count': user.get_following_count,
            'followers_count': user.get_followers_count,
            'bio': user.bio,
            'set_account_private': '/users/'+user.username+'/set_private',
            'sent_requests_url': 'users/sent_requests/',
            'requests_received': 'users/requests_received/',
            'create_post': 'users/create_post',
            'current_user': user.username,
            'posts_count': user.posts.count()
        })
    else:
        return jsonify({'error': f"No user found with username '{username}'"}), 404
