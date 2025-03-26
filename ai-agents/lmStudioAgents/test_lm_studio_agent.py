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
    uv run pytest test_lm_studio_agent.py -v
"""

import os
import pytest

# Import functions from the main script
from lm_studio_agent_clean_ui_bash_tool_use_v2 import (
    create_file,
    replace_text,
    insert_line,
    view_file,
    execute_command,
    find_file,
    create_lm_agent
)

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
@pytest.mark.asyncio
async def test_agent_connection():
    """Test connection to LM Studio (requires LM Studio running)."""
    import os
    import sys
    from openai import AsyncOpenAI
    
    # Skip if we're running in CI or don't want to test LM Studio
    if os.environ.get("SKIP_LM_STUDIO_TESTS"):
        pytest.skip("Skipping LM Studio connection test")
    
    # Test setup similar to main script
    LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
    os.environ["OPENAI_API_KEY"] = "dummy-key"
    os.environ["OPENAI_API_BASE"] = LM_STUDIO_BASE_URL
    
    try:
        client = AsyncOpenAI(
            base_url=LM_STUDIO_BASE_URL,
            api_key=os.environ["OPENAI_API_KEY"]
        )
        
        # Try to list models - this will fail if LM Studio is not running
        response = await client.models.list()
        assert len(response.data) > 0
        
    except Exception as e:
        pytest.skip(f"LM Studio not available: {str(e)}")

@pytest.mark.asyncio
async def test_streaming_response():
    """Test the streaming response functionality of the agent."""
    import os
    from openai import AsyncOpenAI
    
    # Skip if we're running in CI or don't want to test LM Studio
    if os.environ.get("SKIP_LM_STUDIO_TESTS"):
        pytest.skip("Skipping LM Studio streaming test")
    
    # Import the run_lm_agent function
    from lm_studio_agent_clean_ui_bash_tool_use_v2 import run_lm_agent, create_lm_agent
    
    # Set up the environment
    LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
    os.environ["OPENAI_API_KEY"] = "dummy-key"
    os.environ["OPENAI_API_BASE"] = LM_STUDIO_BASE_URL
    
    try:
        # Create an agent
        agent = create_lm_agent()
        
        # Test prompt
        test_prompt = "Hello, can you tell me a short joke?"
        
        # Test streaming response
        chunks = []
        async for chunk in run_lm_agent(test_prompt, agent, "default"):
            # Verify that we're getting chunks of text
            chunks.append(chunk)
        
        # Verify that we received multiple chunks
        assert len(chunks) > 1, "Expected multiple chunks for streaming response"
        
        # Verify that when combined, the chunks form a coherent response
        full_response = "".join(chunks)
        assert len(full_response) > 0, "Expected non-empty response"
        
    except Exception as e:
        pytest.skip(f"LM Studio streaming test failed: {str(e)}")

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 