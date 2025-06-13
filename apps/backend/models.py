# models.py

from django.db import models


class UserSearch(models.Model):
    task_id = models.CharField(max_length=255)  # Assuming you have some way to identify users
    search_query = models.CharField(max_length=255)
    # Add any other fields you want to save from the session
    activity_tag = models.CharField(max_length=255)

    picked_countries = models.CharField(max_length=255, default=None, null=True)
    picked_cities = models.CharField(max_length=255, default=None, null=True)

    # Optionally, add a timestamp to track when the search was made
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'backend'

    def __str__(self):
        return (f"User ID: {self.task_id}, Search Query: {self.search_query}, Activity Tag: {self.activity_tag}, "
                f"Timestamp: {self.timestamp}, Picked Countries: {self.picked_countries}, Picked Cities: {self.picked_cities}")
