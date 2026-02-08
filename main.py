# Valentine Surprise Creator - With Song Lyrics & Countdown
import os
import random
import string
import json
import uuid
from datetime import datetime, timedelta

from flask import Flask, request, render_template_string, jsonify, send_from_directory
from markupsafe import escape
import time

app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get("SECRET_KEY", "valentine-song-lyrics-2024")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Storage
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'images'), exist_ok=True)

# Create music directory for built-in songs
os.makedirs(os.path.join('static', 'music'), exist_ok=True)

surprises = {}
view_counts = {}

# Available built-in songs with actual lyrics
BUILTIN_SONGS = [
    {
        "id": "song1",
        "name": "Ordinary - Alex Warren",
        "file": "ordinary.mp3",
        "lyrics": [
            "I'm just ordinary",
            "But you make me feel extraordinary",
            "In your eyes, I see something magical",
            "Something that I never knew I'd find",
            "You take my ordinary heart",
            "And make it beat in extraordinary ways",
            "With you, every moment feels like magic",
            "And I never want this feeling to end"
        ]
    },
    {
        "id": "song2",
        "name": "Romantic Piano",
        "file": "romantic_piano.mp3",
        "lyrics": [
            "Soft melodies of love",
            "Playing gently in the air",
            "Every note reminds me of you",
            "And how much I truly care",
            "The piano sings our story",
            "A tale of love so true",
            "Every chord, every harmony",
            "Whispers I love you"
        ]
    },
    {
        "id": "song3",
        "name": "Love Melody",
        "file": "love_melody.mp3",
        "lyrics": [
            "Your love is like a melody",
            "That plays inside my heart",
            "A beautiful symphony",
            "Right from the very start",
            "Every day with you is music",
            "A song that never ends",
            "My love for you keeps growing",
            "On you my heart depends"
        ]
    },
    {
        "id": "song4",
        "name": "Heart Strings",
        "file": "heart_strings.mp3",
        "lyrics": [
            "You play my heart like strings",
            "Creating music soft and sweet",
            "Every touch, a note that sings",
            "Making my existence complete",
            "Harmony in every glance",
            "Melody in every kiss",
            "With you, I have this chance",
            "To experience eternal bliss"
        ]
    },
    {
        "id": "song5",
        "name": "Eternal Love",
        "file": "eternal_love.mp3",
        "lyrics": [
            "This love will last forever",
            "Through every single day",
            "Nothing can ever sever",
            "This bond in every way",
            "Like stars that shine so bright",
            "Our love will never fade",
            "Guiding us through the night",
            "With promises we've made"
        ]
    }
]

# Romantic words for animation
ROMANTIC_WORDS = [
    "LOVE", "KISS", "HUG", "DEAR", "SWEET", "HONEY", "DARLING", "ANGEL",
    "HEART", "SOUL", "CARE", "WARM", "GENTLE", "TENDER", "ADORE", "CHARM",
    "DREAM", "FAITH", "GLOW", "HAPPY", "JOY", "KIND", "MAGIC", "PEACE",
    "PURE", "ROSY", "SOFT", "TRUE", "WISH", "ZEAL", "BLISS", "CHERISH"
]

# Flowers for falling animation
FALLING_FLOWERS = ["🌹", "🌹", "🌹", "🌹", "🌹", ]


def generate_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


