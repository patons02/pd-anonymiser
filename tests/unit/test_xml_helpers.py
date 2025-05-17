from lxml import etree
from pd_anonymiser.xml_helpers import (
    extract_comments,
    extract_footnotes,
    extract_textboxes,
)


class DummyPart:
    def __init__(self, blob_bytes):
        self.blob = blob_bytes


def test_extract_comments_single_comment():
    xml = b"""<?xml version="1.0"?>
<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:comment w:commentId="0">
    <w:p><w:r><w:t>Hello World</w:t></w:r></w:p>
    <w:p><w:r><w:t>Another Node</w:t></w:r></w:p>
  </w:comment>
</w:comments>
"""
    part = DummyPart(xml)
    texts, nodes = extract_comments(part)
    assert texts == ["Hello World", "Another Node"]
    assert all(node.tag.endswith("t") for node in nodes)
    assert len(nodes) == 2


def test_extract_footnotes_multiple():
    xml = b"""<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:footnote w:id="1">
    <w:p><w:r><w:t>Footnote text</w:t></w:r></w:p>
  </w:footnote>
  <w:footnote w:id="2">
    <w:p><w:r><w:t>Second footnote</w:t></w:r></w:p>
  </w:footnote>
</w:footnotes>
"""
    part = DummyPart(xml)
    texts, nodes = extract_footnotes(part)
    assert texts == ["Footnote text", "Second footnote"]
    assert len(nodes) == 2


def test_extract_textboxes_no_text():
    xml = etree.fromstring(
        b"""<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <!-- no textboxes -->
  </w:body>
</w:document>
"""
    )
    texts, nodes = extract_textboxes(xml)
    assert texts == []
    assert nodes == []


def test_extract_textboxes_with_text():
    xml = etree.fromstring(
        b"""<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r>
        <w:txbxContent xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
          <w:p><w:r><w:t>Boxed Text</w:t></w:r></w:p>
        </w:txbxContent>
      </w:r>
    </w:p>
  </w:body>
</w:document>
"""
    )
    texts, nodes = extract_textboxes(xml)
    assert texts == ["Boxed Text"]
    assert len(nodes) == 1
