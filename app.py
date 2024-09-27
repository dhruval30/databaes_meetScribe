from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter
import re

app = Flask(__name__)

# Directory to save uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to read the transcript and get speaker interactions
def get_speaker_data():
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'transcript.txt'), 'r', encoding='utf-8') as file:
        text_data = file.read()

    # Extract speaker mentions (assuming "Speaker [A-Z]" format)
    pattern = r"Speaker [A-Z]"
    speakers = re.findall(pattern, text_data)
    speaker_counts = Counter(speakers)

    return speaker_counts, speakers

# Function to calculate the max individual peak for a speaker
def get_max_individual_peak(speakers):
    num_parts = 10
    max_peak = 0

    for speaker in set(speakers):  # Loop through each unique speaker
        speaker_time_data = [0] * num_parts
        speaker_mentions = [i for i, sp in enumerate(speakers) if sp == speaker]

        # Distribute mentions into time slots
        for mention in speaker_mentions:
            time_slot = mention % num_parts
            speaker_time_data[time_slot] += 1

        # Check the peak interaction for this speaker
        max_peak = max(max_peak, max(speaker_time_data))

    return max_peak

# Function to read the transcript text
def get_transcript_text():
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'transcript.txt'), 'r', encoding='utf-8') as file:
        return file.read()

# Route for the landing page (file upload form)
@app.route('/')
def landing():
    return render_template('landing.html')

# Route to handle file upload and redirect to selection page
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'transcript' not in request.files:
        return redirect('/')
    
    file = request.files['transcript']
    if file.filename == '':
        return redirect('/')
    
    if file and file.filename.endswith('.txt'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'transcript.txt')
        file.save(filepath)  # Save the uploaded file as transcript.txt
        return redirect(url_for('selection'))
    else:
        return "Invalid file format. Please upload a .txt file."

# Route for the selection page where users can choose between "Meety" or "Dashboard"
@app.route('/selection')
def selection():
    return render_template('selection.html')

# Chat page after successful file upload
@app.route('/chat')
def chat():
    return render_template('chat.html')

# Route for the dashboard page
@app.route('/dashboard')
def dashboard():
    # Get speaker counts and mentions
    speaker_counts, speakers = get_speaker_data()

    # Generate overall participation graph (retain default Y-axis behavior)
    fig, ax = plt.subplots()
    speaker_names = list(speaker_counts.keys())
    interaction_counts = list(speaker_counts.values())
    ax.bar(speaker_names, interaction_counts)
    ax.set_title("Overall Participation")
    ax.set_xlabel("Speakers")
    ax.set_ylabel("Number of Interactions")

    # Save the graph to a PNG image in memory
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    overall_graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # Render the dashboard
    return render_template('dashboard.html', speaker_counts=speaker_counts, overall_graph_url=overall_graph_url)

# Route to handle AJAX requests to update the graph for each speaker
@app.route('/update_graph', methods=['POST'])
def update_graph():
    selected_speaker = request.form.get('speaker')

    # Get speaker data and mentions
    speaker_counts, speakers = get_speaker_data()

    # Find the max peak of individual speaker interactions
    max_individual_peak = get_max_individual_peak(speakers)

    # Time slot analysis (e.g., split into 10 parts)
    num_parts = 10
    speaker_time_data = [0] * num_parts
    speaker_mentions = [i for i, speaker in enumerate(speakers) if speaker == selected_speaker]

    # Distribute mentions into time slots
    for mention in speaker_mentions:
        time_slot = mention % num_parts
        speaker_time_data[time_slot] += 1

    # Create a graph for the selected speaker
    fig, ax = plt.subplots()
    ax.plot(range(num_parts), speaker_time_data)
    ax.set_title(f"Interaction Over Time for {selected_speaker}")
    ax.set_xlabel("Time Slot")
    ax.set_ylabel("Number of Interactions")
    ax.set_ylim(0, max_individual_peak)  # Set Y-axis to start from 0, and use the max individual peak
    ax.grid(True)

    # Save the updated graph to a PNG image in memory
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    # Return the updated graph as a JSON response
    return jsonify({'graph_url': graph_url})

# Route to generate action points based on the transcript
@app.route('/generate_action_points', methods=['POST'])
def generate_action_points():
    # Get the transcript text
    transcript_text = get_transcript_text()

    # Generate action points (simple mock-up for demonstration)
    action_points = "1. Review key ideas.\n2. Follow up on unresolved discussions.\n3. Plan the next meeting."
    
    # You could replace the above with actual NLP-based analysis if available.

    return jsonify({'action_points': action_points})

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
