from flask import Flask
from flask import render_template
from flask import request
from config import true_pass

import sqlite3

app = Flask(__name__)

# итоговый вариант блога

@app.route('/')
@app.route('/index/')
def index():
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()

    cur.execute("""select hello, about from main;""")
    for hello, about_me in cur.fetchall():
        context = {'hello': hello, 'about_me': about_me}
    conn.close()
    context['active'] = 'index'

    return render_template('index.html', **context)


@app.route('/blog/')
def blog():
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()

    cur.execute("""select head, story, image from blog where visible == ?;""", (True,))
    stories = []
    for head, text, image in cur.fetchall():
        stories.append({'head': head, 'text': text, 'image': image, })
    conn.close()

    context = {'stories': stories,
               'active': 'blog'}
    return render_template('blog.html', **context)

@app.route('/about/')
def about():
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()
    cur.execute("""select contact from contacts;""")

    contacts = []

    for contact in cur.fetchall():
        contacts.append(contact[0])
    conn.close()

    context = {'contacts': contacts,
               'active': 'about'}
    return render_template('about.html', **context)


@app.route('/secret/')
@app.route('/secret/<name>/')
def secret(name=None):
    secret_text = {'John': 'Это послание для тебя. Под тремя камнями я спрятал клад',
                   'Вероника': 'Эта глава станет доступна, если ты пришлешь мне тайное сообщение, ты знаешь какое',
                   'Nemo': 'Они всё ещё не починили двигатель, поторопи их!'
                   }

    no_name = """
    <h1>Привет, незнакомец!</h1>
    <p>Тебе сюда: <a href="/">Главная</a></p>
    """

    start_html = '<h1>Рад тебя видеть на моём сайте, '
    end_html = '<p>Проходи <a href="/">по ссылке</a></p>'

    if secret_text.get(name) is None:
        return no_name
    else:
        return start_html + name + '<h1><p>' + secret_text[name] + '</p>' + end_html



@app.route('/edit/', methods = ['GET', 'POST'])
@app.route('/edit/<int:db_id>/')
def edit(db_id=None):
    if request.method == 'POST':
        if request.form.get('password') != true_pass:
            return 'Доступ закрыт, залогинтесь'

        db_id = request.form.get('db_id')
        head = request.form.get('head')
        story = request.form.get('story')
        image = request.form.get('image')
        visible = True if request.form.get('visible') else False


        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()

        cur.execute("""update blog set head = ?, story = ?, image =?, visible = ? where id == ?;""",
                    (head, story, image, visible, db_id))
        conn.commit()
        conn.close()

        return """<h2>Информация обновлена</h2> <a href='/'>Главная</a>"""

    if db_id is None:
        return "Введи номер истории"

    # Получаем истории из бд
    conn = sqlite3.connect('db.sqlite')
    cur = conn.cursor()

    cur.execute("""select id, head, story, image, visible from blog where id == ?;""",
                (db_id,))

    context = None

    for db_id, head, story, image, visible in cur.fetchall():
        context = {'db_id': db_id, 'head': head, 'story': story, 'image': image, 'visible': visible}
    conn.close()

    if context is None:
        return 'Такой записи нет'
    context['do'] = 'edit'

    return render_template('form.html', **context)


@app.route('/add/', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        if request.form.get('password') != true_pass:
            return 'Доступ закрыт, залогинтесь'

        head = request.form.get('head')
        story = request.form.get('story')
        image = request.form.get('image')
        visible = True if request.form.get('visible') else False


        conn = sqlite3.connect('db.sqlite')
        cur = conn.cursor()

        cur.execute("""insert into blog (head, story, image, visible) values (?,?,?,?);""",
                    (head, story, image, visible))
        conn.commit()
        conn.close()

        return """<h2>Информация добавлена</h2> <a href='/'>Главная</a>"""

    context = {'db_id': 'Заполняется автоматически', 'head': 'Заголовок', 'text': 'История',
               'image': 'файл изображения', 'visible': True, 'do': 'add'}

    return render_template('form.html', **context)


if __name__ == '__main__':
    app.run()
