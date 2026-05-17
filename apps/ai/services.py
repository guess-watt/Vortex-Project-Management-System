import os
import json
import google.generativeai as genai
from django.conf import settings


class AITaskGenerator:
    """Service for generating project tasks using Google Gemini API (FREE)"""
    
    def __init__(self):
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in settings")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_tasks(self, project_description, num_tasks=5):
        """
        Generate tasks based on project description using Google Gemini
        
        Args:
            project_description (str): Description of the project or feature
            num_tasks (int): Number of tasks to generate (default: 5)
            
        Returns:
            list: List of task dictionaries with title, description, and status
        """
        try:
            prompt = self._build_prompt(project_description, num_tasks)
            
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini API")
            
            tasks = self._parse_tasks(response.text)
            
            return tasks
            
        except Exception as e:
            raise Exception(f"Error generating tasks: {str(e)}")
    
    def _build_prompt(self, project_description, num_tasks):
        """Build the prompt for Gemini API"""
        return f"""Generate {num_tasks} specific, actionable tasks for the following project:

Project Description: {project_description}

For each task, provide:
1. A clear, concise title (max 100 characters)
2. A detailed description (2-3 sentences)
3. Recommended status (not_started, pending, or completed)

Format your response as a JSON array with this structure:
[
  {{
    "title": "Task title here",
    "description": "Detailed description here",
    "status": "not_started"
  }}
]

IMPORTANT: Return ONLY the JSON array, no additional text before or after.
Make the tasks specific, actionable, and ordered logically for project execution."""
    
    def _parse_tasks(self, content):
        """Parse the AI response into structured task data"""
        try:
            # Clean the response - remove markdown code blocks if present
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # Try to extract JSON from the response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON array found in response")
            
            json_str = content[start_idx:end_idx]
            tasks = json.loads(json_str)
            
            # Validate and clean task data
            validated_tasks = []
            valid_statuses = ['not_started', 'pending', 'completed']
            
            for task in tasks:
                if not isinstance(task, dict):
                    continue
                
                title = task.get('title', '').strip()
                description = task.get('description', '').strip()
                status = task.get('status', 'not_started').strip()
                
                # Validate required fields
                if not title:
                    continue
                
                # Ensure status is valid
                if status not in valid_statuses:
                    status = 'not_started'
                
                validated_tasks.append({
                    'title': title[:200],  # Limit to model max length
                    'description': description,
                    'status': status
                })
            
            return validated_tasks
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing tasks: {str(e)}")

# Made with Bob