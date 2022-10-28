"""Tabs."""
import xml.etree.ElementTree as etree
from .block import Block, type_boolean


class Tabs(Block):
    """
    Tabbed container.

    Arguments (1 required):
    - A tab title.

    Options:
    - `new` (boolean): since consecutive tabs are automatically grouped, `new` can force a tab
      to start a new tab container.

    Content:
    Detail body.
    """

    NAME = 'tab'

    ARGUMENTS = {'required': 1}
    OPTIONS = {
        'new': [False, type_boolean],
        'select': [False, type_boolean]
    }

    def on_init(self):
        """Handle initialization."""

        # Track tab group count across the entire page.
        if 'tab_group_count' not in self.tracker:
            self.tracker['tab_group_count'] = 0

        self.tab_content = None

    def last_child(self, parent):
        """Return the last child of an `etree` element."""

        if len(parent):
            return parent[-1]
        else:
            return None

    def on_add(self, parent):
        """Adjust where the content is added."""

        if self.tab_content is None:
            for d in parent.findall('div'):
                c = d.attrib['class']
                if c == 'tabbed-content' or c.startswith('tabbed-content '):
                    self.tab_content = list(d)[-1]
                    return self.tab_content

            # This shouldn't happen, but if it does, just return the parent.
            # This can only happen if something else comes in and destroys are structure.
            return parent  # pragma: no cover
        else:
            return self.tab_content

    def on_create(self, parent):
        """Create the element."""

        new_group = self.options['new']
        select = self.options['select']
        title = self.args[0] if self.args and self.args[0] else ''
        sibling = self.last_child(parent)
        tabbed_set = 'tabbed-set tabbed-alternate'

        if (
            sibling and sibling.tag.lower() == 'div' and
            sibling.attrib.get('class', '') == tabbed_set and
            not new_group
        ):
            first = False
            tab_group = sibling

            index = [index for index, _ in enumerate(tab_group.findall('input'), 1)][-1]
            labels = None
            content = None
            for d in tab_group.findall('div'):
                if d.attrib['class'] == 'tabbed-labels':
                    labels = d
                elif d.attrib['class'] == 'tabbed-content':
                    content = d
                if labels is not None and content is not None:
                    break
        else:
            first = True
            self.tracker['tab_group_count'] += 1
            tab_group = etree.SubElement(
                parent,
                'div',
                {'class': tabbed_set, 'data-tabs': '%d:0' % self.tracker['tab_group_count']}
            )

            index = 0
            labels = etree.SubElement(
                tab_group,
                'div',
                {'class': 'tabbed-labels'}
            )
            content = etree.SubElement(
                tab_group,
                'div',
                {'class': 'tabbed-content'}
            )

        data = tab_group.attrib['data-tabs'].split(':')
        tab_set = int(data[0])
        tab_count = int(data[1]) + 1

        attributes = {
            "name": "__tabbed_%d" % tab_set,
            "type": "radio",
            "id": "__tabbed_%d_%d" % (tab_set, tab_count)
        }

        if first or select:
            attributes['checked'] = 'checked'
            # Remove any previously assigned "checked states" to siblings
            for i in tab_group.findall('input'):
                if i.attrib.get('name', '') == '__tabbed_{}'.format(tab_set):
                    if 'checked' in i.attrib:
                        del i.attrib['checked']

        input_el = etree.Element(
            'input',
            attributes
        )
        tab_group.insert(index, input_el)
        lab = etree.SubElement(
            labels,
            "label",
            {
                "for": "__tabbed_%d_%d" % (tab_set, tab_count)
            }
        )
        lab.text = title

        attrib = {'class': 'tabbed-block'}
        etree.SubElement(
            content,
            "div",
            attrib
        )

        tab_group.attrib['data-tabs'] = '%d:%d' % (tab_set, tab_count)

        return tab_group
