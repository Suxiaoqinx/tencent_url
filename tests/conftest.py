"""
Shared pytest fixtures for the QQ Music API testing infrastructure.

This module provides common fixtures that can be used across all test modules
to ensure consistent testing setup and reduce code duplication.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock
import sys
import os

# Add the project root to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def temp_dir():
    """
    Creates a temporary directory for test files.
    
    Yields:
        Path: Path to the temporary directory
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_config():
    """
    Provides a sample configuration dictionary for testing.
    
    Returns:
        dict: Sample configuration data
    """
    return {
        'base_url': 'https://u.y.qq.com/cgi-bin/musicu.fcg',
        'guid': '10000',
        'uin': '0',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'timeout': 30
    }


@pytest.fixture
def sample_song_data():
    """
    Provides sample song data for testing music-related functionality.
    
    Returns:
        dict: Sample song information
    """
    return {
        'name': 'Test Song',
        'album': 'Test Album',
        'singer': 'Test Artist',
        'mid': 'test123mid',
        'id': 123456789,
        'pic': 'https://example.com/cover.jpg'
    }


@pytest.fixture
def sample_music_url_response():
    """
    Provides a sample music URL response for testing.
    
    Returns:
        dict: Sample music URL response data
    """
    return {
        'req_1': {
            'data': {
                'midurlinfo': [{
                    'purl': 'M800test123mid.mp3?guid=10000&vkey=test_vkey'
                }],
                'sip': ['', 'https://ws.stream.qqmusic.qq.com/']
            }
        }
    }


@pytest.fixture
def sample_lyric_response():
    """
    Provides sample lyric response data for testing.
    
    Returns:
        dict: Sample lyric response
    """
    import base64
    
    sample_lyric = "[00:00.00]Test lyric line 1\n[00:05.00]Test lyric line 2"
    encoded_lyric = base64.b64encode(sample_lyric.encode('utf-8')).decode('utf-8')
    
    return {
        'music.musichallSong.PlayLyricInfo.GetPlayLyricInfo': {
            'data': {
                'lyric': encoded_lyric,
                'trans': encoded_lyric
            }
        }
    }


@pytest.fixture
def mock_requests_session():
    """
    Creates a mock requests session for testing HTTP calls.
    
    Returns:
        Mock: Mocked requests session
    """
    session = Mock()
    response = Mock()
    response.status_code = 200
    response.json.return_value = {'status': 'success'}
    response.text = 'Mock response text'
    response.headers = {'Content-Type': 'application/json'}
    
    session.get.return_value = response
    session.post.return_value = response
    
    return session


@pytest.fixture
def mock_flask_app():
    """
    Creates a mock Flask app for testing web endpoints.
    
    Returns:
        Mock: Mocked Flask application
    """
    app = Mock()
    app.config = {}
    app.test_client.return_value = Mock()
    return app


@pytest.fixture
def mock_qqmusic_instance():
    """
    Creates a mock QQMusic instance for testing.
    
    Returns:
        Mock: Mocked QQMusic instance
    """
    mock_qq = Mock()
    mock_qq.base_url = 'https://u.y.qq.com/cgi-bin/musicu.fcg'
    mock_qq.guid = '10000'
    mock_qq.uin = '0'
    mock_qq.cookies = {}
    mock_qq.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Mock methods
    mock_qq.set_cookies.return_value = None
    mock_qq.ids.return_value = 'test123mid'
    mock_qq.get_music_url.return_value = {
        'url': 'https://example.com/music.mp3',
        'bitrate': 'flac'
    }
    mock_qq.get_music_song.return_value = {
        'name': 'Test Song',
        'album': 'Test Album',
        'singer': 'Test Artist',
        'mid': 'test123mid',
        'id': 123456789
    }
    mock_qq.get_music_lyric_new.return_value = {
        'lyric': 'Test lyric content',
        'tylyric': 'Translated lyric content'
    }
    
    return mock_qq


@pytest.fixture
def environment_variables():
    """
    Sets up environment variables for testing.
    
    Yields:
        dict: Dictionary of environment variables set for testing
    """
    test_env = {
        'FLASK_ENV': 'testing',
        'DEBUG': 'True',
        'TESTING': 'True'
    }
    
    # Set environment variables
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield test_env
    
    # Restore original environment variables
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def json_data():
    """
    Provides utilities for working with JSON data in tests.
    
    Returns:
        dict: Dictionary with JSON utility functions
    """
    def create_json_file(data, filepath):
        """Create a JSON file with the given data."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_json_file(filepath):
        """Load JSON data from a file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {
        'create_file': create_json_file,
        'load_file': load_json_file,
        'dumps': json.dumps,
        'loads': json.loads
    }


@pytest.fixture
def network_responses():
    """
    Provides common network response patterns for testing.
    
    Returns:
        dict: Dictionary of common response patterns
    """
    return {
        'success': {'status': 'success', 'code': 200},
        'error': {'status': 'error', 'code': 400, 'message': 'Bad Request'},
        'not_found': {'status': 'error', 'code': 404, 'message': 'Not Found'},
        'server_error': {'status': 'error', 'code': 500, 'message': 'Internal Server Error'},
        'timeout': {'status': 'error', 'code': 408, 'message': 'Request Timeout'}
    }


@pytest.fixture(autouse=True)
def reset_global_state():
    """
    Automatically resets any global state between tests.
    
    This fixture runs automatically before each test to ensure
    clean state and prevent test interference.
    """
    # Reset any global variables or state here if needed
    yield
    # Cleanup after test if needed


@pytest.fixture
def capture_logs(caplog):
    """
    Enhanced log capturing fixture with common log level setup.
    
    Args:
        caplog: pytest's built-in log capture fixture
    
    Returns:
        LoggingHelper: Helper object for log assertions
    """
    import logging
    
    # Set log level to capture all messages
    caplog.set_level(logging.DEBUG)
    
    class LoggingHelper:
        def __init__(self, caplog):
            self.caplog = caplog
        
        def assert_log_contains(self, message, level=None):
            """Assert that logs contain a specific message."""
            for record in self.caplog.records:
                if message in record.getMessage():
                    if level is None or record.levelname == level:
                        return True
            raise AssertionError(f"Log message '{message}' not found")
        
        def get_logs_by_level(self, level):
            """Get all log messages of a specific level."""
            return [record.getMessage() for record in self.caplog.records 
                   if record.levelname == level]
    
    return LoggingHelper(caplog)