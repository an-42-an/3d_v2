from flask import *
from flask_login import LoginManager, UserMixin, login_required, login_user,\
    logout_user, current_user
import csv
import os
import pickle
from argon2 import PasswordHasher, exceptions
argon2 = PasswordHasher()
app=Flask(__name__)
app.secret_key = "any key"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
games={}
deleted={}
import os
import subprocess
original_dir = os.getcwd() 
GIT_USER = os.environ['GIT_USER']
GIT_EMAIL = os.environ['GIT_EMAIL']
GIT_TOKEN = os.environ['GIT_TOKEN']
REPO = f'https://{GIT_USER}:{GIT_TOKEN}@github.com/{GIT_USER}/3d_v2.git'
REPO_DIR = os.environ.get('REPO_DIR',os.getcwd())#'/opt/render/project/src'  
# default Render working directory

def setup_git():
    subprocess.run(['git', 'config', '--global', 'user.email', GIT_EMAIL])
    subprocess.run(['git', 'config', '--global', 'user.name', GIT_USER])

def push_all_data(commit_msg='Update user data'):
    setup_git()
    os.chdir(REPO_DIR)

    # Stage users.csv
    subprocess.run(['git', 'add', 'users.csv'])

    # Stage all .dat files inside ./saved/
    for root, dirs, files in os.walk('saved'):
        for file in files:
            if file.endswith('.dat'):
                full_path = os.path.join(root, file)
                subprocess.run(['git', 'add', full_path])

    # Commit and push
    subprocess.run(['git', 'commit', '-m', commit_msg])
    subprocess.run(['git', 'push', REPO, 'main'], check=True)
    os.chdir(original_dir)

def push_everything_v1():
    setup_git()
    os.chdir(REPO_DIR)
    result = subprocess.run(['git', 'remote'], capture_output=True, text=True)
    remotes = result.stdout.strip().split('\n')
    if 'origin' not in remotes:
        subprocess.run(['git', 'remote', 'add', 'origin', REPO], check=True)
    subprocess.run(['git', 'checkout', 'main'], check=True)
    subprocess.run(['git', 'pull', 'origin', 'main', '--rebase'], check=True)
    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run(['git', 'commit', '-m', 'Update user data render'], check=True)
    subprocess.run(['git', 'push', 'origin', 'main'], check=True)
    os.chdir(original_dir)
