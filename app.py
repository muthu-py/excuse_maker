from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from modules.user_auth import register_user, authenticate_user, get_user_by_id
from modules.generate_exucuse import excuse_generator, generate_apology
from modules.excuse_history import save_excuse, get_user_excuses, mark_excuse_favorite, delete_excuse
from modules.generate_proof import generate_fake_document, generate_fake_chat_image, save_excuse_audio, generate_all_proofs, generate_fake_location
from modules.call_sms import send_real_emergency_sms, trigger_emergency_call
import os
import json
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('username')
        password = request.form.get('password')
        
        if not user_id or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('login.html')
        
        # Authenticate user
        if authenticate_user(user_id, password):
            # Get user info and store in session
            user_info = get_user_by_id(user_id)
            if user_info:
                session['user_id'] = user_info[0]  # user_id
                session['username'] = user_info[1]  # username
                session['email'] = user_info[2]  # email

                return redirect(url_for('dashboard'))
            else:
                flash('User information not found.', 'error')
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_id = request.form.get('username')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm')
        name = request.form.get('name')
        
        # Validate required fields
        if not all([user_id, username, email, password, confirm_password, name]):
            flash('Please fill in all required fields.', 'error')
            return render_template('register.html')
        
        # Validate email format
        if '@' not in email or '.' not in email:
            flash('Please enter a valid email address.', 'error')
            return render_template('register.html')
        
        # Validate password length
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        # Validate password confirmation
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        try:
            # Register user
            result = register_user(user_id, username, email, password)
            if "successfully" in result:
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash(result, 'error')
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access the dashboard.', 'error')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', 
                         username=session.get('username'),
                         email=session.get('email'))

# API Routes for Dashboard

