import requests
import json

# API endpoint URL (assuming the server is running on localhost:8000)
BASE_URL = "http://localhost:8000"
ENDPOINT = f"{BASE_URL}/generate-intro"

# Test cases from the comment section in generate_dish_intro function
test_cases = [
    {
        "original_name": "宫保鸡丁",
        "target_lang": "English"
    },
    {
        "original_name": "麻婆豆腐",
        "target_lang": "English"
    },
    {
        "original_name": "Beef Wellington",
        "target_lang": "中文"
    },
    {
        "original_name": "Sushi",
        "target_lang": "Japanese"
    }
]

def test_generate_intro():
    """Test the POST endpoint with examples from the comment section."""
    print("Testing POST endpoint: /generate-intro")
    print("Note: First call will fetch from OpenAI and save to DynamoDB.")
    print("      Subsequent calls will fetch from DynamoDB.\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test Case {i}:")
        print(f"  Original Name: {test_case['original_name']}")
        print(f"  Target Language: {test_case['target_lang']}")
        
        try:
            response = requests.post(
                ENDPOINT,
                json=test_case,
                headers={"Content-Type": "application/json"}
            )
            
            # Check if request was successful
            if response.status_code == 200:
                result = response.json()
                print(f"  Status: Success")
                print(f"  Source: {result.get('source', 'unknown')}")
                
                # Display the result in a more readable format
                if 'result' in result:
                    result_data = result['result']
                    if isinstance(result_data, dict):
                        print(f"  Translated Name: {result_data.get('translated_name', 'N/A')}")
                        print(f"  Introduction: {result_data.get('introduction', 'N/A')}")
                    else:
                        # Fallback for old format
                        print(f"  Result: {result_data}")
                else:
                    print(f"  Full Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            else:
                print(f"  Status: Error {response.status_code}")
                print(f"  Response: {response.text}")
        
        except requests.exceptions.ConnectionError:
            print(f"  Status: Connection Error - Make sure the FastAPI server is running on {BASE_URL}")
        except Exception as e:
            print(f"  Status: Error - {str(e)}")
        
        print()  # Empty line between test cases

if __name__ == "__main__":
    test_generate_intro()

