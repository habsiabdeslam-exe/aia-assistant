import os
import logging
from typing import Optional
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """
    Configuration management with Azure Key Vault integration.
    
    Production (ENVIRONMENT=production):
    - Reads secrets from Azure Key Vault: ahakv01 (East US)
    - Uses DefaultAzureCredential (Managed Identity)
    
    Development (ENVIRONMENT=development or not set):
    - Reads from local environment variables
    - No Key Vault connection required
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one Config instance."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize configuration based on environment."""
        if self._initialized:
            return
        
        self.environment = os.getenv("ENVIRONMENT", "development").lower()
        self.key_vault_name = "ahakv01"
        self.is_production = self.environment == "production"
        
        self._secret_client: Optional[SecretClient] = None
        
        if self.is_production:
            logger.info("Running in PRODUCTION mode - using Azure Key Vault")
            try:
                self._initialize_key_vault()
            except Exception as e:
                logger.error(f"Failed to initialize Key Vault in production mode: {e}")
                raise
        else:
            logger.info("Running in DEVELOPMENT mode - using environment variables")
        
        self._initialized = True
    
    def _initialize_key_vault(self):
        """Initialize Azure Key Vault client with DefaultAzureCredential."""
        try:
            vault_url = f"https://{self.key_vault_name}.vault.azure.net"
            credential = DefaultAzureCredential()
            self._secret_client = SecretClient(vault_url=vault_url, credential=credential)
            
            # Test connection
            logger.info(f"Successfully connected to Azure Key Vault: {self.key_vault_name}")
        except ClientAuthenticationError as e:
            logger.error(f"Authentication failed for Key Vault '{self.key_vault_name}': {e}")
            raise
        except Exception as e:
            logger.error(f"Error initializing Key Vault client: {e}")
            raise
    
    def _get_secret_from_key_vault(self, secret_name: str) -> Optional[str]:
        """Retrieve secret from Azure Key Vault using exact secret name."""
        if not self._secret_client:
            return None
        
        try:
            secret = self._secret_client.get_secret(secret_name)
            logger.debug(f"Retrieved secret '{secret_name}' from Key Vault")
            return secret.value
        except ResourceNotFoundError:
            logger.error(f"Secret '{secret_name}' not found in Key Vault {self.key_vault_name}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving secret '{secret_name}' from Key Vault: {e}")
            return None
    
    def _get_secret(self, kv_secret_name: str, env_var_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get secret value from Key Vault (production) or environment variables (development).
        
        Args:
            kv_secret_name: Exact Key Vault secret name (e.g., "AZURE-OPENAI-KEY")
            env_var_name: Environment variable name (e.g., "AZURE_OPENAI_KEY")
            default: Default value if secret not found
        
        Returns:
            Secret value or default
        """
        if self.is_production:
            # Production: Read from Key Vault
            value = self._get_secret_from_key_vault(kv_secret_name)
            if value:
                return value
            logger.error(f"Secret '{kv_secret_name}' not found in Key Vault")
            if default:
                logger.warning(f"Using default value for '{kv_secret_name}'")
                return default
            raise ValueError(f"Required secret '{kv_secret_name}' not found in Key Vault")
        else:
            # Development: Read from environment variables
            value = os.getenv(env_var_name)
            if value:
                logger.debug(f"Retrieved '{env_var_name}' from environment variables")
                return value
            if default:
                logger.debug(f"Using default value for '{env_var_name}'")
                return default
            logger.warning(f"Environment variable '{env_var_name}' not set")
            return None
    
    # Azure OpenAI Configuration
    @property
    def azure_openai_endpoint(self) -> str:
        value = self._get_secret("AZURE-OPENAI-ENDPOINT", "AZURE_OPENAI_ENDPOINT")
        if not value:
            raise ValueError("Azure OpenAI endpoint not configured")
        return value
    
    @property
    def azure_openai_key(self) -> str:
        value = self._get_secret("AZURE-OPENAI-KEY", "AZURE_OPENAI_KEY")
        if not value:
            raise ValueError("Azure OpenAI key not configured")
        return value
    
    @property
    def gpt4_deployment(self) -> str:
        value = self._get_secret("AZURE-OPENAI-GPT4-DEP", "AZURE_OPENAI_GPT4_DEPLOYMENT", "gpt-4")
        return value
    
    @property
    def embedding_deployment(self) -> str:
        value = self._get_secret("AZURE-OPENAI-EMBED-DEP", "AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
        return value
    
    # Azure AI Search Configuration
    @property
    def azure_search_endpoint(self) -> str:
        value = self._get_secret("AZURE-SEARCH-ENDPOINT", "AZURE_SEARCH_ENDPOINT")
        if not value:
            raise ValueError("Azure Search endpoint not configured")
        return value
    
    @property
    def azure_search_key(self) -> str:
        value = self._get_secret("AZURE-SEARCH-KEY", "AZURE_SEARCH_KEY")
        if not value:
            raise ValueError("Azure Search key not configured")
        return value
    
    @property
    def azure_search_index_name(self) -> str:
        value = self._get_secret("AZURE-SEARCH-INDEX-NAME", "AZURE_SEARCH_INDEX_NAME", "tad-knowledge-base")
        return value


# Singleton instance
config = Config()
