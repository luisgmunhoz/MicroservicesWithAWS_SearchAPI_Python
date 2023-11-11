from unittest.mock import patch, MagicMock
from elasticsearch_dsl import Search, Q
import app


@patch.object(Search, "execute")
@patch.object(Search, "query")
@patch("app.get_es")
def test_search_hotels_no_city(mock_get_es, mock_query, mock_execute):
    # Arrange
    mock_es_instance = MagicMock()
    mock_get_es.return_value = mock_es_instance
    mock_query.return_value = Search()
    mock_execute.return_value.hits.hits = [
        {"_source": MagicMock(to_dict=lambda: {"hotel": "test"})}
    ]

    # Act
    result = app.search_hotels(None, 1, mock_es_instance)

    # Assert
    mock_query.assert_called_once_with(Q("match_all") & Q("range", Rating={"gte": 1}))
    assert result == [{"hotel": "test"}]


@patch.object(Search, "execute")
@patch.object(Search, "query")
@patch("app.get_es")
def test_search_hotels_with_city(mock_get_es, mock_query, mock_execute):
    # Arrange
    mock_es_instance = MagicMock()
    mock_get_es.return_value = mock_es_instance
    mock_query.return_value = Search()
    mock_execute.return_value.hits.hits = [
        {"_source": MagicMock(to_dict=lambda: {"hotel": "test"})}
    ]

    # Act
    result = app.search_hotels("test_city", 1, mock_es_instance)

    # Assert
    mock_query.assert_called_once_with(
        Q("prefix", CityName={"value": "test_city".lower()})
        & Q("range", Rating={"gte": 1})
    )
    assert result == [{"hotel": "test"}]


@patch.object(Search, "execute")
@patch.object(Search, "query")
@patch("app.get_es")
def test_search_hotels_exception(mock_get_es, mock_query, mock_execute):
    # Arrange
    mock_es_instance = MagicMock()
    mock_get_es.return_value = mock_es_instance
    mock_query.return_value = Search()
    mock_execute.side_effect = Exception

    # Act
    result = app.search_hotels("test_city", 1, mock_es_instance)

    # Assert
    assert result == []
