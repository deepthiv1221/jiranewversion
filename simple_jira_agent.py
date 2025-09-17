import os
from jira import JIRA
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Connect JIRA ---
jira = None
try:
    if not JIRA_URL or not JIRA_EMAIL or not JIRA_API_TOKEN:
        print("❌ Missing JIRA credentials in .env")
    else:
        jira = JIRA(server=JIRA_URL, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))
        print(f"🔗 Connected to JIRA as: {JIRA_EMAIL}")
except Exception as e:
    print(f"❌ JIRA connection error: {e}")

# --- AI Setup (Gemini + OpenAI fallback) ---
AI_ENABLED = True
use_gemini = True if GEMINI_API_KEY else False

def ask_ai(prompt):
    global use_gemini

    if not AI_ENABLED:
        return "⚠️ AI is disabled."

    try:
        if use_gemini:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(prompt)
            return response.text
        elif OPENAI_API_KEY:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        else:
            return "⚠️ No AI keys configured in .env"
    except Exception as e:
        if "429" in str(e) and use_gemini:
            print("⚠️ Gemini quota exceeded. Switching to OpenAI fallback...")
            use_gemini = False
            return ask_ai(prompt)
        return f"❌ AI Error: {e}"

# --- Menu Functions ---
def search_recent_issues():
    try:
        # Restrict search to your project (MFLP) and only last 10
        issues = jira.search_issues("project=MFLP ORDER BY created DESC", maxResults=10)
        if not issues:
            print("⚠️ No issues found.")
            return
        for issue in issues:
            print(f"{issue.key}: {issue.fields.summary}")
    except Exception as e:
        print(f"❌ Error searching issues: {e}")

def search_issues_by_keyword(keyword):
    try:
        jql = f'project=MFLP AND text ~ "{keyword}" ORDER BY created DESC'
        issues = jira.search_issues(jql, maxResults=10)
        if not issues:
            print("⚠️ No issues match that keyword.")
            return
        for issue in issues:
            print(f"{issue.key}: {issue.fields.summary}")
    except Exception as e:
        print(f"❌ Error searching issues: {e}")

def get_issue_details(issue_key):
    try:
        issue = jira.issue(issue_key)
        print(f"\n📋 Issue Details:\n{issue.key} - {issue.fields.summary}\n{issue.fields.description}")
    except Exception as e:
        print(f"❌ Error getting issue details: {e}")

def view_projects():
    try:
        projects = jira.projects()
        for project in projects:
            print(f"{project.key}: {project.name}")
    except Exception as e:
        print(f"❌ Error fetching projects: {e}")

def create_issue(project_key, summary, description=""):
    try:
        new_issue = jira.create_issue(project=project_key, summary=summary,
                                      description=description, issuetype={"name": "Task"})
        print(f"✅ Successfully created issue: {new_issue.key}")
    except Exception as e:
        print(f"❌ Error creating issue: {e}")

# --- Menu ---
def show_menu():
    print("""
══════════════════════════════════════════════════
╔════════════════════════════════════════╗
║            JIRA AGENT MENU             ║
╚════════════════════════════════════════╝
📋 BASIC OPERATIONS:
1️⃣  Search all recent issues
2️⃣  Search issues by keyword
3️⃣  Get issue details by key
4️⃣  View all projects
5️⃣  Create new issue
🤖 AI OPERATIONS:
6️⃣  Ask AI about your JIRA data      
7️⃣  Get AI summary of recent issues  
🔧 UTILITIES:
8️⃣  Test JIRA connection
9️⃣  Show this menu
0️⃣  Exit
══════════════════════════════════════════════════
    """)

def main():
    if not jira:
        return

    print("🚀 Initializing Simple JIRA Agent...")
    print("✅ JIRA Agent ready!")
    print("🎉 Welcome to Simple JIRA Agent! 🎉")
    show_menu()

    while True:
        choice = input("Enter your choice (0-9): ").strip()

        if choice == "1":
            search_recent_issues()
        elif choice == "2":
            keyword = input("Enter search keyword: ")
            search_issues_by_keyword(keyword)
        elif choice == "3":
            issue_key = input("Enter issue key (e.g., MFLP-6): ")
            get_issue_details(issue_key)
        elif choice == "4":
            view_projects()
        elif choice == "5":
            project = input("Enter project key (e.g., MFLP): ")
            summary = input("Enter issue summary: ")
            desc = input("Enter description (optional): ")
            create_issue(project, summary, desc)
        elif choice == "6":
            prompt = input("Ask AI about your JIRA: ")
            print("\n🤖 AI Response:")
            print(ask_ai(prompt))
        elif choice == "7":
            print("\n🤖 AI Summary of Recent Issues:")
            summary_prompt = "Summarize the most recent issues from my JIRA project."
            print(ask_ai(summary_prompt))
        elif choice == "8":
            try:
                jira.myself()
                print("✅ JIRA connection successful.")
            except Exception as e:
                print(f"❌ JIRA connection failed: {e}")
        elif choice == "9":
            show_menu()
        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("⚠️ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
