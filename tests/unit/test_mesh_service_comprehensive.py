"""
Unit tests for MeSH Service.

Tests MeSH vocabulary mapping, singleton pattern, lazy loading,
and graceful degradation when MeSH data unavailable.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.services.mesh_service import (
    _load_mesh_index_from_env,
    get_mesh_index,
    map_to_mesh,
)


class TestMeshIndexLoading:
    """Test MeSH index loading and initialization."""

    @patch("src.services.mesh_service.os.getenv")
    def test_load_mesh_index_from_env_no_path_set(self, mock_getenv):
        """Test that None is returned when MESH_JSON_PATH not set."""
        mock_getenv.return_value = None
        result = _load_mesh_index_from_env()
        assert result is None

    @patch("src.services.mesh_service.os.getenv")
    @patch("src.services.mesh_service.Path")
    def test_load_mesh_index_from_env_file_not_exists(self, mock_path, mock_getenv):
        """Test that None is returned when MeSH file doesn't exist."""
        mock_getenv.return_value = "/path/to/mesh.json"
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        result = _load_mesh_index_from_env()
        assert result is None

    @patch("src.services.mesh_service.os.getenv")
    @patch("src.services.mesh_service.Path")
    @patch("src.services.mesh_service.MeshIndex")
    def test_load_mesh_index_from_env_success(
        self, mock_mesh_index, mock_path, mock_getenv
    ):
        """Test successful MeSH index loading."""
        mock_getenv.return_value = "/path/to/mesh.json"
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_index = MagicMock()
        mock_mesh_index.from_json_file.return_value = mock_index

        result = _load_mesh_index_from_env()
        assert result == mock_index
        mock_mesh_index.from_json_file.assert_called_once()

    @patch("src.services.mesh_service.os.getenv")
    @patch("src.services.mesh_service.Path")
    @patch("src.services.mesh_service.MeshIndex")
    def test_load_mesh_index_handles_exceptions(
        self, mock_mesh_index, mock_path, mock_getenv
    ):
        """Test that exceptions during loading are caught."""
        mock_getenv.return_value = "/path/to/mesh.json"
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        mock_mesh_index.from_json_file.side_effect = Exception("Parse error")

        result = _load_mesh_index_from_env()
        assert result is None


class TestGetMeshIndex:
    """Test MeSH index singleton pattern."""

    def test_get_mesh_index_returns_none_when_unavailable(self):
        """Test that get_mesh_index returns None when MeSH unavailable."""
        # Reset global state
        import src.services.mesh_service as mesh_module

        mesh_module._mesh_index = None

        with patch("src.services.mesh_service._load_mesh_index_from_env") as mock_load:
            mock_load.return_value = None
            result = get_mesh_index()
            assert result is None

    def test_get_mesh_index_loads_once(self):
        """Test that MeSH index is loaded only once (singleton)."""
        import src.services.mesh_service as mesh_module

        mesh_module._mesh_index = None

        mock_index = MagicMock()
        with patch("src.services.mesh_service._load_mesh_index_from_env") as mock_load:
            mock_load.return_value = mock_index

            # First call loads
            result1 = get_mesh_index()
            assert result1 == mock_index
            assert mock_load.call_count == 1

            # Second call uses cached
            result2 = get_mesh_index()
            assert result2 == mock_index
            assert mock_load.call_count == 1  # Not called again

    def test_get_mesh_index_returns_cached_instance(self):
        """Test that cached instance is returned on subsequent calls."""
        import src.services.mesh_service as mesh_module

        mock_index = MagicMock()
        mesh_module._mesh_index = mock_index

        result = get_mesh_index()
        assert result == mock_index


class TestMapToMesh:
    """Test MeSH term mapping functionality."""

    def test_map_to_mesh_returns_empty_when_no_index(self):
        """Test that empty list is returned when MeSH index unavailable."""
        with patch("src.services.mesh_service.get_mesh_index") as mock_get:
            mock_get.return_value = None
            result = map_to_mesh("diabetes")
            assert result == []

    def test_map_to_mesh_calls_index_map(self):
        """Test that map_to_mesh calls index.map() with correct parameters."""
        mock_index = MagicMock()
        mock_index.map.return_value = [
            {"term": "Diabetes Mellitus", "mesh_id": "D003920", "score": 0.95}
        ]

        with patch("src.services.mesh_service.get_mesh_index") as mock_get:
            mock_get.return_value = mock_index

            result = map_to_mesh("diabetes", top_k=5)
            mock_index.map.assert_called_once_with("diabetes", top_k=5)
            assert len(result) == 1

    def test_map_to_mesh_returns_results(self):
        """Test that map_to_mesh returns MeSH mapping results."""
        mock_index = MagicMock()
        expected_results = [
            {"term": "Diabetes Mellitus", "mesh_id": "D003920", "score": 0.95},
            {
                "term": "Diabetes Mellitus, Type 2",
                "mesh_id": "D003924",
                "score": 0.88,
            },
        ]
        mock_index.map.return_value = expected_results

        with patch("src.services.mesh_service.get_mesh_index") as mock_get:
            mock_get.return_value = mock_index

            result = map_to_mesh("diabetes")
            assert result == expected_results

    def test_map_to_mesh_default_top_k(self):
        """Test that map_to_mesh uses default top_k=5."""
        mock_index = MagicMock()
        mock_index.map.return_value = []

        with patch("src.services.mesh_service.get_mesh_index") as mock_get:
            mock_get.return_value = mock_index

            map_to_mesh("test")
            mock_index.map.assert_called_with("test", top_k=5)

    def test_map_to_mesh_custom_top_k(self):
        """Test that map_to_mesh respects custom top_k parameter."""
        mock_index = MagicMock()
        mock_index.map.return_value = []

        with patch("src.services.mesh_service.get_mesh_index") as mock_get:
            mock_get.return_value = mock_index

            map_to_mesh("test", top_k=10)
            mock_index.map.assert_called_with("test", top_k=10)


