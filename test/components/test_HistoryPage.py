import unittest

from streamlit.testing.v1 import AppTest



class TestHistoryPage():

    def test_history_page(self):

        def run_app():
            from src.components.HistoryPage import HistoryPage

            page = HistoryPage("test")
            page.render()

        at = AppTest.from_function(run_app).run()

        assert at
        assert at.title[0].value == "History Section"
        assert at.markdown[0].value == "Here is the history of queries and there responses"
        assert at.markdown[1].value == "Source URL: test"



