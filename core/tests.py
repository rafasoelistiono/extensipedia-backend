from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class SchemaEndpointTests(APITestCase):
    def test_openapi_schema_endpoint_is_accessible(self):
        response = self.client.get(reverse("schema"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("openapi", response.data)
