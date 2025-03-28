#!/usr/bin/env -S uv run --script

# /// script
# dependencies = [
#   "openai-agents>=0.0.6",
#   "rich>=13.9.4",
#   "openai>=1.68.2",
#   "pytest>=8.3.5",
#   "pytest-asyncio>=0.25.3",
# ]
# ///

"""
Tests for LM Studio Local Agent

This file contains tests for the LM Studio agent functionality.
It uses pytest for testing various aspects of the agent's behavior.

Run with:
    uv run test_lm_studio_agent.py -v
"""

import os
import pytest
import glob
import asyncio

LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
LM_STUDIO_API_KEY = "dummy-key"  # LM Studio doesn't need a real API key

# Import functions from the main script
from lm_studio_agent_clean_ui_bash_tool_use_vision_v4 import (
    create_file,
    replace_text,
    insert_line,
    view_file,
    execute_command,
    find_file,
    describe_image,
    create_lm_agent,
    run_lm_agent
)

# Define a fixture for LM Studio connectivity
@pytest.fixture(scope="session")
def lm_studio_client():
    """Create a client for LM Studio and verify connectivity.
    
    This fixture will be used by tests that require LM Studio to be running.
    Tests will be skipped if LM Studio is not available or if SKIP_LM_STUDIO_TESTS is set.
    """
    # Skip if we're running in CI or don't want to test LM Studio
    if os.environ.get("SKIP_LM_STUDIO_TESTS"):
        pytest.skip("Skipping LM Studio tests due to SKIP_LM_STUDIO_TESTS environment variable")
        
    # Try to connect to LM Studio    
    try:
        # Quick check if LM Studio is available
        from openai import OpenAI
        client = OpenAI(
            base_url=LM_STUDIO_BASE_URL,
            api_key=LM_STUDIO_API_KEY
        )
        
        # Check if LM Studio is available
        response = client.models.list()
        if not response.data:
            pytest.skip("No models available in LM Studio")
            
        # Return the client and model info for tests to use
        return {"client": client, "models": response.data}
    except Exception as e:
        pytest.skip(f"LM Studio connection failed: {str(e)}")

# Test helper functions
def test_find_file():
    """Test that find_file correctly handles various inputs."""
    # Create a temporary file for testing
    test_file = "test_find_file_temp.txt"
    with open(test_file, 'w') as f:
        f.write("Test content")
    
    try:
        # Test with exact file path
        result = find_file(test_file)
        assert result["status"] == "found"
        assert result["file_path"] == test_file
        
        # Test with non-existent file
        result = find_file("nonexistent_file.txt")
        assert result["status"] == "not_found"
        
        # Test with partial file name
        result = find_file("test_find_file")
        assert result["status"] == "suggestions" or result["status"] == "found"
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)

def test_create_file():
    """Test creating a file."""
    test_file = "test_create_temp.txt"
    content = "Test content for creation"
    
    try:
        # Test creating a file
        result = create_file(test_file, content)
        assert result["status"] == "success"
        
        # Verify the file exists and has correct content
        assert os.path.exists(test_file)
        with open(test_file, 'r') as f:
            assert f.read() == content
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)

def test_view_file():
    """Test viewing a file."""
    test_file = "test_view_temp.txt"
    content = "Test content for viewing"
    
    try:
        # Create a test file
        with open(test_file, 'w') as f:
            f.write(content)
        
        # Test viewing the file
        result = view_file(test_file)
        assert result["status"] == "success"
        assert result["content"] == content
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)

def test_replace_text():
    """Test replacing text in a file."""
    test_file = "test_replace_temp.txt"
    original_content = "This is a test for replacing text."
    search_text = "replacing"
    replacement_text = "modifying"
    
    try:
        # Create a test file
        with open(test_file, 'w') as f:
            f.write(original_content)
        
        # Test replacing text
        result = replace_text(test_file, search_text, replacement_text)
        assert result["status"] == "success"
        
        # Verify the content was replaced
        with open(test_file, 'r') as f:
            assert f.read() == original_content.replace(search_text, replacement_text)
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)

def test_insert_line():
    """Test inserting a line in a file."""
    test_file = "test_insert_temp.txt"
    original_content = "Line 1\nLine 3"
    insert_content = "Line 2"
    line_number = 2
    
    try:
        # Create a test file
        with open(test_file, 'w') as f:
            f.write(original_content)
        
        # Test inserting a line
        result = insert_line(test_file, line_number, insert_content)
        assert result["status"] == "success"
        
        # Verify the line was inserted
        with open(test_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 3
            assert lines[1].strip() == insert_content
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)

def test_execute_command():
    """Test executing a command."""
    # Test a simple command that should work on all platforms
    command = "echo hello"
    
    result = execute_command(command)
    assert result["status"] == "success"
    assert "hello" in result["stdout"]

def test_create_lm_agent():
    """Test creating an LM Studio agent."""
    agent = create_lm_agent()
    assert agent.name == "LocalAssistant"
    assert len(agent.instructions) > 0
    assert agent.model == "default"

# Additional tests that require LM Studio running
def test_agent_connection(lm_studio_client):
    """Test connection to LM Studio (requires LM Studio running)."""
    # Since we're using the fixture, we can assume LM Studio is available
    # and skip the connection check since it was done in the fixture
    
    # Create the agent
    agent = create_lm_agent()
    
    # Verify the agent was created successfully
    assert agent is not None
    assert agent.name == "LocalAssistant"
    
    # Verify we have a running model
    assert len(lm_studio_client["models"]) > 0
    model = lm_studio_client["models"][0]
    assert model.id is not None
    print(f"Connected to LM Studio with model: {model.id}")

@pytest.mark.asyncio
async def test_streaming_response(lm_studio_client):
    """Test the streaming response functionality of the agent."""
    # Create the agent
    agent = create_lm_agent()
    
    # Test prompt
    prompt = "Say hello in one short sentence."
    
    # Collect the response
    response_text = ""
    async for content in run_lm_agent(prompt, agent, lm_studio_client["models"][0].id):
        response_text += content
        
    # Verify we got a response
    assert len(response_text) > 0
    print(f"Streaming response: {response_text}")

def test_describe_image(lm_studio_client):
    """Test the image description capability."""
    # Find any image files in the current directory
    image_files = glob.glob("*.jpeg") + glob.glob("*.png")
    
    if not image_files:
        pytest.skip("No compatible image files found in the current directory. Please add an .jpeg or .png image file to test the image description capability.")
    
    # Use the first image file found
    test_image = image_files[0]
    print(f"Testing image description with: {test_image}")
    
    # Test describing the image
    result = describe_image(test_image)
    
    # Print the result for debugging
    print(f"Result: {result}")
    
    # Check if LM Studio returned an error related to vision capabilities
    if result["status"] == "error" and ("llama_decode" in result.get("message", "") or 
                                        "vision" in result.get("message", "").lower()):
        pytest.skip(f"LM Studio model may not support vision capabilities: {result['message']}")
    
    # If not a vision capability error, then we should have a success
    assert result["status"] == "success", f"Expected success but got: {result}"
    assert "description" in result
    assert len(result["description"]) > 0
    
    print(f"Image description: {result['description'][:100]}...")  # Print first 100 chars of description

if __name__ == "__main__":
    pytest.main(["-v", __file__])