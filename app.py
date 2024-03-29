from SimpleTM import SimpleTM
import hashlib
import flask
from flask import request, jsonify, render_template, send_file, flash, redirect, url_for
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
import flask_login
from forms import RegistrationForm, NewGameForm, UpdatePermissionForm, DeleteGameForm, UpdateTokenForm
from config import Config
from permission import must_has_permission, Permission
import secrets
import os

# change this if deployed to a different domain
PROTOCAL = 'https'
BASE_URL = "simpletm.jscrosoft.com"
if 'PROTOCAL' in os.environ and os.environ['PROTOCAL']:
    PROTOCAL = os.environ['PROTOCAL']
if 'BASE_URL' in os.environ and os.environ['BASE_URL']:
    BASE_URL = os.environ['BASE_URL']

def hash(s):
    return hashlib.sha256(s.encode()).hexdigest()

def genToken(k=32):
    return secrets.token_urlsafe(k)

def get_secret_key():
    f = open('.secret', 'r')
    return f.read().strip()

def make_shared_url(user, apitoken, game):
    return f'simpletm://{PROTOCAL}/{BASE_URL}/{user}/{apitoken}/{game}'

app = flask.Flask(__name__)
app.secret_key = get_secret_key()
CORS(app)
auth = HTTPBasicAuth()
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

def verify_password(username, password):
    db = SimpleTM(Config.dbFileName)
    user = db.GetUser(username)
    if user and user[0] == username and user[1] == hash(password):
        return username

@auth.verify_password
def verify_token(username, token):
    db = SimpleTM(Config.dbFileName)
    tokens = db.GetUserAPIToken(username)
    print(tokens)
    if tokens and tokens[0][0] == token:
        return username

@auth.error_handler
def error_handler(status):
    em = {401:'Unauthorized', 403:'Forbidden'}
    m = status
    try:
        m = em[status]
    except:
        pass
    return jsonify(Result='False', Message=str(m))

