from django.db import models

from treenode.models import TreeNodeModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class EdiMessage(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name

class EdiMessageItem(models.Model):
    edimessage =models.ForeignKey(EdiMessage, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self) -> str:
        return self.object_id

class Record(TreeNodeModel):

    # the field used to display the model instance
    # default value 'pk'
    treenode_display_field = "name"
    edimessage = models.ForeignKey(EdiMessage,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50, default=None, null=True, blank=True)
    field_editable = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name
    
    class Meta(TreeNodeModel.Meta):
        verbose_name = "Record"
        verbose_name_plural = "Record"


class Field(models.Model):

    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50, default='')

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        ordering = ['record','id']