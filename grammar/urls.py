from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_grammar_files, name='list_grammars'),
    path('list/', views.list_grammar_files_ajax, name='list_grammars_ajax'),
    path('import/<path:file_path>/', views.import_grammar, name='import_grammar'),
    path('save/', views.save_grammar, name='save_grammar'),
    # Keep existing paths
    path('tree/', views.tree_view, name='grammar_tree_view'),
    path('node/create/', views.create_node, name='create_node'),  # Changed path
    path('import/', views.import_file, name='import_file'),
    path('export/', views.export_grammar, name='export_grammar'),
    path('save_recorddefs/', views.save_recorddefs, name='save_recorddefs'),
    path('save_recorddefs_in_current_file/', views.save_recorddefs_in_current_file, name='save_recorddefs_in_current_file'),
    path('grammar/create/', views.create_grammar, name='create_grammar'),  # Changed path
]
