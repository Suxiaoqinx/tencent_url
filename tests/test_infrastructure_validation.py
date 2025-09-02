"""
Infrastructure validation tests.

These tests verify that the testing infrastructure is properly set up
and working correctly. They should be run first to ensure the test
environment is functional before running any application-specific tests.
"""

import pytest
import json
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch


class TestTestingInfrastructure:
    """Test the testing infrastructure setup."""
    
    def test_pytest_is_working(self):
        """Verify that pytest is functioning correctly."""
        assert True, "Basic pytest assertion should pass"
    
    def test_python_path_includes_project_root(self):
        """Verify that the project root is in the Python path."""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        assert project_root in sys.path, "Project root should be in Python path"
    
    def test_can_import_app_module(self):
        """Verify that we can import the main application module."""
        try:
            import app
            assert hasattr(app, 'QQMusic'), "QQMusic class should be importable"
            assert hasattr(app, 'app'), "Flask app should be importable"
        except ImportError as e:
            pytest.fail(f"Failed to import app module: {e}")


class TestFixtures:
    """Test that all fixtures are working correctly."""
    
    def test_temp_dir_fixture(self, temp_dir):
        """Test the temp_dir fixture."""
        assert temp_dir.exists(), "Temporary directory should exist"
        assert temp_dir.is_dir(), "temp_dir should be a directory"
        
        # Test we can create files in it
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists(), "Should be able to create files in temp dir"
    
    def test_sample_config_fixture(self, sample_config):
        """Test the sample_config fixture."""
        assert isinstance(sample_config, dict), "Config should be a dictionary"
        assert 'base_url' in sample_config, "Config should have base_url"
        assert 'guid' in sample_config, "Config should have guid"
        assert 'uin' in sample_config, "Config should have uin"
    
    def test_sample_song_data_fixture(self, sample_song_data):
        """Test the sample_song_data fixture."""
        assert isinstance(sample_song_data, dict), "Song data should be a dictionary"
        assert 'name' in sample_song_data, "Song data should have name"
        assert 'album' in sample_song_data, "Song data should have album"
        assert 'singer' in sample_song_data, "Song data should have singer"
        assert 'mid' in sample_song_data, "Song data should have mid"
        assert 'id' in sample_song_data, "Song data should have id"
    
    def test_sample_music_url_response_fixture(self, sample_music_url_response):
        """Test the sample_music_url_response fixture."""
        assert isinstance(sample_music_url_response, dict), "Response should be a dictionary"
        assert 'req_1' in sample_music_url_response, "Response should have req_1 key"
        assert 'data' in sample_music_url_response['req_1'], "Response should have data"
        assert 'midurlinfo' in sample_music_url_response['req_1']['data'], "Response should have midurlinfo"
    
    def test_mock_requests_session_fixture(self, mock_requests_session):
        """Test the mock_requests_session fixture."""
        assert hasattr(mock_requests_session, 'get'), "Mock session should have get method"
        assert hasattr(mock_requests_session, 'post'), "Mock session should have post method"
        
        # Test mock responses
        response = mock_requests_session.get('http://example.com')
        assert response.status_code == 200, "Mock should return 200 status"
        assert response.json()['status'] == 'success', "Mock should return success status"
    
    def test_mock_qqmusic_instance_fixture(self, mock_qqmusic_instance):
        """Test the mock_qqmusic_instance fixture."""
        assert hasattr(mock_qqmusic_instance, 'base_url'), "Mock should have base_url"
        assert hasattr(mock_qqmusic_instance, 'guid'), "Mock should have guid"
        assert hasattr(mock_qqmusic_instance, 'set_cookies'), "Mock should have set_cookies method"
        assert hasattr(mock_qqmusic_instance, 'get_music_url'), "Mock should have get_music_url method"
        
        # Test mock method responses
        result = mock_qqmusic_instance.get_music_url('test_mid')
        assert 'url' in result, "Mock method should return expected structure"
        assert 'bitrate' in result, "Mock method should return expected structure"
    
    def test_json_data_fixture(self, json_data, temp_dir):
        """Test the json_data fixture utilities."""
        test_data = {'test': 'value', 'number': 42}
        test_file = temp_dir / 'test.json'
        
        # Test creating JSON file
        json_data['create_file'](test_data, test_file)
        assert test_file.exists(), "JSON file should be created"
        
        # Test loading JSON file
        loaded_data = json_data['load_file'](test_file)
        assert loaded_data == test_data, "Loaded data should match original"
        
        # Test JSON utilities
        json_string = json_data['dumps'](test_data)
        assert isinstance(json_string, str), "dumps should return string"
        
        parsed_data = json_data['loads'](json_string)
        assert parsed_data == test_data, "loads should parse correctly"
    
    def test_network_responses_fixture(self, network_responses):
        """Test the network_responses fixture."""
        assert 'success' in network_responses, "Should have success response"
        assert 'error' in network_responses, "Should have error response"
        assert 'not_found' in network_responses, "Should have not_found response"
        
        success_response = network_responses['success']
        assert success_response['status'] == 'success', "Success response should have correct status"
        assert success_response['code'] == 200, "Success response should have correct code"


