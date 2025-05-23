import unittest
from unittest.mock import MagicMock
import numpy as np
from stl import mesh
from src.core.core import Object3D, Scene
import unittest
from unittest.mock import MagicMock


class TestObject3D(unittest.TestCase):
    def test_transform_sequence(self):
        # Create a dummy mesh
        dummy_vectors = np.zeros((1, 3, 3))
        dummy_mesh = mesh.Mesh(np.zeros(1, dtype=mesh.Mesh.dtype))
        dummy_mesh.vectors = dummy_vectors

        # Create mock transformation functions
        mock_flexibility = MagicMock(return_value=dummy_vectors.reshape(-1, 3))
        mock_rotation = MagicMock(return_value=dummy_vectors.reshape(-1, 3))
        mock_translation = MagicMock(return_value=dummy_vectors.reshape(-1, 3))

        # Instantiate Object3D with mocks
        obj = Object3D(
            name="TestObject",
            stl_mesh=dummy_mesh,
            translation_transform=mock_translation,
            rotation_transform=mock_rotation,
            flexibility_transform=mock_flexibility
        )

        position = np.array([1, 2, 3])
        angles = np.array([0.1, 0.2, 0.3])
        t = 0.5

        # Call the transform method
        transformed_mesh = obj.transform(position, angles, t)

        # Assertions to ensure each transform is called correctly
        mock_flexibility.assert_called_once()
        mock_rotation.assert_called_once()
        mock_translation.assert_called_once()


class TestScene(unittest.TestCase):
    def test_transform_all_sprites(self):
        # Create mock Sprites
        mock_sprite1 = MagicMock()
        mock_sprite1.transform.return_value = "mesh1"
        mock_sprite2 = MagicMock()
        mock_sprite2.transform.return_value = "mesh2"

        scene = Scene(objects=[mock_sprite1, mock_sprite2])

        t = 0
        result = scene.transform(t)

        # Assertions
        mock_sprite1.transform.assert_called_once_with(t)
        mock_sprite2.transform.assert_called_once_with(t)
        self.assertEqual(result, ["mesh1", "mesh2"])
