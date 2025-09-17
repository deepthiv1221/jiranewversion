print("Testing imports...")

try:
    import os
    print("✅ os imported")
except ImportError as e:
    print(f"❌ os failed: {e}")

try:
    from dotenv import load_dotenv
    print("✅ dotenv imported")
except ImportError as e:
    print(f"❌ dotenv failed: {e}")

try:
    import langchain
    print("✅ langchain imported")
except ImportError as e:
    print(f"❌ langchain failed: {e}")

try:
    from atlassian import Jira
    print("✅ atlassian imported")
except ImportError as e:
    print(f"❌ atlassian failed: {e}")

try:
    import openai
    print("✅ openai imported")
except ImportError as e:
    print(f"❌ openai failed: {e}")

print("Import test completed!")