class User(flask_login.UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def user_loader(user_id):
    db = SimpleTM(Config.dbFileName)
    user_record = db.QueryUser(user_id)
    if not user_record:
        return
    user = User(user_id)
    return user

@login_manager.request_loader
def request_loader(request):
    db = SimpleTM(Config.dbFileName)
    user_id = request.form.get('username')
    user_record = db.QueryUser(user_id)
    if not user_record:
        return
    user = User(user_id)
    return user
    

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        db = SimpleTM(Config.dbFileName)
        try:
            db.AddUser(username, hash(password), genToken())
            flash('注册成功', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(str(e), 'danger')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = verify_password(request.form['username'], request.form['password'])
        if user_id:
            flask_login.login_user(User(user_id))
            return redirect(url_for('home'))
        else:
            flash('用户名或密码不正确', 'danger')
    return render_template('login.html')

@app.route('/home', methods=['GET','POST'])
@flask_login.login_required
def home():
    form = NewGameForm(request.form)
    user = flask_login.current_user.id
    db = SimpleTM(Config.dbFileName)
    if request.method == 'POST' and form.validate_on_submit():
        gid = form.gid.data
        description = form.description.data
        print(gid, description)
        if '/' in gid:
            flash(f"项目名不能包含/", "danger")
        else:
            try:
                db.AddGameAsUser(user, gid, description)
                flash(f"项目{gid}创建成功", "success")
            except Exception as e:
                print(e)
                flash("该项目已存在，请换一个项目名", "danger")
    token = db.GetUserAPIToken(user)[0][0]
    tform = UpdateTokenForm()
    games = db.GetGamesByUser(user)
    pforms, dforms = {}, {}
    gameUsers = {}
    for g in games:
        pforms[g['game_id']] = UpdatePermissionForm()
        dforms[g['game_id']] = DeleteGameForm()
        gameUsers[g['game_id']] = db.GetUsersByGame(g['game_id'])
    return render_template('home.html', user=user, token=token,
         projects=games, form=form, pforms=pforms, tform=tform,
        dforms=dforms, gameUsers=gameUsers)

@app.route('/project/<string:game>', methods=['GET'])
@flask_login.login_required
def project(game):
    try:
        user = flask_login.current_user.id
        db = SimpleTM(Config.dbFileName)
        token = db.GetUserAPIToken(user)[0][0]
        return render_template('project.html', user=user, game=game, token=token, base_url=f"{PROTOCAL}://{BASE_URL}")
    except Exception as e:
        flash(str(e), "danger")
        return render_template('index.html')

@app.route('/home/updatePermission', methods=['POST'])
@flask_login.login_required
def update_permission():
    form = UpdatePermissionForm(request.form)
    user = flask_login.current_user.id
    try:
        if form.validate_on_submit():
            db = SimpleTM(Config.dbFileName)
            gid = form.gid.data
            must_has_permission(user, gid, Permission.ADMIN)
            target_uid = form.uid.data
            if user == target_uid:
                raise RuntimeError("不能更改自己的权限")
            target_perm = form.perm.data
            print(target_uid, gid, target_perm)
            if target_perm == 3 and target_uid[0] == '_':
                raise RuntimeError("不能将由系统托管的用户设为管理员")
            assert db.UpdatePermission(target_uid, gid, target_perm)
            if target_perm == 0 and target_uid[0] == '_':
                db.DeleteUser(target_uid)
            flash(f'成功更改项目{gid}中用户{target_uid}的权限', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('home'))

@app.route('/home/deleteGame', methods=['POST'])
@flask_login.login_required
def delete_game():
    form = DeleteGameForm(request.form)
    user = flask_login.current_user.id
    try:
        if form.validate_on_submit():
            db = SimpleTM(Config.dbFileName)
            gid = form.gid.data
            must_has_permission(user, gid, Permission.ADMIN)
            db.DeleteGame(gid)
            flash(f'已删除项目{gid}', 'success')
            
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('home'))

@app.route('/home/updateToken', methods=['POST'])
@flask_login.login_required
def update_token():
    form = UpdateTokenForm(request.form)
    user = flask_login.current_user.id
    try:
        if form.validate_on_submit():
            db = SimpleTM(Config.dbFileName)
            uid = form.uid.data
            assert db.UpdateToken(uid, genToken())
            flash(f'已更新API Token', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('home'))

@app.route('/home/generateShareURL/<string:game>', methods=['GET'])
@flask_login.login_required
def generate_share_url(game):
    try:
        user = flask_login.current_user.id
        temp_user = f'_{user}_share_{genToken(8)}'
        temp_user_password = genToken(8)
        temp_user_token = genToken()
        temp_user_permission = 2 # read/write
        db = SimpleTM(Config.dbFileName)
        db.AddUser(temp_user, hash(temp_user_password), temp_user_token)
        db.UpdatePermission(temp_user, game, temp_user_permission)
        flash(f'请保存分享链接：{make_shared_url(temp_user, temp_user_token, game)}', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('home'))   

@app.route('/logout')
def logout():
    flask_login.logout_user()
    flash('已登出', 'primary')
    if flask_login.current_user.is_authenticated:
        print('still authed')
    return redirect(url_for('index'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    flash('请先登录', 'warning')
    return redirect(url_for('login'))

@app.route('/api/querybygame/<string:game>', methods=['GET'])
@auth.login_required
def api_querybygame(game):
    try:
        must_has_permission(auth.current_user(), game, Permission.READ)
        SimpleTMObj = SimpleTM(Config.dbFileName)
        ret = SimpleTMObj.QueryByGame(game)
        SimpleTMObj.Close()
        json_lst = []
        for line in ret:
            tmp_json_dict = {}
            tmp_json_dict['raw'] = line[0]
            tmp_json_dict['translate'] = line[1]
            json_lst.append(tmp_json_dict)
        return jsonify(json_lst)
    except Exception as e:
        return jsonify(Result='False', Message=str(e))


@app.route('/api/insert/<string:game>/<string:rawWord>/<string:translate>', methods=['GET'])
@auth.login_required
def api_insert(game, rawWord, translate):
    try:
        must_has_permission(auth.current_user(), game, Permission.EDIT)
        SimpleTMObj = SimpleTM(Config.dbFileName)
        ret = SimpleTMObj.AddTranslation(rawWord, translate, game)
        SimpleTMObj.Close()
        if ret == True:
            return jsonify(Result='True', Message='')
        else:
            return jsonify(Result='False', Message='')
    except Exception as e:
        return jsonify(Result='False', Message=str(e))


@app.route('/api/update/<string:game>/<string:rawWord>/<string:translate>', methods=['GET'])
@auth.login_required
def api_update(game, rawWord, translate):
    try:
        must_has_permission(auth.current_user(), game, Permission.EDIT)
        SimpleTMObj = SimpleTM(Config.dbFileName)
        ret = SimpleTMObj.UpdateTranslation(rawWord, translate, game)
        SimpleTMObj.Close()
        if ret == True:
            return jsonify(Result='True', Message='')
        else:
            return jsonify(Result='False', Message='')
    except Exception as e:
        return jsonify(Result='False', Message=str(e))
    
@app.route('/api/delete/<string:game>/<string:rawWord>', methods=['GET'])
@auth.login_required
def api_delete(game, rawWord):
    try:
        must_has_permission(auth.current_user(), game, Permission.EDIT)
        SimpleTMObj = SimpleTM(Config.dbFileName)
        ret = SimpleTMObj.DeleteTranslation(rawWord, game)
        SimpleTMObj.Close()
        if ret == True:
            return jsonify(Result='True', Message='')
        else:
            return jsonify(Result='False', Message='')
    except Exception as e:
        return jsonify(Result='False', Message=str(e))


@app.route('/maintain/upload')
@flask_login.login_required
def api_maintain_upload():
    return render_template("file_upload_form.html")


@app.route('/maintain/success', methods=['POST'])
@flask_login.login_required
def api_maintain_upload_success():
    try:
        if request.method == 'POST':
            f = request.files['file']
            f.save(Config.dbFileName)
            return render_template("success.html", name=f.filename)
        else:
            return jsonify(Result='False', Message='Not a POST action!')
    except Exception as e:
        return jsonify(Result='False', Message=str(e))


@app.route('/maintain/download')
@flask_login.login_required
def api_maintain_download():
    try:
        return send_file(Config.dbFileName, attachment_filename='TM.db')
    except Exception as e:
        return jsonify(Result='False', Message=str(e))


if __name__ == '__main__':
    app.run(host="0.0.0.0")
