from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from mysql_util import MysqlUtil
from passlib.hash import sha256_crypt
from functools import wraps
import time
from forms import RegisterForm,ArticleForm

app = Flask(__name__)

# 首页
@app.route('/')
def index():
    return render_template('home.html')

# 关于我们
@app.route('/about')
def about():
    return render_template('about.html')

# 笔记列表
@app.route('/articles')
def articles():
    db = MysqlUtil()
    sql = 'SELECT * FROM articles  ORDER BY create_date DESC'
    articles = db.fetchall(sql)
    if articles :
        return render_template('articles.html', articles=articles)
    else:
        msg = '暂无笔记'
        return render_template('articles.html', msg=msg) # 渲染模板

# 笔记详情
@app.route('/article/<string:id>/')
def article(id):
    db = MysqlUtil()
    sql = "SELECT * FROM articles WHERE id = '%s'" % (id)
    article = db.fetchone(sql)
    return render_template('article.html', article=article)


# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        # 获取字段内容
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        db = MysqlUtil()
        sql = "INSERT INTO users(email,username,password) \
               VALUES ('%s', '%s', '%s')" % (email,username,password)
        db.insert(sql)

        flash('您已注册成功，请先登录', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if "logged_in" in session:
        return redirect(url_for("dashboard"))

    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        sql = "SELECT * FROM users  WHERE username = '%s'" % (username)
        db = MysqlUtil()
        result = db.fetchone(sql)
        if result :
            password = result['password']
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                flash('登录成功！', 'success')
                return redirect(url_for('dashboard'))
            else:  # 如果密码错误
                error = '用户名和密码不匹配'
                return render_template('login.html', error=error)
        else:
            error = '用户名不存在'
            return render_template('login.html', error=error)
    return render_template('login.html')

# 如果用户已经登录
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('无权访问，请先登录', 'danger')
            return redirect(url_for('login'))
    return wrap

# 退出
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('您已成功退出', 'success')
    return redirect(url_for('login'))

# 控制台
@app.route('/dashboard')
@is_logged_in
def dashboard():
    db = MysqlUtil()
    sql = "SELECT * FROM articles WHERE author = '%s' ORDER BY create_date DESC" % (session['username'])
    result = db.fetchall(sql)
    if result:
        return render_template('dashboard.html', articles=result)
    else:
        msg = '暂无笔记信息'
        return render_template('dashboard.html', msg=msg)

# 添加笔记
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        content = form.content.data
        author = session['username']
        create_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        db = MysqlUtil()
        sql = "INSERT INTO articles(title,content,author,create_date) \
               VALUES ('%s', '%s', '%s','%s')" % (title,content,author,create_date) # 插入数据的SQL语句
        db.insert(sql)
        flash('创建成功', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)


# 编辑笔记
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    db = MysqlUtil()
    fetch_sql = "SELECT * FROM articles WHERE id = '%s' and author = '%s'" % (id,session['username'])
    article = db.fetchone(fetch_sql)
    if not article:
        flash('ID错误', 'danger')
        return redirect(url_for('dashboard'))
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = request.form['title']
        content = request.form['content']
        update_sql = "UPDATE articles SET title='%s', content='%s' WHERE id='%s' and author = '%s'" % (title, content, id,session['username'])
        db = MysqlUtil()
        db.update(update_sql)
        flash('更改成功', 'success')
        return redirect(url_for('dashboard'))

    # 从数据库中获取表单字段的值
    form.title.data = article['title']
    form.content.data = article['content']
    return render_template('edit_article.html', form=form)

# 删除笔记
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    db = MysqlUtil()
    sql = "DELETE FROM articles WHERE id = '%s' and author = '%s'" % (id,session['username'])
    db.delete(sql)
    flash('删除成功', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)