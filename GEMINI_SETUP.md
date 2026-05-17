# Google Gemini AI Task Generation Setup Guide (100% FREE)

This guide will help you set up the FREE AI task generation feature using Google's Gemini API for your Django Hackathon Project Management System.

## Why Google Gemini?

✅ **Completely FREE** - No credit card required
✅ **Generous free tier** - 60 requests per minute
✅ **High quality** - Powered by Google's latest AI
✅ **Easy setup** - Simple API key generation
✅ **No billing** - Never charges you

## Prerequisites

- Python 3.8 or higher
- Django 5.2.8
- Google account (Gmail)

## Installation Steps

### 1. Install Required Package

Install the Google Generative AI Python package:

```bash
pip install google-generativeai>=0.3.0
```

Or install from requirements:

```bash
pip install -r requirements.txt
```

### 2. Get FREE Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Select "Create API key in new project" or choose existing project
5. Copy the API key (save it somewhere safe)

**Note:** The API key is completely FREE with no credit card required!

### 3. Set Environment Variable

#### Windows (PowerShell):
```powershell
$env:GEMINI_API_KEY="your-gemini-api-key-here"
```

#### Windows (Command Prompt):
```cmd
set GEMINI_API_KEY=your-gemini-api-key-here
```

#### Linux/Mac:
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

#### For Permanent Setup (Recommended):

**Windows:**
1. Search for "Environment Variables" in Windows
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "User variables", click "New"
5. Variable name: `GEMINI_API_KEY`
6. Variable value: Your Gemini API key
7. Click OK

**Linux/Mac:**
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
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

**Mobile Game:**
```
Design a mobile puzzle game with multiple levels, score tracking, leaderboards, in-game purchases, daily challenges, social sharing features, and offline play capability.
```

## Features

- **100% FREE AI Generation:** Uses Google Gemini Pro (no cost)
- **No Credit Card Required:** Completely free to use
- **Generous Limits:** 60 requests per minute
- **High Quality:** Powered by Google's latest AI technology
- **Customizable:** Specify the number of tasks (3-15)
- **Smart Parsing:** Automatically extracts task titles, descriptions, and statuses
- **Preview Before Save:** Review and remove unwanted tasks before saving
- **Seamless Integration:** Generated tasks integrate with existing Kanban board and dashboard
- **Error Handling:** Graceful error messages if API fails

## API Limits (FREE Tier)

- **Requests per minute:** 60
- **Requests per day:** 1,500
- **Cost:** $0.00 (FREE forever)
- **No credit card required**

For a hackathon project, these limits are more than sufficient!

## Troubleshooting

### "GEMINI_API_KEY not found in settings"
- Ensure you've set the environment variable correctly
- Restart your terminal/IDE after setting the variable
- Verify the variable is set: `echo $GEMINI_API_KEY` (Linux/Mac) or `echo %GEMINI_API_KEY%` (Windows)

### "Error generating tasks"
- Check your Gemini API key is valid
- Ensure you have internet connection
- Check if you've exceeded rate limits (60/min)
- Review the error message for specific details

### "No module named 'google.generativeai'"
- Run `pip install google-generativeai>=0.3.0`
- Ensure you're using the correct Python environment

### Tasks not appearing in Kanban board
- Refresh the page
- Check that tasks were saved successfully (look for success message)
- Verify you have access to the project

### Rate Limit Exceeded
- Wait 1 minute before trying again
- The free tier allows 60 requests per minute
- For hackathons, this is usually more than enough

## Comparison: Gemini vs OpenAI

| Feature | Google Gemini | OpenAI GPT-3.5 |
|---------|---------------|----------------|
| **Cost** | FREE | $0.001-$0.005 per request |
| **Credit Card** | Not required | Required |
| **Quality** | Excellent | Excellent |
| **Speed** | Fast (2-5s) | Fast (2-5s) |
| **Rate Limit** | 60/min (free) | Varies by plan |
| **Setup** | Very easy | Easy |

## Getting Your FREE API Key

### Step-by-Step with Screenshots

1. **Visit Google AI Studio**
   - Go to: https://makersuite.google.com/app/apikey
   - Sign in with your Google account

2. **Create API Key**
   - Click "Create API Key" button
   - Choose "Create API key in new project"
   - Wait a few seconds

3. **Copy Your Key**
   - Your API key will be displayed
   - Click the copy icon
   - Save it somewhere safe

4. **Set Environment Variable**
   - Follow the instructions in Step 3 above
   - Restart your development server

That's it! No credit card, no billing, completely free!

## File Structure

```
apps/ai/
├── services.py       # ✅ Updated to use Gemini
├── forms.py          # ✅ Same (no changes needed)
├── views.py          # ✅ Same (no changes needed)
├── urls.py           # ✅ Same (no changes needed)
└── templates/
    └── ai/
        ├── generate_tasks.html   # ✅ Same
        └── preview_tasks.html    # ✅ Same

config/
└── settings.py       # ✅ Updated (GEMINI_API_KEY)

requirements.txt      # ✅ Updated (google-generativeai)
```

## Security Notes

- Never commit your API key to version control
- Use environment variables for API keys
- Consider using `.env` files with `python-deotenv` for production
- The free tier has built-in rate limiting for protection

## Advanced Configuration

### Using Different Gemini Models

You can modify [`apps/ai/services.py`](apps/ai/services.py:15) to use different models:

```python
# Default (FREE)
self.model = genai.GenerativeModel('gemini-pro')

# For vision tasks (if needed in future)
self.model = genai.GenerativeModel('gemini-pro-vision')
```

### Adjusting Generation Parameters

Modify the `generate_content` call in [`apps/ai/services.py`](apps/ai/services.py:30):

```python
response = self.model.generate_content(
    prompt,
    generation_config={
        'temperature': 0.7,  # Creativity (0.0-1.0)
        'top_p': 0.8,
        'top_k': 40,
        'max_output_tokens': 2048,
    }
)
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Django logs for error details
3. Visit [Google AI Studio](https://makersuite.google.com/) for API status
4. Check [Gemini API Documentation](https://ai.google.dev/docs)

## Why This is Perfect for Hackathons

✅ **No Cost** - Focus on building, not billing
✅ **Fast Setup** - Get API key in 30 seconds
✅ **Reliable** - Backed by Google infrastructure
✅ **Generous Limits** - 1,500 requests/day is plenty
✅ **No Surprises** - Never get charged
✅ **High Quality** - Latest AI technology

## Frequently Asked Questions

**Q: Is it really free?**
A: Yes! 100% free, no credit card required, no hidden costs.

**Q: Will I ever be charged?**
A: No. The free tier never charges you.

**Q: What happens if I exceed limits?**
A: You'll get a rate limit error. Just wait a minute and try again.

**Q: Can I use this in production?**
A: Yes, but consider the rate limits. For production, you might want to upgrade to a paid tier for higher limits.

**Q: How long does the API key last?**
A: Forever! It doesn't expire unless you revoke it.

**Q: Can I use multiple API keys?**
A: Yes, you can create multiple keys for different projects.

---

**Made with Bob**
**Powered by Google Gemini (FREE)**