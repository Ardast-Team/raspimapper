from django.db import models

from treenode.models import TreeNodeModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class EdiGrammar(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name

class EdiGrammarItem(models.Model):
    edigrammar =models.ForeignKey(EdiGrammar, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self) -> str:
        return self.object_id

class GrammarRecord(TreeNodeModel):

    # the field used to display the model instance
    # default value 'pk'
    treenode_display_field = "name"
    edigrammar = models.ForeignKey(EdiGrammar,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50, default=None, null=True, blank=True)
    # structure
    min = models.IntegerField(default=None, null=True, blank=True)
    max = models.IntegerField(default=None, null=True, blank=True)
    count = models.IntegerField(default=None, null=True, blank=True)
    subtranslation = models.CharField(max_length=50, default=None, null=True, blank=True)
    botsidnr = models.IntegerField(default=None, null=True, blank=True)
    fixedrecordlength = models.BooleanField(default=False, null=True, blank=True)
    # recorddef
    mandatory = models.BooleanField(default=False, null=True, blank=True)
    length = models.CharField(max_length=10,default=None, null=True, blank=True)
    format = models.CharField(max_length=2,default=None, null=True, blank=True)
    is_field = models.BooleanField(default=False, null=True, blank=True)
    decimals = models.BooleanField(default=False, null=True, blank=True)
    minlength = models.CharField(max_length=10,default=None, null=True)
    bformat = models.CharField(max_length=2,default=None, null=True, blank=True)
    maxrepeat = models.IntegerField(default=None, null=True, blank=True)
    subfields = models.CharField(max_length=50, default=None, null=True, blank=True)

# LENGTH = 2
# SUBFIELDS = 2   #for composites
# FORMAT = 3      #format in grammar file
# ISFIELD = 4
# DECIMALS = 5
# MINLENGTH = 6
# BFORMAT = 7     #internal bots format; formats in grammar are converted to bformat
# MAXREPEAT = 8

    def __str__(self) -> str:
        return self.name
    
    class Meta(TreeNodeModel.Meta):
        verbose_name = "Record"
        verbose_name_plural = "Record"


# from mptt.models import MPTTModel, TreeForeignKey

# class EdiMessage(models.Model):
#     name = models.CharField(max_length=50)

#     def __str__(self) -> str:
#         return self.name

# # class EdiMessageItem(models.Model):
# #     edimessage =models.ForeignKey(EdiMessage, on_delete=models.CASCADE)
# #     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
# #     object_id = models.PositiveIntegerField()
# #     content_object = GenericForeignKey()

# #     def __str__(self) -> str:
# #         return self.object_id

# class Record(MPTTModel):

#     edimessage = models.ForeignKey(EdiMessage,on_delete=models.CASCADE)
#     parent = TreeForeignKey('self',on_delete=models.CASCADE, null=True, blank=True, related_name='children')
#     name = models.CharField(max_length=50)

#     def __str__(self) -> str:
#         return self.name
    
#     class MPTTMeta:
#         verbose_name = "Record"
#         verbose_name_plural = "Record"
#         order_insertion_by = ['id']

# class Field(models.Model):

#     record = models.ForeignKey(Record, on_delete=models.CASCADE)
#     name = models.CharField(max_length=50)
#     value = models.CharField(max_length=50, default='')

#     def __str__(self) -> str:
#         return self.name
    
#     class Meta:
#         ordering = ['record','id']