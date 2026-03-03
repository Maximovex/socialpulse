from collector.hn_client import top_ids, get_story
from unittest.mock import patch, Mock


def test_top_ids():
    assert isinstance(top_ids(1), list)
    assert len(top_ids(5)) == 5
    assert all([isinstance(elem, int) for elem in top_ids(5)])


def test_top_ids_mocked():
    fake_response = Mock()
    fake_response.json.return_value = [1, 2, 3, 4, 5]

    with patch("collector.hn_client.requests.get", return_value=fake_response):
        result = top_ids(3)
        assert result == [1, 2, 3]
        assert len(result) == 3


def test_get_story():
    fake_response = Mock()
    fake_response.json.return_value = {"title": "Test", "score": 10}
    with patch("collector.hn_client.requests.get", return_value=fake_response):
        result = get_story(3)
        assert result == {"title": "Test", "score": 10}

def test_broken():
    assert 1==2