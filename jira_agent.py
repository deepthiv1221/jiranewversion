import os
import logging
from typing import Optional, List, Dict, Any, Type
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain_openai import OpenAI
from langchain.tools import BaseTool
from langchain.schema import AgentAction, AgentFinish
from pydantic import BaseModel, Field
from atlassian import Jira
import json

# DEBUG: Check if file is being executed
print("🚀 Starting JIRA Agent...")
print("Python is working!")

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JiraConfig:
    """Configuration class for JIRA connection"""
    def __init__(self):
        self.jira_url = os.getenv('JIRA_URL')
        self.jira_username = os.getenv('JIRA_USERNAME')
        self.jira_api_token = os.getenv('JIRA_API_TOKEN')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not all([self.jira_url, self.jira_username, self.jira_api_token, self.openai_api_key]):
            raise ValueError("Missing required environment variables. Check your .env file.")

class JiraSearchTool(BaseTool):
    """Tool for searching JIRA issues"""
    name: str = "jira_search"
    description: str = "Search for JIRA issues using JQL (JIRA Query Language). Use this to find specific issues, bugs, or tasks."
    
    def __init__(self, jira_client):
        super().__init__()
        self._jira_client = jira_client
    
    @property
    def jira_client(self):
        return self._jira_client
    
    def _run(self, query: str) -> str:
        """Search JIRA issues"""
        try:
            # If query doesn't look like JQL, create a simple text search
            if not any(keyword in query.lower() for keyword in ['project', 'status', 'assignee', 'summary']):
                jql = f'text ~ "{query}" ORDER BY created DESC'
            else:
                jql = query
            
            issues = self.jira_client.jql(jql, limit=10)
            
            if not issues['issues']:
                return "No issues found matching your search criteria."
            
            result = []
            for issue in issues['issues']:
                result.append({
                    'key': issue['key'],
                    'summary': issue['fields']['summary'],
                    'status': issue['fields']['status']['name'],
                    'assignee': issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned',
                    'priority': issue['fields']['priority']['name'] if issue['fields']['priority'] else 'None'
                })
            
            return json.dumps(result, indent=2)
        except Exception as e:
            logger.error(f"Error searching JIRA: {str(e)}")
            return f"Error searching JIRA: {str(e)}"

class JiraCreateIssueTool(BaseTool):
    """Tool for creating JIRA issues"""
    name: str = "jira_create_issue"
    description: str = "Create a new JIRA issue. Provide project key, issue type, summary, and description."
    
    def __init__(self, jira_client):
        super().__init__()
        self._jira_client = jira_client
    
    @property
    def jira_client(self):
        return self._jira_client
    
    def _run(self, issue_data: str) -> str:
        """Create a new JIRA issue"""
        try:
            # Parse the issue data (expect JSON format)
            data = json.loads(issue_data)
            
            issue_dict = {
                'project': {'key': data.get('project_key', 'TEST')},
                'summary': data.get('summary', 'New Issue'),
                'description': data.get('description', ''),
                'issuetype': {'name': data.get('issue_type', 'Task')},
            }
            
            if data.get('assignee'):
                issue_dict['assignee'] = {'name': data['assignee']}
            
            if data.get('priority'):
                issue_dict['priority'] = {'name': data['priority']}
            
            new_issue = self.jira_client.issue_create(fields=issue_dict)
            return f"Successfully created issue: {new_issue['key']}"
            
        except json.JSONDecodeError:
            return "Error: Please provide issue data in JSON format"
        except Exception as e:
            logger.error(f"Error creating JIRA issue: {str(e)}")
            return f"Error creating JIRA issue: {str(e)}"

class JiraUpdateIssueTool(BaseTool):
    """Tool for updating JIRA issues"""
    name: str = "jira_update_issue"
    description: str = "Update an existing JIRA issue. Provide issue key and fields to update."
    
    def __init__(self, jira_client):
        super().__init__()
        self._jira_client = jira_client
    
    @property
    def jira_client(self):
        return self._jira_client
    
    def _run(self, update_data: str) -> str:
        """Update a JIRA issue"""
        try:
            data = json.loads(update_data)
            issue_key = data.get('issue_key')
            
            if not issue_key:
                return "Error: issue_key is required"
            
            update_fields = {}
            
            if data.get('summary'):
                update_fields['summary'] = data['summary']
            if data.get('description'):
                update_fields['description'] = data['description']
            if data.get('assignee'):
                update_fields['assignee'] = {'name': data['assignee']}
            if data.get('status'):
                # For status updates, we need to use transitions
                return self._transition_issue(issue_key, data['status'])
            
            if update_fields:
                self.jira_client.issue_update(issue_key, fields=update_fields)
                return f"Successfully updated issue: {issue_key}"
            else:
                return "No valid fields provided for update"
                
        except json.JSONDecodeError:
            return "Error: Please provide update data in JSON format"
        except Exception as e:
            logger.error(f"Error updating JIRA issue: {str(e)}")
            return f"Error updating JIRA issue: {str(e)}"
    
    def _transition_issue(self, issue_key: str, new_status: str) -> str:
        """Transition issue to new status"""
        try:
            transitions = self.jira_client.get_issue_transitions(issue_key)
            
            for transition in transitions['transitions']:
                if transition['name'].lower() == new_status.lower():
                    self.jira_client.issue_transition(issue_key, transition['id'])
                    return f"Successfully transitioned {issue_key} to {new_status}"
            
            return f"Status '{new_status}' not available for issue {issue_key}"
        except Exception as e:
            return f"Error transitioning issue: {str(e)}"

