import google.generativeai as genai
import sys

# Format the API key (removing accidental spaces from copy-pasting)
API_KEY = "AIzaSyAc6-zS0aK  ve1wlzbS_EzpzQbDJK1Msdxw".replace(" ", "")

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    print(f"Error configuring API key: {e}")
    sys.exit(1)

def generate_tasks(project_description, num_tasks):
    try:
        # Using gemini-2.5-flash as it is fast and efficient
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        You are an expert project manager. I need you to break down a project into exactly {num_tasks} actionable tasks.
        
        Project Description: "{project_description}"
        
        Please provide the response as a numbered list of {num_tasks} tasks.
        Each task should have a short title and a 1-sentence description.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating tasks: {e}"

if __name__ == "__main__":
    description = "Create a real estate website where users can view property listings and contact agents."
    tasks = 5
    
    print("Testing the Gemini API Key with a sample project...")
    print(f"\nProject: {description}")
    print(f"Number of tasks requested: {tasks}\n")
    print("-" * 50)
    
    result = generate_tasks(description, tasks)
    print(result)
