import markdown
from bs4 import BeautifulSoup

def parse_table_definitions(md_file_path):
    raw_text = md_file_path.read_text(encoding="utf-8", errors="ignore")

    html_output = markdown.markdown(raw_text, extensions=['fenced_code', 'tables'])
    soup = BeautifulSoup(html_output, "html.parser")

    table_docs = {}
    current_table = None
    current_body_elements = []
    current_test = {}

    for element in soup.find_all(recursive=False):
        if element.name in ['h1', 'h2', 'h3', 'h4']:
            if current_table:
                if current_body_elements:
                    table_docs[current_table] = current_body_elements
                elif current_test:
                    table_docs[current_table] = current_test

            current_table = element.get_text().replace("`", '').lower().strip()
            current_body_elements = []  # Reset structural array for the new table
            current_test = {}
        elif current_table is not None:
            if element.name == 'table':
                headers = [th.get_text().strip() for th in element.find_all('th')]

                for row in element.find_all('tr'):
                    cells = row.find_all('td')
                    if not cells:
                        continue

                    row_values = [cell.get_text().strip() for cell in cells]
                    row_dict = dict(zip(headers, row_values))
                    current_body_elements.append(row_dict)
            else:
                text_content = element.get_text().strip()
                if text_content:
                    key, _, value = text_content.partition("\n")
                    current_test[key.strip()] = value.strip()

    if current_table and current_body_elements:
        table_docs[current_table] = current_body_elements
    elif current_test:
        table_docs[current_table] = current_test
    return table_docs