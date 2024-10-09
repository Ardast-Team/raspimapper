from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_grammar_files, name='list_grammars'),
    path('import/<path:file_path>/', views.import_grammar, name='import_grammar'),
    path('save/', views.save_grammar, name='save_grammar'),
    # Keep existing paths
    path('tree/', views.tree_view, name='grammar_tree_view'),
    path('create/', views.create_node, name='create_node'),
    path('import/', views.import_file, name='import_file'),
    path('export/', views.export_grammar, name='export_grammar'),
]