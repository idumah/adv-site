from flask import Flask, render_template, redirect, request, make_response
from flask import session
from data.users import User
from data.news import News
from data.favourites import Favourites
from forms.user import RegisterForm
from forms.loginform import LoginForm
from forms.news import NewsForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter()
    if current_user.is_authenticated:
        favs = [int(i.post_id) for i in db_sess.query(Favourites).filter(Favourites.user_id == current_user.id)]
    else:
        favs = []
    return render_template("index.html", news=news, title='Главная страница', favs=favs)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Новое объявление',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование объявления',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/favourites')
def favourite_posts():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        favourites = db_sess.query(Favourites).filter(
            (Favourites.user_id == current_user.get_user_id()))
        s = list(set([i.post_id for i in favourites]))
        res = []
        for i in s:
            res.append(db_sess.query(News).filter(News.id == i).first())
    else:
        return redirect('/')
    return render_template("favourites.html", news=res, title='Избранное')


@app.route('/add_favourite_post/<int:id>', methods=['GET', 'POST'])
@login_required
def fav_add(id):
    f = Favourites()
    f.user_id = current_user.get_user_id()
    f.post_id = id
    db_sess = db_session.create_session()
    db_sess.add(f)
    db_sess.commit()
    return redirect('/')


@app.route('/delete_favourite_post/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_favourite_post(id):
    db_sess = db_session.create_session()
    news = db_sess.query(Favourites).filter(Favourites.post_id == id,
                                            Favourites.user_id == current_user.id)
    if news:
        for i in news:
            db_sess.delete(i)
            db_sess.commit()
    else:
        abort(404)
    return redirect('/favourites')


@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if user:
        info = user.get_info()
        info[-1] = str(info[-1]).split('.')[0]
        name, email, inf, date = info
    else:
        return redirect('/not_found')
    return render_template("profile.html", name=name, email=email, info=inf, date=date,
                           title='Профиль')


@app.route('/not_found')
def not_found():
    return render_template("notfound.html")


def if_post_in_favourites(user_id, post_id):
    db_sess = db_session.create_session()
    news = db_sess.query(Favourites).filter(Favourites.post_id == post_id,
                                            Favourites.user_id == user_id)
    if news:
        return True
    else:
        return False


def main():
    db_session.global_init("db/ads.db")
    app.run()


if __name__ == '__main__':
    main()