class TestPytestMarkers:
    """Test custom pytest markers."""
    
    @pytest.mark.unit
    def test_unit_marker(self):
        """Test that unit marker works."""
        assert True, "Unit marker test should pass"
    
    @pytest.mark.integration
    def test_integration_marker(self):
        """Test that integration marker works."""
        assert True, "Integration marker test should pass"
    
    @pytest.mark.slow
    def test_slow_marker(self):
        """Test that slow marker works."""
        assert True, "Slow marker test should pass"


class TestEnvironmentSetup:
    """Test environment setup and configuration."""
    
    def test_environment_variables_fixture(self, environment_variables):
        """Test environment variables fixture."""
        assert 'FLASK_ENV' in environment_variables, "Should set FLASK_ENV"
        assert os.environ.get('FLASK_ENV') == 'testing', "FLASK_ENV should be set to testing"
        assert os.environ.get('DEBUG') == 'True', "DEBUG should be set to True"
        assert os.environ.get('TESTING') == 'True', "TESTING should be set to True"


class TestLoggingCapture:
    """Test logging capture functionality."""
    
    def test_capture_logs_fixture(self, capture_logs):
        """Test the capture_logs fixture."""
        import logging
        
        logger = logging.getLogger(__name__)
        test_message = "Test log message"
        
        logger.info(test_message)
        capture_logs.assert_log_contains(test_message, 'INFO')
        
        info_logs = capture_logs.get_logs_by_level('INFO')
        assert test_message in info_logs, "Should capture INFO level logs"


class TestMockingCapabilities:
    """Test mocking and patching capabilities."""
    
    def test_basic_mocking(self):
        """Test basic mocking functionality."""
        mock_obj = Mock()
        mock_obj.method.return_value = "mocked_result"
        
        result = mock_obj.method()
        assert result == "mocked_result", "Mock should return expected value"
        mock_obj.method.assert_called_once(), "Mock method should be called once"
    
    @patch('requests.get')
    def test_patching_requests(self, mock_get):
        """Test patching external dependencies."""
        mock_response = Mock()
        mock_response.json.return_value = {'mocked': True}
        mock_get.return_value = mock_response
        
        import requests
        response = requests.get('http://example.com')
        result = response.json()
        
        assert result['mocked'] is True, "Patched request should return mocked data"
        mock_get.assert_called_once_with('http://example.com')


class TestTestDiscovery:
    """Test that pytest can discover and run tests correctly."""
    
    def test_in_unit_directory_would_be_discovered(self):
        """This test verifies test discovery patterns work."""
        # This test is in the main tests directory, but similar tests
        # in tests/unit/ and tests/integration/ should be discovered
        assert True, "Test discovery should work"
    
    def test_file_naming_convention(self):
        """Test that file naming conventions are working."""
        # This file starts with test_ so it should be discovered
        assert __file__.endswith('test_infrastructure_validation.py'), \
            "Test file should follow naming convention"


if __name__ == '__main__':
    # Allow running this test file directly
    pytest.main([__file__, '-v'])