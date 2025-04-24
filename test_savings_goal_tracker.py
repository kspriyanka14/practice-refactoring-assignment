import unittest
from datetime import datetime
from currency_converter import CurrencyConverter
from savings_goal_tracker import SavingsGoalTracker

class TestSavingsGoalTracker(unittest.TestCase):
    def setUp(self):
        self.converter = CurrencyConverter()
        self.tracker = SavingsGoalTracker(self.converter)
    
    def test_create_goal(self):
        # Test creating a valid goal
        goal = self.tracker.create_goal("user1", "Tokyo Trip", 1000, "USD", "Vacation in Tokyo")
        self.assertIsNotNone(goal)
        self.assertEqual(goal["name"], "Tokyo Trip")
        self.assertEqual(goal["target_amount"], 1000)
        self.assertEqual(goal["currency"], "USD")
        self.assertEqual(goal["progress"], 0)
        
        # Test creating a goal with invalid parameters
        invalid_goal = self.tracker.create_goal("", "Trip", 1000, "USD")
        self.assertIsNone(invalid_goal)
        
        # Test creating a goal with invalid currency
        invalid_goal = self.tracker.create_goal("user1", "Trip", 1000, "XYZ")
        self.assertIsNone(invalid_goal)
    
    def test_add_contribution(self):
        # Create a goal first
        goal = self.tracker.create_goal("user1", "Europe Trip", 500, "EUR")
        goal_id = goal["id"]
        
        # Test adding a valid contribution
        updated_goal = self.tracker.add_contribution("user1", goal_id, 100)
        self.assertIsNotNone(updated_goal)
        self.assertEqual(updated_goal["current_amount"], 100)
        self.assertEqual(updated_goal["progress"], 20)
        
        # Add another contribution
        updated_goal = self.tracker.add_contribution("user1", goal_id, 150)
        self.assertEqual(updated_goal["current_amount"], 250)
        self.assertEqual(updated_goal["progress"], 50)
        
        # Test adding contribution to non-existent goal
        result = self.tracker.add_contribution("user1", "nonexistent-id", 100)
        self.assertIsNone(result)
        
        # Test adding invalid contribution amount
        result = self.tracker.add_contribution("user1", goal_id, -50)
        self.assertIsNone(result)
    
    def test_convert_goal_currency(self):
        # Create a goal with a contribution
        goal = self.tracker.create_goal("user1", "New Camera", 1000, "USD")
        goal_id = goal["id"]
        
        # Add a contribution (50% progress)
        self.tracker.add_contribution("user1", goal_id, 500)
        
        # Convert the goal to EUR
        updated_goal = self.tracker.convert_goal_currency("user1", goal_id, "EUR")
        self.assertIsNotNone(updated_goal)
        self.assertEqual(updated_goal["currency"], "EUR")
        
        # Check that progress remains at 50%
        self.assertAlmostEqual(updated_goal["progress"], 50, places=0)
        
        # Test converting a nonexistent goal
        result = self.tracker.convert_goal_currency("user1", "nonexistent-id", "EUR")
        self.assertIsNone(result)
        
        # Test converting to an invalid currency
        result = self.tracker.convert_goal_currency("user1", goal_id, "XYZ")
        self.assertIsNone(result)
    
    def test_get_goal(self):
        # Create a goal
        goal = self.tracker.create_goal("user1", "House Down Payment", 20000, "USD")
        goal_id = goal["id"]
        
        # Test getting the goal
        retrieved_goal = self.tracker.get_goal("user1", goal_id)
        self.assertIsNotNone(retrieved_goal)
        self.assertEqual(retrieved_goal["name"], "House Down Payment")
        
        # Test getting nonexistent goal
        result = self.tracker.get_goal("user1", "nonexistent-id")
        self.assertIsNone(result)
    
    def test_get_all_goals(self):
        # Create multiple goals
        self.tracker.create_goal("user1", "Goal 1", 1000, "USD")
        self.tracker.create_goal("user1", "Goal 2", 2000, "EUR")
        
        # Create goal for different user
        self.tracker.create_goal("user2", "Other Goal", 5000, "GBP")
        
        # Test getting all goals for user1
        goals = self.tracker.get_all_goals("user1")
        self.assertEqual(len(goals), 2)
        
        # Test getting goals for user with no goals
        goals = self.tracker.get_all_goals("user3")
        self.assertEqual(len(goals), 0)

if __name__ == "__main__":
    unittest.main()