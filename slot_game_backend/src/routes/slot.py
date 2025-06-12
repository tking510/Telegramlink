from flask import Blueprint, request, jsonify
from src.models.user import db, SlotUser, WinRecord
from datetime import datetime
import random

slot_bp = Blueprint(\'slot_bp\', __name__)

# 確率設定 (A:高確率, B:低確率)
PROBABILITIES = {
    \'A\': {
        \'jackpot\': 10.0,  # 全て同じ絵柄
        \'bigWin\': 20.0,   # 2つ同じ絵柄
        \'smallWin\': 30.0, # 特定の組み合わせ
        \'lose\': 40.0      # ハズレ
    },
    \'B\': {
        \'jackpot\': 1.0,
        \'bigWin\': 5.0,
        \'smallWin\': 15.0,
        \'lose\': 79.0
    }
}

SYMBOLS = [
    {\'name\': \'cherry\', \'src\': \'https://www.svgrepo.com/show/499364/cherry.svg\'},
    {\'name\': \'lemon\', \'src\': \'https://www.svgrepo.com/show/499365/lemon.svg\'},
    {\'name\': \'orange\', \'src\': \'https://www.svgrepo.com/show/499366/orange.svg\'},
    {\'name\': \'grape\', \'src\': \'https://www.svgrepo.com/show/499363/grape.svg\'},
    {\'name\': \'bell\', \'src\': \'https://www.svgrepo.com/show/499362/bell.svg\'},
    {\'name\': \'bar\', \'src\': \'https://www.svgrepo.com/show/499361/bar.svg\'},
    {\'name\': \'seven\', \'src\': \'https://www.svgrepo.com/show/499367/seven.svg\'}
]

@slot_bp.route(\'/spin\', methods=[\'POST\'] )
def spin():
    data = request.get_json()
    user_id = data.get(\'user_id\')

    if not user_id:
        return jsonify({\'error\': \'User ID is required\'}), 400

    user = SlotUser.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({\'error\': \'User not found\'}), 404

    if user.played_at:
        return jsonify({\'message\': \'You have already played.\', \'result\': {\'message\': \'ゲームは終了しました。\', \'code\': None, \'type\': \'played\'}}), 403

    user.played_at = datetime.utcnow()
    db.session.commit()

    slot_type = user.slot_type
    probabilities = PROBABILITIES.get(slot_type, PROBABILITIES[\'A\']) # デフォルトはA

    rand = random.uniform(0, 100)
    cumulative_probability = 0
    win_type = \'lose\'

    if rand < (cumulative_probability := cumulative_probability + probabilities[\'jackpot\']):
        win_type = \'jackpot\'
    elif rand < (cumulative_probability := cumulative_probability + probabilities[\'bigWin\']):
        win_type = \'bigWin\'
    elif rand < (cumulative_probability := cumulative_probability + probabilities[\'smallWin\']):
        win_type = \'smallWin\'
    else:
        win_type = \'lose\'

    final_symbols = []
    if win_type == \'jackpot\':
        symbol = random.choice(SYMBOLS)
        final_symbols = [symbol, symbol, symbol]
    elif win_type == \'bigWin\':
        symbol1 = random.choice(SYMBOLS)
        symbol2 = random.choice([s for s in SYMBOLS if s != symbol1])
        pattern = random.choice([[symbol1, symbol1, symbol2], [symbol1, symbol2, symbol1], [symbol2, symbol1, symbol1]])
        final_symbols = pattern
    elif win_type == \'smallWin\':
        # チェリーが1つでもあればスモールウィンとする
        cherry_symbol = next((s for s in SYMBOLS if s[\'name\'] == \'cherry\'), None)
        if cherry_symbol:
            pos = random.randint(0, 2)
            s1 = random.choice(SYMBOLS)
            s2 = random.choice(SYMBOLS)
            s3 = random.choice(SYMBOLS)
            if pos == 0: s1 = cherry_symbol
            elif pos == 1: s2 = cherry_symbol
            else: s3 = cherry_symbol
            final_symbols = [s1, s2, s3]
        else:
            # チェリーがない場合はランダムなシンボル
            final_symbols = [random.choice(SYMBOLS) for _ in range(3)]
    else: # lose
        # 全て異なるシンボル、かつチェリーがないようにする（簡易的に）
        shuffled_symbols = random.sample(SYMBOLS, 3)
        final_symbols = shuffled_symbols

    code = generate_code(win_type) if win_type != \'lose\' else None

    win_record = WinRecord(user_id=user_id, win_type=win_type, code=code)
    db.session.add(win_record)
    db.session.commit()

    message = get_win_message(win_type)

    return jsonify({
        \'result\': {
            \'message\': message,
            \'code\': code,
            \'type\': win_type,
            \'symbols\': final_symbols
        }
    }), 200

@slot_bp.route(\'/verify_code\', methods=[\'POST\'])
def verify_code_api():
    data = request.get_json()
    code = data.get(\'code\')

    if not code:
        return jsonify({\'error\': \'Code is required\'}), 400

    # 簡易的なチェックサム検証
    parts = code.split(\'-\')
    if len(parts) < 4:
        return jsonify({\'valid\': False, \'message\': \'Invalid code format\'}), 200

    raw_code = \'-\'.join(parts[:-1])
    received_checksum = parts[-1]

    if generate_checksum(raw_code) == received_checksum:
        # コードがデータベースに存在するか確認（二重利用防止など）
        # ここでは簡易的に、コードが存在すれば有効とする
        win_record = WinRecord.query.filter_by(code=code).first()
        if win_record:
            return jsonify({\'valid\': True, \'message\': \'Code is valid\', \'win_type\': win_record.win_type}), 200
        else:
            return jsonify({\'valid\': False, \'message\': \'Code not found in records\'}), 200
    else:
        return jsonify({\'valid\': False, \'message\': \'Checksum mismatch\'}), 200

@slot_bp.route(\'/stats\', methods=[\'GET\'])
def get_stats():
    total_plays = WinRecord.query.count()
    jackpot_count = WinRecord.query.filter_by(win_type=\'jackpot\').count()
    big_win_count = WinRecord.query.filter_by(win_type=\'bigWin\').count()
    small_win_count = WinRecord.query.filter_by(win_type=\'smallWin\').count()
    lose_count = WinRecord.query.filter_by(win_type=\'lose\').count()

    return jsonify({
        \'totalPlays\': total_plays,
        \'jackpotCount\': jackpot_count,
        \'bigWinCount\': big_win_count,
        \'smallWinCount\': small_win_count,
        \'loseCount\': lose_count
    }), 200

@slot_bp.route(\'/win_history\', methods=[\'GET\'])
def get_win_history():
    history = WinRecord.query.order_by(WinRecord.timestamp.desc()).all()
    history_data = []
    for record in history:
        history_data.append({
            \'user_id\': record.user_id,
            \'win_type\': record.win_type,
            \'code\': record.code,
            \'timestamp\': record.timestamp.isoformat()
        })
    return jsonify({\'history\': history_data}), 200

def generate_code(prefix):
    timestamp = datetime.utcnow().strftime(\'%Y%m%d%H%M%S\')
    random_str = \'\'.join(random.choices(\'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\', k=6))
    raw_code = f\'{prefix}-{timestamp}-{random_str}\'
    checksum = generate_checksum(raw_code)
    return f\'{raw_code}-{checksum}\'

def generate_checksum(str_val):
    s = sum(ord(c) for c in str_val)
    return str(s % 100).zfill(2)

def get_win_message(win_type):
    messages = {
        \'jackpot\': \'🎉 ジャックポット！ 🎉\',
        \'bigWin\': \'✨ ビッグウィン！ ✨\',
        \'smallWin\': \'🍒 スモールウィン！ 🍒\',
        \'lose\': \'残念！ハズレ\'
    }
    return messages.get(win_type, \'結果\')
