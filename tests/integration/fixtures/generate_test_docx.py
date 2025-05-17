# generate_test_docx.py

import zipfile

# Define the internal file structure and XML contents for the test .docx
docx_structure = {
    "[Content_Types].xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>
  <Override PartName="/word/comments.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"/>
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
</Types>
""",
    "_rels/.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1"
                Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
                Target="word/document.xml"/>
</Relationships>
""",
    "word/document.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <!-- Paragraph -->
    <w:p>
      <w:r><w:t>John Smith went to Harvard.</w:t></w:r>
    </w:p>

    <!-- Table -->
    <w:tbl>
      <w:tr>
        <w:tc>
          <w:p><w:r><w:t>His SSN is 123-45-6789.</w:t></w:r></w:p>
        </w:tc>
      </w:tr>
    </w:tbl>

    <!-- Footnote reference -->
    <w:p>
      <w:r><w:footnoteReference w:id="1"/></w:r>
    </w:p>

    <!-- Text box -->
    <w:p>
      <w:r>
        <w:drawing>
          <wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">
            <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
              <a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
                <w:txbxContent xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
                  <w:p><w:r><w:t>Contact John Smith</w:t></w:r></w:p>
                </w:txbxContent>
              </a:graphicData>
            </a:graphic>
          </wp:inline>
        </w:drawing>
      </w:r>
    </w:p>

    <w:sectPr/>
  </w:body>
</w:document>
""",
    "word/comments.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:comments xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:comment w:author="Author" w:date="2025-05-15T12:00:00Z" w:initials="AA" w:paraId="12345678" w:parentId="0" w:commentId="0">
    <w:p><w:r><w:t>Review this with John Smith</w:t></w:r></w:p>
  </w:comment>
</w:comments>
""",
    "word/footnotes.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:footnote w:id="1">
    <w:p><w:r><w:t>Smith lives at 123 Main St</w:t></w:r></w:p>
  </w:footnote>
</w:footnotes>
""",
    "word/_rels/document.xml.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments" Target="comments.xml"/>
</Relationships>
"""
}

def create_test_docx(path: str):
    with zipfile.ZipFile(path, mode="w", compression=zipfile.ZIP_DEFLATED) as docx_file:
        for internal_path, xml in docx_structure.items():
            docx_file.writestr(internal_path, xml)

if __name__ == "__main__":
    create_test_docx("comments_footnotes_textboxes.docx")