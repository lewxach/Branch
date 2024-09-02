from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from firebase_admin import credentials, initialize_app, storage, firestore, auth
import os

app = Flask(__name__)
app.secret_key = 'B&(*^A36&R(*A31546&N)*:"<MK34621346OISJM.A{P>O()*AN(*)}&A%^AJ79.N,,,**ch'

# init firebase
cred = credentials.Certificate('creds.json')
firebase_app = initialize_app(cred, {
    'storageBucket': 'branch-10920.appspot.com'
})
bucket = storage.bucket()
db = firestore.client()

@app.route('/')
def home():
    if 'user_id' in session:
        user_id = session['user_id']
        videos_ref = db.collection('videos').where('owner', '==', user_id)
        videos = [{'id': doc.id, **doc.to_dict()} for doc in videos_ref.stream()]
        return render_template('feed.html', videos=videos, user_id=user_id)
    return redirect(url_for('login'))

@app.route('/uploadform')
def upload_form():
    if 'user_id' in session:
        return render_template('upload.html')
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    file = request.files['file']
    if file:
        filename = file.filename
        blob = bucket.blob(filename)
        blob.upload_from_file(file, content_type='video/mp4')
        blob.make_public()
        video_url = blob.public_url
        
        user_id = session['user_id']
        db.collection('videos').add({
            'url': video_url,
            'owner': user_id,
            'likes': 0,
            'dislikes': 0,
            'liked_by': [],
            'disliked_by': []
        })
        return redirect(url_for('home'))
    return 'Failed to upload video'

@app.route('/profile/<user_id>', methods=['GET', 'POST'])
def profile(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login'))
    
    user_ref = db.collection('users').document(user_id)
    user = user_ref.get().to_dict()
    
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        bio = request.form.get('bio')
        profile_url = request.form.get('profile_url')
        user_ref.set({
            "nickname": nickname,
            "bio": bio,
            "profile_url": profile_url
        }, merge=True)
        return redirect(url_for('profile', user_id=user_id))
    
    videos_ref = db.collection('videos').where('owner', '==', user_id)
    user_videos = [{'id': doc.id, **doc.to_dict()} for doc in videos_ref.stream()]
    return render_template('profile.html', user=user, user_videos=user_videos)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_ref = db.collection('users').document(user_id)
    user = user_ref.get().to_dict()

    if request.method == 'POST':
        nickname = request.form.get('nickname')
        bio = request.form.get('bio')
        profile_url = request.form.get('profile_url')
        user_ref.set({
            "nickname": nickname,
            "bio": bio,
            "profile_url": profile_url
        }, merge=True)
        return redirect(url_for('settings'))

    return render_template('settings.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.get_user_by_email(email)
            session['user_id'] = user.uid
            return redirect(url_for('home'))
        except Exception as e:
            return str(e)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        nickname = request.form.get('nickname', '')
        bio = request.form.get('bio', '')
        profile_url = request.form.get('profile_url', '')
        try:
            user = auth.create_user(
                email=email,
                password=password
            )
            db.collection('users').document(user.uid).set({
                "nickname": nickname,
                "bio": bio,
                "profile_url": profile_url
            })
            session['user_id'] = user.uid
            return redirect(url_for('home'))
        except Exception as e:
            return str(e)
    return render_template('register.html')

@app.route('/like', methods=['POST'])
def like_video():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401
    
    user_id = session['user_id']
    video_id = request.json.get('video_id')
    video_ref = db.collection('videos').document(video_id)
    video = video_ref.get().to_dict()

    if user_id not in video.get('liked_by', []):
        video_ref.update({
            "likes": firestore.Increment(1),
            "liked_by": firestore.ArrayUnion([user_id])
        })
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Already liked"}), 403

@app.route('/dislike', methods=['POST'])
def dislike_video():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401
    
    user_id = session['user_id']
    video_id = request.json.get('video_id')
    video_ref = db.collection('videos').document(video_id)
    video = video_ref.get().to_dict()

    if user_id not in video.get('disliked_by', []):
        video_ref.update({
            "dislikes": firestore.Increment(1),
            "disliked_by": firestore.ArrayUnion([user_id])
        })
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Already disliked"}), 403

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)