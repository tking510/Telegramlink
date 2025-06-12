from flask import Blueprint, request, jsonify
from src.models.user import db, SlotUser

user_bp = Blueprint(\'user_bp\', __name__)

@user_bp.route(\'/users\', methods=[\'POST\'])
def create_user():
    data = request.get_json()
    user_id = data.get(\'user_id\')
    slot_type = data.get(\'slot_type\', \'A\')

    if not user_id:
        return jsonify({\'error\': \'User ID is required\'}), 400

    if slot_type not in [\'A\', \'B\']:
        return jsonify({\'error\': \'Invalid slot type. Must be A or B\'}), 400

    existing_user = SlotUser.query.filter_by(user_id=user_id).first()
    if existing_user:
        return jsonify({\'message\': \'User already exists\', \'user\': {\n            \'user_id\': existing_user.user_id,
            \'slot_type\': existing_user.slot_type,
            \'played_at\': existing_user.played_at
        }}), 200

    new_user = SlotUser(user_id=user_id, slot_type=slot_type)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({\'message\': \'User created successfully\', \'user\': {\n        \'user_id\': new_user.user_id,
        \'slot_type\': new_user.slot_type,
        \'played_at\': new_user.played_at
    }}), 201

@user_bp.route(\'/users/<user_id>\', methods=[\'GET\'])
def get_user(user_id):
    user = SlotUser.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({\'error\': \'User not found\'}), 404
    return jsonify({\'user\': {\n        \'user_id\': user.user_id,
        \'slot_type\': user.slot_type,
        \'played_at\': user.played_at
    }}), 200

@user_bp.route(\'/users\', methods=[\'GET\'])
def get_all_users():
    users = SlotUser.query.all()
    users_data = []
    for user in users:
        users_data.append({
            \'user_id\': user.user_id,
            \'slot_type\': user.slot_type,
            \'played_at\': user.played_at
        })
    return jsonify({\'users\': users_data}), 200

@user_bp.route(\'/users/<user_id>\', methods=[\'PUT\'])
def update_user(user_id):
    user = SlotUser.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({\'error\': \'User not found\'}), 404

    data = request.get_json()
    slot_type = data.get(\'slot_type\')
    played_at = data.get(\'played_at\')

    if slot_type and slot_type not in [\'A\', \'B\']:
        return jsonify({\'error\': \'Invalid slot type. Must be A or B\'}), 400

    if slot_type:
        user.slot_type = slot_type
    if played_at is not None: # Allow setting to null
        user.played_at = datetime.fromisoformat(played_at) if played_at else None

    db.session.commit()
    return jsonify({\'message\': \'User updated successfully\', \'user\': {\n        \'user_id\': user.user_id,
        \'slot_type\': user.slot_type,
        \'played_at\': user.played_at
    }}), 200

@user_bp.route(\'/users/<user_id>\', methods=[\'DELETE\'])
def delete_user(user_id):
    user = SlotUser.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({\'error\': \'User not found\'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({\'message\': \'User deleted successfully\'}), 200
