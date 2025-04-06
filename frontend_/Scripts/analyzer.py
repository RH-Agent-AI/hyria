import os
import requests
import json
import re
# --- Configuration ---
MISTRAL_API_KEY = 'OZSyUAoFi2DmsjJz5Cuqg8vWeFzG9grq'  # Remplacez par votre clé API Mistral
MODEL_NAME = 'mistral-large-latest'  # Nom du modèle à utiliser
API_URL = 'https://api.mistral.ai/v1/chat/completions'

# --- Fonction d'analyse ---
def analyze_cv_and_conversation(cv_text, job_description, hr_conversation):
    """
    Analyzes the CV and HR conversation using the Mistral AI API.

    Args:
        cv_text (str): Candidate's CV text.
        job_description (str): Job description text.
        hr_conversation (str): Transcript of the HR conversation.

    Returns:
        dict: Parsed analysis results in JSON format.
    """
    # Building the prompt
    prompt = f"""
    You are an expert HR analyst. Your task is to analyze a candidate's CV and an accompanying HR conversation transcript based on the provided job description.
    You should provide feedback and scores for the candidate's suitability, considering insights from BOTH the CV and the HR conversation.

    Please structure your response as a JSON object with the following keys:
    - 'education', 'experience', 'technical_skills', 'soft_skills', 'additional', and 'overall'.
    Each of these keys (except 'overall') should map to an object containing exactly three sub-keys:
        - 'summary' (string derived from the CV and conversation)
        - 'feedback' (string reflecting the CV and conversation)
        - 'score' (integer between 0 and 100)

    The 'overall' key should be an object containing exactly three sub-keys:
        - 'summary' (string derived from the CV and conversation)
        - 'feedback' (string reflecting the CV and conversation)
        - 'score' (integer between 0 and 100)

    Example structure for a field (DO NOT treat braces as variables):
    "experience": {{
        "summary": "5 years Python developer (CV). Mentioned leading a small project team and interest in cloud tech (HR conversation).",
        "feedback": "Solid experience matching requirements. Leadership mention is a plus. Expressed relevant interest.",
        "score": 90
    }}

    Example for overall:
    "overall": {{
        "summary": "Strong technical background (CV), good communication and enthusiasm shown (HR conversation).",
        "feedback": "Very promising fit based on CV and conversation, recommend for technical interview.",
        "score": 92
    }}

    Here is the job description:
    {job_description}

    Here is the CV text:
    {cv_text}

    Here is the HR conversation transcript:
    {hr_conversation}
    
    Please provide your analysis in the above JSON format.
    """

    # Request body
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {MISTRAL_API_KEY}'
    }
    data = {
        'model': MODEL_NAME,
        'messages': [{'role': 'user', 'content': prompt}]
    }

    # Sending the request
    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        # Process the response
        response_data = response.json()
        raw_response = response_data.get('choices', [])[0].get('message', {}).get('content', '')

        # Use regex to extract the JSON part
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)  # This will match everything between { and }
        if json_match:
            try:
                # Attempt to load the JSON
                analysis_data = json.loads(json_match.group(0))
                return analysis_data
            except json.JSONDecodeError:
                print("Error decoding the JSON in the model response.")
                return None
        else:
            print("No valid JSON found in the model response.")
            return None
    else:
        print(f"Error calling the Mistral AI API: {response.status_code}")
        print(response.text)
        return None

# --- Example Usage ---
if __name__ == "__main__":
    # Example CV text
    cv_text = "Jean Dupont, Python developer with 5 years of experience, passionate about AI and Data Science."

    # Example job description
    job_description = "Seeking a candidate with experience in AI, machine learning, and proficiency in Python and PySpark."

    # Example HR conversation transcript
    hr_conversation = """
    HR: Can you tell me why you're interested in this role?
    Candidate: I'm excited about the advancements in AI and have worked on data modeling using Python and PySpark.
    """

    # Run the analysis
    analysis_result = analyze_cv_and_conversation(cv_text, job_description, hr_conversation)

    if analysis_result:
        print("Analysis completed successfully.")
        print(json.dumps(analysis_result, indent=2))
    else:
        print("Analysis failed.")
