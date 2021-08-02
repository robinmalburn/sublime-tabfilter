# Copyright (c) 2013 - 2021 Robin Malburn
# See the file license.txt for copying permission.

from unittest import TestCase
from unittest.mock import patch
from typing import List, Tuple, Optional
try:
    import entities
except ImportError:
    # If we're running these tests in UnitTesting, then we need to use
    # The package name - Tab Filter - so let's grab import lib and try again.
    from importlib import import_module
    entities = import_module(".entities", "Tab Filter")

Tab = entities.Tab


class TabTestCase(TestCase):
    """Tests the tab entity works as expected."""

    @patch("os.path.dirname")
    def test_initialisation(self, mock_dirname) -> None:
        """Test initialising a Tab."""
        dirname: str = "/stub/"
        mock_dirname.return_value = dirname

        dataset: Tuple[Tuple[str, bool, Optional[str]], ...] = (
            ("foo", False, None),
            ("bar", True, dirname)
        )

        for (name, is_file, path) in dataset:
            with self.subTest(name=name, is_file=is_file, path=path):
                entity: Tab = Tab(name, is_file)
                self.assertEquals(name, entity.name)
                self.assertEquals(bool(is_file), entity.is_file)
                self.assertEquals(path, entity.path)

    def test_add_caption(self) -> None:
        """Test adding captions to a Tab."""
        entity: Tab = Tab("foo")

        # Ensure we start with no captions.
        self.assertListEqual([], entity.captions)

        entity.add_caption("bar")

        # Ensure a regular caption can be added.
        self.assertListEqual(["bar"], entity.captions)

        entity.add_caption("baz")

        # Ensure additional captions can be added.
        self.assertListEqual(["bar", "baz"], entity.captions)

        entity = Tab("foo")

        entity.add_caption(123)  # type: ignore

        # Ensure captions are stringified
        self.assertListEqual(["123"], entity.captions)

    def test_get_caption(self) -> None:
        """Test getting captions for a Tab."""
        entity: Tab = Tab("foo")

        entity.add_caption("bar")

        self.assertEquals("bar", entity.get_caption())

        entity.add_caption("baz")

        self.assertEquals("bar, baz", entity.get_caption())

    def test_get_details_caption_configuration(self) -> None:
        """Test getting details for a Tab with various caption settings."""
        entity: Tab = Tab("foo", False)

        details: List[str] = entity.get_details(
            prefix_trim=0,
            include_path=False,
            show_captions=False
        )

        # Without captions at all.
        self.assertListEqual(["foo", "foo"], details)

        details = entity.get_details(
            prefix_trim=0,
            include_path=False,
            show_captions=True
        )

        # With empty captions.
        self.assertListEqual(["foo", "foo", ""], details)

        entity.add_caption("bar")

        # With varying captions.
        details = entity.get_details(
            prefix_trim=0,
            include_path=False,
            show_captions=True
        )

        self.assertListEqual(["foo", "foo", "bar"], details)

        entity.add_caption("baz")

        details = entity.get_details(
            prefix_trim=0,
            include_path=False,
            show_captions=True
        )

        self.assertListEqual(["foo", "foo", "bar, baz"], details)

    def test_get_details_prefix_trimming(self):
        """Test getting details for a Tab with prefix trimming (files only)."""
        path: str = "/tmp/foo/bar/baz"
        entity: Tab = Tab(path, True)

        for i in range(0, 4):
            with self.subTest(prefix_trim=i):
                details: List[str] = entity.get_details(
                    prefix_trim=i,
                    include_path=False,
                    show_captions=False
                )
                expected: str = path[i:]
                if i > 0:
                    expected = "...{}".format(path[i:])

                self.assertListEqual(["baz", expected], details)

    def test_get_details_include_path(self):
        """Test getting details for a Tab with path included (files only)."""
        path: str = "/tmp/foo/bar/baz"
        entity: Tab = Tab(path, True)

        for i in range(0, 4):
            with self.subTest(prefix_trim=i):
                details: List[str] = entity.get_details(
                    prefix_trim=i,
                    include_path=True,
                    show_captions=False
                )
                expected: str = path[i:]
                if i > 0:
                    expected = "...{}".format(path[i:])

                self.assertListEqual([expected, expected], details)
