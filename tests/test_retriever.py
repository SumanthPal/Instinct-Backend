import pytest
from unittest.mock import patch, MagicMock
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.data_retriever import DataRetriever  # Replace with the actual module name

# Fixture for DataRetriever instance
@pytest.fixture
def data_retriever():
    return DataRetriever()

# Test for get_user_dir method
def test_get_user_dir(data_retriever):
    # Test the user directory construction
    expected_path = os.path.join(os.path.dirname(__file__), '..', 'data')
    assert data_retriever.get_user_dir().endswith('../data')

# Test for club_data_exists method
@patch('os.path.exists')
def test_club_data_exists(mock_exists, data_retriever):
    # Case where club directory and posts directory exist
    mock_exists.side_effect = lambda path: path.endswith("posts") or path.endswith("club_name")
    assert data_retriever.club_data_exists("club_name") is True

    # Case where one or both directories do not exist
    mock_exists.side_effect = lambda path: False
    assert data_retriever.club_data_exists("club_name") is False

# Test for fetch_club_info method
@patch('os.path.exists')
@patch('builtins.open', new_callable=MagicMock)
def test_fetch_club_info(mock_open, mock_exists, data_retriever):
    # Mocking os.path.exists to return True for valid directories
    mock_exists.side_effect = lambda path: path.endswith("club_name") or path.endswith("posts")

    # Mocking the file content of club_info.json
    mock_open.return_value.__enter__.return_value.read.return_value = '{"club_name": "Test Club"}'
    
    # Test valid scenario: club info should be returned correctly
    club_info = data_retriever.fetch_club_info("club_name")
    assert club_info == {"club_name": "Test Club"}
    
    # Test invalid scenario: FileNotFoundError should be raised
    mock_exists.side_effect = lambda path: False
    with pytest.raises(FileNotFoundError):
        data_retriever.fetch_club_info("club_name")

# Test for retrieve_club_list method
@patch('builtins.open', new_callable=MagicMock)
def test_retrieve_club_list(mock_open, data_retriever):
    # Mocking club list data
    mock_open.return_value.__enter__.return_value.read.return_value = '[{"club_name": "Test Club"}]'
    
    # Test: should return the club list
    club_list = data_retriever.retrieve_club_list()
    assert club_list == [{"club_name": "Test Club"}]

# Test for modify_club_list method
@patch('builtins.open', new_callable=MagicMock)
def test_modify_club_list(mock_open, data_retriever):
    # Mocking open to write to the clubs.json file
    mock_open.return_value.__enter__.return_value.write = MagicMock()

    club_list = [{'testclub': {"club_name": "Test Club", "genre": "Test Genre"}}]
    
    # Test modifying club list
    data_retriever.modify_club_list(club_list)
    mock_open.return_value.__enter__.return_value.write.assert_any_call({'testclub': {"club_name": "Test Club", "genre": "Test Genre"}})

# Test for fetch_club_posts method
@patch('os.path.exists')
@patch('os.listdir')
@patch('builtins.open', new_callable=MagicMock)
def test_fetch_club_posts(mock_open, mock_listdir, mock_exists, data_retriever):
    # Mocking the existence of club directories
    mock_exists.side_effect = lambda path: path.endswith("club_name") or path.endswith("posts")

    # Mocking posts directory to return post files
    mock_listdir.return_value = ["post1.json", "post2.json"]
    
    # Mocking post file content
    mock_open.return_value.__enter__.return_value.read.return_value = '{"post_title": "Test Post"}'

    # Test valid scenario: should return a list of posts
    posts = data_retriever.fetch_club_posts("club_name")
    assert posts == [{"post_title": "Test Post"}, {"post_title": "Test Post"}]

    # Test: if no posts found, FileNotFoundError should be raised
    mock_listdir.return_value = []
    with pytest.raises(FileNotFoundError):
        data_retriever.fetch_club_posts("club_name")

    # Test: if club directory does not exist, FileNotFoundError should be raised
    mock_exists.side_effect = lambda path: False
    with pytest.raises(FileNotFoundError):
        data_retriever.fetch_club_posts("club_name")
