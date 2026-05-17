import os
import json
import requests
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta


class WorkloadBalancerService:
    """Service for AI-powered workload balancing using watsonx Granite"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'WATSONX_API_KEY', None)
        self.project_id = getattr(settings, 'WATSONX_PROJECT_ID', None)
        self.api_url = getattr(settings, 'WATSONX_API_URL', 'https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29')
        
        if not self.api_key:
            raise ValueError("WATSONX_API_KEY not found in settings")
    
    def get_team_workload_data(self, project):
        """
        Gather comprehensive workload data for all team members
        
        Args:
            project: Project instance
            
        Returns:
            dict: Team workload data including active tasks, overdue tasks, priorities
        """
        team_data = []
        
        # Get all team members (owner + members)
        all_members = [project.owner]
        all_members.extend(project.members.all())
        
        for member in all_members:
            # Get tasks for this member in this project
            member_tasks = member.assigned_tasks.filter(project=project)
            
            # Active tasks (not done/completed)
            active_tasks = member_tasks.exclude(status__in=['done', 'completed'])
            active_count = active_tasks.count()
            
            # Overdue tasks
            today = timezone.now().date()
            overdue_tasks = active_tasks.filter(due_date__lt=today)
            overdue_count = overdue_tasks.count()
            
            # Priority breakdown
            priority_breakdown = {
                'urgent': active_tasks.filter(priority='urgent').count(),
                'high': active_tasks.filter(priority='high').count(),
                'medium': active_tasks.filter(priority='medium').count(),
                'low': active_tasks.filter(priority='low').count(),
            }
            
            # Calculate workload score (weighted)
            workload_score = (
                priority_breakdown['urgent'] * 4 +
                priority_breakdown['high'] * 3 +
                priority_breakdown['medium'] * 2 +
                priority_breakdown['low'] * 1 +
                overdue_count * 2  # Overdue tasks add extra weight
            )
            
            team_data.append({
                'user_id': str(member.id),
                'username': member.username,
                'email': member.email,
                'active_tasks': active_count,
                'overdue_tasks': overdue_count,
                'priority_breakdown': priority_breakdown,
                'workload_score': workload_score,
                'is_owner': member == project.owner
            })
        
        return team_data
    
    def get_unassigned_tasks(self, project):
        """
        Get all unassigned tasks for the project
        
        Args:
            project: Project instance
            
        Returns:
            list: List of unassigned task dictionaries
        """
        unassigned_tasks = project.tasks.filter(assigned_to__isnull=True).exclude(
            status__in=['done', 'completed']
        )
        
        tasks_data = []
        for task in unassigned_tasks:
            tasks_data.append({
                'task_id': str(task.id),
                'title': task.title,
                'description': task.description[:200] if task.description else '',
                'priority': task.priority,
                'status': task.status,
                'due_date': task.due_date.isoformat() if task.due_date else None,
            })
        
        return tasks_data
    
    def balance_workload(self, project):
        """
        Use AI to suggest optimal task assignments
        
        Args:
            project: Project instance
            
        Returns:
            list: List of assignment suggestions with confidence scores
        """
        try:
            # Gather data
            team_data = self.get_team_workload_data(project)
            unassigned_tasks = self.get_unassigned_tasks(project)
            
            if not unassigned_tasks:
                return {
                    'success': True,
                    'suggestions': [],
                    'message': 'No unassigned tasks found'
                }
            
            if not team_data:
                return {
                    'success': False,
                    'error': 'No team members found'
                }
            
            # Build prompt for AI
            prompt = self._build_prompt(team_data, unassigned_tasks)
            
            # Call watsonx API (or fallback to rule-based if API not configured)
            if self.api_key and self.project_id:
                suggestions = self._call_watsonx_api(prompt)
            else:
                # Fallback to rule-based assignment
                suggestions = self._rule_based_assignment(team_data, unassigned_tasks)
            
            return {
                'success': True,
                'suggestions': suggestions,
                'team_data': team_data,
                'unassigned_count': len(unassigned_tasks)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_prompt(self, team_data, unassigned_tasks):
        """Build the prompt for watsonx Granite"""
        team_json = json.dumps(team_data, indent=2)
        tasks_json = json.dumps(unassigned_tasks, indent=2)
        
        return f"""You are a project manager AI assistant. Given these team members and their current workloads, suggest the best assignee for each unassigned task.

Consider:
- Current workload (active tasks count)
- Overdue tasks (indicates capacity issues)
- Task priority distribution
- Avoid overloading anyone
- Balance workload fairly across team

