import uuid
import bleach
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from bson import ObjectId

from .access import get_plan_or_403
from .utils import upload_image_to_cloudinary

plan_bp = Blueprint('plan', __name__, url_prefix='/plan')

ALLOWED_BOX_TAGS = ['p', 'br', 'strong', 'em', 'u', 'a', 'img', 'ol', 'ul', 'li']
ALLOWED_BOX_ATTRS = {'a': ['href', 'target', 'rel'], 'img': ['src', 'alt']}


def sanitize_box(html):
    return bleach.clean(html, tags=ALLOWED_BOX_TAGS, attributes=ALLOWED_BOX_ATTRS, strip=True)


def serialize_plan(plan):
    plan['_id'] = str(plan['_id'])
    plan['leader_id'] = str(plan.get('leader_id'))
    plan['member_ids'] = [str(uid) for uid in plan.get('member_ids', [])]
    if plan.get('converted_trip_id'):
        plan['converted_trip_id'] = str(plan['converted_trip_id'])
    return plan


@plan_bp.route('/add', methods=['POST'])
@login_required
def add_or_update_plan():
    db = current_app.db

    plan_id = request.form.get('plan_id')
    if plan_id:
        get_plan_or_403(db, plan_id)

    title = request.form.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    update_data = {
        'title': title,
        'destination': request.form.get('destination', '').strip(),
        'boxes': {
            'transportation': sanitize_box(request.form.get('box_transportation', '')),
            'accommodation': sanitize_box(request.form.get('box_accommodation', '')),
            'activity': sanitize_box(request.form.get('box_activity', '')),
            'food': sanitize_box(request.form.get('box_food', '')),
        },
    }

    image_file = request.files.get('image')
    if image_file and image_file.filename:
        update_data['img'] = upload_image_to_cloudinary(image_file)

    if plan_id:
        db.plans.update_one({'_id': ObjectId(plan_id)}, {'$set': update_data})
    else:
        update_data['todos'] = []
        update_data['converted_trip_id'] = None
        update_data['created_at'] = datetime.now(timezone.utc)
        update_data['leader_id'] = ObjectId(current_user.id)
        update_data['member_ids'] = [ObjectId(current_user.id)]
        inserted = db.plans.insert_one(update_data)
        plan_id = str(inserted.inserted_id)

    return jsonify({'ok': True, 'plan_id': plan_id})


@plan_bp.route('/<plan_id>', methods=['GET'])
@login_required
def get_plan(plan_id):
    db = current_app.db
    plan = get_plan_or_403(db, plan_id)
    return jsonify(serialize_plan(plan))


@plan_bp.route('/<plan_id>/delete', methods=['POST'])
@login_required
def delete_plan(plan_id):
    db = current_app.db
    get_plan_or_403(db, plan_id)
    db.plans.delete_one({'_id': ObjectId(plan_id)})
    return jsonify({'ok': True})


@plan_bp.route('/<plan_id>/convert', methods=['POST'])
@login_required
def convert_plan(plan_id):
    db = current_app.db
    plan = get_plan_or_403(db, plan_id)
    return jsonify({'title': plan.get('title', ''), 'destination': plan.get('destination', '')})


@plan_bp.route('/<plan_id>/todo/add', methods=['POST'])
@login_required
def add_todo(plan_id):
    db = current_app.db
    get_plan_or_403(db, plan_id)

    text = request.form.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Text is required'}), 400

    todo = {'id': str(uuid.uuid4()), 'text': text, 'done': False}
    db.plans.update_one({'_id': ObjectId(plan_id)}, {'$push': {'todos': todo}})
    return jsonify({'ok': True})


@plan_bp.route('/<plan_id>/todo/<todo_id>/toggle', methods=['POST'])
@login_required
def toggle_todo(plan_id, todo_id):
    db = current_app.db
    plan = get_plan_or_403(db, plan_id)

    todo = next((t for t in plan.get('todos', []) if t['id'] == todo_id), None)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    db.plans.update_one(
        {'_id': ObjectId(plan_id), 'todos.id': todo_id},
        {'$set': {'todos.$.done': not todo['done']}}
    )
    return jsonify({'ok': True})


@plan_bp.route('/<plan_id>/todo/<todo_id>/delete', methods=['POST'])
@login_required
def delete_todo(plan_id, todo_id):
    db = current_app.db
    get_plan_or_403(db, plan_id)
    db.plans.update_one({'_id': ObjectId(plan_id)}, {'$pull': {'todos': {'id': todo_id}}})
    return jsonify({'ok': True})