class TestGracefulDegradation:
    """Test graceful degradation when MeSH unavailable."""

    def test_map_to_mesh_handles_none_index(self):
        """Test that map_to_mesh handles None index gracefully."""
        with patch("src.services.mesh_service.get_mesh_index") as mock_get:
            mock_get.return_value = None

            result = map_to_mesh("heart failure")
            assert result == []
            assert isinstance(result, list)

    def test_map_to_mesh_empty_term(self):
        """Test mapping with empty term."""
        mock_index = MagicMock()
        mock_index.map.return_value = []

        with patch("src.services.mesh_service.get_mesh_index") as mock_get:
            mock_get.return_value = mock_index

            result = map_to_mesh("")
            assert result == []

    def test_multiple_calls_with_unavailable_mesh(self):
        """Test multiple calls when MeSH consistently unavailable."""
        with patch("src.services.mesh_service.get_mesh_index") as mock_get:
            mock_get.return_value = None

            result1 = map_to_mesh("diabetes")
            result2 = map_to_mesh("hypertension")
            result3 = map_to_mesh("asthma")

            assert result1 == []
            assert result2 == []
            assert result3 == []


class TestMeshIntegration:
    """Integration tests for MeSH service."""

    def test_full_mesh_workflow(self):
        """Test complete MeSH mapping workflow."""
        mock_index = MagicMock()
        mock_index.map.return_value = [
            {
                "term": "Hypertension",
                "mesh_id": "D006973",
                "score": 0.92,
            }
        ]

        import src.services.mesh_service as mesh_module

        mesh_module._mesh_index = None

        with patch("src.services.mesh_service._load_mesh_index_from_env") as mock_load:
            mock_load.return_value = mock_index

            # First get_mesh_index loads
            index = get_mesh_index()
            assert index == mock_index

            # map_to_mesh uses loaded index
            results = map_to_mesh("high blood pressure")
            assert len(results) == 1
            assert results[0]["term"] == "Hypertension"

    def test_mesh_service_independence(self):
        """Test that MeSH service calls are independent."""
        mock_index = MagicMock()

        def side_effect_map(term, top_k):
            if term == "diabetes":
                return [{"term": "Diabetes Mellitus", "mesh_id": "D003920", "score": 1}]
            elif term == "asthma":
                return [{"term": "Asthma", "mesh_id": "D001249", "score": 1}]
            return []

        mock_index.map.side_effect = side_effect_map

        with patch("src.services.mesh_service.get_mesh_index") as mock_get:
            mock_get.return_value = mock_index

            result1 = map_to_mesh("diabetes")
            result2 = map_to_mesh("asthma")

            assert result1[0]["term"] == "Diabetes Mellitus"
            assert result2[0]["term"] == "Asthma"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_map_to_mesh_with_zero_top_k(self):
        """Test mapping with top_k=0."""
        mock_index = MagicMock()
        mock_index.map.return_value = []

        with patch("src.services.mesh_service.get_mesh_index") as mock_get:
            mock_get.return_value = mock_index

            result = map_to_mesh("test", top_k=0)
            assert result == []
            mock_index.map.assert_called_with("test", top_k=0)

    def test_map_to_mesh_with_large_top_k(self):
        """Test mapping with very large top_k."""
        mock_index = MagicMock()
        mock_index.map.return_value = []

        with patch("src.services.mesh_service.get_mesh_index") as mock_get:
            mock_get.return_value = mock_index

            map_to_mesh("test", top_k=1000)
            mock_index.map.assert_called_with("test", top_k=1000)

    def test_map_to_mesh_with_special_characters(self):
        """Test mapping with special characters in term."""
        mock_index = MagicMock()
        mock_index.map.return_value = []

        with patch("src.services.mesh_service.get_mesh_index") as mock_get:
            mock_get.return_value = mock_index

            map_to_mesh("COVID-19 & SARS-CoV-2")
            assert mock_index.map.called

    def test_map_to_mesh_with_unicode(self):
        """Test mapping with Unicode characters."""
        mock_index = MagicMock()
        mock_index.map.return_value = []

        with patch("src.services.mesh_service.get_mesh_index") as mock_get:
            mock_get.return_value = mock_index

            map_to_mesh("café au lait spots")
            assert mock_index.map.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
