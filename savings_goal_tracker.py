# savings_goal_tracker.py (Smelly Version)
import datetime
from typing import Dict, List, Optional

class SavingsGoalTracker:
    def __init__(self, currency_converter):
        self.currency_converter = currency_converter
        self.goals = {}
        self.goal_id_counter = 0
    
    # Bad Smell 1: Long Method with too many responsibilities
    def create_goal(self, user_id, name, target_amount, currency, description=""):
        if not user_id or not name or target_amount <= 0 or not currency:
            return None
        
        # Generate a unique ID for the goal
        self.goal_id_counter += 1
        goal_id = f"GOAL-{self.goal_id_counter}"
        
        # Initialize the goal with details
        timestamp = datetime.datetime.now().isoformat()
        
        # Check if currency is valid by trying to get its rate to USD
        try:
            self.currency_converter.get_rate(currency, "USD")
        except ValueError:
            return None
        
        # Create goal object
        goal = {
            "id": goal_id,
            "user_id": user_id,
            "name": name,
            "description": description,
            "target_amount": target_amount,
            "current_amount": 0,
            "currency": currency,
            "created_at": timestamp,
            "updated_at": timestamp,
            "contributions": []
        }
        
        # Store the goal
        if user_id not in self.goals:
            self.goals[user_id] = {}
        self.goals[user_id][goal_id] = goal
        
        # Calculate initial progress
        progress = 0
        
        # Log creation event
        print(f"Created goal {goal_id} for user {user_id}: {name}, {target_amount} {currency}")
        
        # Return the goal with calculated progress
        return {**goal, "progress": progress}
    
    # Bad Smell 2: Duplicate code and logic
    def add_contribution(self, user_id, goal_id, amount):
        # Find the goal
        if user_id not in self.goals or goal_id not in self.goals[user_id]:
            return None
        
        goal = self.goals[user_id][goal_id]
        
        # Validate amount
        if amount <= 0:
            return None
        
        # Create contribution record
        timestamp = datetime.datetime.now().isoformat()
        contribution = {
            "amount": amount,
            "timestamp": timestamp
        }
        
        # Update goal
        goal["current_amount"] += amount
        goal["updated_at"] = timestamp
        goal["contributions"].append(contribution)
        
        # Calculate progress
        progress = (goal["current_amount"] / goal["target_amount"]) * 100
        
        # Log contribution
        print(f"Added contribution of {amount} {goal['currency']} to goal {goal_id}")
        
        # Return updated goal with progress
        return {**goal, "progress": progress}
    
    def convert_goal_currency(self, user_id, goal_id, new_currency):
        # Find the goal
        if user_id not in self.goals or goal_id not in self.goals[user_id]:
            return None
        
        goal = self.goals[user_id][goal_id]
        
        # Validate currency
        try:
            self.currency_converter.get_rate(new_currency, "USD")
        except ValueError:
            return None
        
        old_currency = goal["currency"]
        
        # Skip if same currency
        if old_currency == new_currency:
            progress = (goal["current_amount"] / goal["target_amount"]) * 100
            return {**goal, "progress": progress}
        
        # Convert target amount
        target_result = self.currency_converter.convert(
            goal["target_amount"], old_currency, new_currency
        )
        
        # Convert current amount
        current_result = self.currency_converter.convert(
            goal["current_amount"], old_currency, new_currency
        )
        
        # Update goal
        goal["target_amount"] = target_result["converted_amount"]
        goal["current_amount"] = current_result["converted_amount"]
        goal["currency"] = new_currency
        goal["updated_at"] = datetime.datetime.now().isoformat()
        
        # Calculate progress
        progress = (goal["current_amount"] / goal["target_amount"]) * 100
        
        # Log conversion
        print(f"Converted goal {goal_id} from {old_currency} to {new_currency}")
        
        # Return updated goal with progress
        return {**goal, "progress": progress}
    
    def get_goal(self, user_id, goal_id):
        if user_id not in self.goals or goal_id not in self.goals[user_id]:
            return None
        
        goal = self.goals[user_id][goal_id]
        
        # Calculate progress
        progress = (goal["current_amount"] / goal["target_amount"]) * 100
        
        # Return goal with progress
        return {**goal, "progress": progress}
    
    def get_all_goals(self, user_id):
        if user_id not in self.goals:
            return []
        
        # Calculate progress for each goal
        goals_with_progress = []
        for goal_id, goal in self.goals[user_id].items():
            progress = (goal["current_amount"] / goal["target_amount"]) * 100
            goals_with_progress.append({**goal, "progress": progress})
        
        return goals_with_progress