
# # A very simple Flask Hello World app for you to get started with...

# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello from Flask!'


#!/usr/bin/python3
#从 flask 模块中引入 request 对象，request 对象中的属性 files 记录了上传文件的相关信息
#从 flask 模块中引入函数 send_from_directory，该函数用于实现下载文件
from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for
from flask import Flask, render_template, request, redirect, url_for, flash, abort
#log-in model
from flask_login import (LoginManager, UserMixin, login_user, logout_user,
                            current_user, login_required, fresh_login_required)
import os
import pandas as pd

app = Flask(__name__)
#flask error solved!!
app.config['SECRET_KEY'] = '123456'
app.debug=True




#log in model
login_manager = LoginManager(app)
# 设置登录视图的名称，如果一个未登录用户请求一个只有登录用户才能访问的视图，（打注解，受保护）
# 则闪现一条错误消息，并重定向到这里设置的登录视图。
# 如果未设置登录视图，则直接返回401错误。
login_manager.login_view = 'login'
# 设置当未登录用户请求一个只有登录用户才能访问的视图时，闪现的错误消息的内容，
# 默认的错误消息是：Please log in to access this page.。
login_manager.login_message = 'please login first'
# 设置闪现的错误消息的类别
login_manager.login_message_category = "info"

users = [
    {'username': 'Tom', 'password': '111111'},
    {'username': 'aaa', 'password': 'aaa'},
    {'username': 'Michael', 'password': '123456'}
]


class User(UserMixin):
    pass

# 通过用户名，获取用户记录，如果不存在，则返回None
def query_user(username):
    for user in users:
        if user['username'] == username:
            return user

# 如果用户名存在则构建一个新的用户类对象，并使用用户名作为ID
# 如果不存在，必须返回None
# 它是一个回调函数，在每次请求过来后，Flask-Login都会从Session中寻找”user_id”的值，
# 如果找到的话，就会用这个”user_id”值来调用此回调函数，并构建一个用户类对象
@login_manager.user_loader  #回掉函数
def load_user(username):
    if query_user(username) is not None:
        curr_user = User()
        curr_user.id = username
        return curr_user
    # Must return None if username not found


# #@login_required装饰器对于未登录用户访问的默认处理是重定向到登录视图，如
# #果我们不想它这么做的话，可以自定义处理方法：
# @login_manager.unauthorized_handler
# def unauthorized_handler():
#     return 'Unauthorized'



# #注解，确保只有登录用户才能访问这个index视图，
# #Flask-Login帮我们实现了这个装饰器。如果用户未登录，它就会将页面重定向到登录视图
# @app.route('/')
# @login_required
# def index():
#     return render_template('hello.html')

#当用户通过账号和密码登录后，Flask-Login会将其标识为Fresh登录
#而用户通过”Remember Me”自动登录的话，则不标识为Fresh登录
#有些情况下，我们会强制要求用户登录一次，比如修改登录密码，
#这时候，我们可以用@fresh_login_required装饰器来修饰该视图
@app.route('/home')
@fresh_login_required
def home():
    return 'Logged in as: %s' % current_user.get_id()


#登录按键
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #由登录名得到用户实例
        username = request.form.get('username')
        user = query_user(username)
        # 验证表单中提交的用户名和密码
        if user is not None and request.form['password'] == user['password']:
            curr_user = User()
            curr_user.id = username

            # 通过Flask-Login的login_user方法登录用户
            login_user(curr_user, remember=True)

            # 如果请求中有next参数，则重定向到其指定的地址，
            # 没有next参数，则重定向到"index"视图
            next = request.args.get('next')
            return redirect(next or url_for('index'))
        #错误用户名
        flash('Wrong username or password!')
    # GET 请求
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return 'Logged out successfully!'











#首页
@app.route('/')
@login_required
def index():
	#设置访问路径 / 时，使用函数 index 进行处理，函数 index 列出目录 upload 下所有的文件名，作为参数传给首页的模板 index.html
	#在首页 index.html 中根据 entries 显示每个文件的下载链接。
	#absulote path!!!!
    entries = os.listdir("/home/chaos16/myMalDect/upload")
    return render_template('index.html', entries = entries)

