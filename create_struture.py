import os
# Define the folder structure
folder_structure =  {
        "config": ["config.yaml", "logging.yaml"],
        "data_ingestion": ["__init__.py", "forum_scraper.py", "financial_api.py"],
        "preprocessing": ["text_cleaning.py"],
        "summarization": ["summarizer.py"],
        "sentiment_analysis": ["sentiment.py"],
        "financial_data": ["metrics.py"],
        "screening_ml": ["screening.py"],
        "knowledge_graph": ["kg_builder.py"],
        "rag_pipeline": ["rag.py"],
        "dashboard": ["app.py"],
        "scheduler": ["job_runner.py"],
        "utils": ["logger.py", "error_handling.py"],
        "tests": ["test_forum_scraper.py"],
        "requirements.txt": None,
        "README.md": None,
    }
# Function to create the folder structure
def create_structure(base_path, structure):
    for folder_name, contents in structure.items():
        # Create folder
        folder_path = os.path.join(base_path, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # Create files if any
        if contents is not None:
            for file_name in contents:
                file_path = os.path.join(folder_path, file_name)
                with open(file_path, 'w') as f:
                    # Optionally write some initial content to files
                    f.write(f"# {file_name}\n\n")
                    
# Create the folder structure
create_structure(".", folder_structure)
print("Folder structure created successfully.")