"""Details."""
import xml.etree.ElementTree as etree
from .block import Block, type_boolean, type_html_identifier
from ..blocks import BlocksExtension
import re

RE_SEP = re.compile(r'[_-]+')
RE_VALID_NAME = re.compile(r'[\w-]+')


class Details(Block):
    """
    Details.

    Arguments (1 optional):
    - A summary.

    Options:
    - `open` (boolean): force the details block to be in an open state opposed to collapsed.
    - `type` (string): Attach a single special class for styling purposes. If more are needed,
      use the built-in `attributes` options to apply as many classes as desired.

    Content:
    Detail body.
    """

    NAME = 'details'

    ARGUMENT = None
    OPTIONS = {
        'open': [False, type_boolean],
        'type': ['', type_html_identifier]
    }

    CONFIG = {
        "types": []
    }

    def on_validate(self, parent):
        """Handle on validate event."""

        if self.NAME != 'details':
            self.options['type'] = self.NAME
        return True

    def on_create(self, parent):
        """Create the element."""

        # Is it open?
        attributes = {}
        if self.options['open']:
            attributes['open'] = 'open'

        # Set classes
        dtype = self.options['type']
        if dtype:
            attributes['class'] = dtype

        # Create Detail element
        el = etree.SubElement(parent, 'details', attributes)

        # Create the summary
        if not self.argument:
            if not dtype:
                summary = None
            else:
                summary = dtype.capitalize()
        else:
            summary = self.argument

        # Create the summary
        if summary is not None:
            s = etree.SubElement(el, 'summary')
            s.text = summary

        return el


class DetailsExtension(BlocksExtension):
    """Admonition Blocks Extension."""

    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.config = {
            "types": [
                [],
                "Generate Admonition block extensions for the given types."
            ]
        }

        super().__init__(*args, **kwargs)

    def extendMarkdownBlocks(self, md, block_mgr):
        """Extend Markdown blocks."""

        block_mgr.register(Details, self.getConfigs())

        # Generate an details subclass based on the given names.
        for b in self.getConfig('types', []):
            subclass = RE_SEP.sub('', b.title())
            block_mgr.register(
                type(subclass, (Details,), {'OPTIONS': {'open': [False, type_boolean]}, 'NAME': b, 'CONFIG': {}}), {}
            )


def makeExtension(*args, **kwargs):
    """Return extension."""

    return DetailsExtension(*args, **kwargs)
