from django.db import models
import subprocess
from django.contrib.postgres.fields import ArrayField


class Diffusion(models.Model):
    RESULT_BASE_PATH = './ShockOutputs/'


    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('finished', 'Finished'),
        ('failed', 'Failed'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='pending')
    
    number_of_iterations = models.PositiveIntegerField() 
    integration = models.CharField(max_length=36) #TODO: That's better it maps to integration model
    sources = ArrayField(
        models.CharField(max_length=12),
    )
    destinations = ArrayField(
        models.CharField(max_length=12),
    )
    shock_types = ArrayField(
        models.CharField(max_length=12),
    )
    shock_amounts = ArrayField(
        models.CharField(max_length=12),
    )
    threshold_one = models.IntegerField()
    threshold_two = models.IntegerField()
    threshold_three = models.IntegerField()
    
    def __str__(self):
        return f"Diffusion {self.unique_id} - {self.status}"
    

    @property
    def output_file_name(self):
        return self.id
    
    @property
    def output_file_path(self):
        return Diffusion.RESULT_BASE_PATH + self.output_file_name
    
    def _diffusion_command(self):
        ordered_command_list = list()
        ordered_command_list.append('java')
        ordered_command_list.append('-jar')
        ordered_command_list.append(self.output_file_path)

        return ordered_command_list 

    def run_diffusion(self):
        subprocess.call(self._diffusion_command, shell=True)