#上传
#设置访问路径 /upload 时，使用函数 upload 进行处理。
#函数 upload 从 request 对象中获取上传的文件信息，request.files 是一个字典，使用表单中的文件字段名作为索引。
@app.route('/upload', methods=['POST'])
@login_required
def upload():
    #files = request.files['files']
    files = request.files.getlist('files')

    for f in files:
        if f.filename == '':
            flash('please selected file!')
            return redirect(url_for('index'))

    # if not len(files):
    #     flash('please selected file!')
    #     return redirect(url_for('index'))

    for f in files:
        if not allowed_file(f.filename):
            flash('file type error!')
            return redirect(url_for('index'))

    for f in files:
        #设置保存路径
        path = os.path.join('/home/chaos16/myMalDect/upload', f.filename)
        #保存文件
        f.save(path)

    #跳转至上传成功界面
    return render_template('upload.html')



    #单一文件单上传
    # f = request.files['file']

    # if f.filename == '':
    #     flash('No selected file')
    #     #return redirect(request.url)
    #     return redirect(url_for('index'))

    # if not allowed_file(f.filename):
    #     flash('file type error!')
    #     #return redirect(request.url)
    #     return redirect(url_for('index'))

    # #设置保存路径
    # path = os.path.join('/home/chaos16/myMalDect/upload', f.filename)
    # #保存文件
    # f.save(path)
    # #跳转至上传成功界面
    # return render_template('upload.html')

#type select
def allowed_file(filename):
    #file type
    ALLOWED_EXTENSIONS = set(['apk','txt'])
    # 获取文件扩展名，以'.'为右分割然后取第二个值
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


#下载
#每个文件都有一个下载链接，形式为 /files/ 文件名，假如文件名为 test.txt，则下载链接为 /files/test.txt。
@app.route('/files/<filename>')
#函数 files 调用 send_from_directory 将 upload 目录下的文件发送给客户，as_attachment=True 表示文件作为附件下载
def files(filename):
    return send_from_directory('/home/chaos16/myMalDect/upload', filename, as_attachment=True)


#响应检测按键
@app.route('/check')
@login_required
def check():

    #提取quanxian
    print("before extract")
    extract()

    #获取权限
    results=get_results()
    #获取文件名
    apk_name_list=get_apk_name_list()

    #print(apk_name_list)
    return render_template('details.html',results=results,apk_name_list=apk_name_list)

def get_apk_name_list():
    #注意中文编码的问题
    apk_name_list = pd.read_csv('/home/chaos16/myMalDect/permissions/apk_name_list.csv',encoding='gbk')
    apk_name_list=apk_name_list.columns.values
    return apk_name_list


#用3种模型进行检测并返回结果
def get_results():
    import sys
    import numpy as np
    sys.path.append(r'/home/chaos16/myMalDect/classifier/knn')
    sys.path.append(r'/home/chaos16/myMalDect/classifier/BN')
    sys.path.append(r'/home/chaos16/myMalDect/classifier/dt')
    '''python import模块时， 是在sys.path里按顺序查找的。
    sys.path是一个列表，里面以字符串的形式存储了许多路径。
    使用A.py文件中的函数需要先将他的文件路径放到sys.path中'''

    #1
    import knn
    results_knn=knn.knn_classifier()

    #2
    import nb
    results_nb=nb.nb_classifier()

    #3
    import dt
    results_dt=dt.dt_classifier()

    results=np.append(results_knn,results_nb,axis=0)
    results=np.append(results,results_dt,axis=0)
    # 3*n矩阵
    results=results.T
    print(results)
    return results

#提取权限，得到csv矩阵
def extract():
    #coding:utf-8
    '''
    simple demo of extracting apk permission list
    the result will be saved in the "permission_list.csv"
    please put all apk file in the "source_apk" folder
    '''
    from androguard.core.bytecodes.apk import APK
    import os
    import pandas as pd
    import numpy as np

    #input:apk文件所在目录
    #output：apk文件名列表
    def file_name(file_dir):
        file_list = []
        for root, dirs, files in os.walk(file_dir):
            file_list.append(files)
        return file_list[0]

    #找到权限字典163维度模板：
    permissions = pd.read_csv('/home/chaos16/myMalDect/permissions/permissions_extract0.csv')
    permissions_columns=permissions.columns.values


    #遍历upload文件夹
    file_list = file_name('/home/chaos16/myMalDect/upload')
    print('processing...')

    #apk——name记录文件
    f_apk_name = open('/home/chaos16/myMalDect/permissions/apk_name_list.csv','w')

    #记录apk文件总个数，一个写入一行
    apk_counter=0
    for apk in file_list:
        #添加全0行
        permissions.loc[apk_counter] = 0
        print(apk_counter,"finish")
        #得到apk文件路径
        apk_path = APK('/home/chaos16/myMalDect/upload/' + apk)
        #得到每个apk文件的权限list
        permissions_ofapk = apk_path.get_permissions()

        #遍历apk文件的声明权限列表，若在模板中有，则写为1，否则默认为0
        for permission_index in permissions_ofapk:
            if permission_index in permissions_columns:
                permissions.loc[apk_counter,permission_index]=1

        #apk名称写入文件
        f_apk_name.write(apk+',')
        apk_counter=apk_counter+1


    #程序正确，人工检测一遍！！！！！！！！！！！！
    permissions.to_csv('/home/chaos16/myMalDect/permissions/permissions_extract.csv',index=False)

    print('finish_extract!')
























