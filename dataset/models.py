import csv
import io
from django.conf import settings

from django.db import models


class Dataset(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, unique=True)
    file = models.FileField(upload_to="datasets/")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="datasets"
    )
    
    def __str__(self):
        return self.name

    @property
    def file_path(self):
        return self.file.path

    def extract_countries_and_industries(self):
        """
        Reads the dataset CSV and extracts distinct countries and industries
        from the first row (header).
        """
        with self.file.open("rb") as f:  # binary mode
            text_file = io.TextIOWrapper(f, encoding="utf-8")
            reader = csv.reader(text_file)
            header = next(reader, None)

        if not header:
            return {"countries": [], "industries": []}

        countries = set()
        industries = set()

        for col in header:
            if "_" not in col:
                continue
            country, industry = col.split("_", 1)
            countries.add(country.strip())
            industries.add(industry.strip())

        return {
            "countries": sorted(countries),
            "industries": sorted(industries),
        }
