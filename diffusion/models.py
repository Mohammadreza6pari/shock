from django.db import models
from django.contrib.postgres.fields import ArrayField
import os 
import threading
from dataset.models import Dataset
import pandas as pd
from collections import defaultdict

class Diffusion(models.Model):
    RESULT_BASE_PATH = './diffusion/outputs/csv/'
    EXECUTABLE_JAR_FILE_PATH = './diffusion/diffusion_files/diffusion_version3.jar'
    BASE_INTEGRATION_FILES_PATH = './diffusion/diffusion_files/'
    DEFAULT_LIMIT_LARGEST_SHOCKS = 5

    SUCCESS_CMD_OUTPUT = "Time is"

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('finished', 'Finished'),
        ('failed', 'Failed'),
        ('deleted', 'Deleted')

    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=72, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    logs = models.JSONField(default=dict, blank=True)
    
    number_of_iterations = models.PositiveIntegerField() 
    integration = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    sources = ArrayField(
        models.CharField(max_length=12, blank=True, null=True),
    )
    destinations = ArrayField(
        models.CharField(max_length=12, blank=True, null=True),
    )
    shock_types = ArrayField(
        models.CharField(max_length=12, blank=True, null=True),
    )
    shock_amounts = ArrayField(
        models.CharField(max_length=12, blank=True, null=True),
    )
    threshold_one = models.FloatField()
    threshold_two = models.FloatField()
    threshold_three = models.FloatField()
    

    def __str__(self):
        return f"Diffusion {self.id} - {self.status}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.status == 'pending':
            self.run_diffusion_async()

    @property
    def output_file_name(self):
        return str(self.id) + "/"
    
    @property
    def output_folder_path(self):
        return Diffusion.RESULT_BASE_PATH + self.output_file_name

    @property
    def output_zip_file_path(self):
        return Diffusion.RESULT_BASE_PATH + "zip/" + self.output_file_name

    @property
    def output_zip_file_name(self):
        return self.output_zip_file_path + str(self.id) + ".zip"

    @property
    def output_folder_path_exists(self):
        return os.path.exists(self.output_folder_path) and os.path.isdir(self.output_folder_path)

    @property
    def output_integration_folder_path(self):
        return self.integration.file_path
            
    def create_output_folder(self):
        if self.output_folder_path_exists:
            raise Exception("floder exist")
        os.makedirs(self.output_folder_path, exist_ok=True)
        return self.output_folder_path
    
    @staticmethod
    def to_cmd_argument_fields(fields):
        return ":".join(fields)
    
    @property
    def cmd_arguments(self):
        command_args = [
            'java', '-jar', 
            Diffusion.EXECUTABLE_JAR_FILE_PATH,
            self.output_integration_folder_path,  # Integration CSV file path
            self.output_folder_path,  # Result path for output
            Diffusion.to_cmd_argument_fields(self.sources),  # Sources as a colon-separated string
            Diffusion.to_cmd_argument_fields(self.destinations),  # Destinations as a colon-separated string
            Diffusion.to_cmd_argument_fields(self.shock_types),  # Shock types as a colon-separated string
            Diffusion.to_cmd_argument_fields(self.shock_amounts),  # Shock amounts as a colon-separated string
            str(self.number_of_iterations),  # Iterations
            str(self.threshold_one),  # Threshold 1
            str(self.threshold_two),  # Threshold 2
            str(self.threshold_three)# Threshold 3
        ]
        return command_args
    
    def run_diffusion_async(self):
        from .tasks import run_diffusion

        if self.status == 'pending':
            self.status = 'running'
            self.save(update_fields=['status'])
            thread = threading.Thread(target=run_diffusion, args=(self.id,))
            thread.start()


    def process_logs(self, limit_largest_shocks=DEFAULT_LIMIT_LARGEST_SHOCKS, country_groups=None, countries=None, grouped_countries=None):
        if self.status != "finished":
            return False, "Diffusion must be finished to retrieve iteration details."

        log_file_path = os.path.join(self.output_folder_path, "log.csv")

        if not os.path.exists(log_file_path):
            return False, "Log file not found."

        # Determine final country filter set
        country_filter_set = None
        if countries or grouped_countries:
            country_filter_set = set(countries or []) | set(grouped_countries or [])

        success, result = Diffusion.parse_log_to_graphs_fast(
            log_file_path,
            shock_threshold=limit_largest_shocks,
            country_groups=country_groups or [],
            country_filter_set=country_filter_set
        )

        return success, result


    @staticmethod
    def parse_log_to_graphs_fast(log_file_path, shock_threshold, country_groups, country_filter_set):
        if not os.path.exists(log_file_path):
            return False, "Log file not found."

        try:
            df = pd.read_csv(log_file_path)
            df = df.dropna(subset=['Source', 'Destination', 'Shock', 'Iteration'])

            df['Shock'] = pd.to_numeric(df['Shock'], errors='coerce')
            df['Iteration'] = pd.to_numeric(df['Iteration'], errors='coerce')
            df = df.dropna(subset=['Shock', 'Iteration'])

            df = df[df['Shock'].abs() > shock_threshold]

            group_map = {}
            if country_groups:
                for group in country_groups:
                    if len(group) < 2:
                        continue
                    group_name = "_".join(sorted(group))
                    for country in group:
                        group_map[country] = group_name

            def map_country(name):
                return group_map.get(name, name)

            df['Source'] = df['Source'].map(map_country)
            df['Destination'] = df['Destination'].map(map_country)

            df = df.groupby(['Iteration', 'Source', 'Destination'], as_index=False)['Shock'].sum()

            graphs = []

            for iteration, group in df.groupby('Iteration'):
                edges = []
                nodes = set(group['Source']).union(set(group['Destination']))

                if country_filter_set is not None:
                    nodes = {n for n in nodes if n in country_filter_set}
                    group = group[(group['Source'].isin(nodes)) & (group['Destination'].isin(nodes))]

                for _, row in group.iterrows():
                    edges.append({
                        'source': row['Source'],
                        'target': row['Destination'],
                        'weight': row['Shock']
                    })

                graphs.append({
                    'iteration': int(iteration),
                    'nodes': [{'id': node} for node in nodes],
                    'edges': edges
                })

            return True, graphs

        except Exception as e:
            return False, f"Error processing log file: {e}"