@app.route('/api/generate_excuse', methods=['POST'])
def api_generate_excuse():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        category = data.get('category', '')
        context = data.get('context', '')
        tone = data.get('tone', 'neutral')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Generate excuse using the backend module
        excuse = excuse_generator(prompt+context+category+tone)
        
        return jsonify({
            'excuse': excuse,
            'category': category,
            'context': context,
            'tone': tone
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save_excuse', methods=['POST'])
def api_save_excuse():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        user_id = session['user_id']
        prompt = data.get('prompt', '')
        excuse = data.get('excuse', '')
        category = data.get('category', 'general')
        tone = data.get('tone', 'neutral')
        
        # Generate apology using the backmakeend module
        apology = generate_apology(prompt+category+tone)
        
        # Save to database
        result = save_excuse(user_id, prompt, excuse, apology)
        
        return jsonify({
            'message': 'Excuse saved successfully',
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_excuses', methods=['GET'])
def api_get_excuses():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_id = session['user_id']
        excuses = get_user_excuses(user_id)
        
        # Convert to list of dictionaries
        excuse_list = []
        for excuse in excuses:
            excuse_list.append({
                'excuse_id': excuse[0],
                'user_id': excuse[1],
                'prompt': excuse[2],
                'excuse': excuse[3],
                'apology': excuse[4],
                'pdf_path': excuse[5],
                'chat_image_path': excuse[6],
                'voice_path': excuse[7],
                'favorite': excuse[8],
                'timestamp': excuse[9].isoformat() if excuse[9] else None
            })
        
        return jsonify({'excuses': excuse_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_excuse/<int:excuse_id>', methods=['DELETE'])
def api_delete_excuse(excuse_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_id = session['user_id']
        result = delete_excuse(excuse_id, user_id)
        return jsonify({'message': result})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_proof', methods=['POST'])
def api_generate_proof():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        excuse = data.get('excuse', '')
        proof_types = data.get('proof_types', [])
        
        if not excuse:
            return jsonify({'error': 'Excuse is required'}), 400
        
        user_id = session['user_id']
        
        # If specific proof types are requested, generate only those
        if proof_types:
            proofs = {}
            
            for proof_type in proof_types:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                prefix = f"{user_id}_{timestamp}"
                
                if proof_type == 'document':
                    pdf_filename = f"{prefix}_document.pdf"
                    pdf_path = f"static/proofs/{pdf_filename}"
                    generate_fake_document(excuse, output_path=pdf_path)
                    proofs['pdf_path'] = f"/download_proof/{pdf_filename}"
                
                elif proof_type == 'chat':
                    chat_filename = f"{prefix}_chat.png"
                    chat_path = f"static/proofs/{chat_filename}"
                    generate_fake_chat_image(excuse, output_path=chat_path)
                    proofs['chat_image_path'] = f"/download_proof/{chat_filename}"
                
                elif proof_type == 'audio':
                    audio_filename = f"{prefix}_audio.mp3"
                    audio_path = f"static/proofs/{audio_filename}"
                    save_excuse_audio(excuse, output_path=audio_path)
                    proofs['voice_path'] = f"/download_proof/{audio_filename}"
                
                elif proof_type == 'location':
                    proofs['location_data'] = generate_fake_location(excuse)
            
            return jsonify(proofs)
        
        else:
            # Generate all proofs using the comprehensive function
            proofs = generate_all_proofs(excuse, user_id)
            
            # Convert file paths to download URLs
            result = {}
            if proofs.get('document'):
                filename = os.path.basename(proofs['document'])
                result['pdf_path'] = f"/download_proof/{filename}"
            if proofs.get('chat_image'):
                filename = os.path.basename(proofs['chat_image'])
                result['chat_image_path'] = f"/download_proof/{filename}"
            if proofs.get('audio'):
                filename = os.path.basename(proofs['audio'])
                result['voice_path'] = f"/download_proof/{filename}"
            result['location_data'] = proofs.get('location_data')
            
            return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/send_sms', methods=['POST'])
def api_send_sms():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        to_number = data.get('to_number', '')
        excuse_text = data.get('excuse_text', '')
        
        if not to_number or not excuse_text:
            return jsonify({'error': 'Phone number and excuse text are required'}), 400
        
        # Get Twilio credentials from environment
        sid = os.getenv('TWILIO_SID')
        token = os.getenv('TWILIO_TOKEN')
        from_number = os.getenv('TWILIO_FROM_NUMBER')
        
        if not all([sid, token, from_number]):
            return jsonify({'error': 'Twilio credentials not configured'}), 500
        
        # Send SMS using the backend module
        result = send_real_emergency_sms(to_number, excuse_text, sid, token, from_number)
        
        # Log the SMS
        user_id = session['user_id']
        from modules.excuse_history import save_emergency_log
        save_emergency_log(user_id, 'sms', to_number, excuse_text)
        
        return jsonify({
            'message': 'SMS sent successfully',
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/make_call', methods=['POST'])
def api_make_call():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        to_number = data.get('to_number', '')
        excuse_text = data.get('excuse_text', '')
        
        if not to_number or not excuse_text:
            return jsonify({'error': 'Phone number and excuse text are required'}), 400
        
        # Get Twilio credentials from environment
        sid = os.getenv('TWILIO_SID')
        token = os.getenv('TWILIO_TOKEN')
        from_number = os.getenv('TWILIO_FROM_NUMBER')
        
        if not all([sid, token, from_number]):
            return jsonify({'error': 'Twilio credentials not configured'}), 500
        
        # Make call using the backend module
        result = trigger_emergency_call(to_number, excuse_text, sid, token, from_number)
        
        # Log the call
        user_id = session['user_id']
        from modules.excuse_history import save_emergency_log
        save_emergency_log(user_id, 'call', to_number, excuse_text)
        
        return jsonify({
            'message': 'Call initiated successfully',
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_sms_logs', methods=['GET'])
def api_get_sms_logs():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        user_id = session['user_id']
        from modules.excuse_history import get_emergency_logs
        logs = get_emergency_logs(user_id)
        
        # Convert to list of dictionaries
        log_list = []
        for log in logs:
            log_list.append({
                'id': log[0],
                'user_id': log[1],
                'method': log[2],
                'phone': log[3],
                'message': log[4],
                'timestamp': log[5].isoformat() if log[5] else None
            })
        
        return jsonify({'logs': log_list})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_proof/<path:filename>')
def download_proof(filename):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Construct the full path to the file
        file_path = os.path.join('static', 'proofs', filename)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Serve the file with proper headers for download
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preview_proof/<path:filename>')
def preview_proof(filename):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        # Construct the full path to the file
        file_path = os.path.join('static', 'proofs', filename)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Serve the file for preview (without download headers)
        return send_file(file_path)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
