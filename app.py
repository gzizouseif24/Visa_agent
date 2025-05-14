import os
import sys
import logging # Added for better logging
from flask import Flask, request, jsonify, render_template, Response # Added Response
from dotenv import load_dotenv
import vertexai # Ensure vertexai is imported for init if not already by rag_agent
from vertexai.preview import reasoning_engines

# Attempt to import the agent and trigger its __init__.py for Vertex AI setup
try:
    from rag_agent.agent import root_agent
    print("Successfully imported root_agent.")
except ImportError as e:
    print(f"Error importing root_agent: {e}. Ensure rag_agent is in PYTHONPATH.")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred during agent import: {e}")
    sys.exit(1)

# Configure basic logging
logging.basicConfig(level=logging.INFO) # Changed to INFO for less verbose logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

flask_app = Flask(__name__)

# Initialize Vertex AI (explicitly, as a fallback or primary way)
# Your rag_agent/__init__.py should also attempt this.
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")

if not PROJECT_ID or not LOCATION:
    logger.error("GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION must be set in .env or environment.")
    sys.exit(1)

try:
    logger.info(f"Initializing Vertex AI with project={PROJECT_ID}, location={LOCATION}")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    logger.info("Vertex AI initialized successfully in app.py.")
except Exception as e:
    logger.error(f"Failed to initialize Vertex AI in app.py: {e}")
    # Depending on the setup, this might not be fatal if rag_agent.__init__ succeeded.

# Create an AdkApp instance to interact with the agent
if 'root_agent' in globals():
    adk_app_instance = reasoning_engines.AdkApp(agent=root_agent)
    logger.info("AdkApp instance created.")
else:
    logger.error("root_agent not available for AdkApp instantiation. Exiting.")
    sys.exit(1)

# User ID for the session
APP_USER_ID = "flask_user_001"

# Create a session when the app starts and store its ID
actual_session_id = None
try:
    logger.info(f"Creating ADK session for user_id: {APP_USER_ID}...")
    # create_session() returns a session object or dict, typically with an 'id' field
    created_session = adk_app_instance.create_session(user_id=APP_USER_ID)
    
    # Determine how to access the session ID based on its type
    if hasattr(created_session, 'id'): # If it's an object with an .id attribute
        actual_session_id = created_session.id
    elif isinstance(created_session, dict) and 'id' in created_session: # If it's a dict with an 'id' key
        actual_session_id = created_session['id']
    else:
        logger.error(f"Could not determine session ID from created_session: {created_session}")
        sys.exit(1)
        
    logger.info(f"ADK Session created successfully. Session ID: {actual_session_id}")
except Exception as e:
    logger.error(f"Failed to create ADK session: {e}", exc_info=True)
    sys.exit(1)

@flask_app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@flask_app.route('/query', methods=['POST'])
def handle_query():
    """Handles queries to the RAG agent."""
    global actual_session_id # Ensure we're using the globally stored session ID
    if not actual_session_id:
        logger.error("ADK Session ID not available for query.")
        # Attempt to recreate session if lost (simple retry)
        try:
            logger.info(f"Recreating ADK session for user_id: {APP_USER_ID}...")
            created_session = adk_app_instance.create_session(user_id=APP_USER_ID)
            if hasattr(created_session, 'id'): actual_session_id = created_session.id
            elif isinstance(created_session, dict) and 'id' in created_session: actual_session_id = created_session['id']
            else: raise ValueError("Failed to get ID from recreated session")
            logger.info(f"ADK Session recreated: {actual_session_id}")
        except Exception as e_retry:
            logger.error(f"Failed to recreate ADK session: {e_retry}", exc_info=True)
            return jsonify({'error': 'ADK session not initialized and could not be recreated'}), 500
            
    data = request.get_json()
    user_query = data.get('query')

    if not user_query:
        return jsonify({'error': 'No query provided'}), 400

    def generate_agent_responses():
        logger.info(f"Streaming query: '{user_query}' for session: {actual_session_id}")
        for event in adk_app_instance.stream_query(
            user_id=APP_USER_ID,
            session_id=actual_session_id,
            message=user_query
        ):
            logger.debug(f"Raw event from AdkApp: {event}")
            if isinstance(event, dict) and 'content' in event and event.get('content') is not None:
                content_val = event['content']
                if isinstance(content_val, dict) and 'parts' in content_val and content_val.get('parts') is not None:
                    parts_list = content_val['parts']
                    if isinstance(parts_list, list):
                        for part_item in parts_list:
                            if isinstance(part_item, dict) and 'text' in part_item and part_item.get('text') is not None:
                                text_chunk = part_item['text']
                                logger.debug(f"Yielding text chunk: {text_chunk}")
                                yield text_chunk # Stream each text chunk
        logger.info("Finished streaming agent response.")

    try:
        return Response(generate_agent_responses(), mimetype='text/plain')
    except Exception as e:
        logger.error(f"Error during query streaming: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure rag_agent is importable, re-check path if needed
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    try:
        from rag_agent.agent import root_agent # Ensure this import path is correct from app.py location
    except ImportError:
        logger.error("Could not import root_agent. Ensure app.py is in the project root or PYTHONPATH is set.")
        sys.exit(1)
    
    flask_app.run(debug=True, host='0.0.0.0', port=5000) 