"""
Knowledge Base Manager
Stores and manages learned conversations.
"""

import json
import os
from datetime import datetime
from pathlib import Path


class KnowledgeBase:
    def __init__(self, filepath="data/knowledge_base.json"):
        self.filepath = filepath
        self.ensure_data_dir()
        self.load_knowledge()

    # ==========================================
    # CREATE DATA DIRECTORY
    # ==========================================
    def ensure_data_dir(self):
        """Create data directory if it does not exist."""
        Path(self.filepath).parent.mkdir(parents=True, exist_ok=True)

    # ==========================================
    # LOAD KNOWLEDGE
    # ==========================================
    def load_knowledge(self):
        """Load the knowledge base from the JSON file."""
        default_structure = {
            "conversations": [],
            "learned_qa": {},
            "stats": {
                "total_messages": 0,
                "total_conversations": 0,
            },
        }

        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self.knowledge = json.load(f)
            except Exception as e:
                print("Error loading knowledge base:", e)
                self.knowledge = default_structure
        else:
            self.knowledge = default_structure

    # ==========================================
    # SAVE KNOWLEDGE
    # ==========================================
    def save_knowledge(self):
        """Save the knowledge base to a JSON file."""
        self.ensure_data_dir()
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.knowledge, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print("Error saving knowledge:", e)

    # ==========================================
    # ADD CONVERSATION
    # ==========================================
    def add_conversation(self, user_message, bot_response):
        """Add a user/bot conversation pair to the knowledge base."""
        conversation = {
            "user": user_message,
            "bot": bot_response,
            "timestamp": datetime.now().isoformat(),
        }

        self.knowledge["conversations"].append(conversation)
        keywords = self.extract_keywords(user_message)
        found_similar = False

        for qa in self.knowledge["learned_qa"].values():
            score = self.similarity_score(user_message, qa["question"])
            if score > 0.7:
                qa["count"] += 1
                qa["last_updated"] = datetime.now().isoformat()
                found_similar = True
                break

        if not found_similar:
            qa_id = f"qa_{len(self.knowledge['learned_qa']) + 1}"
            self.knowledge["learned_qa"][qa_id] = {
                "question": user_message,
                "response": bot_response,
                "keywords": keywords,
                "count": 1,
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
            }

        self.knowledge["stats"]["total_messages"] += 2
        self.knowledge["stats"]["total_conversations"] += 1
        self.save_knowledge()

    # ==========================================
    # GET LEARNED RESPONSE
    # ==========================================
    def get_learned_response(self, user_message):
        """Return the best learned response for the given message."""
        best_match = None
        best_score = 0.75

        for qa in self.knowledge["learned_qa"].values():
            score = self.similarity_score(user_message, qa["question"])
            if score > best_score:
                best_score = score
                best_match = qa

        return best_match

    # ==========================================
    # EXTRACT KEYWORDS
    # ==========================================
    def extract_keywords(self, text):
        """Extract simple keywords from text."""
        stop_words = {
            "the", "a", "an", "is", "are",
            "was", "were", "what", "how",
            "why", "where", "when", "who",
            "which", "this", "that", "can",
            "you", "tell",
        }

        words = text.lower().split()
        keywords = [
            word for word in words
            if len(word) > 3 and word not in stop_words
        ]

        return keywords[:5]

    # ==========================================
    # SIMILARITY SCORE
    # ==========================================
    def similarity_score(self, text1, text2):
        """Calculate a simple Jaccard similarity score."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union

    # ==========================================
    # GET STATS
    # ==========================================
    def get_stats(self):
        """Return current knowledge base statistics."""
        return {
            "total_learned_qa": len(self.knowledge["learned_qa"]),
            "total_messages": self.knowledge["stats"]["total_messages"],
            "total_conversations": self.knowledge["stats"]["total_conversations"],
        }

    # ==========================================
    # EXPORT KNOWLEDGE
    # ==========================================
    def export_knowledge(self):
        """Return learned QA items in a readable exported format."""
        qa_list = [
            {
                "Question": qa["question"],
                "Answer": qa["response"],
                "Uses": qa["count"],
            }
            for qa in self.knowledge["learned_qa"].values()
        ]

        return sorted(qa_list, key=lambda x: x["Uses"], reverse=True)
