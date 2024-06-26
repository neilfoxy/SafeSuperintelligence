from flask import Flask, request, jsonify
import numpy as np
from modules.prefrontal_cortex import PrefrontalCortex
from modules.hippocampus import Hippocampus
from training_pair_generator.llama3_interface import Llama3Interface
from web_scraping_engine.curiosity_scraper import CuriosityScraper

app = Flask(__name__)

# Initialize brain modules
prefrontal_cortex = PrefrontalCortex()
hippocampus = Hippocampus()

# Initialize training pair generator
llama3_interface = Llama3Interface()

# Initialize web scraping engine
curiosity_scraper = CuriosityScraper()

conversation_history = []
feedback_history = []

@app.route('/predict', methods=['POST'])
def predict_route():
    data = request.json
    input_data = {'input': data['input']}  # Wrap the input list in a dictionary
    prediction = prefrontal_cortex.make_decision(input_data)
    return jsonify({'decision': prediction})

@app.route('/scrape', methods=['POST'])
def scrape_route():
    data = request.json
    url = data['url']
    content = curiosity_scraper.scrape_webpage(url)
    prefrontal_cortex.update_knowledge_base(url, content)
    return jsonify({'content': content})

@app.route('/conversation', methods=['POST'])
def conversation_route():
    global conversation_history
    user_input = request.json['user_input']
    conversation_history.append(f"User: {user_input}")
    
    response, reflection = process_conversation(user_input, conversation_history)
    
    conversation_history.append(f"AI: {response}")
    
    return jsonify({'response': response, 'learning_reflection': reflection})

def process_conversation(user_input, conversation_history):
    decision = prefrontal_cortex.make_decision({
        'user_input': user_input, 
        'conversation_history': conversation_history
    })
    
    # Generate training pairs based on the conversation
    training_pairs = llama3_interface.generate_pairs(user_input)
    for pair in training_pairs:
        prefrontal_cortex.update_knowledge_base(pair['question'], pair['answer'])
    
    reflection = prefrontal_cortex.reflect_on_decision(decision)
    
    return decision, reflection

@app.route('/feedback', methods=['POST'])
def feedback_route():
    global feedback_history
    feedback = request.json['feedback']
    response = request.json['response']
    feedback_history.append({'response': response, 'feedback': feedback})
    
    prefrontal_cortex.process_feedback(response, feedback)
    if "great" in feedback.lower():
        prefrontal_cortex.reinforce_behavior(response)
    elif "bad" in feedback.lower():
        prefrontal_cortex.adjust_behavior(response)
    
    return jsonify({'status': 'Feedback received and processed'})

@app.route('/update-dataset', methods=['POST'])
def update_dataset_route():
    data = request.json
    urls = data.get('urls', [])
    if urls:
        new_data = curiosity_scraper.fetch_and_update_data(urls)
        for url, content in new_data.items():
            prefrontal_cortex.update_knowledge_base(url, content)
        return jsonify({'status': 'Dataset updated'})
    return jsonify({'status': 'No URLs provided'})

@app.route('/process_image', methods=['POST'])
def process_image():
    image = request.files['image']
    result = visual_cortex.process_image(image)
    prefrontal_cortex.integrate_sensory_input('visual', result)
    return jsonify({'status': 'Image processed', 'result': result})

@app.route('/process_audio', methods=['POST'])
def process_audio():
    audio = request.files['audio']
    result = auditory_cortex.process_audio(audio)
    prefrontal_cortex.integrate_sensory_input('auditory', result)
    return jsonify({'status': 'Audio processed', 'result': result})

@app.route('/make_decision', methods=['POST'])
def make_decision():
    data = request.json['data']
    decision = prefrontal_cortex.make_decision(data)
    return jsonify({'decision': decision})

@app.route('/store_memory', methods=['POST'])
def store_memory():
    data = request.json['data']
    memory_id = hippocampus.store_memory(data)
    prefrontal_cortex.update_knowledge_base(f"memory_{memory_id}", data)
    return jsonify({'status': 'Memory stored', 'memory_id': memory_id})

@app.route('/recall_memory', methods=['POST'])
def recall_memory():
    query = request.json['query']
    memory = hippocampus.recall_memory(query)
    prefrontal_cortex.integrate_memory(memory)
    return jsonify({'memory': memory})

@app.route('/generate_training_pairs', methods=['POST'])
def generate_training_pairs():
    prompt = request.json['prompt']
    pairs = llama3_interface.generate_pairs(prompt)
    for pair in pairs:
        prefrontal_cortex.update_knowledge_base(pair['question'], pair['answer'])
    return jsonify({'pairs': pairs})

@app.route('/get-knowledge', methods=['GET'])
def get_knowledge_route():
    key = request.args.get('key')
    knowledge = prefrontal_cortex.get_knowledge(key)
    return jsonify({'knowledge': knowledge})

@app.route('/update-knowledge', methods=['POST'])
def update_knowledge_route():
    data = request.json
    key = data.get('key')
    value = data.get('value')
    prefrontal_cortex.update_knowledge_base(key, value)
    return jsonify({'status': 'Knowledge updated'})

@app.route('/set-goal', methods=['POST'])
def set_goal_route():
    data = request.json
    goal = data.get('goal')
    priority = data.get('priority', 1.0)
    prefrontal_cortex.set_goal(goal, priority)
    return jsonify({'status': 'Goal set'})

@app.route('/save-state', methods=['POST'])
def save_state_route():
    filename = request.json.get('filename', 'brain_state.pkl')
    state = {
        'prefrontal_cortex': prefrontal_cortex.save_state(),
        'hippocampus': hippocampus.save_state(),
        'visual_cortex': visual_cortex.save_state(),
        'auditory_cortex': auditory_cortex.save_state()
    }
    joblib.dump(state, filename)
    return jsonify({'status': 'State saved'})

@app.route('/load-state', methods=['POST'])
def load_state_route():
    filename = request.json.get('filename', 'brain_state.pkl')
    state = joblib.load(filename)
    prefrontal_cortex.load_state(state['prefrontal_cortex'])
    hippocampus.load_state(state['hippocampus'])
    visual_cortex.load_state(state['visual_cortex'])
    auditory_cortex.load_state(state['auditory_cortex'])
    return jsonify({'status': 'State loaded'})

if __name__ == '__main__':
    app.run(port=5000)
