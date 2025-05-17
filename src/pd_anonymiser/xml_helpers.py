from lxml import etree

# WordprocessingML namespace
_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_NSMAP = {"w": _W_NS}

def extract_text_nodes(xml_tree, xpath_expr):
    """
    Run a namespace-aware XPath against a python-docx OxmlElement.
    Returns a list of matching <w:t> text nodes.
    """
    xp = etree.XPath(xpath_expr, namespaces=_NSMAP)
    return xp(xml_tree)


def extract_comments(part):
    """
    Extract text and text-node references from comments.xml.

    Args:
        part: a doc.part.comments_part

    Returns:
        Tuple of (list of comment texts, list of XML text nodes)
    """
    comments_xml = etree.fromstring(part.blob)
    text_nodes = extract_text_nodes(comments_xml, ".//w:comment//w:t")
    text = [node.text for node in text_nodes if node.text]
    return text, text_nodes


def extract_footnotes(part):
    """
    Extract text and text-node references from footnotes.xml.

    Args:
        part: a doc.part.footnotes_part

    Returns:
        Tuple of (list of footnote texts, list of XML text nodes)
    """
    xml = etree.fromstring(part.blob)
    text_nodes = extract_text_nodes(xml, ".//w:footnote//w:t")
    text = [node.text for node in text_nodes if node.text]
    return text, text_nodes


def extract_textboxes(doc_element):
    """
    Extract text and text-node references from text boxes (shapes) in the main document.xml.

    Args:
        doc_element: the root element of document.xml (doc.part.element)

    Returns:
        Tuple of (list of textbox texts, list of XML text nodes)
    """
    text_nodes = extract_text_nodes(doc_element, ".//w:txbxContent//w:t")
    text = [node.text for node in text_nodes if node.text]
    return text, text_nodes
