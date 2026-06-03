from utils.parser import parse_table_definitions


class TestVectorService:

    def test_parse_markdown_documentation(self):
        md_file_path = "src/docs/definitions/01_table_definitions.md"
        result = parse_table_definitions(md_file_path)