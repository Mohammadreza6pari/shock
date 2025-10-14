import io
import csv
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Dataset


class DatasetGroupingViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_approved=True
        )
        self.client.force_authenticate(user=self.user)

        # Create a small test CSV data
        csv_data = [
            ['', 'AUS_01', 'AUS_02', 'USA_01', 'USA_02'],
            ['row1', 1, 2, 3, 4],
            ['row2', 5, 6, 7, 8],
        ]

        # Create CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        for row in csv_data:
            writer.writerow(row)
        csv_content = output.getvalue()

        # Create dataset
        self.dataset = Dataset.objects.create(name='test_dataset')
        self.dataset.file.save('test.csv', io.BytesIO(csv_content.encode('utf-8')))

    def test_group_countries_and_industries(self):
        # Test grouping countries and industries
        data = {
            'dataset_id': self.dataset.id,
            'country_groups': [
                {'name': 'GROUP', 'members': ['AUS', 'USA']}
            ],
            'group_all_industries': True
        }

        response = self.client.post('/api/datasets/group/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check new dataset created
        new_dataset_id = response.data['id']
        new_dataset = Dataset.objects.get(id=new_dataset_id)
        self.assertEqual(new_dataset.name, f"{self.dataset.name}_grouped")

        # Read the grouped CSV
        with new_dataset.file.open('rb') as f:
            text_file = io.TextIOWrapper(f, encoding='utf-8')
            reader = csv.reader(text_file)
            rows = list(reader)

        # Expected grouped data: GROUP_ALL with summed values
        expected_rows = [
            ['GROUP_ALL'],
            ['10'],  # 1+2+3+4
            ['26'],  # 5+6+7+8
        ]

        self.assertEqual(rows, expected_rows)

    def test_group_countries_only(self):
        # Test grouping countries only
        data = {
            'dataset_id': self.dataset.id,
            'country_groups': [
                {'name': 'GROUP', 'members': ['AUS', 'USA']}
            ],
            'group_all_industries': False
        }

        response = self.client.post('/api/datasets/group/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check new dataset created
        new_dataset_id = response.data['id']
        new_dataset = Dataset.objects.get(id=new_dataset_id)

        # Read the grouped CSV
        with new_dataset.file.open('rb') as f:
            text_file = io.TextIOWrapper(f, encoding='utf-8')
            reader = csv.reader(text_file)
            rows = list(reader)

        # Expected grouped data: GROUP_01, GROUP_02 with summed values
        expected_rows = [
            ['GROUP_01', 'GROUP_02'],
            ['4', '6'],  # 1+3, 2+4
            ['12', '14'],  # 5+7, 6+8
        ]

        self.assertEqual(rows, expected_rows)

    def test_no_grouping(self):
        # Test with no grouping
        data = {
            'dataset_id': self.dataset.id,
            'country_groups': [],
            'group_all_industries': False
        }

        response = self.client.post('/api/datasets/group/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check new dataset created
        new_dataset_id = response.data['id']
        new_dataset = Dataset.objects.get(id=new_dataset_id)

        # Read the grouped CSV (should be same as original)
        with new_dataset.file.open('rb') as f:
            text_file = io.TextIOWrapper(f, encoding='utf-8')
            reader = csv.reader(text_file)
            rows = list(reader)

        # Should be same as original
        expected_rows = [
            ['', 'AUS_01', 'AUS_02', 'USA_01', 'USA_02'],
            ['', '1', '2', '3', '4'],
            ['', '5', '6', '7', '8'],
        ]

        self.assertEqual(rows, expected_rows)
