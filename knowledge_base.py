"""
Knowledge Base Manager
Stores and manages learned conversations
"""

import json
import os
from datetime import datetime
from pathlib import Path

class KnowledgeBase:
    def __init__(self, filepath='data/knowledge_base.json'):
        self.filepath = filepath
        self.ensure_data_dir()
        self.load_knowledge()
    
    def ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        Path(self.filepath).parent.mkdir(parents=True, exist_ok=True)
    
    def load_knowledge(self):
        """Load knowledge base from file"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.knowledge = json.load(f)
            except:
                self.knowledge = {
                    'conversations': [],
                    'learned_qa': {},
                    'stats': {'total_messages': 0, 'total_conversations': 0}
                }
        else:
            self.knowledge = {
                'conversations': [],
                'learned_qa': {},
                'stats': {'total_messages': 0, 'total_conversations': 0}
            }
    
    def save_knowledge(self):
        """Save knowledge base to file"""
        self.ensure_data_dir()
        with open(self.filepath, 'w') as f:
            json.dump(self.knowledge, f, indent=2)
    
    def add_conversation(self, user_message, bot_response):
        """Add a conversation pair to the knowledge base"""
        # Extract keywords from user message
        keywords = self.extract_keywords(user_message)
        
        # Check if similar question exists
        found_similar = False
        for qa in self.knowledge['learned_qa'].values():
            if self.similarity_score(user_message, qa['question']) > 0.7:
                qa['count'] += 1
                qa['last_updated'] = datetime.now().isoformat()
                found_similar = True
                break
        
        # Add as new Q&A if not similar
        if not found_similar:
            qa_id = f"qa_{len(self.knowledge['learned_qa']) + 1}"
            self.knowledge['learned_qa'][qa_id] = {
                'question': user_message,
                'response': bot_response,
                'keywords': keywords,
                'count': 1,
                'created': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        
        # Update stats
        self.knowledge['stats']['total_messages'] += 2
        
        # Save to file
        self.save_knowledge()
    
    def get_learned_response(self, user_message):
        """Try to find a learned response for the user message"""
        best_match = None
        best_score = 0.6
        
        for qa in self.knowledge['learned_qa'].values():
            score = self.similarity_score(user_message, qa['question'])
            if score > best_score:
                best_score = score
                best_match = qa
        
        return best_match
    
    def extract_keywords(self, text):
        """Extract keywords from text"""
        # Simple keyword extraction - split and filter
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'how', 'why', 'where', 'when', 'who', 'which'}
        words = text.lower().split()
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        return keywords[:5]  # Top 5 keywords
    
    def similarity_score(self, text1, text2):
        """Calculate similarity between two texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0
    
    def get_stats(self):
        """Get learning statistics"""
        return {
            'total_learned_qa': len(self.knowledge['learned_qa']),
            'total_messages': self.knowledge['stats']['total_messages'],
            'total_conversations': len(self.knowledge['conversations'])
        }
    
    def export_knowledge(self):
        """Export learned knowledge as readable format"""
        qa_list = []
        for qa in self.knowledge['learned_qa'].values():
            qa_list.append({
                'Q': qa['question'],
                'A': qa['response'],
                'Uses': qa['count']
            })
        return sorted(qa_list, key=lambda x: x['Uses'], reverse=True)
