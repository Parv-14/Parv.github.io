from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
import smtplib

from_mail = "parvomgoyal123@gmail.com"
to_email = "zuagzuparv@gmail.com"
app_password = "uhon cjns uati bzqe"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
class NewPost(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Author's Name", validators=[DataRequired()])
    img_url = StringField("Background Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Body", validators=[DataRequired()])
    submit = SubmitField("Submit")
class EditPost(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Author's Name", validators=[DataRequired()])
    img_url = StringField("Background Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Body", validators=[DataRequired()])
    submit = SubmitField("Submit")

ckeditor = CKEditor(app)
# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    posts = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template("index.html", all_posts=posts)

@app.route('/post/<int:post_id>')
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)

@app.route("/new-post", methods=["GET","POST"])
def new_post():
    form = NewPost()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            date= date.today().strftime("%B %d, %Y"),
            body= form.body.data,
            author= form.author.data,
            img_url= form.img_url.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, is_edit=False)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    post = db.get_or_404(BlogPost, id)
    form = EditPost(
        title=post.title,
        subtitle=post.subtitle,
        author= post.author, 
        body= post.body,            
        img_url= post.img_url
    )
    if form.validate_on_submit():
        post.title=form.title.data
        post.subtitle=form.subtitle.data
        post.body= form.body.data
        post.author= form.author.data          
        post.img_url= form.img_url.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=form , is_edit=True)

@app.route("/delete/<int:id>")
def delete(id):
    post = db.get_or_404(BlogPost, id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone_number = request.form.get("phone")
        message = request.form.get("message")
        send_email(name, email, phone_number, message)
        return render_template("contact.html", msg_sent=True)
    
    return render_template("contact.html", msg_sent=False)

def send_email(name, email, phonenumber, message):
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(from_mail, app_password)
        connection.sendmail(
            from_addr=from_mail,
            to_addrs=to_email,
            msg=f"Subject:New Message\n\nName: {name}\nEmail: {email}\n Phone Number: {phonenumber}\n Message: {message}"
        )


if __name__ == "__main__":
    app.run(debug=True)

