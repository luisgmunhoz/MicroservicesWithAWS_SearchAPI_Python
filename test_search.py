from unittest.mock import MagicMock, patch

from fastapi import HTTPException
import pytest
import pybreaker
import app
import json


@patch("app.get_es")
@patch("app.search_hotels")
def test_search_success(mock_search_hotels, mock_get_es):
    # Arrange
    mock_es_instance = MagicMock()
    mock_get_es.return_value = mock_es_instance
    mock_search_hotels.return_value = [{"hotel": "test"}]

    # Act
    response = app.search(city="test_city", rating=1, es=mock_es_instance)

    # Assert
    assert response.status_code == 200
    assert json.loads(response.body) == [{"hotel": "test"}]
    mock_search_hotels.assert_called_once_with("test_city", 1, mock_es_instance)


@patch("app.get_es")
@patch("app.search_hotels")
def test_search_failure(mock_search_hotels, mock_get_es):
    # Arrange
    mock_es_instance = MagicMock()
    mock_get_es.return_value = mock_es_instance
    mock_search_hotels.side_effect = pybreaker.CircuitBreakerError

    # Act
    with pytest.raises(HTTPException) as e:
        app.search(city="test_city", rating=1, es=mock_es_instance)

    # Assert
    assert e.value.status_code == 503
    assert str(e.value.detail) == "Service temporarily unavailable"
    mock_search_hotels.assert_called_once_with("test_city", 1, mock_es_instance)
