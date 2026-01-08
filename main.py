"""
AI Chatbot Application
Main entry point for the Flask-based chatbot with learning capability
"""

from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from openai import OpenAI
from knowledge_base import KnowledgeBase

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    print("INFO: Running in DEMO mode (no OpenAI API key configured)")
    client = None
else:
    client = OpenAI(api_key=openai_api_key)

# Initialize Knowledge Base
kb = KnowledgeBase()

# Store conversation history for context
conversation_history = []

# Demo responses for offline mode
DEMO_RESPONSES = {
    'hello': 'Hello! How can I help you today?',
    'hi': 'Hi there! What can I do for you?',
    'how are you': 'I\'m doing great, thanks for asking! How about you?',
    'what is ai': 'AI (Artificial Intelligence) refers to computer systems designed to perform tasks that typically require human intelligence.',
    'what is python': 'Python is a popular programming language known for its simplicity and readability.',
    'help': 'You can ask me questions about anything! Try asking me about AI, Python, or just say hello.',
    'thank you': 'You\'re welcome! If you have more questions, feel free to ask.',
    'default': 'That\'s an interesting question! In demo mode, I can provide helpful responses. For more advanced AI features, please configure an OpenAI API key.'
}

def get_demo_response(user_message):
    """Generate a demo response based on keywords"""
    message_lower = user_message.lower().strip()
    
    # Check for keyword matches
    for keyword, response in DEMO_RESPONSES.items():
        if keyword in message_lower:
            return response
    
    # Return default response
    return DEMO_RESPONSES['default']

@app.route('/')
def index():
    """Render the main chatbot page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests with learning capability"""
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'status': 'error', 'message': 'Empty message'}), 400
    
    try:
        # First, try to get response from learned knowledge
        learned = kb.get_learned_response(user_message)
        if learned and learned['count'] > 0:
            bot_message = learned['response']
            source = 'learned'
        else:
            # Then try OpenAI if available
            if client:
                try:
                    response = client.chat.completions.create(
                        model='gpt-3.5-turbo',
                        messages=[{'role': 'user', 'content': user_message}],
                        max_tokens=500,
                        temperature=0.7
                    )
                    bot_message = response.choices[0].message.content
                    source = 'openai'
                except Exception as api_error:
                    print(f"OpenAI error: {str(api_error)}")
                    # Fall back to demo if OpenAI fails
                    bot_message = get_demo_response(user_message)
                    source = 'demo'
            else:
                # Use demo/offline mode
                bot_message = get_demo_response(user_message)
                source = 'demo'
        
        # Learn from this conversation
        kb.add_conversation(user_message, bot_message)
        
        return jsonify({
            'status': 'success',
            'message': bot_message,
            'source': source,
            'learned': len(kb.knowledge['learned_qa'])
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'version': '1.0.0'})

@app.route('/api/stats', methods=['GET'])
def stats():
    """Get learning statistics"""
    return jsonify(kb.get_stats())

@app.route('/api/knowledge', methods=['GET'])
def get_knowledge():
    """Get all learned knowledge"""
    return jsonify(kb.export_knowledge())

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=5000)
