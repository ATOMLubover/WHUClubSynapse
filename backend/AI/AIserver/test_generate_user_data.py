import requests
import json
import unittest
import os
import sys
import datetime

# Add the parent directory to the Python path to import config_manager
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from config_manager import config
except ImportError:
    # Fallback to default values if config_manager cannot be imported
    class DefaultConfig:
        server_host = "127.0.0.1"
        server_port = 8000
    config = DefaultConfig()

class TestGenerateUserData(unittest.TestCase):
    def setUp(self):
        self.base_url = f"http://{config.server_host}:{config.server_port}"
        self.endpoint = "/generate_user_data"
        self.full_url = f"{self.base_url}{self.endpoint}"
        self.generated_data_dir = os.path.join(current_dir, "generated_data")
        os.makedirs(self.generated_data_dir, exist_ok=True)
        # Ensure the test file is unique
        self.test_save_file = f"test_user_data_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}.jsonl"
        self.expected_file_path_prefix = os.path.join(self.generated_data_dir, f"test_user_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")

    def tearDown(self):
        # Clean up any generated test files
        for f_name in os.listdir(self.generated_data_dir):
            if f_name.startswith("test_user_data_") and f_name.endswith(".jsonl"):
                try:
                    os.remove(os.path.join(self.generated_data_dir, f_name))
                except OSError as e:
                    print(f"Error removing test file {f_name}: {e}")

    def test_generate_user_data_success(self):
        print(f"Testing endpoint: {self.full_url}")
        num_users_to_generate = 5
        payload = {
            "num_users": num_users_to_generate,
            "save_file": self.test_save_file
        }

        try:
            response = requests.post(self.full_url, json=payload, timeout=60) # Increased timeout
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")

            self.assertEqual(response.status_code, 200)
            self.assertIn("generated_count", data)
            self.assertIn("message", data)
            self.assertIn("sample_data", data)
            self.assertIn("file_path", data)

            self.assertEqual(data["generated_count"], num_users_to_generate)
            self.assertIsInstance(data["sample_data"], list)
            self.assertEqual(len(data["sample_data"]), min(num_users_to_generate, 3)) # sample_data is capped at 3

            generated_ids = set()
            for user_item in data["sample_data"]:
                self.assertIn("user_id", user_item)
                self.assertIn("username", user_item)
                self.assertIn("email", user_item)
                self.assertIn("role", user_item)
                self.assertIn("created_at", user_item)
                self.assertIn("updated_at", user_item)
                self.assertIn("last_active_at", user_item)
                self.assertIn("extension", user_item)

                self.assertIsInstance(user_item["user_id"], int)
                self.assertIsInstance(user_item["username"], str)
                self.assertIsInstance(user_item["email"], str)
                self.assertIsInstance(user_item["role"], str)
                self.assertIsInstance(user_item["created_at"], str)
                self.assertIsInstance(user_item["updated_at"], str)
                self.assertIsInstance(user_item["last_active_at"], str)
                self.assertIsInstance(user_item["extension"], dict)

                # Check unique user_id in sample data
                self.assertNotIn(user_item["user_id"], generated_ids)
                generated_ids.add(user_item["user_id"])

                # Check extension content
                extension = user_item["extension"]
                self.assertIn("realName", extension)
                self.assertIn("studentId", extension)
                self.assertIn("major", extension)
                self.assertIn("bio", extension)
                self.assertIn("preferences", extension)
                self.assertIn("tags", extension)
                self.assertIn("phone", extension)

                preferences = extension["preferences"]
                self.assertIn("interestedCategories", preferences)
                self.assertIn("emailNotifications", preferences)
                self.assertIn("applicationNotifications", preferences)
                self.assertIn("activityNotifications", preferences)
                self.assertIn("profilePublic", preferences)
                self.assertIn("showJoinedClubs", preferences)
                
            # Verify the file was created and contains the correct number of lines
            file_path = data["file_path"]
            self.assertTrue(os.path.exists(file_path))
            
            # Count lines in the generated file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            self.assertEqual(len(lines), num_users_to_generate)

            # Check if each line is a valid JSON and maps to UserItem
            for line in lines:
                user_data = json.loads(line)
                self.assertIn("user_id", user_data)
                self.assertIn("username", user_data)
                # No need to validate every field again, basic structure check is enough

        except requests.exceptions.RequestException as e:
            self.fail(f"Request to {self.full_url} failed: {e}")
        except json.JSONDecodeError as e:
            self.fail(f"Failed to decode JSON response: {e}. Response content: {response.text}")
        except Exception as e:
            self.fail(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    unittest.main() 