def push_everything():
    setup_git()
    os.chdir(REPO_DIR)
    result = subprocess.run(['git', 'remote'], capture_output=True, text=True)
    remotes = result.stdout.strip().split('\n')
    if 'origin' not in remotes:
        subprocess.run(['git', 'remote', 'add', 'origin', REPO], check=True)

    subprocess.run(['git', 'checkout', 'main'], check=True)
    # Handle possible pull errors
    try:
        subprocess.run(['git', 'pull', 'origin', 'main', '--rebase'], check=True)
    except subprocess.CalledProcessError:
        # Abort rebase if stuck
        subprocess.run(['git', 'rebase', '--abort'], check=False)
        # Reset to origin/main (WARNING: This discards local changes!)
        subprocess.run(['git', 'fetch', 'origin'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main', '--force'], check=True)
    subprocess.run(['git', 'add', '.'], check=True)
    try:
        subprocess.run(['git', 'commit', '-m', 'Update user data render'], check=True)
    except subprocess.CalledProcessError:
        # No changes to commit
        pass
    subprocess.run(['git', 'push', 'origin', 'main'], check=True)
    os.chdir(original_dir)
def prep():
    setup_git()
    os.chdir(REPO_DIR)
    result = subprocess.run(['git', 'remote'], capture_output=True, text=True)
    remotes = result.stdout.strip().split('\n')
    if 'origin' not in remotes:
        subprocess.run(['git', 'remote', 'add', 'origin', REPO], check=True)
    subprocess.run(['git', 'fetch'], check=True)
    subprocess.run(['git', 'reset', '--hard', 'origin/main'], check=True)
    os.chdir(original_dir)
def later():
    os.chdir(REPO_DIR)
    subprocess.run(['git', 'checkout', 'main'], check=True)
    subprocess.run(['git', 'add', '.'], check=True)
    try:
        subprocess.run(['git', 'commit', '-m', 'Update user data render'], check=True)
    except subprocess.CalledProcessError:
        # No changes to commit
        pass
    subprocess.run(['git', 'push', 'origin', 'main'], check=True)
    os.chdir(original_dir)
prep()
f=open('users.csv','r',newline='')
k=csv.reader(f)
u=[a[0] for a in k]
f.close()
c=0
for a in u:
    try:
        f=open(f'./saved/%s/games.dat'%(a,),'ab')
        f.close()
    except:
        c=1
        os.mkdir(f'./saved/%s'%(a,))
        f=open(f'./saved/%s/games.dat'%(a,),'wb')
        f.close()
if c:
    later()

class User(UserMixin):
    def __init__(self, id,pwd):
        self.id = id
        self.pwd = pwd    
    def __repr__(self):
        return "%s/%s" % (self.id, self.pwd)

def createlist():
    return [[['' if b==5 and c==0 else ' ' for a in range(7)] for b in range(6)] for c in range(5)]

def dfs(surf,row,cell,game,d):
    print(d)
    #print(surf,row,cell)
    p=games[game][1][surf][row][cell]    
    for a in range(4):
        try:
            if games[game][1][surf][row][cell]!=p:
                print('if',surf,row,cell)
                break
            else:
                surf+=d[0]
                row-=d[1]
                cell+=d[2]
        except Exception as e:
            #print(e)
            break

    for a in range(1,5):
        try:
            if games[game][1][surf-a*d[0]][row+a*d[1]][cell-a*d[2]]!=p:
                raise ValueError
        except Exception as e:
            #print(e)
            return 0,0,0
    else:
        print('return',surf,row,cell)
        return surf,row,cell        

def checkwin(surf,row,cell,game):
    directions = [
        (1, 0, 0),  # x (col)
        (0, 1, 0),  # y (row)
        (0, 0, 1),  # z (surf)
        (1, 1, 0),  # diagonal on x-y
        (1, 0, 1),  # diagonal on x-z
        (0, 1, 1),  # diagonal on y-z
        (1, -1, 0), # reverse diag x-y
        (1, 0, -1), # reverse diag x-z
        (0, 1, -1), # reverse diag y-z
        (1, 1, 1),  # diagonal across all 3
        (1, -1, -1), # reverse diag across all 3
        (1,1,-1),
        (1,-1,1)
    ]
    for d in directions:
        ns,nr,nc=dfs(surf,row,cell,game,d)
        if ns or nr or nc:
            return ns, nr, nc,d
    return 0,0,0,0

def winlist(ns,nr,nc,d):
    l=[]
    for a in range(1,5):
        l.append((ns-a*d[0],nr+a*d[1],nc-a*d[2]))
    print(l)
    return l

@app.route('/',methods=['GET','POST'])
def login():
    if request.method=='GET':
        '''f=open('users.csv','r',newline='')
        k=csv.reader(f)
        u=[a for a in k]
        f.close()
        print(u)'''
        return render_template('login.html',msg="Enter your login credentials")
    else:
        f=open('users.csv','r',newline='',encoding='utf-8')
        k=csv.reader(f)
        u=[a for a in k]
        f.close()
        user=request.form.get('user')
        pwd=request.form.get('pwd')
        for saved_user, saved_hash in u:
            if user == saved_user:
                try:
                    if argon2.verify(saved_hash,pwd):
                        login_user(User(user, saved_hash))
                        return redirect(f'/home/{user}')
                except:
                    pass

        return render_template('login.html', msg="Invalid credentials. Enter correct details")


@app.route('/create',methods=['GET','POST'])
def create():
    if request.method=='GET':
        f=open('users.csv','r',newline='',encoding='utf-8')
        k=csv.reader(f)
        u=[a for a in k]
        f.close()
        #print(u)
        return render_template('create.html',u=u)
    elif request.method=='POST':
        #return 'done'
        prep()
        user=request.form['user']
        pwd=request.form['pwd']
        hashpwd = argon2.hash(pwd)
        f=open('users.csv','r',newline='',encoding='utf-8')
        k=csv.reader(f)
        u=[a for a in k]
        f.close()
        if user in [a[0] for a in u]:
            return render_template('create.html',u=u)
        for a in user:
            if a.isalpha() or a.isdigit():
                pass
            else:
                return render_template('create.html',u=u)
        f=open('users.csv','a',newline='',encoding='utf-8')
        k=csv.writer(f)
        k.writerow([user,hashpwd])
        f.close()
        try:
            os.mkdir(f'./saved/%s'%(user,))
        except:
            pass
        f=open(f'./saved/%s/games.dat'%(user,),'wb')
        f.close()
        later()
        login_user(User(user,hashpwd))
        return redirect(f'/home/%s'%(user,))

@login_manager.user_loader
def load_user(id):
    with open('users.csv', 'r', newline='') as f:
        k = csv.reader(f)
        for row in k:
            if row[0] == id:
                return User(row[0], row[1])
    return None
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')

@app.route('/home/<id>')
@login_required
def home(id):
    if current_user.id != id:
        return redirect('/')
    return render_template('home.html',id=id)
@app.route('/new/<id>',methods=['GET','POST'])
@login_required
def new(id):
    if current_user.id != id:
        return redirect('/')
    if request.method=='GET':
        return render_template('new.html',msg='Create a new game',id=id)
    else:
        game=request.form['game']
        for a in game:
            if a.isalpha() or a.isdigit():
                pass
            else:
                return render_template('new.html',id=id,msg='No special characters')
        if game in games:
            return render_template('new.html',msg='Already exists. Give a different name',id=id)
        games[game]=[{id:'X'},createlist(),id,0]
        deleted[game]=[]
        #print(games)
        return redirect(f'/join/%s/%s'%(id,game))
    
@app.route('/join/<id>',methods=['GET','POST'])
@login_required
def join(id):
    if current_user.id != id:
        return redirect('/')
    if request.method=='GET':
        g=[]
        for game in games:
            if id in games[game][0]:
                g.append(game)
            elif len(games[game][0])<2:
                g.append(game)
        return render_template('games.html',g=g,id=id)
    else:
        game=request.form['game']
        if id in games[game][0]:
            return redirect(f'/join/%s/%s'%(id,game))
        if len(games[game][0])<2:
            games[game][0][id]='O'
            return redirect(f'/join/%s/%s'%(id,game))
        g=[]
        for game in games:
            if len(games[game][0])<2:
                g.append(game)
        return render_template('games.html',g=g,id=id)
    
@app.route('/join/<id>/<game>',methods=['GET','POST'])
@login_required
def gamefn(id,game):
    if games[game][3]!=0:
        return render_template('over.html',game=game,board=games[game][1],\
                               l=games[game][3],id1=id,p=games[game][0])
    if current_user.id != id:
        return redirect('/')
    try:
        move = request.args['move'] 
        surf, row, cell = map(int, move.split(','))
        if games[game][1][surf][row][cell]!='':
            return redirect(f'/join/{id}/{game}')
        if id==games[game][2]:
            return redirect(f'/join/{id}/{game}')
        games[game][1][surf][row][cell]=games[game][0][id]
        try:
            games[game][1][surf+1][row][cell]=''
        except:
            pass
        if row>0 and surf==0:
            games[game][1][surf][row-1][cell]=''
        games[game][2]=id #request.args.get('user')
        print(surf,row,cell)
        ns,nr,nc,d=checkwin(surf,row,cell,game)
        if ns or nr or nc:
            l=winlist(ns,nr,nc,d)
            games[game][3]=l
        return redirect(f'/join/{id}/{game}')
    except Exception as e:
        if id==games[game][2]:
            print(e)
            return render_template('gamenot.html',game=game,board=games[game][1],id1=id,\
                                   p=games[game][0])
        return render_template('game.html',game=game,board=games[game][1],id1=id,p=games[game][0])

@app.route('/delete/<id>/<game>',methods=['GET','POST'])
@login_required
def deleting(id,game):
    if current_user.id != id:
        return redirect('/')
    if id in games[game][0] and id not in deleted[game]:
        deleted[game].append(id)        
    if len(deleted[game])==2:
        deleted.pop(game)
        games.pop(game)
    return redirect(f'/home/{id}')      

@app.route('/save/<id>/<game>',methods=['GET','POST'])
@login_required
def save(id,game):
    if current_user.id != id:
        return redirect('/')
    if request.method=='GET':
        return render_template('save.html',msg='Save As',game=game,id=id)
    else:
        prep()
        try:
            f=open(f'./saved/%s/games.dat'%(id,),'rb')
            k=pickle.load(f) 
            f.close() 
        except:
            k={}
        for a in k:
            if a==request.form['game']:
                return render_template('save.html',msg='Already exists. Enter a different name'\
                                       ,game=game,id=id)
        game1=request.form['game']
        for a in game1:
            if a.isalpha() or a.isdigit():
                pass
            else:
                return render_template('save.html',game=game,id=id,\
                                       msg='No special characters. Save as')
        k[game1]=games[game]
        f=open(f'./saved/%s/games.dat'%(id,),'wb')
        pickle.dump(k,f)
        f.close()
        later()
        return redirect(f'/home/{id}')

@app.route('/saved/<id>',methods=['GET','POST'])
@login_required
def saved(id):
    if current_user.id != id:
        return redirect('/')
    f=open(f'./saved/%s/games.dat'%(id,),'ab+')
    f.seek(0)
    g=[]
    try:
        k=pickle.load(f)  
    except:
        k={}
    for a in k:
        g.append(a)
    return render_template('saved.html',g=g,id=id)

@app.route('/saved/<id>/<game>',methods=['GET','POST'])
@login_required
def savedgame(id,game):
    if current_user.id != id:
        return redirect('/')
    f=open(f'./saved/%s/games.dat'%(id,),'ab+')
    f.seek(0)
    try:
        k=pickle.load(f)  
    except:
        k={}
    for a in k:
        if a==game:
            return render_template('show.html',game=game,board=k[game][1],\
                                   l=k[game][3],id1=id,p=k[a][0])
            
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)