Team Members Data:
{team_json}

Unassigned Tasks:
{tasks_json}

Respond ONLY in valid JSON format with this exact structure:
[
  {{
    "task_id": "uuid-here",
    "task_title": "task title",
    "suggested_user_id": "uuid-here",
    "suggested_username": "username",
    "reason": "Brief explanation (max 100 chars)",
    "confidence_percent": 85
  }}
]

Rules:
- confidence_percent must be 0-100
- reason must be concise and actionable
- Distribute tasks evenly
- Consider priority when assigning
- Return ONLY the JSON array, no other text"""
    
    def _call_watsonx_api(self, prompt):
        """Call watsonx Granite API"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            payload = {
                'model_id': 'ibm/granite-13b-chat-v2',
                'input': prompt,
                'parameters': {
                    'max_new_tokens': 2000,
                    'temperature': 0.3,
                    'top_p': 0.9,
                    'top_k': 50
                },
                'project_id': self.project_id
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('results', [{}])[0].get('generated_text', '')
                return self._parse_suggestions(generated_text)
            else:
                raise Exception(f"watsonx API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            # Fallback to rule-based if API fails
            print(f"watsonx API failed, using rule-based: {str(e)}")
            return None
    
    def _parse_suggestions(self, content):
        """Parse AI response into structured suggestions"""
        try:
            # Clean the response
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # Extract JSON array
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                return None
            
            json_str = content[start_idx:end_idx]
            suggestions = json.loads(json_str)
            
            # Validate suggestions
            validated = []
            for suggestion in suggestions:
                if not isinstance(suggestion, dict):
                    continue
                
                # Ensure all required fields exist
                if all(k in suggestion for k in ['task_id', 'task_title', 'suggested_user_id', 'suggested_username', 'reason', 'confidence_percent']):
                    # Validate confidence
                    confidence = suggestion.get('confidence_percent', 50)
                    if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 100:
                        confidence = 50
                    
                    validated.append({
                        'task_id': str(suggestion['task_id']),
                        'task_title': str(suggestion['task_title'])[:200],
                        'suggested_user_id': str(suggestion['suggested_user_id']),
                        'suggested_username': str(suggestion['suggested_username']),
                        'reason': str(suggestion['reason'])[:150],
                        'confidence_percent': int(confidence)
                    })
            
            return validated if validated else None
            
        except Exception as e:
            print(f"Error parsing suggestions: {str(e)}")
            return None
    
    def _rule_based_assignment(self, team_data, unassigned_tasks):
        """
        Fallback rule-based assignment algorithm
        Assigns tasks to team members with lowest workload score
        """
        suggestions = []
        
        # Sort team by workload score (ascending - least busy first)
        sorted_team = sorted(team_data, key=lambda x: x['workload_score'])
        
        for task in unassigned_tasks:
            # Find best assignee based on priority and workload
            best_member = None
            best_score = float('inf')
            
            for member in sorted_team:
                # Calculate assignment score
                score = member['workload_score']
                
                # Adjust for task priority
                if task['priority'] == 'urgent':
                    # Prefer members with fewer urgent tasks
                    score += member['priority_breakdown']['urgent'] * 2
                elif task['priority'] == 'high':
                    score += member['priority_breakdown']['high'] * 1.5
                
                # Penalize if member has overdue tasks
                score += member['overdue_tasks'] * 3
                
                if score < best_score:
                    best_score = score
                    best_member = member
            
            if best_member:
                # Calculate confidence based on workload difference
                avg_workload = sum(m['workload_score'] for m in team_data) / len(team_data)
                if avg_workload == 0:
                    confidence = 90
                else:
                    workload_ratio = best_member['workload_score'] / avg_workload
                    confidence = max(50, min(95, int(100 - (workload_ratio * 30))))
                
                # Build reason
                reason = f"Lowest workload ({best_member['active_tasks']} active tasks)"
                if best_member['overdue_tasks'] > 0:
                    reason = f"{best_member['active_tasks']} tasks, {best_member['overdue_tasks']} overdue"
                
                suggestions.append({
                    'task_id': task['task_id'],
                    'task_title': task['title'],
                    'suggested_user_id': best_member['user_id'],
                    'suggested_username': best_member['username'],
                    'reason': reason,
                    'confidence_percent': confidence
                })
                
                # Update member's workload for next iteration
                best_member['workload_score'] += 2
                best_member['active_tasks'] += 1
        
        return suggestions


# Made with Bob