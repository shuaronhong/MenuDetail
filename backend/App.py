from fastapi import FastAPI
from pydantic import BaseModel
from intro import generate_dish_intro
import json
import uvicorn
import boto3
import re
from botocore.exceptions import ClientError

app = FastAPI()

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('dish_intro')

class DishRequest(BaseModel):
    original_name: str
    target_lang: str

def parse_intro_result(result_str: str) -> dict:
    """
    Parse the result string from generate_dish_intro to extract translated_name and introduction.
    
    Expected format:
    {"translated name: "xxx",
    "introduction: xxx"
    }
    """
    try:
        translated_name = ""
        introduction = ""
        
        # Try to extract translated name - handle various formats
        # Format 1: "translated name: "xxx""
        translated_name_match = re.search(r'"translated name":\s*"([^"]+)"', result_str, re.IGNORECASE)
        if not translated_name_match:
            # Format 2: "translated name: "xxx" (with colon inside quotes)
            translated_name_match = re.search(r'translated name:\s*"([^"]+)"', result_str, re.IGNORECASE)
        if translated_name_match:
            translated_name = translated_name_match.group(1).strip()
        
        # Try to extract introduction - handle various formats
        # Format 1: "introduction: "xxx""
        introduction_match = re.search(r'"introduction":\s*"([^"]+)"', result_str, re.IGNORECASE | re.DOTALL)
        if not introduction_match:
            # Format 2: "introduction: "xxx" (with colon inside quotes)
            introduction_match = re.search(r'introduction:\s*"([^"]+)"', result_str, re.IGNORECASE | re.DOTALL)
        if not introduction_match:
            # Format 3: introduction: xxx (without quotes, until end or newline)
            introduction_match = re.search(r'introduction:\s*(.+?)(?:\n\s*}|$)', result_str, re.IGNORECASE | re.DOTALL)
        if introduction_match:
            introduction = introduction_match.group(1).strip().strip('"')
        
        # If introduction is still empty, use the whole result string
        if not introduction:
            introduction = result_str.strip()
        
        return {
            "translated_name": translated_name,
            "introduction": introduction
        }
    except Exception as e:
        # Fallback: return the whole string as introduction
        return {
            "translated_name": "",
            "introduction": result_str
        }

def get_from_dynamodb(original_name: str, target_lang: str) -> dict:
    """Query DynamoDB for existing record."""
    try:
        response = table.get_item(
            Key={
                'dish_original_name': original_name,
                'target_lang': target_lang
            }
        )
        if 'Item' in response:
            return response['Item']
        return None
    except ClientError as e:
        print(f"Error querying DynamoDB: {e}")
        return None

def save_to_dynamodb(original_name: str, target_lang: str, translated_name: str, introduction: str):
    """Save the result to DynamoDB."""
    try:
        table.put_item(
            Item={
                'dish_original_name': original_name,
                'target_lang': target_lang,
                'translated_name': translated_name,
                'introduction': introduction
            }
        )
    except ClientError as e:
        print(f"Error saving to DynamoDB: {e}")

@app.post("/generate-intro")
async def generate_intro(request: DishRequest):
    """
    Generate dish introduction endpoint.
    
    Accepts original_name and target_lang in the request body,
    checks DynamoDB first, and if not found, calls generate_dish_intro function,
    then saves the result to DynamoDB.
    """
    # Check DynamoDB first
    existing_record = get_from_dynamodb(request.original_name, request.target_lang)
    
    if existing_record:
        # Return existing record from DynamoDB
        return {
            "result": {
                "translated_name": existing_record.get('translated_name', ''),
                "introduction": existing_record.get('introduction', '')
            },
            "source": "dynamodb"
        }
    
    # If not found in DynamoDB, generate new intro
    result_str = generate_dish_intro(request.original_name, request.target_lang)
    
    # Parse the result to extract translated_name and introduction
    parsed_result = parse_intro_result(result_str)
    
    # Save to DynamoDB
    save_to_dynamodb(
        request.original_name,
        request.target_lang,
        parsed_result['translated_name'],
        parsed_result['introduction']
    )
    
    return {
        "result": parsed_result,
        "source": "openai"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

