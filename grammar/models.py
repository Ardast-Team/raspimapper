from django.db import models

class GrammarNode(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'grammar'  # Explicitly set the app label