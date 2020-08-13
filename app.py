from SimpleTM import SimpleTM
import flask
from flask import request, jsonify, render_template, send_file

app = flask.Flask(__name__)
dbFileName = 'SimpleTM.db'
@app.route('/', methods=['GET'])
def home():
    return "<h1>Just a hello world!</h1>"


@app.route('/api/query/<string:rawWord>', methods=['GET'])
def api_query(rawWord):
    try:
        SimpleTMObj = SimpleTM(dbFileName)
        ret = SimpleTMObj.Query(rawWord)
        SimpleTMObj.Close()
        json_lst = []
        for line in ret:
            tmp_json_dict = {}
            tmp_json_dict['raw:'] = line[0]
            tmp_json_dict['translate:'] = line[1]
            tmp_json_dict['game:'] = line[2]
            json_lst.append(tmp_json_dict)
        return jsonify(json_lst)
    except Exception as e:
        return jsonify(Result='False', Message=str(e))

@app.route('/api/querybygame/<string:game>', methods=['GET'])
def api_querybygame(game):
    try:
        SimpleTMObj = SimpleTM(dbFileName)
        ret = SimpleTMObj.QueryByGame(game)
        SimpleTMObj.Close()
        json_lst = []
        for line in ret:
            tmp_json_dict = {}
            tmp_json_dict['raw:'] = line[0]
            tmp_json_dict['translate:'] = line[1]
            tmp_json_dict['game:'] = line[2]
            json_lst.append(tmp_json_dict)
        return jsonify(json_lst)
    except Exception as e:
        return jsonify(Result='False', Message=str(e))


@app.route('/api/insert/<string:rawWord>/<string:translate>/<string:game>', methods=['GET'])
def api_insert(rawWord,translate,game):
    try:
        SimpleTMObj = SimpleTM(dbFileName)
        ret = SimpleTMObj.Insert(rawWord, translate, game)
        SimpleTMObj.Close()
        if ret == True:
            return jsonify(Result='True', Message='')
        else:
            return jsonify(Result='False', Message='')
    except Exception as e:
        return jsonify(Result='False', Message=str(e))


@app.route('/api/update/<string:rawWord>/<string:translate>/<string:game>', methods=['GET'])
def api_update(rawWord,translate,game):
    try:
        SimpleTMObj = SimpleTM(dbFileName)
        ret = SimpleTMObj.Update(rawWord, translate, game)
        SimpleTMObj.Close()
        if ret == True:
            return jsonify(Result='True', Message='')
        else:
            return jsonify(Result='False', Message='')
    except Exception as e:
        return jsonify(Result='False', Message=str(e))


@app.route('/maintain/upload')
def api_maintain_upload():
    return render_template("file_upload_form.html")


@app.route('/maintain/success', methods=['POST'])
def api_maintain_upload_success():
    try:
        if request.method == 'POST':
            f = request.files['file']
            f.save(dbFileName)
            return render_template("success.html", name=f.filename)
        else:
            return jsonify(Result='False', Message='Not a POST action!')
    except Exception as e:
        return jsonify(Result='False', Message=str(e))


@app.route('/maintain/download')
def api_maintain_download():
    try:
        return send_file(dbFileName, attachment_filename='TM.db')
    except Exception as e:
        return jsonify(Result='False', Message=str(e))


if __name__ == '__main__':
    app.run(host="0.0.0.0")
