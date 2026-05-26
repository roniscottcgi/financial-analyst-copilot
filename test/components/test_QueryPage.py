import unittest

from streamlit.testing.v1 import AppTest



class TestQueryPage():

    def test_query_page(self):

        def run_app():
            from src.components.QueryPage import QueryPage

            page = QueryPage("test")
            page.render()

        at = AppTest.from_function(run_app).run()

        assert at
        assert at.header[0].value == "Main Centered Section"
        assert at.markdown[0].value == "This content is perfectly centered within the main area"
        assert at.markdown[1].value == "Source URL: test"