class JiraGetIssueTool(BaseTool):
    """Tool for getting detailed information about a specific JIRA issue"""
    name: str = "jira_get_issue"
    description: str = "Get detailed information about a specific JIRA issue by its key (e.g., PROJ-123)."
    
    def __init__(self, jira_client):
        super().__init__()
        self._jira_client = jira_client
    
    @property
    def jira_client(self):
        return self._jira_client
    
    def _run(self, issue_key: str) -> str:
        """Get detailed issue information"""
        try:
            issue = self.jira_client.issue(issue_key)
            
            issue_info = {
                'key': issue['key'],
                'summary': issue['fields']['summary'],
                'description': issue['fields']['description'] or 'No description',
                'status': issue['fields']['status']['name'],
                'assignee': issue['fields']['assignee']['displayName'] if issue['fields']['assignee'] else 'Unassigned',
                'reporter': issue['fields']['reporter']['displayName'],
                'priority': issue['fields']['priority']['name'] if issue['fields']['priority'] else 'None',
                'created': issue['fields']['created'],
                'updated': issue['fields']['updated'],
                'issue_type': issue['fields']['issuetype']['name']
            }
            
            return json.dumps(issue_info, indent=2)
            
        except Exception as e:
            logger.error(f"Error getting JIRA issue: {str(e)}")
            return f"Error getting JIRA issue: {str(e)}"

class JiraAgent:
    """Main JIRA Agent class"""
    
    def __init__(self):
        print("📋 Loading configuration...")
        self.config = JiraConfig()
        print("🔗 Connecting to JIRA...")
        self.jira_client = self._initialize_jira_client()
        print("🤖 Initializing AI...")
        self.llm = OpenAI(openai_api_key=self.config.openai_api_key, temperature=0)
        print("🛠️ Setting up tools...")
        self.tools = self._initialize_tools()
        print("⚡ Starting agent...")
        self.agent = self._initialize_agent()
        print("✅ JIRA Agent ready!")
    
    def _initialize_jira_client(self):
        """Initialize JIRA client"""
        try:
            jira = Jira(
                url=self.config.jira_url,
                username=self.config.jira_username,
                password=self.config.jira_api_token
            )
            # Test connection
            user_info = jira.myself()
            logger.info(f"Successfully connected to JIRA as {user_info.get('displayName', 'User')}")
            return jira
        except Exception as e:
            logger.error(f"Failed to connect to JIRA: {str(e)}")
            print(f"❌ JIRA connection failed: {str(e)}")
            print("💡 Check your .env file credentials!")
            raise
    
    def _initialize_tools(self):
        """Initialize all JIRA tools"""
        return [
            JiraSearchTool(self.jira_client),
            JiraCreateIssueTool(self.jira_client),
            JiraUpdateIssueTool(self.jira_client),
            JiraGetIssueTool(self.jira_client)
        ]
    
    def _initialize_agent(self):
        """Initialize the LangChain agent"""
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=3
        )
    
    def run(self, query: str) -> str:
        """Run the agent with a query"""
        try:
            response = self.agent.run(query)
            return response
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}")
            return f"Error: {str(e)}"

def main():
    """Main function to run the JIRA agent"""
    try:
        print("=" * 50)
        print("🤖 JIRA AI AGENT")
        print("=" * 50)
        
        # Initialize the agent
        agent = JiraAgent()
        
        print("\n" + "=" * 50)
        print("🎉 JIRA Agent is ready!")
        print("=" * 50)
        print("You can ask me to:")
        print("💡 Search for issues: 'Find all bugs assigned to me'")
        print("💡 Get issue details: 'Get details for PROJ-123'") 
        print("💡 Create issues: 'Create a new task for user authentication'")
        print("💡 Update issues: 'Update PROJ-123 status to In Progress'")
        print("💡 Type 'quit' to exit")
        print("=" * 50 + "\n")
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            if not user_input:
                continue
                
            print("\n🤖 Agent is thinking...")
            print("-" * 30)
            response = agent.run(user_input)
            print(f"\n💬 Response: {response}")
            print("\n" + "=" * 50)
    
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("💡 Make sure your .env file is configured correctly!")
        print("💡 Check your API keys and JIRA credentials!")

if __name__ == "__main__":
    main()