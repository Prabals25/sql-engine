import subprocess
import os
from typing import Tuple, List
import ollama

class ModelInitializer:
    """
    A class to handle the initialization and management of Ollama models.
    This class handles model installation, checking, and creation.
    """
    
    def __init__(self):
        """Initialize the ModelInitializer class"""
        self.required_models = ['sqls', 'checker']
        self.base_model = 'llama3.2'
        
    def setup_ollama(self) -> bool:
        """
        Install ollama package if not already installed
        
        Returns:
            bool: True if setup was successful, False otherwise
        """
        try:
            import ollama
            return True
        except ImportError:
            try:
                subprocess.run(['pip', 'install', 'ollama'], check=True)
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error installing ollama: {str(e)}")
                return False
    
    def pull_base_model(self) -> bool:
        """
        Pull the base llama3.2 model from ollama
        
        Returns:
            bool: True if pull was successful, False otherwise
        """
        try:
            subprocess.run(['ollama', 'pull', self.base_model], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error pulling base model: {str(e)}")
            return False
    
    def check_models_exist(self) -> Tuple[bool, List[str]]:
        """
        Check if required models exist in the system
        
        Returns:
            Tuple[bool, List[str]]: (all_models_exist, missing_models)
        """
        try:
            # Get list of installed models
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            print("Ollama list output:", result.stdout)  # Debug print
            
            # Split by newlines and get model names
            installed_models = []
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip():  # Skip empty lines
                    model_name = line.split()[0][:-7]  # First column is model name
                    installed_models.append(model_name)
            
            print("Installed models:", installed_models)  # Debug print
            print("Required models:", self.required_models)  # Debug print
            
            # Check for missing models
            missing_models = [model for model in self.required_models if model not in installed_models]
            print("Missing models:", missing_models)  # Debug print
            
            all_exist = len(missing_models) == 0
            print("All models exist:", all_exist)  # Debug print
            
            return (all_exist, missing_models)
            
        except subprocess.CalledProcessError as e:
            print(f"Error checking models: {str(e)}")
            return (False, self.required_models)
    
    def create_models(self) -> Tuple[bool, str]:
        """
        Create SQL and checker models from Modelfiles if they don't exist
        
        Returns:
            Tuple[bool, str]: (success status, message)
        """
        try:
            # First check if models already exist
            models_exist, missing_models = self.check_models_exist()
            print("In create_models - models_exist:", models_exist)  # Debug print
            if models_exist:
                print("Models already exist, skipping creation")  # Debug print
                return True, "All required models already exist"
            
            # Get the current directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Create only missing models
            for model in missing_models:
                if model == 'sqls':
                    sql_model_path = os.path.join(current_dir, 'Models', 'sqls', 'Modelfile')
                    if not os.path.exists(sql_model_path):
                        return False, f"SQL Modelfile not found at {sql_model_path}"
                    print("Creating SQL model...")  # Debug print
                    subprocess.run(['ollama', 'create', 'sqls', '-f', sql_model_path], check=True)
                    print("Created SQL model successfully")
                
                elif model == 'checker':
                    checker_model_path = os.path.join(current_dir, 'Models', 'checker', 'Modelfile')
                    if not os.path.exists(checker_model_path):
                        return False, f"Checker Modelfile not found at {checker_model_path}"
                    print("Creating checker model...")  # Debug print
                    subprocess.run(['ollama', 'create', 'checker', '-f', checker_model_path], check=True)
                    print("Created checker model successfully")
            
            return True, "Models created successfully!"
            
        except subprocess.CalledProcessError as e:
            return False, f"Error creating models: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def initialize_models(self) -> Tuple[bool, str]:
        """
        Initialize all required models by:
        1. Setting up ollama
        2. Pulling base model
        3. Checking for existing models
        4. Creating missing models if needed
        
        Returns:
            Tuple[bool, str]: (success status, message)
        """
        try:
            # Setup ollama
            if not self.setup_ollama():
                return False, "Failed to setup ollama"
            
            # Pull base model
            if not self.pull_base_model():
                return False, "Failed to pull base model"
            
            # Check existing models
            models_exist, missing_models = self.check_models_exist()
            print("In initialize_models - models_exist:", models_exist)  # Debug print
            
            if models_exist:
                print("All required models are already installed")  # Debug print
                return True, "All required models are already installed"
            
            # Only create models if they don't exist
            if missing_models:
                print("Creating missing models:", missing_models)  # Debug print
                success, message = self.create_models()
                if not success:
                    return False, message
                return True, "Models initialized successfully"
            
            return True, "No models needed to be created"
            
        except Exception as e:
            return False, f"Error during initialization: {str(e)}"
