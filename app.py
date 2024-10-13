"""Blogly application."""

from flask import Flask, render_template, request, redirect
from models import db, connect_db, User, Post, Tag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'ihaveasecret'

with app.app_context():
    connect_db(app)
    db.create_all()


@app.route('/')
def root():
    """Show recent posts"""

    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template("posts/homepage.html", posts=posts)


@app.errorhandler(404)
def page_not_found(e):
    """404 page"""

    return render_template('404.html'), 404




############################ users ##############################



@app.route('/list')
def list_users():
    """shows list of all users in db"""

    users = User.query.all()
    return render_template('list.html', users=users)


@app.route('/user_form')
def create_user():
    return render_template('user_form.html')


@app.route('/user_form', methods=["POST"])
def create_user_form():
    """create a user form"""

    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image_url = request.form["image_url"]

    user = User(first_name=first_name, last_name=last_name, image_url=image_url)
    db.session.add(user)
    db.session.commit()

    return redirect(f"/{user.id}")


@app.route('/<int:user_id>')
def show_details(user_id):
    """shows details of user"""

    user = User.query.get_or_404(user_id)
    return render_template("details.html", user=user)


@app.route('/<int:user_id>/edit')
def edit_user(user_id):
    """edit a user"""

    user = User.query.get_or_404(user_id)
    return render_template('edit_user.html', user=user)

@app.route('/<int:user_id>/edit', methods=["POST"])
def edit_user_form(user_id):
    """edit a user form redirecting to user"""

    user = User.query.get_or_404(user_id)

    user.first_name = request.form["first_name"]
    user.last_name = request.form["last_name"]
    user.image_url = request.form["image_url"]

    db.session.add(user)
    db.session.commit()

    return redirect(f"/{user.id}")


@app.route('/<int:user_id>/delete', methods=["GET", "POST"])
def delete_user(user_id):
    """delete a user redirect"""

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/")





###################### posts ########################


@app.route('<int:user_id>/posts/new')
def posts_form(user_id):
    """Show a form to create a new post"""

    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template('new_post.html', user=user, tags=tags)


@app.route('<int:user_id>/posts/new', methods=["POST"])
def posts_new(user_id):
    """Handles submission for new post"""

    user = User.query.get_or_404(user_id)
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    new_post = Post(title=request.form['title'],
                    content=request.form['content'],
                    user=user,
                    tags=tags)

    db.session.add(new_post)
    db.session.commit()

    return redirect(f"/{user_id}")


@app.route('<int:post_id>')
def posts_show(post_id):
    """show a post"""

    post = Post.query.get_or_404(post_id)
    return render_template('show_post.html', post=post)


@app.route('<int:post_id>/edit')
def posts_edit(post_id):
    """Show form to edit a post"""

    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template('edit_post.html', post=post, tags=tags)


@app.route('<int:post_id>/edit', methods=["POST"])
def posts_update(post_id):
    """Handles submission for editting a post"""

    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    tag_ids = [int(num) for num in request.form.getlist("tags")]
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    db.session.add(post)
    db.session.commit()

    return redirect(f"{post.user_id}")


@app.route('<int:post_id>/delete', methods=["POST"])
def posts_destroy(post_id):
    """Handles submission for deleting a post"""

    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()

    return redirect(f"{post.user_id}")



######################## tags ###########################

@app.route('/tags')
def tags_index():
    """Show a page with info on all tags"""

    tags = Tag.query.all()
    return render_template('tags_index.html', tags=tags)


@app.route('/tags/new')
def tags_new_form():
    """Show a form to create a new tag"""

    posts = Post.query.all()
    return render_template('nww_tags.html', posts=posts)


@app.route("/tags/new", methods=["POST"])
def tags_new():
    """Handle form submission for creating a new tag"""

    post_ids = [int(num) for num in request.form.getlist("posts")]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    new_tag = Tag(name=request.form['name'], posts=posts)

    db.session.add(new_tag)
    db.session.commit()

    return redirect("/tags")


@app.route('/tags/<int:tag_id>')
def tags_show(tag_id):
    """Show a page with info on a specific tag"""

    tag = Tag.query.get_or_404(tag_id)
    return render_template('show_tags.html', tag=tag)


@app.route('/tags/<int:tag_id>/edit')
def tags_edit_form(tag_id):
    """Show a form to edit an existing tag"""

    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('edit_tags.html', tag=tag, posts=posts)


@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def tags_edit(tag_id):
    """Handle form submission for updating an existing tag"""

    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['name']
    post_ids = [int(num) for num in request.form.getlist("posts")]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()

    return redirect("/tags")


@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def tags_destroy(tag_id):
    """Handle form submission for deleting an existing tag"""

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()

    return redirect("/tags")



if __name__ == "__main__":
    app.run(debug=True)