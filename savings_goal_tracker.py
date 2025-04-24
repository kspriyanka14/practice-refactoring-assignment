import datetime
from typing import Dict, List, Optional, Union

class SavingsGoalTracker:
    def __init__(self, currency_converter):
        self.currency_converter = currency_converter
        self.goals = {}
        self.goal_id_counter = 0
    
    def _generate_goal_id(self) -> str:
        """Generate a unique goal identifier."""
        self.goal_id_counter += 1
        return f"GOAL-{self.goal_id_counter}"
    
    def _get_current_timestamp(self) -> str:
        """Get the current timestamp in ISO format."""
        return datetime.datetime.now().isoformat()
    
    def _validate_currency(self, currency: str) -> bool:
        """Validate that a currency is supported."""
        try:
            self.currency_converter.get_rate(currency, "USD")
            return True
        except ValueError:
            return False
    
    def _calculate_progress(self, current: float, target: float) -> float:
        """Calculate progress percentage."""
        return (current / target) * 100 if target > 0 else 0
    
    # Refactored: Shorter method with single responsibility
    def create_goal(self, user_id: str, name: str, target_amount: float, 
                   currency: str, description: str = "") -> Optional[Dict]:
        """Create a new savings goal for a user."""
        # Validate inputs
        if not user_id or not name or target_amount <= 0 or not currency:
            return None
        
        # Validate currency
        if not self._validate_currency(currency):
            return None
        
        goal_id = self._generate_goal_id()
        timestamp = self._get_current_timestamp()
        
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
        
        # Return the goal with calculated progress
        return self._format_goal_with_progress(goal)
    
    # Refactored: Eliminated duplicate code by extracting common functionality
    def _format_goal_with_progress(self, goal: Dict) -> Dict:
        """Add progress percentage to a goal object."""
        progress = self._calculate_progress(goal["current_amount"], goal["target_amount"])
        return {**goal, "progress": progress}
    
    def add_contribution(self, user_id: str, goal_id: str, amount: float) -> Optional[Dict]:
        """Add a contribution to a savings goal."""
        # Get the goal
        goal = self._get_goal_dict(user_id, goal_id)
        if not goal:
            return None
        
        # Validate amount
        if amount <= 0:
            return None
        
        # Create contribution record
        timestamp = self._get_current_timestamp()
        contribution = {
            "amount": amount,
            "timestamp": timestamp
        }
        
        # Update goal
        goal["current_amount"] += amount
        goal["updated_at"] = timestamp
        goal["contributions"].append(contribution)
        
        return self._format_goal_with_progress(goal)
    
    def _get_goal_dict(self, user_id: str, goal_id: str) -> Optional[Dict]:
        """Retrieve a goal dictionary without progress calculation."""
        if user_id not in self.goals or goal_id not in self.goals[user_id]:
            return None
        return self.goals[user_id][goal_id]
    
    def convert_goal_currency(self, user_id: str, goal_id: str, new_currency: str) -> Optional[Dict]:
        """Convert a goal's currency to a different currency."""
        # Get the goal
        goal = self._get_goal_dict(user_id, goal_id)
        if not goal:
            return None
        
        # Validate currency
        if not self._validate_currency(new_currency):
            return None
        
        old_currency = goal["currency"]
        
        # Skip if same currency
        if old_currency == new_currency:
            return self._format_goal_with_progress(goal)
        
        # Convert amounts
        target_result = self.currency_converter.convert(
            goal["target_amount"], old_currency, new_currency
        )
        
        current_result = self.currency_converter.convert(
            goal["current_amount"], old_currency, new_currency
        )
        
        # Update goal
        goal["target_amount"] = target_result["converted_amount"]
        goal["current_amount"] = current_result["converted_amount"]
        goal["currency"] = new_currency
        goal["updated_at"] = self._get_current_timestamp()
        
        return self._format_goal_with_progress(goal)
    
    def get_goal(self, user_id: str, goal_id: str) -> Optional[Dict]:
        """Get a savings goal with progress calculation."""
        goal = self._get_goal_dict(user_id, goal_id)
        if not goal:
            return None
        return self._format_goal_with_progress(goal)
    
    def get_all_goals(self, user_id: str) -> List[Dict]:
        """Get all savings goals for a user with progress calculation."""
        if user_id not in self.goals:
            return []
        
        return [self._format_goal_with_progress(goal) 
                for goal in self.goals[user_id].values()]