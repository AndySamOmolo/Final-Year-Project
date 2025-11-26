from django.test import TestCase, RequestFactory
from unittest.mock import patch
from .views import generate_pdf_report
from django.contrib.auth.models import User
from bakery.models import Order

class ReportTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser('admin', 'admin@test.com', 'password')

    @patch('admin_dashboard.views.render_to_string')
    @patch('admin_dashboard.views.pisa.CreatePDF')
    def test_order_summary_context(self, mock_pisa, mock_render):
        request = self.factory.get('/admin_dashboard/generate-report/order_summary/')
        request.user = self.user
        
        # Create some orders
        Order.objects.create(total_price=100)
        
        generate_pdf_report(request, 'order_summary')
        
        # Check if render_to_string was called
        self.assertTrue(mock_render.called)
        
        # Get the context passed to render_to_string
        args, kwargs = mock_render.call_args
        template_name = args[0]
        context = args[1]
        
        self.assertEqual(template_name, 'admin_dashboard/reports/order_summary.html')
        self.assertIn('orders', context, "orders should be in context")
        self.assertEqual(context['orders'].count(), 1)
