import unittest

from langchain_core.documents import Document
from streamlit.testing.v1 import AppTest



class TestHistoryPage():

    def test_history_page(self):

        def run_app():
            from src.components.HistoryPage import HistoryPage

            page = HistoryPage("test")
            page.render()

        at = AppTest.from_function(run_app)

        history = {
            "db_schema_results": [
                (Document(
                    id='table_blueprint::revenue_facts',
                    metadata={'use_case': 'general', 'table_name': 'revenue_facts'},
                    page_content="test"), 0.57981205),
                (Document(
                    id='table_blueprint::customers',
                    metadata={'use_case': 'general', 'table_name': 'customers'},
                    page_content="test"), 0.5971259),
                (Document(
                    id='table_blueprint::finance_periods',
                    metadata={'use_case': 'general', 'table_name': 'finance_periods'},
                    page_content="test"), 0.6511679)],
            "user_docs_results": [
                (Document(id='0:05_cutover_issue_log_guidance.docx',
                          metadata={'source': '05_cutover_issue_log_guidance.docx'},
                          page_content='C...ed controls include grounded answers, traceable metadata, risk-aware review, and a fallback path when evidence is incomplete.'),
                 0.56882197),
                (Document(id='0:03_milestone_replan_checklist.docx',
                          metadata={'source': '03_milestone_replan_checklist.docx'},
                          page_content='M...ed controls include grounded answers, traceable metadata, risk-aware review, and a fallback path when evidence is incomplete.'),
                 0.57845765),
                (Document(id='0:06_security_review_delay_response.pdf',
                          metadata={'source': '06_security_review_delay_response.pdf'},
                          page_content='incomplete.\nSecurity Review Delay Response — section 2. This section documents enterprise guidance for the project delivery'),
                 0.59229755)]
        }

        history_1 = {
            "db_schema_results": [
                (Document(
                    id='table_blueprint::revenue_facts_1',
                    metadata={'use_case': 'general', 'table_name': 'revenue_facts'},
                    page_content="test"), 0.57981205),
                (Document(
                    id='table_blueprint::customers_1',
                    metadata={'use_case': 'general', 'table_name': 'customers'},
                    page_content="test"), 0.5971259),
                (Document(
                    id='table_blueprint::finance_periods_1',
                    metadata={'use_case': 'general', 'table_name': 'finance_periods'},
                    page_content="test"), 0.6511679)],
            "user_docs_results": [
                (Document(id='0:05_cutover_issue_log_guidance.docx_1',
                          metadata={'source': '05_cutover_issue_log_guidance.docx'},
                          page_content='C...ed controls include grounded answers, traceable metadata, risk-aware review, and a fallback path when evidence is incomplete.'),
                 0.56882197),
                (Document(id='0:03_milestone_replan_checklist.docx_1',
                          metadata={'source': '03_milestone_replan_checklist.docx'},
                          page_content='M...ed controls include grounded answers, traceable metadata, risk-aware review, and a fallback path when evidence is incomplete.'),
                 0.57845765),
                (Document(id='0:06_security_review_delay_response.pdf_1',
                          metadata={'source': '06_security_review_delay_response.pdf'},
                          page_content='incomplete.\nSecurity Review Delay Response — section 2. This section documents enterprise guidance for the project delivery'),
                 0.59229755)]
        }
        at.session_state.query_history = [history, history_1]

        at.run()

        assert at
        # assert at.title[0].value == "History Section"
        # assert at.markdown[0].value == "Here is the history of queries and there responses"
        # assert at.markdown[1].value == "Source URL: test"



# [
#     {'db_schema_results': [
#         (Document(id='table_blueprint::revenue_facts', metadata={'use_case': 'general', 'table_name': 'revenue_facts', 'business_domain...KEY (customer_id) REFERENCES customers(customer_id),\n  FOREIGN KEY (product_id) REFERENCES products(product_id)\n)\n        '), 0.57981205),
#        (Document(id='table_blueprint::customers', metadata={'business_domain': 'general', 'table_name': 'customers', 'use_case': 'gene...er_name VARCHAR(120),\n  segment VARCHAR(40),\n  region VARCHAR(40),\n  status VARCHAR(20),\n  created_date DATE\n)\n        '), 0.5971259),
#        (Document(id='table_blueprint::finance_periods', metadata={'business_domain': 'general', 'object_type': 'enriched_table_schema''...,\n  fiscal_year INT,\n  fiscal_month INT,\n  period_start DATE,\n  period_end DATE,\n  close_status VARCHAR(20)\n)\n       '), 0.6511679), '
#        (Document(id=')table_blueprint::support_tickets', metadata={'use_case': 'general', 'object_type': 'enriched_table_schema', 'tabl... FOREIGN KEY (product_id) REFERE...
#
#
# [
#            (Document(id='0:05_cutover_issue_log_guidance.docx', metadata={'source': '05_cutover_issue_log_guidance.docx'}, page_content='C...ed controls include grounded answers, traceable metadata, risk-aware review, and a fallback path when evidence is incomplete.'), 0.56882197),
#            (Document(id='0:03_milestone_replan_checklist.docx', metadata={'source': '03_milestone_replan_checklist.docx'}, page_content='M...ed controls include grounded answers, traceable metadata, risk-aware review, and a fallback path when evidence is incomplete.'), 0.57845765),
#            (Document(id='0:06_security_review_delay_response.pdf', metadata={'source': '06_security_review_delay_response.pdf'}, page_cont... incomplete.\nSecurity Review Delay Response — section 2. This section documents enterprise guidance for the project delivery'), 0.59229755)]