"""
Vertex AI RAG Agent

A package for interacting with Google Cloud Vertex AI RAG capabilities.
"""

# import os # No longer needed here for PROJECT_ID/LOCATION
# import vertexai # No longer needed here for init
# from dotenv import load_dotenv # No longer needed here

# # Load environment variables
# load_dotenv() # REMOVED

# # Get Vertex AI configuration from environment
# PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT") # REMOVED
# LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION") # REMOVED

# # Initialize Vertex AI at package load time
# try: # REMOVED THIS ENTIRE TRY-EXCEPT BLOCK
#     if PROJECT_ID and LOCATION:
#         print(f"Initializing Vertex AI with project={PROJECT_ID}, location={LOCATION}")
#         vertexai.init(project=PROJECT_ID, location=LOCATION)
#         print("Vertex AI initialization successful")
#     else:
#         print(
#             f"Missing Vertex AI configuration. PROJECT_ID={PROJECT_ID}, LOCATION={LOCATION}. "
#             f"Tools requiring Vertex AI may not work properly."
#         )
# except Exception as e:
#     print(f"Failed to initialize Vertex AI: {str(e)}")
#     print("Please check your Google Cloud credentials and project settings.")

# Import agent. It will use the Vertex AI configuration initialized by the main application (app.py).
from . import agent