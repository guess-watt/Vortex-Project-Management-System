# AI Task Generation Setup Guide

This guide will help you set up the AI task generation feature for your Django Hackathon Project Management System.

## Prerequisites

- Python 3.8 or higher
- Django 5.2.8
- OpenAI API account

## Installation Steps

### 1. Install Required Package

Install the OpenAI Python package:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install openai>=1.0.0
```

### 2. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key (you won't be able to see it again)

### 3. Set Environment Variable

#### Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY="your-api-key-here"
```

#### Windows (Command Prompt):
```cmd
set OPENAI_API_KEY=your-api-key-here
```

#### Linux/Mac:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

#### For Permanent Setup (Recommended):

**Windows:**
1. Search for "Environment Variables" in Windows
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "User variables", click "New"
5. Variable name: `OPENAI_API_KEY`
6. Variable value: Your OpenAI API key
7. Click OK

**Linux/Mac:**
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 4. Restart Development Server

After setting the environment variable, restart your Django development server:

```bash
python manage.py runserver
```

## Usage

### Generating Tasks with AI

1. **Navigate to a Project:**
   - Go to your project detail page
   - Click the "Generate Tasks with AI" button (green button with magic icon)

2. **Enter Project Description:**
   - Provide a detailed description of your project or feature
   - Specify the number of tasks you want (3-15)
   - Click "Generate Tasks"

3. **Review Generated Tasks:**
   - Review the AI-generated tasks
   - Remove any tasks you don't want
   - Click "Save All Tasks" to add them to your project

4. **View Tasks:**
   - Generated tasks will appear in your project dashboard
   - They will also be visible in the Kanban board
   - You can edit or delete tasks as needed

### Example Prompts

**E-commerce Website:**
```
Build an e-commerce website with user authentication, product catalog with search and filters, shopping cart functionality, payment integration using Stripe, order management system, and admin dashboard for managing products and orders.
```

**Social Media App:**
```
Create a social media application with user profiles, post creation with images, like and comment functionality, follow/unfollow system, news feed with infinite scroll, and real-time notifications.
```

**Task Management System:**
```
Develop a task management system with project creation, task assignment to team members, priority levels, due dates, status tracking (todo, in progress, done), file attachments, and activity timeline.
```

## Features

- **AI-Powered Task Generation:** Uses OpenAI GPT-3.5 to generate structured tasks
- **Customizable:** Specify the number of tasks (3-15)
- **Smart Parsing:** Automatically extracts task titles, descriptions, and statuses
- **Preview Before Save:** Review and remove unwanted tasks before saving
- **Seamless Integration:** Generated tasks integrate with existing Kanban board and dashboard
- **Error Handling:** Graceful error messages if API fails

## API Costs

- The feature uses OpenAI's GPT-3.5-turbo model
- Typical cost per task generation: $0.001 - $0.005
- Monitor your usage at [OpenAI Usage Dashboard](https://platform.openai.com/usage)

## Troubleshooting

### "OPENAI_API_KEY not found in settings"
- Ensure you've set the environment variable correctly
- Restart your terminal/IDE after setting the variable
- Verify the variable is set: `echo $OPENAI_API_KEY` (Linux/Mac) or `echo %OPENAI_API_KEY%` (Windows)

### "Error generating tasks"
- Check your OpenAI API key is valid
- Ensure you have credits in your OpenAI account
- Check your internet connection
- Review the error message for specific details

### "No module named 'openai'"
- Run `pip install openai>=1.0.0`
- Ensure you're using the correct Python environment

### Tasks not appearing in Kanban board
- Refresh the page
- Check that tasks were saved successfully (look for success message)
- Verify you have access to the project

## File Structure

```
apps/ai/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py          # AI task generation form
├── models.py
├── services.py       # OpenAI integration service
├── tests.py
├── urls.py           # AI routes
├── views.py          # AI views (generate, preview)
└── templates/
    └── ai/
        ├── generate_tasks.html   # Task generation page
        └── preview_tasks.html    # Task preview page
```

## Security Notes

- Never commit your API key to version control
- Use environment variables for API keys
- Consider using `.env` files with `python-deotenv` for production
- Monitor your API usage regularly
- Set spending limits in your OpenAI account

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Django logs for error details
3. Verify OpenAI API status at [status.openai.com](https://status.openai.com)

---

**Made with Bob**