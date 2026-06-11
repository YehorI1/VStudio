import os
import tempfile

from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, SimpleTestCase, override_settings

from .loadbtn_view import upload_sales_data
from .views import build_dashboard_context


class UploadSalesDataTests(SimpleTestCase):
    def test_upload_sales_data_writes_csv_to_dashboard_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with override_settings(BASE_DIR=tmpdir):
                csv_content = (
                    'category;outcome_price;income_price;sales_channel;order_status;date;amount;customer;id\n'
                    'Phones;100;80;Website;Paid;2026-01-01;1;Alice;1\n'
                )
                uploaded_file = SimpleUploadedFile(
                    'orders.csv',
                    csv_content.encode('utf-8'),
                    content_type='text/csv',
                )
                request = RequestFactory().post('/stat/upload/', {'excel_file': uploaded_file})
                request.user = AnonymousUser()

                response = upload_sales_data(request)

                self.assertEqual(response.status_code, 302)
                data_file = os.path.join(tmpdir, 'data', 'all_orders.csv')
                self.assertTrue(os.path.exists(data_file))
                with open(data_file, encoding='utf-8') as handle:
                    self.assertIn('Phones', handle.read())


class DashboardContextTests(SimpleTestCase):
    def test_build_dashboard_context_resets_state_between_calls(self):
        first_orders = [
            {
                'category': 'Phones',
                'outcome_price': '100',
                'income_price': '80',
                'sales_channel': 'Website',
                'order_status': 'Paid',
                'date': '2024-01-01',
                'amount': '1',
            },
            {
                'category': 'Phones',
                'outcome_price': '50',
                'income_price': '40',
                'sales_channel': 'Website',
                'order_status': 'Cancelled',
                'date': '2024-02-01',
                'amount': '1',
            },
        ]
        second_orders = [
            {
                'category': 'Laptops',
                'outcome_price': '30',
                'income_price': '20',
                'sales_channel': 'Instagram',
                'order_status': 'Paid',
                'date': '2024-03-01',
                'amount': '1',
            }
        ]

        first_context = build_dashboard_context(first_orders)
        second_context = build_dashboard_context(second_orders)

        self.assertEqual(first_context['orders'], 2)
        self.assertEqual(second_context['orders'], 1)
        self.assertEqual(second_context['labels_category'], ['Laptops'])
        self.assertEqual(second_context['data_category'], [30])






# from django.test import SimpleTestCase

# from .views import build_dashboard_context


# class DashboardContextTests(SimpleTestCase):
#     def test_build_dashboard_context_resets_state_between_calls(self):
#         first_orders = [
#             {
#                 'category': 'Phones',
#                 'outcome_price': '100',
#                 'income_price': '80',
#                 'sales_channel': 'Website',
#                 'order_status': 'Paid',
#                 'date': '2024-01-01',
#                 'amount': '1',
#             },
#             {
#                 'category': 'Phones',
#                 'outcome_price': '50',
#                 'income_price': '40',
#                 'sales_channel': 'Website',
#                 'order_status': 'Cancelled',
#                 'date': '2024-02-01',
#                 'amount': '1',
#             },
#         ]
#         second_orders = [
#             {
#                 'category': 'Laptops',
#                 'outcome_price': '30',
#                 'income_price': '20',
#                 'sales_channel': 'Instagram',
#                 'order_status': 'Paid',
#                 'date': '2024-03-01',
#                 'amount': '1',
#             }
#         ]

#         first_context = build_dashboard_context(first_orders)
#         second_context = build_dashboard_context(second_orders)

#         self.assertEqual(first_context['orders'], 2)
#         self.assertEqual(second_context['orders'], 1)
#         self.assertEqual(second_context['labels_category'], ['Laptops'])
#         self.assertEqual(second_context['data_category'], [30])
