from unittest.mock import patch, MagicMock
import app


@patch("app.Elasticsearch")
def test_get_es(mock_es):
    # Arrange
    mock_es_instance = MagicMock()
    mock_es.return_value = mock_es_instance

    expected_host = [app.HOST]
    expected_http_auth = (app.USERNAME, app.PASSWORD)

    # Act
    result = app.get_es()

    # Assert
    mock_es.assert_called_once_with(expected_host, http_auth=expected_http_auth)
    assert result == mock_es_instance
