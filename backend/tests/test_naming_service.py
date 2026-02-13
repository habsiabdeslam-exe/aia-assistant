import pytest
from unittest.mock import Mock, patch
from app.services.naming_service import NamingService


class TestNamingService:
    """Test suite for NamingService"""
    
    @pytest.fixture
    def naming_service(self):
        """Create a NamingService instance for testing"""
        return NamingService()
    
    @pytest.fixture
    def mock_rag_results(self):
        """Mock RAG results with Sodexo naming convention"""
        return [
            {
                "content": """
                Resource Group Naming Convention for Private PaaS Assets
                
                Pattern: {Business Line}-{Region}-{Cloud Region}-{Project}-{Environment}-RG##
                
                Examples:
                - GLB-GLB-IENO-IOT-PRD-RG01
                - OSS-NAM-USEA-ANALYTICS-DEV-RG01
                - IST-COE-NLWE-DATAPLATFORM-TST-RG02
                
                Business Line Codes:
                - GLB: Global
                - OSS: On-Site Services
                - IST: Infrastructure Services & Technology
                - FMS: Facilities Management Services
                
                Region Codes:
                - GLB: Global
                - NAM: North America
                - COE: Central & Eastern Europe
                - LAM: Latin America
                
                Cloud Region Codes:
                - IENO: Ireland North Europe
                - NLWE: Netherlands West Europe
                - USEA: US East
                - UKSO: UK South
                
                Environment Codes:
                - PRD: Production
                - DEV: Development
                - TST: Test
                - STG: Staging
                """,
                "title": "GCCC-POL-Naming-Convention-Policy.pdf",
                "score": 0.95
            },
            {
                "content": """
                Additional naming references for Azure resources.
                Resource Groups must follow the standard pattern with hyphen separators.
                All codes must be uppercase.
                """,
                "title": "GCCC-POL-Naming-Convention-References.pdf",
                "score": 0.82
            }
        ]
    
    def test_search_naming_convention_for_resource_groups(self, naming_service):
        """Test RAG search for RG naming convention"""
        with patch.object(naming_service.search_service, 'hybrid_search') as mock_search, \
             patch.object(naming_service.embedding_service, 'generate_embedding') as mock_embed:
            
            mock_embed.return_value = [0.1] * 1536
            mock_search.return_value = [
                {
                    "content": "Resource Group naming pattern RG## example",
                    "title": "naming-convention.pdf",
                    "score": 0.9
                }
            ]
            
            results = naming_service.search_naming_convention_for_resource_groups()
            
            assert len(results) > 0
            assert mock_search.called
            assert mock_embed.called
    
    def test_extract_rg_naming_pattern_success(self, naming_service, mock_rag_results):
        """Test successful pattern extraction from RAG results"""
        pattern_info = naming_service.extract_rg_naming_pattern(mock_rag_results)
        
        assert pattern_info is not None
        assert "pattern" in pattern_info
        assert "segments" in pattern_info
        assert "source" in pattern_info
        assert pattern_info["separator"] == "-"
        assert len(pattern_info["segments"]) == 6
        assert "Business Line" in pattern_info["segments"]
        assert "RG##" in pattern_info["segments"]
    
    def test_extract_rg_naming_pattern_no_results(self, naming_service):
        """Test pattern extraction with no RAG results"""
        pattern_info = naming_service.extract_rg_naming_pattern([])
        
        assert pattern_info is None
    
    def test_extract_naming_codes(self, naming_service, mock_rag_results):
        """Test extraction of naming code tables"""
        codes = naming_service.extract_naming_codes(mock_rag_results)
        
        assert "business_lines" in codes
        assert "regions" in codes
        assert "cloud_regions" in codes
        assert "environments" in codes
        
        assert "GLB" in codes["business_lines"]
        assert codes["business_lines"]["GLB"] == "Global"
        
        assert "IENO" in codes["cloud_regions"]
        assert "Ireland" in codes["cloud_regions"]["IENO"]
        
        assert "PRD" in codes["environments"]
        assert codes["environments"]["PRD"] == "Production"
    
    def test_map_azure_region_to_sodexo_code(self, naming_service):
        """Test Azure region to Sodexo code mapping"""
        extracted_codes = {
            "IENO": "Ireland North Europe",
            "NLWE": "Netherlands West Europe",
            "USEA": "US East"
        }
        
        code = naming_service.map_azure_region_to_sodexo_code("North Europe", extracted_codes)
        assert code == "IENO"
        
        code = naming_service.map_azure_region_to_sodexo_code("West Europe", extracted_codes)
        assert code == "NLWE"
        
        code = naming_service.map_azure_region_to_sodexo_code("Unknown Region", extracted_codes)
        assert code is None
    
    def test_generate_resource_group_name_success(self, naming_service, mock_rag_results):
        """Test successful RG name generation"""
        with patch.object(naming_service, 'search_naming_convention_for_resource_groups') as mock_search:
            mock_search.return_value = mock_rag_results
            
            requirements = {
                "project_name": "IOT",
                "cloud_region": "North Europe",
                "environment": "PRD"
            }
            
            result = naming_service.generate_resource_group_name(requirements)
            
            assert "error" not in result
            assert result["name"] == "GLB-GLB-IENO-IOT-PRD-RG01"
            assert result["pattern"] == "{Business Line}-{Region}-{Cloud Region}-{Project}-{Environment}-RG##"
            assert result["validation"]["rag_query_executed"] is True
            assert result["validation"]["naming_convention_found"] is True
            assert "source" in result
            assert result["source"]["file"] == "GCCC-POL-Naming-Convention-Policy.pdf"
    
    def test_generate_resource_group_name_dev_environment(self, naming_service, mock_rag_results):
        """Test RG name generation for DEV environment"""
        with patch.object(naming_service, 'search_naming_convention_for_resource_groups') as mock_search:
            mock_search.return_value = mock_rag_results
            
            requirements = {
                "project_name": "ANALYTICS",
                "cloud_region": "West Europe",
                "environment": "DEV",
                "business_line": "OSS",
                "region": "NAM"
            }
            
            result = naming_service.generate_resource_group_name(requirements)
            
            assert "error" not in result
            assert result["name"] == "OSS-NAM-NLWE-ANALYTICS-DEV-RG01"
            assert result["components"]["business_line"]["value"] == "OSS"
            assert result["components"]["environment"]["value"] == "DEV"
    
    def test_generate_resource_group_name_no_rag_results(self, naming_service):
        """Test RG name generation when RAG returns no results"""
        with patch.object(naming_service, 'search_naming_convention_for_resource_groups') as mock_search:
            mock_search.return_value = []
            
            requirements = {
                "project_name": "IOT",
                "cloud_region": "North Europe",
                "environment": "PRD"
            }
            
            result = naming_service.generate_resource_group_name(requirements)
            
            assert "error" in result
            assert "not found in AI Search index" in result["error"]
            assert result["name"] is None
            assert result["validation"]["rag_query_executed"] is True
            assert result["validation"]["naming_convention_found"] is False
    
    def test_generate_resource_group_name_invalid_region(self, naming_service, mock_rag_results):
        """Test RG name generation with unmappable Azure region"""
        with patch.object(naming_service, 'search_naming_convention_for_resource_groups') as mock_search:
            mock_search.return_value = mock_rag_results
            
            requirements = {
                "project_name": "IOT",
                "cloud_region": "Mars Region",  # Invalid region
                "environment": "PRD"
            }
            
            result = naming_service.generate_resource_group_name(requirements)
            
            assert "error" in result
            assert "Could not map Azure region" in result["error"]
            assert result["name"] is None
    
    def test_validate_resource_group_name_valid(self, naming_service):
        """Test validation of a valid RG name"""
        result = naming_service.validate_resource_group_name("GLB-GLB-IENO-IOT-PRD-RG01")
        
        assert result["valid"] is True
        assert "segments" in result
        assert result["segments"]["business_line"] == "GLB"
        assert result["segments"]["project"] == "IOT"
        assert result["segments"]["environment"] == "PRD"
        assert result["segments"]["suffix"] == "RG01"
    
    def test_validate_resource_group_name_invalid_pattern(self, naming_service):
        """Test validation of invalid RG name"""
        result = naming_service.validate_resource_group_name("invalid-name")
        
        assert result["valid"] is False
        assert "error" in result
    
    def test_validate_resource_group_name_wrong_segments(self, naming_service):
        """Test validation with wrong number of segments"""
        result = naming_service.validate_resource_group_name("GLB-GLB-IENO-IOT-RG01")
        
        assert result["valid"] is False
        assert "6 segments" in result["error"]
    
    def test_validate_resource_group_name_missing_rg_suffix(self, naming_service):
        """Test validation with missing RG suffix"""
        result = naming_service.validate_resource_group_name("GLB-GLB-IENO-IOT-PRD-XX01")
        
        assert result["valid"] is False
        assert "must start with 'RG'" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