def allowed_file(filename, file_type='image'):
    if '.' not in filename:
        return False

    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'image':
        return ext in {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return False


def save_uploaded_file(file, file_type='image'):
    if not file or file.filename == '':
        return None

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(UPLOAD_FOLDER, 'images')
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    return file_path


@app.route('/')
def home():
    """Home page with form shaking effect"""
    song_options = ''.join([f'''
                            <div class="song-option" onclick="selectSong('{song['id']}', '{song['name']}')" data-song="{song['id']}">
                                <i class="fas fa-music"></i>
                                <span>{song['name']}</span>
                            </div>
                            ''' for song in BUILTIN_SONGS])

    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>💖 Valentine Surprise Creator</title>
        <link href="https://fonts.googleapis.com/css2?family=Pacifico&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                background: #ff0000 !important;
                color: white;
                font-family: 'Segoe UI', sans-serif;
                min-height: 100vh;
                overflow-x: hidden;
            }}

            /* TERRIBLE SHAKE ANIMATION */
            @keyframes terribleShake {{
                0%, 100% {{ transform: translateX(0); }}
                10%, 30%, 50%, 70%, 90% {{ 
                    transform: translateX(-15px) rotate(-3deg); 
                }}
                20%, 40%, 60%, 80% {{ 
                    transform: translateX(15px) rotate(3deg); 
                }}
            }}

            .form-shake {{
                animation: terribleShake 0.8s ease-in-out;
            }}

            /* Simple background bursts */
            .burst {{
                position: fixed;
                font-size: 24px;
                opacity: 0;
                pointer-events: none;
                z-index: 1;
                animation: burstAnimation 3s ease-out forwards;
            }}

            @keyframes burstAnimation {{
                0% {{
                    transform: scale(0) rotate(0deg);
                    opacity: 0;
                }}
                20% {{
                    transform: scale(1.5) rotate(180deg);
                    opacity: 1;
                }}
                100% {{
                    transform: scale(0) rotate(360deg);
                    opacity: 0;
                }}
            }}

            .container {{
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                position: relative;
                z-index: 2;
            }}

            .header {{
                text-align: center;
                padding: 40px 20px;
                margin-bottom: 30px;
            }}

            .main-title {{
                font-family: 'Pacifico', cursive;
                font-size: 3.5rem;
                color: white;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                margin-bottom: 10px;
            }}

            .subtitle {{
                font-size: 1.3rem;
                opacity: 0.9;
            }}

            .form-container {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 30px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                margin-bottom: 30px;
                position: relative;
                overflow: hidden;
            }}

            .form-group {{
                margin-bottom: 20px;
            }}

            .form-label {{
                display: block;
                margin-bottom: 8px;
                color: white;
                font-weight: 600;
            }}

            .form-input, .form-textarea {{
                width: 100%;
                padding: 15px;
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.4);
                border-radius: 10px;
                color: white;
                font-size: 1rem;
                transition: all 0.3s;
            }}

            .form-input:focus, .form-textarea:focus {{
                background: rgba(255, 255, 255, 0.3);
                outline: none;
                border-color: white;
            }}

            .form-textarea {{
                min-height: 120px;
                resize: vertical;
            }}

            .suggestions {{
                display: flex;
                gap: 10px;
                margin-top: 15px;
                flex-wrap: wrap;
            }}

            .suggestion-btn {{
                padding: 10px 15px;
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                color: white;
                cursor: pointer;
                transition: all 0.3s;
            }}

            .suggestion-btn:hover {{
                background: rgba(255, 255, 255, 0.3);
            }}

            /* Song Selection */
            .song-selection {{
                margin-top: 15px;
            }}

            .song-options {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
                gap: 10px;
                margin-top: 10px;
            }}

            .song-option {{
                padding: 15px;
                background: rgba(255, 255, 255, 0.15);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                color: white;
                cursor: pointer;
                transition: all 0.3s;
                text-align: center;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 8px;
            }}

            .song-option:hover {{
                background: rgba(255, 255, 255, 0.25);
                transform: translateY(-3px);
            }}

            .song-option.selected {{
                background: rgba(255, 255, 255, 0.3);
                border-color: white;
                box-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
            }}

            .song-option i {{
                font-size: 1.5rem;
            }}

            .file-upload {{
                margin-top: 10px;
            }}

            .upload-btn {{
                display: block;
                padding: 20px;
                background: rgba(255, 255, 255, 0.15);
                border: 2px dashed rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                text-align: center;
                color: white;
                cursor: pointer;
                transition: all 0.3s;
            }}

            .upload-btn:hover {{
                background: rgba(255, 255, 255, 0.25);
            }}

            /* CREATE MY OWN Button with shake effect */
            .create-btn {{
                width: 100%;
                padding: 20px;
                background: white;
                color: #ff0000;
                border: none;
                border-radius: 15px;
                font-family: 'Pacifico', cursive;
                font-size: 1.5rem;
                cursor: pointer;
                transition: all 0.3s;
                margin-top: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                position: relative;
                overflow: hidden;
            }}

            .create-btn:hover {{
                transform: scale(1.05);
                box-shadow: 0 10px 30px rgba(255, 255, 255, 0.2);
            }}

            .create-btn::after {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
                transform: translateX(-100%);
            }}

            .create-btn:hover::after {{
                animation: shine 1.5s ease-out;
            }}

            @keyframes shine {{
                0% {{ transform: translateX(-100%); }}
                100% {{ transform: translateX(100%); }}
            }}

            .link-overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(255, 0, 0, 0.95);
                display: none;
                justify-content: center;
                align-items: center;
                z-index: 1000;
            }}

            .link-box {{
                background: white;
                padding: 30px;
                border-radius: 20px;
                max-width: 500px;
                width: 90%;
                text-align: center;
            }}

            .link-input {{
                width: 100%;
                padding: 15px;
                margin: 20px 0;
                border: 2px solid #ff0000;
                border-radius: 10px;
                font-size: 1rem;
                text-align: center;
            }}

            .share-buttons {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }}

            .share-btn {{
                padding: 12px;
                background: #ff0000;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s;
            }}

            .share-btn:hover {{
                background: #cc0000;
            }}

            footer {{
                text-align: center;
                padding: 20px;
                color: white;
                opacity: 0.8;
            }}

            /* Edit button */
            .edit-btn {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 50px;
                padding: 15px 25px;
                color: white;
                cursor: pointer;
                z-index: 100;
                display: flex;
                align-items: center;
                gap: 10px;
                transition: all 0.3s;
                backdrop-filter: blur(5px);
            }}

            .edit-btn:hover {{
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-3px);
            }}

            @media (max-width: 600px) {{
                .main-title {{
                    font-size: 2.5rem;
                }}

                .container {{
                    padding: 10px;
                }}

                .form-container {{
                    padding: 20px;
                }}

                .song-options {{
                    grid-template-columns: 1fr;
                }}

                .share-buttons {{
                    grid-template-columns: 1fr;
                }}

                .edit-btn {{
                    bottom: 10px;
                    right: 10px;
                    padding: 10px 20px;
                    font-size: 0.9rem;
                }}
            }}
        </style>
    </head>
    <body>
        <!-- Simple background bursts -->
        <div id="bursts-container"></div>

        <div class="container">
            <div class="header">
                <h1 class="main-title">💖 Valentine Surprise</h1>
                <p class="subtitle">Create your own magical surprise</p>
            </div>

            <div class="form-container" id="surprise-form">
                <form>
                    <div class="form-group">
                        <label class="form-label">Your Name</label>
                        <input type="text" id="sender" class="form-input" placeholder="Enter your name..." required>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Their Name</label>
                        <input type="text" id="receiver" class="form-input" placeholder="Enter their name..." required>
                    </div>

                    <div class="form-group">
                        <label class="form-label">
                            <i class="fas fa-heart"></i> Your Personal Message
                        </label>
                        <textarea id="message" class="form-textarea" placeholder="Write your heartfelt message..." required></textarea>

                        <div class="suggestions">
                            <button type="button" class="suggestion-btn" onclick="useSuggestion('romantic')">
                                Romantic
                            </button>
                            <button type="button" class="suggestion-btn" onclick="useSuggestion('cute')">
                                Cute
                            </button>
                            <button type="button" class="suggestion-btn" onclick="useSuggestion('funny')">
                                Funny
                            </button>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Background Image (Optional)</label>
                        <div class="file-upload">
                            <input type="file" id="background" accept="image/*" style="display: none;">
                            <label for="background" class="upload-btn">
                                <i class="fas fa-image"></i> Choose Image
                            </label>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">
                            <i class="fas fa-music"></i> Choose a Love Song
                        </label>
                        <div class="song-selection">
                            <p style="margin-bottom: 10px; color: rgba(255,255,255,0.8); font-size: 0.9rem;">
                                Select one of our romantic songs:
                            </p>
                            <div class="song-options">
                                {song_options}
                            </div>

                            <input type="hidden" id="selected-song" value="">
                            <input type="hidden" id="selected-song-name" value="">
                        </div>
                    </div>

                    <!-- CREATE MY OWN Button -->
                    <button type="button" class="create-btn" onclick="createSurprise()">
                        <i class="fas fa-magic"></i> CREATE MY OWN SURPRISE
                    </button>
                </form>
            </div>

            <footer>
                <p>Made with <i class="fas fa-heart"></i> • Create something magical!</p>
            </footer>
        </div>

        <!-- Edit Button (shown after creation) -->
        <button class="edit-btn" id="edit-btn" style="display: none;" onclick="editSurprise()">
            <i class="fas fa-edit"></i> Edit & Create Another
        </button>

        <div class="link-overlay" id="link-overlay">
            <div class="link-box">
                <button onclick="closeLink()" style="position: absolute; top: 15px; right: 15px; background: none; border: none; color: #ff0000; font-size: 1.5rem; cursor: pointer;">
                    <i class="fas fa-times"></i>
                </button>

                <h2 style="color: #ff0000; margin-bottom: 20px;">
                    <i class="fas fa-gift"></i> Your Surprise is Ready!
                </h2>

                <input type="text" id="surprise-link" class="link-input" readonly>

                <div class="share-buttons">
                    <button onclick="copyLink()" class="share-btn">
                        <i class="fas fa-copy"></i> Copy
                    </button>
                    <button onclick="shareWhatsApp()" class="share-btn">
                        <i class="fab fa-whatsapp"></i> WhatsApp
                    </button>
                    <a href="#" id="preview-link" target="_blank" class="share-btn" style="text-decoration: none;">
                        <i class="fas fa-eye"></i> Preview
                    </a>
                    <button onclick="showEditButton()" class="share-btn">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                </div>
            </div>
        </div>

        <script>
            // Simple bursts in background
            function createRandomBursts() {{
                const container = document.getElementById('bursts-container');
                const elements = ['💖', '💝', '✨', '🌟', '🌹', '🌸'];

                setInterval(() => {{
                    const burst = document.createElement('div');
                    burst.className = 'burst';
                    burst.textContent = elements[Math.floor(Math.random() * elements.length)];

                    burst.style.left = Math.random() * 100 + 'vw';
                    burst.style.top = Math.random() * 100 + 'vh';
                    burst.style.fontSize = (20 + Math.random() * 30) + 'px';
                    burst.style.color = 'white';

                    container.appendChild(burst);

                    // Remove after animation
                    setTimeout(() => {{
                        if (burst.parentNode === container) {{
                            container.removeChild(burst);
                        }}
                    }}, 3000);
                }}, 1000);
            }}

            const messages = {{
                romantic: [
                    "My heart beats only for you. Every moment with you is magical.",
                    "In your eyes, I found my forever home. I love you endlessly.",
                    "You are my everything. My love for you grows stronger every day."
                ],
                cute: [
                    "You're my favorite person in the whole world!",
                    "I love you more than pizza! You're my perfect slice.",
                    "You make my heart smile every single day."
                ],
                funny: [
                    "Are you a magician? Because whenever I look at you, everyone else disappears!",
                    "Do you have a map? I keep getting lost in your eyes!",
                    "If you were a vegetable, you'd be a cute-cumber!"
                ]
            }};

            // Add terrible shake effect to form
            function shakeFormTerribly() {{
                const form = document.getElementById('surprise-form');
                form.classList.remove('form-shake');
                void form.offsetWidth; // Trigger reflow
                form.classList.add('form-shake');

                // Create burst effect
                createBurstEffect();
            }}

            function useSuggestion(type) {{
                const msgList = messages[type];
                const randomMsg = msgList[Math.floor(Math.random() * msgList.length)];
                document.getElementById('message').value = randomMsg;

                // Shake form terribly
                shakeFormTerribly();
            }}

            function createBurstEffect() {{
                const container = document.getElementById('bursts-container');
                for (let i = 0; i < 5; i++) {{
                    setTimeout(() => {{
                        const burst = document.createElement('div');
                        burst.className = 'burst';
                        burst.textContent = '✨';
                        burst.style.left = '50%';
                        burst.style.top = '50%';
                        burst.style.fontSize = '3rem';
                        burst.style.position = 'fixed';
                        burst.style.zIndex = '9999';

                        container.appendChild(burst);

                        setTimeout(() => {{
                            if (burst.parentNode === container) {{
                                container.removeChild(burst);
                            }}
                        }}, 3000);
                    }}, i * 100);
                }}
            }}

            // Song selection
            function selectSong(songId, songName) {{
                // Remove selection from all options
                document.querySelectorAll('.song-option').forEach(option => {{
                    option.classList.remove('selected');
                }});

                // Add selection to clicked option
                const selectedOption = document.querySelector(`.song-option[data-song="${{songId}}"]`);
                selectedOption.classList.add('selected');

                // Store selected values
                document.getElementById('selected-song').value = songId;
                document.getElementById('selected-song-name').value = songName;

                // Shake form terribly
                shakeFormTerribly();
            }}

            function createSurprise() {{
                const sender = document.getElementById('sender').value.trim();
                const receiver = document.getElementById('receiver').value.trim();
                const message = document.getElementById('message').value.trim();
                const selectedSong = document.getElementById('selected-song').value;
                const selectedSongName = document.getElementById('selected-song-name').value;

                if (!sender || !receiver || !message) {{
                    alert('Please fill in all fields! 💖');
                    shakeFormTerribly();
                    return;
                }}

                if (!selectedSong) {{
                    alert('Please select a song! 🎵');
                    shakeFormTerribly();
                    return;
                }}

                // Shake form terribly before sending
                shakeFormTerribly();

                const btn = document.querySelector('.create-btn');
                const originalText = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Magic...';
                btn.disabled = true;

                // Add extra shake during creation
                const form = document.getElementById('surprise-form');
                form.style.animation = 'terribleShake 0.5s ease-in-out infinite';

                const formData = new FormData();
                formData.append('sender', sender);
                formData.append('receiver', receiver);
                formData.append('message', message);
                formData.append('song', selectedSong);
                formData.append('song_name', selectedSongName);

                const bgFile = document.getElementById('background').files[0];
                if (bgFile) formData.append('background', bgFile);

                fetch('/create_surprise', {{
                    method: 'POST',
                    body: formData
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.error) {{
                        throw new Error(data.error);
                    }}

                    document.getElementById('surprise-link').value = data.url;
                    document.getElementById('preview-link').href = data.url;
                    document.getElementById('link-overlay').style.display = 'flex';

                    // Stop shaking
                    form.style.animation = '';

                    // Mega celebration bursts
                    for (let i = 0; i < 15; i++) {{
                        setTimeout(() => createBurstEffect(), i * 100);
                    }}
                }})
                .catch(error => {{
                    alert('Error: ' + error.message);
                }})
                .finally(() => {{
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                    form.style.animation = '';
                }});
            }}

            function copyLink() {{
                const linkInput = document.getElementById('surprise-link');
                linkInput.select();
                try {{
                    navigator.clipboard.writeText(linkInput.value);
                    const btn = event.target;
                    const original = btn.innerHTML;
                    btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    setTimeout(() => btn.innerHTML = original, 2000);
                }} catch (err) {{
                    document.execCommand('copy');
                    alert('Link copied!');
                }}
            }}

            function shareWhatsApp() {{
                const link = document.getElementById('surprise-link').value;
                const text = encodeURIComponent(`💖 I created a Valentine surprise for you! ${{link}}`);
                window.open(`https://wa.me/?text=${{text}}`, '_blank');
            }}

            function closeLink() {{
                document.getElementById('link-overlay').style.display = 'none';
            }}

            function showEditButton() {{
                closeLink();
                document.getElementById('edit-btn').style.display = 'flex';
            }}

            function editSurprise() {{
                // Reset form values
                document.getElementById('sender').value = '';
                document.getElementById('receiver').value = '';
                document.getElementById('message').value = '';
                document.getElementById('background').value = '';
                document.getElementById('selected-song').value = '';
                document.getElementById('selected-song-name').value = '';

                // Remove selection from songs
                document.querySelectorAll('.song-option').forEach(option => {{
                    option.classList.remove('selected');
                }});

                // Hide edit button
                document.getElementById('edit-btn').style.display = 'none';

                // Scroll to top
                window.scrollTo({{ top: 0, behavior: 'smooth' }});

                // Shake form
                shakeFormTerribly();
            }}

            // Initialize
            document.addEventListener('DOMContentLoaded', function() {{
                createRandomBursts();

                // File upload handlers
                document.getElementById('background').addEventListener('change', function() {{
                    if (this.files.length > 0) {{
                        shakeFormTerribly();
                        createBurstEffect();
                    }}
                }});

                // Auto-select first song
                setTimeout(() => {{
                    const firstSongOption = document.querySelector('.song-option');
                    if (firstSongOption) {{
                        const songId = firstSongOption.dataset.song;
                        const songName = firstSongOption.querySelector('span').textContent;
                        selectSong(songId, songName);
                    }}
                }}, 500);

                // Add shake effect to all buttons
                document.querySelectorAll('button').forEach(button => {{
                    if (!button.classList.contains('create-btn')) {{
                        button.addEventListener('click', function() {{
                            if (!this.closest('.link-overlay')) {{
                                shakeFormTerribly();
                            }}
                        }});
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    '''


@app.route('/create_surprise', methods=['POST'])
def create_surprise_route():
    """Create a new surprise with song lyrics."""
    try:
        code = generate_code()
        while code in surprises:
            code = generate_code()

        sender = request.form.get('sender', '').strip()
        receiver = request.form.get('receiver', '').strip()
        message = request.form.get('message', '').strip()
        song_id = request.form.get('song', 'song1')
        song_name = request.form.get('song_name', 'Ordinary - Alex Warren')

        if not sender or not receiver or not message:
            return jsonify({'error': 'Please fill all required fields'}), 400

        # Get song details from built-in songs
        selected_song = next((song for song in BUILTIN_SONGS if song['id'] == song_id), BUILTIN_SONGS[0])

        background_path = None
        if 'background' in request.files:
            background_file = request.files['background']
            if background_file and background_file.filename and allowed_file(background_file.filename, 'image'):
                background_path = save_uploaded_file(background_file, 'image')

        surprises[code] = {
            'sender': escape(sender),
            'receiver': escape(receiver),
            'message': escape(message),
            'song_id': song_id,
            'song_name': song_name,
            'song_file': selected_song['file'],
            'song_lyrics': selected_song['lyrics'],
            'background_path': background_path,
            'created': datetime.now().isoformat(),
            'expires': datetime.now() + timedelta(days=30)
        }

        view_counts[code] = 0

        base_url = request.host_url.rstrip('/')
        return jsonify({
            'url': f'{base_url}/surprise/{code}',
            'code': code
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/surprise/<code>')
def surprise(code):
    """The received surprise page with countdown and 7000 flowers."""
    if code not in surprises:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Surprise Not Found</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * { margin: 0; padding: 0; }
                body {
                    background: #ff0000 !important;
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    color: white;
                    font-family: sans-serif;
                    text-align: center;
                }
                .message {
                    padding: 40px;
                    background: rgba(255,255,255,0.1);
                    border-radius: 20px;
                    border: 2px solid rgba(255,255,255,0.3);
                }
                a {
                    color: white;
                    margin-top: 20px;
                    display: inline-block;
                    padding: 10px 20px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 10px;
                    text-decoration: none;
                }
                a:hover {
                    background: rgba(255,255,255,0.3);
                }
            </style>
        </head>
        <body>
            <div class="message">
                <h1 style="font-size: 3rem; margin-bottom: 20px;">💔</h1>
                <h2>Surprise Not Found</h2>
                <p style="margin: 20px 0;">This surprise has expired or doesn't exist.</p>
                <a href="/">Create New Surprise</a>
            </div>
        </body>
        </html>
        ''', 404

    view_counts[code] = view_counts.get(code, 0) + 1
    surprise = surprises[code]

    has_background = surprise.get('background_path') is not None
    background_url = f"/uploads/images/{os.path.basename(surprise['background_path'])}" if has_background else ""

    # Get song details
    song_file = surprise.get('song_file', 'ordinary.mp3')
    song_url = f"/static/music/{song_file}"
    song_lyrics = surprise.get('song_lyrics', BUILTIN_SONGS[0]['lyrics'])

    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>💖 For {{ receiver }} | From {{ sender }}</title>
        <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Pacifico&display=swap" rel="stylesheet">
        <style>
            /* BLACK BACKGROUND FOR COUNTDOWN */
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            html, body {
                width: 100%;
                height: 100%;
                overflow: hidden;
                position: fixed;
                font-family: 'Segoe UI', sans-serif;
            }

            /* BLACK COUNTDOWN BACKGROUND */
            .countdown-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: #000000 !important; /* BLACK BACKGROUND */
                z-index: 1000;
                display: flex;
                justify-content: center;
                align-items: center;
                flex-direction: column;
            }

            .countdown-number {
                font-size: 20rem;
                font-weight: bold;
                color: white;
                text-shadow: 
                    0 0 50px rgba(255, 0, 0, 0.8),
                    0 0 100px rgba(255, 0, 0, 0.6),
                    0 0 150px rgba(255, 0, 0, 0.4);
                animation: countdownPop 1s ease-out;
                font-family: 'Pacifico', cursive;
            }

            .countdown-text {
                font-size: 4rem;
                color: white;
                margin-top: 3rem;
                text-shadow: 0 0 30px rgba(255, 0, 0, 0.7);
                animation: pulse 1s infinite;
                font-family: 'Dancing Script', cursive;
            }

            /* FLASH EFFECT (2 seconds, 5 times) */
            @keyframes flashEffect {
                0%, 100% { 
                    opacity: 0;
                    filter: brightness(1);
                }
                10%, 30%, 50%, 70%, 90% { 
                    opacity: 1;
                    filter: brightness(5);
                }
                20%, 40%, 60%, 80% { 
                    opacity: 0;
                    filter: brightness(1);
                }
            }

            .flash-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: white;
                z-index: 999;
                opacity: 0;
                display: none;
                animation: flashEffect 2s ease-in-out;
            }

            /* MASSIVE FLOWER BURST (7000 flowers) */
            @keyframes flowerBurst {
                0% {
                    transform: translate(-50%, -50%) scale(0) rotate(0deg);
                    opacity: 0;
                }
                10% {
                    opacity: 1;
                    transform: translate(-50%, -50%) scale(1) rotate(180deg);
                }
                30% {
                    transform: translate(
                        calc(-50% + var(--tx) * 300px),
                        calc(-50% + var(--ty) * 300px)
                    ) scale(1.5) rotate(360deg);
                    opacity: 0.9;
                }
                50% {
                    transform: translate(
                        calc(-50% + var(--tx) * 500px),
                        calc(-50% + var(--ty) * 500px)
                    ) scale(1.2) rotate(540deg);
                    opacity: 0.8;
                }
                70% {
                    transform: translate(
                        calc(-50% + var(--tx) * 700px),
                        calc(-50% + var(--ty) * 700px)
                    ) scale(0.8) rotate(720deg);
                    opacity: 0.6;
                }
                90% {
                    transform: translate(
                        calc(-50% + var(--tx) * 900px),
                        calc(-50% + var(--ty) * 900px)
                    ) scale(0.4) rotate(900deg);
                    opacity: 0.3;
                }
                100% {
                    transform: translate(
                        calc(-50% + var(--tx) * 1000px),
                        calc(-50% + var(--ty) * 1000px)
                    ) scale(0.1) rotate(1080deg);
                    opacity: 0;
                }
            }

            .massive-flower {
                position: absolute;
                font-size: 40px;
                opacity: 0;
                pointer-events: none;
                z-index: 800;
                animation: flowerBurst linear forwards;
                left: 50%;
                top: 50%;
            }

            /* SONG LYRICS (just text, no background/border) */
            @keyframes lyricsFloat {
                0% {
                    transform: translateX(100vw) translateY(var(--start-y)) scale(0.8);
                    opacity: 0;
                }
                10% {
                    opacity: 1;
                    transform: translateX(80vw) translateY(calc(var(--start-y) + 10px)) scale(1);
                }
                30% {
                    transform: translateX(60vw) translateY(calc(var(--start-y) - 20px)) scale(1.2);
                }
                50% {
                    transform: translateX(40vw) translateY(calc(var(--start-y) + 15px)) scale(1);
                }
                70% {
                    transform: translateX(20vw) translateY(calc(var(--start-y) - 10px)) scale(0.9);
                }
                90% {
                    transform: translateX(0vw) translateY(var(--start-y)) scale(1);
                    opacity: 1;
                }
                100% {
                    transform: translateX(-20vw) translateY(var(--start-y)) scale(0.8);
                    opacity: 0;
                }
            }

            .song-lyric {
                position: absolute;
                color: white;
                font-size: 36px;
                font-family: 'Dancing Script', cursive;
                text-shadow: 
                    0 0 20px rgba(255, 255, 255, 0.9),
                    0 0 40px rgba(255, 255, 255, 0.7),
                    0 0 60px rgba(255, 51, 102, 0.9);
                opacity: 0;
                pointer-events: none;
                z-index: 3;
                white-space: nowrap;
                animation: lyricsFloat linear forwards;
                font-weight: bold;
                /* NO BACKGROUND, NO BORDER, JUST TEXT */
                background: none !important;
                border: none !important;
                padding: 0 !important;
                backdrop-filter: none !important;
            }

            /* MESSAGE BOX (BOLD TEXT) */
            @keyframes messageAppear {
                0% {
                    transform: translate(-50%, -50%) scale(0);
                    opacity: 0;
                }
                100% {
                    transform: translate(-50%, -50%) scale(1);
                    opacity: 1;
                }
            }

            @keyframes heartbeat {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }

            /* ANIMATIONS */
            @keyframes countdownPop {
                0% { transform: scale(0.1); opacity: 0; }
                50% { transform: scale(1.3); opacity: 1; }
                100% { transform: scale(1); opacity: 1; }
            }

            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }

            /* Main message container */
            .message-container {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 90%;
                max-width: 700px;
                z-index: 4;
                animation: messageAppear 1.5s ease-out forwards;
                opacity: 0;
                display: none;
            }

            /* The message box - BOLD TEXT */
            .message-box {
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(15px);
                padding: 50px;
                border-radius: 30px;
                border: 4px solid rgba(255, 255, 255, 0.4);
                text-align: center;
                box-shadow: 
                    0 30px 60px rgba(0, 0, 0, 0.3),
                    0 0 80px rgba(255, 255, 255, 0.2);
                {% if has_background %}
                background: rgba(255, 255, 255, 0.15) url('{{ background_url }}');
                background-size: cover;
                background-position: center;
                background-blend-mode: overlay;
                {% endif %}
            }

            .top-heart {
                position: absolute;
                top: -80px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 6rem;
                z-index: 5;
                animation: heartbeat 1.5s infinite;
                color: white;
                text-shadow: 0 0 30px rgba(255, 255, 255, 0.8);
                display: none;
            }

            .hearts {
                font-size: 4rem;
                margin-bottom: 20px;
                animation: heartbeat 2s infinite;
                color: white;
            }

            /* BOLD TITLES AND TEXT */
            .title {
                font-family: 'Pacifico', cursive;
                font-size: 3.5rem;
                color: white;
                margin-bottom: 15px;
                text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
                font-weight: 900 !important; /* EXTRA BOLD */
                letter-spacing: 1px;
            }

            .subtitle {
                font-family: 'Dancing Script', cursive;
                font-size: 2.5rem;
                color: white;
                margin-bottom: 30px;
                opacity: 0.9;
                font-weight: 700 !important; /* BOLD */
                letter-spacing: 0.5px;
            }

            .message-content {
                background: rgba(255, 255, 255, 0.25);
                padding: 35px;
                border-radius: 20px;
                border: 3px solid rgba(255, 255, 255, 0.4);
                font-size: 2rem;
                color: white;
                line-height: 1.8;
                margin: 25px 0;
                font-family: 'Dancing Script', cursive;
                white-space: pre-wrap;
                backdrop-filter: blur(10px);
                font-weight: 700 !important; /* BOLD */
                letter-spacing: 0.5px;
            }

            .signature {
                font-size: 2.2rem;
                color: white;
                margin-top: 25px;
                font-family: 'Dancing Script', cursive;
                animation: heartbeat 3s infinite;
                font-weight: 700 !important; /* BOLD */
            }

            .song-info {
                font-size: 1.2rem;
                color: rgba(255, 255, 255, 0.8);
                margin-top: 20px;
                font-style: italic;
                font-weight: 600; /* SEMI-BOLD */
            }

            /* Click hearts */
            .click-heart {
                position: absolute;
                font-size: 2.5rem;
                pointer-events: none;
                z-index: 6;
                animation: flowerBurst 2s ease-out forwards;
            }

            /* Lyrics indicator */
            .lyrics-indicator {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: rgba(255, 255, 255, 0.2);
                padding: 12px 18px;
                border-radius: 12px;
                color: white;
                font-size: 1rem;
                z-index: 7;
                backdrop-filter: blur(5px);
                border: 1px solid rgba(255, 255, 255, 0.3);
                display: flex;
                align-items: center;
                gap: 10px;
                display: none;
            }

            /* Responsive */
            @media (max-width: 768px) {
                .message-box {
                    padding: 30px;
                }

                .title {
                    font-size: 2.5rem;
                }

                .subtitle {
                    font-size: 2rem;
                }

                .message-content {
                    font-size: 1.6rem;
                    padding: 25px;
                }

                .song-lyric {
                    font-size: 28px;
                }

                .massive-flower {
                    font-size: 30px;
                }

                .top-heart {
                    font-size: 4rem;
                    top: -60px;
                }

                .countdown-number {
                    font-size: 12rem;
                }

                .countdown-text {
                    font-size: 2.5rem;
                }

                .lyrics-indicator {
                    bottom: 15px;
                    right: 15px;
                    font-size: 0.9rem;
                }
            }

            @media (max-width: 480px) {
                .message-box {
                    padding: 20px;
                }

                .title {
                    font-size: 2rem;
                }

                .subtitle {
                    font-size: 1.6rem;
                }

                .message-content {
                    font-size: 1.3rem;
                    padding: 20px;
                }

                .song-lyric {
                    font-size: 24px;
                }

                .top-heart {
                    font-size: 3rem;
                    top: -50px;
                }

                .countdown-number {
                    font-size: 8rem;
                }

                .countdown-text {
                    font-size: 1.8rem;
                }

                .lyrics-indicator {
                    padding: 10px 15px;
                    font-size: 0.8rem;
                }
            }

            /* RED BACKGROUND AFTER COUNTDOWN */
            .surprise-background {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: #ff0000 !important;
                z-index: 2;
                display: none;
            }
        </style>
    </head>
    <body>
        <!-- Music -->
        <audio id="love-music" loop style="display: none;">
            <source src="{{ song_url }}" type="audio/mpeg">
        </audio>

        <!-- Countdown Overlay (BLACK BACKGROUND) -->
        <div class="countdown-overlay" id="countdown-overlay">
            <div class="countdown-number">3</div>
            <div class="countdown-text">Get Ready... 💝</div>
        </div>

        <!-- Flash Overlay -->
        <div class="flash-overlay" id="flash-overlay"></div>

        <!-- Red Background (shown after countdown) -->
        <div class="surprise-background" id="surprise-background"></div>

        <!-- Top heart -->
        <div class="top-heart" id="top-heart">💖</div>

        <!-- Lyrics indicator -->
        <div class="lyrics-indicator" id="lyrics-indicator">
            <i class="fas fa-music"></i>
            <span>Now Playing: {{ surprise.song_name }}</span>
        </div>

        <!-- Main message container -->
        <div class="message-container" id="message-container">
            <div class="message-box">
                <div class="hearts">💖</div>
                <h1 class="title">From {{ sender }}</h1>
                <h2 class="subtitle">To {{ receiver }} 💌</h2>

                <div class="message-content">
                    {{ message }}
                </div>

                <div class="signature">
                    With all my love ❤️
                </div>

                <div class="song-info">
                    <i class="fas fa-music"></i> Playing: {{ surprise.song_name }}
                </div>
            </div>
        </div>

        <script>
            // Song lyrics
            const songLyrics = {{ song_lyrics|tojson }};

            // Flowers for massive burst
            const flowers = {{ FALLING_FLOWERS|tojson }};

            // Variables
            let currentLyricIndex = 0;
            let lyricInterval;
            let isMusicPlaying = false;
            let countdownValue = 3;
            let countdownInterval;
            let flowersCreated = 0;
            const TOTAL_FLOWERS = 500; // 500 flowers!

            // Start countdown
            function startCountdown() {
                const countdownNumber = document.querySelector('.countdown-number');
                const countdownText = document.querySelector('.countdown-text');

                countdownInterval = setInterval(() => {
                    if (countdownValue > 1) {
                        countdownValue--;
                        countdownNumber.textContent = countdownValue;

                        // Reset animation
                        countdownNumber.style.animation = 'none';
                        setTimeout(() => {
                            countdownNumber.style.animation = 'countdownPop 1s ease-out';
                        }, 10);

                        // Update text
                        const texts = ["Get Ready... 💝", "Almost There! 💖", "SURPRISE! 💘"];
                        countdownText.textContent = texts[3 - countdownValue];

                    } else {
                        clearInterval(countdownInterval);

                        // Final count
                        countdownNumber.textContent = '💖';
                        countdownText.textContent = 'HERE IT COMES!';

                        // Hide countdown and show flash effect
                        setTimeout(() => {
                            const overlay = document.getElementById('countdown-overlay');
                            overlay.style.opacity = '0';
                            overlay.style.transition = 'opacity 0.5s ease-out';

                            setTimeout(() => {
                                overlay.style.display = 'none';

                                // Show flash effect
                                showFlashEffect();

                            }, 500);
                        }, 1500);
                    }
                }, 1000);
            }

            // Show flash effect (5 times in 2 seconds)
            function showFlashEffect() {
                const flashOverlay = document.getElementById('flash-overlay');
                flashOverlay.style.display = 'block';

                // Restart animation
                flashOverlay.style.animation = 'none';
                setTimeout(() => {
                    flashOverlay.style.animation = 'flashEffect 2s ease-in-out';
                }, 10);

                // Hide flash and start massive flower burst
                setTimeout(() => {
                    flashOverlay.style.display = 'none';

                    // Show red background
                    document.getElementById('surprise-background').style.display = 'block';

                    // Start massive flower burst
                    startMassiveFlowerBurst();

                }, 2000); // 2 seconds for flash
            }

            // Create 7000 flowers burst
            function createMassiveFlower() {
                if (flowersCreated >= TOTAL_FLOWERS) return;

                flowersCreated++;

                const flower = document.createElement('div');
                flower.className = 'massive-flower';
                flower.textContent = flowers[Math.floor(Math.random() * flowers.length)];

                // Random direction (all directions)
                const angle = Math.random() * Math.PI * 2;
                const distance = 1000; // Max distance
                const tx = Math.cos(angle);
                const ty = Math.sin(angle);

                // Set CSS variables for animation
                flower.style.setProperty('--tx', tx);
                flower.style.setProperty('--ty', ty);

                // Random size and duration
                flower.style.fontSize = (20 + Math.random() * 40) + 'px';
                flower.style.animationDuration = (2 + Math.random() * 3) + 's';

                // Random color
                const colors = ['#ffffff', '#ffcccc', '#ffccff', '#ffffcc', '#ccffcc', '#ccccff'];
                flower.style.color = colors[Math.floor(Math.random() * colors.length)];

                document.body.appendChild(flower);

                // Remove after animation
                setTimeout(() => {
                    if (flower.parentNode) {
                        flower.remove();
                    }
                }, 5000);

                return flowersCreated;
            }

            // Start massive flower burst (7000 flowers)
            function startMassiveFlowerBurst() {
                // Create flowers in batches for performance
                const BATCH_SIZE = 100;
                const BATCH_DELAY = 10; // ms between batches

                function createBatch(batchNum) {
                    for (let i = 0; i < BATCH_SIZE; i++) {
                        setTimeout(() => {
                            createMassiveFlower();
                        }, i * 2); // Stagger within batch
                    }

                    if (flowersCreated < TOTAL_FLOWERS) {
                        setTimeout(() => {
                            createBatch(batchNum + 1);
                        }, BATCH_DELAY);
                    } else {
                        // All flowers created, start the surprise
                        setTimeout(() => {
                            startSurprise();
                        }, 1000);
                    }
                }

                createBatch(0);
            }

            // Start the main surprise (after 7000 flowers)
            function startSurprise() {
                // Show elements
                document.getElementById('top-heart').style.display = 'block';
                document.getElementById('message-container').style.display = 'block';
                document.getElementById('lyrics-indicator').style.display = 'flex';

                // Start song lyrics
                startSongLyrics();

                // Play music
                playMusic();
            }

            // Create song lyrics (just text, no background/border)
            function createSongLyric() {
                if (currentLyricIndex >= songLyrics.length) {
                    currentLyricIndex = 0;
                }

                const lyricText = songLyrics[currentLyricIndex];
                currentLyricIndex++;

                const lyric = document.createElement('div');
                lyric.className = 'song-lyric';
                lyric.textContent = lyricText;

                // Random vertical position
                const startY = Math.random() * 70 + 15; // 15% to 85%
                lyric.style.setProperty('--start-y', startY + 'vh');

                // Random size
                lyric.style.fontSize = (28 + Math.random() * 16) + 'px';
                lyric.style.animationDuration = (10 + Math.random() * 5) + 's';

                // Random color (just white with different glow)
                lyric.style.color = 'white';
                lyric.style.textShadow = `0 0 ${20 + Math.random() * 20}px rgba(255, 255, 255, 0.9),
                                         0 0 ${40 + Math.random() * 30}px rgba(255, 255, 255, 0.7),
                                         0 0 ${60 + Math.random() * 40}px rgba(${Math.random() * 255}, ${Math.random() * 255}, 255, 0.9)`;

                document.body.appendChild(lyric);

                // Update lyrics indicator
                document.querySelector('#lyrics-indicator span').textContent = `"${lyricText}"`;

                // Remove after animation
                setTimeout(() => {
                    if (lyric.parentNode) {
                        lyric.remove();
                    }
                }, 15000);

                return lyricText;
            }

            // Start song lyrics
            function startSongLyrics() {
                if (lyricInterval) {
                    clearInterval(lyricInterval);
                }

                // Start lyrics at a regular interval
                lyricInterval = setInterval(() => {
                    if (isMusicPlaying) {
                        createSongLyric();
                    }
                }, 6000); // Every 6 seconds

                // Initial burst of lyrics
                for (let i = 0; i < Math.min(3, songLyrics.length); i++) {
                    setTimeout(() => {
                        createSongLyric();
                    }, i * 2000);
                }
            }

            // Play music
            function playMusic() {
                const audio = document.getElementById('love-music');

                audio.volume = 0.7;
                audio.play()
                    .then(() => {
                        isMusicPlaying = true;

                        // Update lyrics indicator
                        const indicator = document.querySelector('#lyrics-indicator span');
                        indicator.textContent = `Now Playing: {{ surprise.song_name }}`;
                    })
                    .catch(e => {
                        // Play on first interaction
                        const playOnClick = () => {
                            audio.play();
                            isMusicPlaying = true;
                            document.removeEventListener('click', playOnClick);
                            document.removeEventListener('touchstart', playOnClick);
                        };
                        document.addEventListener('click', playOnClick);
                        document.addEventListener('touchstart', playOnClick);
                    });

                audio.addEventListener('play', () => {
                    isMusicPlaying = true;
                });

                audio.addEventListener('pause', () => {
                    isMusicPlaying = false;
                });

                audio.addEventListener('ended', () => {
                    isMusicPlaying = false;
                    setTimeout(() => {
                        audio.play();
                    }, 1000);
                });
            }

            // Create click hearts
            function createClickHeart(x, y) {
                const heart = document.createElement('div');
                heart.className = 'click-heart';
                heart.textContent = '💖';

                heart.style.left = x + 'px';
                heart.style.top = y + 'px';
                heart.style.color = 'white';
                heart.style.fontSize = (25 + Math.random() * 30) + 'px';
                heart.style.animationDuration = '2s';

                document.body.appendChild(heart);

                setTimeout(() => {
                    if (heart.parentNode) {
                        heart.remove();
                    }
                }, 2000);
            }

            // Initialize everything when page loads
            window.addEventListener('load', function() {
                // Start countdown immediately
                startCountdown();

                // Click to create hearts (only after surprise starts)
                setTimeout(() => {
                    document.addEventListener('click', function(event) {
                        if (document.getElementById('countdown-overlay').style.display === 'none') {
                            for (let i = 0; i < 5; i++) {
                                setTimeout(() => {
                                    createClickHeart(event.clientX, event.clientY);
                                }, i * 100);
                            }
                        }
                    });

                    // Touch support
                    document.addEventListener('touchstart', function(event) {
                        if (document.getElementById('countdown-overlay').style.display === 'none') {
                            const touch = event.touches[0];
                            for (let i = 0; i < 5; i++) {
                                setTimeout(() => {
                                    createClickHeart(touch.clientX, touch.clientY);
                                }, i * 100);
                            }
                        }
                    });
                }, 10000); // Enable after everything loads
            });
        </script>
    </body>
    </html>
    ''',
                                  receiver=surprise['receiver'],
                                  sender=surprise['sender'],
                                  message=surprise['message'],
                                  surprise=surprise,
                                  has_background=has_background,
                                  background_url=background_url,
                                  song_url=song_url,
                                  song_lyrics=song_lyrics,
                                  FALLING_FLOWERS=FALLING_FLOWERS)


# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'surprises': len(surprises),
        'total_views': sum(view_counts.values())
    })


# Create placeholder music files
def create_placeholder_music_files():
    for song in BUILTIN_SONGS:
        file_path = os.path.join('static', 'music', song['file'])
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(b'')


if __name__ == '__main__':
    create_placeholder_music_files()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)