from . import post
from flask import jsonify
from app.helper.Exception import CustomException
from flask import request
from app.models.post_model import Post
from app import db
from datetime import datetime, timedelta
from app.helper.Convert import DateTimeCnv
from flask_cors import cross_origin
from app.helper.auth_connector import verify_jwt
from app.helper.auth_connector import Permission
from app.helper.Connection import get_connection
from app.helper.ServiceURL import ServiceURL
from bs4 import BeautifulSoup
from markdown import markdown
from app.models.like_model import Like
from app.models.tag_model import Tags, Tag_post

@post.route('/test')
def test():
    raise CustomException('Test', 404)


@post.route('/<post_id>', methods=['GET'])
def get_post_by_id(post_id):
    post_current = Post.query.filter_by(post_id=post_id).first()
    cur_user_id = request.args.get('user_current_id')
    if cur_user_id is None:
        end_point = '/user_profile?profile_id=' + str(post_current.author_id)
    else:
        end_point = '/user_profile?profile_id=' + str(post_current.author_id) + '&my_user_id=' + str(cur_user_id)
    with get_connection(post, name='profile') as conn:
        resp = conn.get(ServiceURL.PROFILE_SERVICE + end_point)
        if resp.status_code != 200:
            raise CustomException('Cannot found post', 404)
    if post_current is None:
        raise CustomException('Cannot found post', 404)
    post_current.num_views += 1
    db.session.add(post_current)
    db.session.commit()
    ret = post_current.to_json_full(resp.json())
    ret['is_liked'] = False
    if cur_user_id is not None:
        like = post_current.like.filter_by(user_id=cur_user_id).first()
        if like is not None:
            ret['is_liked'] = True
    return jsonify(ret), 200


@post.route('/', methods=['POST'])
@verify_jwt(blueprint=post, permissions=[Permission.WRITE])
def add_post(user_id):
    post_details = request.get_json()
    html = markdown(post_details.get('body'))
    text = '. '.join(BeautifulSoup(html).find_all(text=True))
    post_add = Post(title=post_details.get('title'),
                    body_html=post_details.get('body'),
                    body=text,
                    date_post=datetime.utcnow(),
                    author_id=user_id)
    tags = post_details.get('tags')
    tag_arr = tags.split(',')
    try:
        for tag_name in tag_arr:
            tag_target = Tags.query.filter_by(name=tag_name).first()
            if tag_target is None:
                tag_insert = Tags(name=tag_name)
                db.session.add(tag_insert)
                db.session.flush()
                post_add.tags.append(tag_insert)
            else:
                post_add.tags.append(tag_target)
        db.session.add(post_add)
        db.session.flush()
        db.session.commit()
    except:
        db.session.rollback()
    return jsonify({'message': 'Success'}), 200


@post.route('/<post_id>', methods=['DELETE'])
@verify_jwt(blueprint=post, permissions=[Permission.WRITE])
def delete_post(post_id, user_id):
    post_del = Post.query.filter_by(post_id=post_id).first()
    if post_del is None:
        raise CustomException('Cannot found post', 404)
    db.session.delete(post_del)
    db.session.commit()
    return jsonify({'message': 'Delete Success'}), 200


@post.route('/', methods=['PUT'])
@cross_origin(origins=['http://localhost:3000'])
@verify_jwt(blueprint=post, permissions=[Permission.WRITE])
def update_post(user_id):
    post_details = request.get_json()
    if post_details.get('author_id') != user_id:
        raise CustomException('You dont have permission to change this post', 403)
    post_update = Post.query.filter_by(post_id=post_details.get('post_id')).first()
    if post_update is None:
        raise CustomException('Cannot found post', 404)
    post_update.title = post_details.get('title')
    post_update.body_html = post_details.get('body')
    html = markdown(post_details.get('body'))
    text = '. '.join(BeautifulSoup(html).find_all(text=True))
    post_update.body = text
    db.session.commit()
    return jsonify({'message': 'Change post success'}), 200


@post.route('/get_all', methods=['GET'])
@cross_origin(origins=['http://localhost:3000'])
def get_all_post_by_page():
    page = request.args.get('page') or '0'
    page = int(page)
    itemPerPage = request.args.get('items_per_page') or '20'
    itemPerPage = int(itemPerPage)
    type = int(request.args.get('type', '0'))
    req_from = request.args.get('from') or '2000-01-01 00:00:00'
    date_from = DateTimeCnv(req_from)
    req_to = request.args.get('to') or '3000-01-01 00:00:00'
    date_to = DateTimeCnv(req_to)
    posts = Post.query.filter(Post.date_post >= date_from).filter(Post.date_post <= date_to) \
        .order_by(Post.date_post.desc()) \
        .paginate(page, itemPerPage, error_out=False)
    post_paginated = posts.items
    total = posts.total
    num_page = total // itemPerPage + 1
    list = [str(x.author_id) for x in post_paginated]
    str_list = ','.join(set(list))
    with get_connection(post, name='profile') as conn:
        resp = conn.get(ServiceURL.PROFILE_SERVICE + 'list_user_profile?list=' + str_list)
        if resp.status_code != 200:
            raise CustomException('Cannot found post', 404)
    data = resp.json().get('profile')
    list_post = []
    data_index = [x.get('user_id') for x in data]
    for element in post_paginated:
        index = data_index.index(element.author_id)
        json = element.to_json_summary(data[index])
        json['is_liked'] = False
        current_user_id = request.args.get('user_current_id')
        if current_user_id is not None:
            like = element.like.filter_by(user_id=current_user_id).first()
            if like is not None:
                json['is_liked'] = True
        list_post.append(json)
    return jsonify({'Post': list_post,
                    'page': page,
                    'itemPerPage': itemPerPage,
                    'total_pages': num_page}), 200


