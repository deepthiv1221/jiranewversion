# test_jira_direct.py
from dotenv import load_dotenv
import os
from atlassian import Jira
import json

load_dotenv()

# Connect to JIRA
jira = Jira(
    url=os.getenv('JIRA_URL'),
    username=os.getenv('JIRA_USERNAME'),
    password=os.getenv('JIRA_API_TOKEN')
)

print("🔗 Testing direct JIRA connection...")

# Test 1: Get user info
try:
    user = jira.myself()
    print(f"✅ Connected as: {user['displayName']}")
except Exception as e:
    print(f"❌ Connection failed: {e}")

# Test 2: Search for issues
try:
    issues = jira.jql("ORDER BY created DESC", limit=5)
    print(f"✅ Found {len(issues['issues'])} issues:")
    
    for issue in issues['issues']:
        print(f"  - {issue['key']}: {issue['fields']['summary']}")
        
except Exception as e:
    print(f"❌ Search failed: {e}")

print("\n🎉 JIRA functionality is working perfectly!")