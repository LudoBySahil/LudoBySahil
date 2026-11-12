import random
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Active matches ka data store karne ke liye
matches = {}

@app.route('/')
def index():
    return "Classic Ludo Server is Running!"

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# Unique Match Code Generate karna
@socketio.on('create_match')
def handle_create_match(data):
    match_code = "LUDO" + str(random.randint(1000, 9999))
    players_count = data.get('players', 4)
    
    matches[match_code] = {
        'players': players_count,
        'turn': 'red',
        'forced_dice': {},  # Admin control ke liye
        'move_counts': {'red': 0, 'green': 0, 'yellow': 0, 'blue': 0}
    }
    emit('match_created', {'match_code': match_code})

# Admin ke through dice number fix karna
@socketio.on('admin_set_dice')
def handle_admin_dice(data):
    match_code = data.get('match_code')
    color = data.get('color')
    number = int(data.get('number'))
    
    if match_code in matches:
        matches[match_code]['forced_dice'][color] = number
        emit('admin_ack', {'status': 'success', 'message': f'Dice for {color} set to {number}'}, room=match_code)

# Dice Roll Logic (5-Move Anti-Frustration + Admin Override)
@socketio.on('roll_dice')
def handle_roll_dice(data):
    match_code = data.get('match_code')
    color = data.get('color')
    
    if match_code not in matches:
        return
        
    match = matches[match_code]
    
    # 1. Check if Admin has forced a number
    if color in match['forced_dice'] and match['forced_dice'][color] is not None:
        dice_value = match['forced_dice'][color]
        match['forced_dice'][color] = None # Reset after use
    else:
        # 2. Check 5-Move Rule (Anti-Frustration)
        match['move_counts'][color] += 1
        if match['move_counts'][color] >= 5:
            dice_value = 6
            match['move_counts'][color] = 0 # Reset count
        else:
            dice_value = random.randint(1, 6)
            if dice_value == 6:
                match['move_counts'][color] = 0 # Reset on natural 6
                
    emit('dice_result', {'color': color, 'dice': dice_value}, room=match_code)

if __name__ == '__main__':
    import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
    
    
              
