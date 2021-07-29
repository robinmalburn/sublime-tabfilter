from unittest import TestCase
from unittest.mock import patch
from importlib import import_module
tab = import_module(".tab", "Tab Filter")
	
class TabTestCase(TestCase):
	"""Tests the tab entity works as expected."""

	@patch("os.path.dirname")
	def test_initialisation(self, mock_dirname):
		"""Test initialising a Tab."""
		path = "/stub/"
		mock_dirname.return_value = path
		dataset = (
			("foo", False, None),
			("bar", True, path)
		)

		for (name, is_file, path) in dataset:
			with self.subTest(name=name, is_file=is_file):
				entity = tab.Tab(name, is_file)
				self.assertEquals(name, entity.name)
				self.assertEquals(bool(is_file), entity.is_file)
				self.assertEquals(path, entity.path)

	def test_add_caption(self):
		"""Test the ability to add captions to a Tab."""
		entity = tab.Tab("foo")

		# Ensure we start with no captions.
		self.assertListEqual([], entity.captions)

		entity.add_caption("bar")

		# Ensure a regular caption can be added.
		self.assertListEqual(['bar'], entity.captions)

		entity.add_caption('baz')

		# Ensure additional captions can be added.
		self.assertListEqual(["bar", "baz"], entity.captions)

		entity = tab.Tab("foo")

		entity.add_caption(123)

		# Ensure captions are stringified
		self.assertListEqual(["123"], entity.captions)

	def test_get_caption(self):
		"""Test the ability to get the captions for a Tab."""
		entity = tab.Tab("foo")

		entity.add_caption("bar")

		self.assertEquals("bar", entity.get_caption())

		entity.add_caption("baz")

		self.assertEquals("bar, baz", entity.get_caption())

	def test_get_details_caption_configuration(self):
		"""Test the ability to get details for a Tab with various caption configurations."""
		entity = tab.Tab("foo", False)

		details = entity.get_details(prefix_trim=0, include_path=False, show_captions=False)
		
		# Without captions at all.
		self.assertListEqual(["foo", "foo"], details)

		details = entity.get_details(prefix_trim=0, include_path=False, show_captions=True)

		# With empty captions.
		self.assertListEqual(["foo", "foo", ""], details)

		entity.add_caption("bar")

		# With varying captions.
		details = entity.get_details(prefix_trim=0, include_path=False, show_captions=True)

		self.assertListEqual(["foo", "foo", "bar"], details)

		entity.add_caption("baz")

		details = entity.get_details(prefix_trim=0, include_path=False, show_captions=True)

		self.assertListEqual(["foo", "foo", "bar, baz"], details)

	def test_get_details_prefix_trimming(self):
		"""Test the ability to get details for a Tab with prefix trimming (files only)."""
		path = "/tmp/foo/bar/baz"
		entity = tab.Tab(path, True)

		for i in range(0, 4):
			with self.subTest(prefix_trim=i):
				details = entity.get_details(prefix_trim=i, include_path=False, show_captions=False)
				expected = path[i:]
				if i > 0:
					expected = "...{}".format(path[i:])


				# No prefix trimmed at all.
				self.assertListEqual(["baz", expected], details)

	def test_get_details_include_path(self):
		"""Test the ability to get details for a Tab with path included (files only)."""
		path = "/tmp/foo/bar/baz"
		entity = tab.Tab(path, True)

		for i in range(0, 4):
			with self.subTest(prefix_trim=i):
				details = entity.get_details(prefix_trim=i, include_path=True, show_captions=False)
				expected = path[i:]
				if i > 0:
					expected = "...{}".format(path[i:])

				# No prefix trimmed at all.
				self.assertListEqual([expected, expected], details)