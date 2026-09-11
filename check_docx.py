import zipfile
import xml.etree.ElementTree as ET

docx_path = "network_notes.docx"  # 输入 .docx 放在脚本同目录，或改为实际路径

with zipfile.ZipFile(docx_path, 'r') as z:
    xml_content = z.read('word/document.xml')
    # Print first 3000 chars to understand the structure
    print(xml_content[:3000].decode('utf-8'))
