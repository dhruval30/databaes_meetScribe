from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter
import re

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_speaker_data():
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'transcript.txt'), 'r', encoding='utf-8') as file:
        text_data = file.read()
    pattern = r"Speaker [A-Z]"
    speakers = re.findall(pattern, text_data)
    speaker_counts = Counter(speakers)
    return speaker_counts, speakers

def get_max_individual_peak(speakers):
    num_parts = 10
    max_peak = 0
    for speaker in set(speakers):
        speaker_time_data = [0] * num_parts
        speaker_mentions = [i for i, sp in enumerate(speakers) if sp == speaker]
        for mention in speaker_mentions:
            time_slot = mention % num_parts
            speaker_time_data[time_slot] += 1
        max_peak = max(max_peak, max(speaker_time_data))
    return max_peak

def get_transcript_text():
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'transcript.txt'), 'r', encoding='utf-8') as file:
        return file.read()

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'transcript' not in request.files:
        return redirect('/')
    file = request.files['transcript']
    if file.filename == '':
        return redirect('/')
    if file and file.filename.endswith('.txt'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'transcript.txt')
        file.save(filepath)
        return redirect(url_for('selection'))
    else:
        return "Invalid file format. Please upload a .txt file."

@app.route('/selection')
def selection():
    return render_template('selection.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/dashboard')
def dashboard():
    speaker_counts, speakers = get_speaker_data()
    fig, ax = plt.subplots()
    speaker_names = list(speaker_counts.keys())
    interaction_counts = list(speaker_counts.values())
    ax.bar(speaker_names, interaction_counts)
    ax.set_title("Overall Participation")
    ax.set_xlabel("Speakers")
    ax.set_ylabel("Number of Interactions")
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    overall_graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return render_template('dashboard.html', speaker_counts=speaker_counts, overall_graph_url=overall_graph_url)

@app.route('/update_graph', methods=['POST'])
def update_graph():
    selected_speaker = request.form.get('speaker')
    speaker_counts, speakers = get_speaker_data()
    max_individual_peak = get_max_individual_peak(speakers)
    num_parts = 10
    speaker_time_data = [0] * num_parts
    speaker_mentions = [i for i, speaker in enumerate(speakers) if speaker == selected_speaker]
    for mention in speaker_mentions:
        time_slot = mention % num_parts
        speaker_time_data[time_slot] += 1
    fig, ax = plt.subplots()
    ax.plot(range(num_parts), speaker_time_data)
    ax.set_title(f"Interaction Over Time for {selected_speaker}")
    ax.set_xlabel("Time Slot")
    ax.set_ylabel("Number of Interactions")
    ax.set_ylim(0, max_individual_peak)
    ax.grid(True)
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return jsonify({'graph_url': graph_url})

@app.route('/generate_action_points', methods=['POST'])
def generate_action_points():
    transcript_text = get_transcript_text()
    action_points = "1. Review key ideas.\n2. Follow up on unresolved discussions.\n3. Plan the next meeting."
    return jsonify({'action_points': action_points})

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
