import os
import json

class KnowledgeBase:
    def __init__(self, file_path="knowledge_base.json"):
        self.file_path = file_path
        self.data = self._load_data()

    def _load_data(self):
        """Safely read the JSON file, or return empty tracking data if missing."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {"conversations": []}
        return {"conversations": []}

    def get_learned_response(self, user_message):
        """Scan local cached interactions."""
        # Simple fallback tracker if your storage uses a basic array format
        conversations = self.data.get("conversations", [])
        user_msg_clean = user_message.strip().lower()
        
        for conv in conversations:
            if conv.get("prompt", "").strip().lower() == user_msg_clean:
                return {"response": conv.get("response")}
        return None

    def add_conversation(self, user_message, bot_reply):
        """Append to memory string layer and attempt to update disk safely."""
        if "conversations" not in self.data:
            self.data["conversations"] = []
            
        self.data["conversations"].append({
            "prompt": user_message,
            "response": bot_reply
        })

        # CRASH FIX: Gracefully bypass writing if on read-only environments
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except (IOError, OSError):
            # This catches Vercel's read-only file system restriction silently
            pass