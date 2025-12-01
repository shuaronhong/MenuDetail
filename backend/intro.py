import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_dish_intro(original_name,  target_lang, model="gpt-3.5-turbo"):
    f"""
    Generate a 2-3 sentence introduction for a dish in the target language.
    
    Args:
        original_name: Original dish name (e.g., "宫保鸡丁")
        target_lang: Target language for the translated name and introduction (e.g., "English", "中文", "Japanese")
        model: The model to use (default: "gpt-4o-mini")
    
    Returns:
        str: translated name of the dish and a 2-3 sentence introduction about the dish in the target language
    
    Example:
        intro = generate_dish_intro("宫保鸡丁", "English")
        # Returns: {{"translated name: "Kung Pao Chicken",
        # "introduction: This iconic Sichuan dish features tender chicken pieces,
        # roasted peanuts, and dried chili peppers in a savory-sweet sauce. 
        # Known for its bold flavors and numbing spice from Sichuan peppercorns, 
        # this dish perfectly balances heat with a subtle sweetness." 
        # }}
        Examples:

For "麻婆豆腐" target language in English:
{{"translated name: "Mapo Tofu",
"introduction: This iconic Sichuan dish features silky tofu cubes in a spicy, aromatic sauce made with fermented black beans, chili oil, and ground pork. The distinctive numbing sensation comes from Sichuan peppercorns, creating a perfect balance of heat and flavor. It's traditionally served over steamed rice to soak up the delicious sauce."
}}

For "Beef Wellington" target languagein 中文:
{{"translated name: "威灵顿牛排",
"introduction: 这道经典英式菜肴将嫩煎牛里脊肉裹上蘑菇泥和火腿,再包入酥脆的酥皮中烘烤而成。外层金黄酥脆,内里牛肉鲜嫩多汁,是英国传统宴会上的招牌主菜。层次感和风味非常丰富。"
}}

For "Sushi" target language in Japanese:
{{"translated name: "寿司",
"introduction: 新鮮な魚介類と酢飯を組み合わせた日本の伝統料理です。職人の熟練した技術により、シャリとネタの絶妙なバランスが生まれます。わさびと醤油を添えて、素材本来の味わいを楽しむのが特徴です。"
}}
    """
    
    prompt = f"""You are a knowledgeable food writer specializing in culinary descriptions.

Given a dish with its original name "{original_name}", 
write a paragraph less than 100 words introduction about this dish in {target_lang}. 
If the dish name is confusing, guess the dish name from the original name and write the introduction about the guessed dish name.

Requirements:
1. Write a paragraph less than 100 words (no more)
2. Write in {target_lang} language
3. Include information about key ingredients, cooking method, or cultural significance
4. Keep the tone informative

output format:
{{"translated name: "translated name in {target_lang} language",
"introduction: introduction of the dish in {target_lang} language"
}}
"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,  # Slightly higher for more creative descriptions
            max_tokens=150,
        )
        
        intro = resp.choices[0].message.content.strip()
        return intro
        
    except Exception as e:
        # Fallback message if API fails
        return f"A delicious dish worth trying. ({str(e)})"

