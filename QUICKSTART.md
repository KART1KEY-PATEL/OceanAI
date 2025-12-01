# 🚀 Quick Start Guide - Email Productivity Agent

## What You Need From Your Side

Before you can run the application, you need to provide **ONE API key** from any of these providers:

### Option 1: OpenAI (Recommended)
1. Go to: https://platform.openai.com/api-keys
2. Create an account or sign in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### Option 2: Anthropic (Claude)
1. Go to: https://console.anthropic.com/
2. Create an account
3. Navigate to API Keys
4. Create a new key

### Option 3: Google Gemini
1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Create API key

---

## Setup Steps (2 Minutes)

### 1. Copy Environment File
```bash
cd /Users/kartikey/Desktop/development/oceanAi
cp .env.example .env
```

### 2. Edit .env File
Open `.env` in any text editor and add your API key:

**For OpenAI:**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-actual-key-here
MODEL_NAME=gpt-3.5-turbo
```

**For Anthropic:**
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
MODEL_NAME=claude-3-sonnet-20240229
```

**For Google Gemini:**
```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your-actual-key-here
MODEL_NAME=gemini-pro
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

⚠️ **Note:** If you see errors about `pyarrow` or `cmake`, you can ignore them. The core application doesn't need these packages.

### 4. Run the Application
```bash
streamlit run app.py
```

The browser will automatically open to `http://localhost:8501`

---

## First Time Usage (5 Minutes)

### Step 1: Load Sample Emails
1. Look at the left sidebar
2. Click **"🔄 Load Inbox"** button
3. Wait 2 seconds → You'll see "✅ Successfully loaded 20 emails"

### Step 2: Process Emails
1. Click **"⚡ Process All Emails"** button (in sidebar)
2. Watch the progress bar
3. Wait ~40-60 seconds for all 20 emails to be processed
4. Emails will now have colored category badges! 🎉

### Step 3: Explore Features
1. Click on any email to read it
2. See extracted action items for To-Do emails
3. Click "✉️ Generate Reply" to create a draft
4. Go to **"💬 Email Agent"** tab and ask questions
5. Go to **"📝 Drafts"** tab to view generated replies

---

## What Each Tab Does

### 📬 Inbox Manager
- View all your emails
- Filter by category
- Click email to see full content
- Generate reply drafts
- See extracted action items

### ⚙️ Prompt Config
- Edit how AI categorizes emails
- Change action item extraction rules
- Customize reply generation style
- Test prompts before saving

### 💬 Email Agent
- Chat with AI about your emails
- Ask: "What tasks do I have?"
- Ask: "Summarize this email"
- Ask: "Show me urgent emails"
- Get instant answers!

### 📝 Drafts
- See all generated reply drafts
- Edit draft content
- Create new drafts manually
- **Note: Drafts never sent automatically!**

---

## Common Questions

**Q: Do I need to pay for API access?**
A: OpenAI, Anthropic, and Google all offer free tier/credits for new users. This demo uses minimal tokens.

**Q: Will this actually send my emails?**
A: **NO!** This application NEVER sends emails. It only generates drafts that you can review.

**Q: Can I use custom prompts?**
A: **YES!** Go to "Prompt Config" tab and edit any prompt. Changes apply immediately.

**Q: What if I don't have an API key?**
A: You can still load emails and use basic features, but processing (categorization, etc.) won't work.

**Q: How do I reload emails?**
A: Click "🗑️ Clear All" then "🔄 Load Inbox" again.

---

## Troubleshooting

### "LLM client not initialized"
→ Your API key isn't set correctly in `.env`  
→ Make sure you copied `.env.example` to `.env`  
→ Check that your API key doesn't have extra spaces

### "Prompts not loaded"
→ Go to "Prompt Config" tab  
→ Click "📥 Load Default Prompts" button

### Application won't start
→ Make sure you ran: `pip install -r requirements.txt`  
→ Check you're in the correct directory  
→ Try: `python -m streamlit run app.py`

---

## Demo Video Recording Tips

When recording your demo video:

1. **Start Fresh**: Clear all data and reload inbox
2. **Go Slow**: Give viewers time to see what's happening
3. **Narrate**: Explain what you're clicking and why
4. **Show Results**: After processing, show the categorized emails
5. **Use Chat**: Demonstrate the AI chat with real questions
6. **Edit Prompts**: Show how changing prompts changes behavior

**Recommended Tools:**
- Mac: QuickTime Screen Recording
- Windows: OBS Studio (free)
- Online: Loom.com (free)

---

## 🎉 You're All Set!

Once you have your API key configured, you have a fully functional email productivity agent with:
- ✅ AI-powered email categorization
- ✅ Automatic task extraction
- ✅ Intelligent reply generation
- ✅ Natural language chat interface
- ✅ Customizable AI behavior

**Questions?** Check the main [README.md](file:///Users/kartikey/Desktop/development/oceanAi/README.md) for more details!
