from flask import flash,redirect,render_template,url_for,request,current_app,jsonify,g
from flask_login import current_user,login_required
from datetime import datetime
from flask_login import current_user,login_required
from flask_babel import get_locale,_
from app import db
from app.main import bp
from app.main.forms import PostForm,EmptyForm,EditProfileForm,SearchForm
from app.models import User,Post
from langdetect import LangDetectException,detect




#insert here any function or code to be triggered befor sending any view
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())



@bp.route('/',methods=['GET','POST'])
@bp.route('/index',methods=['GET','POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language =''
        post = Post(body=form.post.data,author=current_user,lang=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is snow live'))
        return redirect(url_for('main.index'))
    page = request.args.get('page',1,type=int)
    posts = current_user.followed_posts().paginate(page=page,per_page=current_app.config['POSTS_PER_PAGE'],
    error_out=False)
    next_url = url_for('main.index',page=posts.next_num) \
    if posts.has_next else None
    prev_url = url_for('main.index',page=posts.prev_num) \
    if posts.has_prev else None
    return  render_template('index.html',title=_('Home Page'),
    form=form,posts=posts.items,next_url=next_url,prev_url=prev_url)


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    
    page = request.args.get('page',1,type=int)
    posts , total = Post.search(g.search_form.q.data,page,current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('main.search',q=g.search_form.q.data,page=page+1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search',q=g.search_form.q.data,page=page-1) \
        if page > 1 else None
    return render_template('search.html',title=_('search'),posts=posts,next=next_url,prev=prev_url)








@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page,
    per_page=current_app.config['POSTS_PER_PAGE'],error_out=False)
    next_url = url_for('main.explore',page=posts.next_num) \
    if posts.has_next else None
    prev_url = url_for('main.explore',page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html',title=_('Explore'),
    posts=posts.items,next_url=next_url,prev_url=prev_url)







@bp.route('/user/')
@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page',1,type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(page=page,
    per_page=current_app.config['POSTS_PER_PAGE'],error_out=False)

    next_url = url_for('main.user',username=user.username,page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user',username=user.username,page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html',user=user,posts=posts.items,form=form,
    prev_url=prev_url,next_url=next_url)


@bp.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',title=_('Edit Profile'),form=form)



@bp.route('/follow/<username>',methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit:
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('user %(username)s not found',username=username))
            return redirect(url_for('index'))
        if user == current_user:
            flash(_('you cannot follow yourself'))
            return redirect(url_for('main.user',username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('you are following %(username)s now',username=username))
        return redirect(url_for('main.user',username=username))
    else:
        return redirect(url_for('main.index'))



@bp.route('/unfollow/<username>',methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit:
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('user %(username)s not found',username=username))
            return redirect(url_for('main.user',username=username))
        if current_user == user:
            flash(_('you cannot follow yourself'))
            return redirect(url_for('main.user',username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('you are not following %(username)s anymore',username=username))
        return redirect(url_for('main.user',username))
    else:
        return redirect(url_for('main.index'))







@bp.route('/translate',methods=['POST'])
@login_required
def translate():
    return jsonify({'text':'No available traduction for {}\
         at this moment'.format(request.form['source_language'])})