@post.route('/<post_id>/like', methods=['POST'])
@cross_origin(origins=['http://localhost:3000'])
@verify_jwt(blueprint=post, permissions=[Permission.FOLLOW])
def like_post(post_id, user_id):
    post_liked = Post.query.filter_by(post_id=post_id).first()
    if post_liked is None:
        raise CustomException('Not found post', 404)
    like = Like(user_id=user_id, post_id=post_id, date_like=datetime.utcnow())
    db.session.add(like)
    db.session.commit()
    return jsonify({'message': 'Like Success'})


@post.route('/<post_id>/like', methods=['DELETE'])
@cross_origin(origins=['http://localhost:3000'])
@verify_jwt(blueprint=post, permissions=[Permission.FOLLOW])
def unlike_post(post_id, user_id):
    post_like = Post.query.filter_by(post_id=post_id).first()
    if post_like is None:
        raise CustomException('Not found post', 404)
    like = post_like.like.filter_by(user_id=user_id).first()
    if like is not None:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'message': 'Like Success'})
    raise CustomException('You not like this', 404)


@post.route('/<user_id>/posts', methods=['GET'])
@cross_origin(origins=['http://localhost:3000'])
def get_user_post(user_id):
    page = int(request.args.get('page', '0'))
    itemPerPage = 10
    with get_connection(post, name='profile') as conn:
        resp = conn.get(ServiceURL.PROFILE_SERVICE + '/user_profile?profile_id=' + str(user_id))
        if resp.status_code != 200:
            raise CustomException('Cannot found user', 404)
    posts = Post.query.filter_by(author_id=user_id).paginate(page, itemPerPage, error_out=False)
    if posts is None:
        return jsonify({'message': 'User have no post'}), 404
    list_post = list(map(lambda d: d.to_json_little(), posts.items))
    with get_connection(post, name='profile') as conn:
        resp = conn.get(ServiceURL.PROFILE_SERVICE + 'user_profile?profile_id=' + str(user_id))
        if resp.status_code != 200:
            raise CustomException('Cannot found post', 404)
    user = resp.json()
    return jsonify({
        'user': user,
        'posts': list_post,
        'page' : page,
        'itemPerPage' : itemPerPage,
        'total_post' : posts.total
    }), 200


@post.route('/<user_id>/total_posts', methods=['GET'])
def get_total_post(user_id):
    total_posts = Post.query.filter_by(author_id=user_id).count()
    return jsonify({'user_id': user_id,
                    'total_posts': total_posts}), 200


@post.route('/search')
def search_post():
    type = request.args.get('type')
    key_word = request.args.get('key_word')
    page = int(request.args.get('page', '0'))
    itemPerPage = 20
    if type == 'title':
        posts = Post.query.filter(Post.title.like(f'%{key_word}%')).paginate(page, itemPerPage, error_out=False)
    else:
        posts = Post.query.filter(db.or_(Post.body.like(f'%{key_word}%'), Post.title.like(f'%{key_word}%'))).paginate(page, itemPerPage, error_out=False)
    post_paginated = posts.items
    total = posts.total
    num_page = total // itemPerPage + 1
    list = [str(x.author_id) for x in post_paginated]
    str_list = ','.join(set(list))
    with get_connection(post, name='profile') as conn:
        resp = conn.get(ServiceURL.PROFILE_SERVICE + 'list_user_profile?list=' + str_list)
        if resp.status_code != 200:
            raise CustomException('Cannot found post', 404)
    data = resp.json().get('profile')
    list_post = []
    data_index = [x.get('user_id') for x in data]
    for element in post_paginated:
        index = data_index.index(element.author_id)
        json = element.to_json_summary(data[index])
        json['is_liked'] = False
        current_user_id = request.args.get('user_current_id')
        if current_user_id is not None:
            like = element.like.filter_by(user_id=current_user_id).first()
            if like is not None:
                json['is_liked'] = True
        list_post.append(json)
    return jsonify({'Post': list_post,
                    'page': page,
                    'itemPerPage': itemPerPage,
                    'total_pages': num_page}), 200
