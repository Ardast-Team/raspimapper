from django.contrib import admin
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.views import LoginView,LogoutView,PasswordChangeView,PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, include
from django.urls import re_path as url
from bots import views
#import debug_toolbar

admin.autodiscover()
staff_required = user_passes_test(lambda u: u.is_staff)
superuser_required = user_passes_test(lambda u: u.is_superuser)
run_permission = user_passes_test(lambda u: u.has_perm('bots.change_mutex'))

#urlpatterns = [
#    path('admin/', admin.site.urls),
#    path('playground/', include('playground.urls')),
#    path('interface/', include('interface.urls')),
#    path('__debug__/', include(debug_toolbar.urls)),
#]


urlpatterns = [
    #path('accounts/', include('django.contrib.auth.urls')),
    path('login/', LoginView.as_view(template_name='bots/login.html'), name='login'),
    #url(r'^login.*', LoginView.as_view(), {'template_name': 'admin/login.html'}),
    path('logout/', LogoutView.as_view()),
    #url(r'^logout.*', LogoutView.as_view(),{'next_page': '/'}),
    path('password_change/', PasswordChangeView.as_view(),name='password_change'),
    #url(r'^password_change/$', PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
    #url(r'^password_change/done/$', PasswordChangeDoneView.as_view(),name='password_change_done'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
 
    #login required
    path('home/', login_required(views.home)),
    #url(r'^home.*', login_required(views.home)),
    path('incoming/', login_required(views.incoming)),
    # url(r'^incoming.*', login_required(views.incoming)),
    path('detail/', login_required(views.detail)),
    # url(r'^detail.*', login_required(views.detail)),
    path('process/', login_required(views.process)),
    # url(r'^process.*', login_required(views.process)),
    path('outgoing/', login_required(views.outgoing)),
    # url(r'^outgoing.*', login_required(views.outgoing)),
    path('document/', login_required(views.document)),
    # url(r'^document.*', login_required(views.document)),
    path('reports/', login_required(views.reports)),
    # url(r'^reports.*', login_required(views.reports)),
    path('confirm/', login_required(views.confirm)),
    # url(r'^confirm.*', login_required(views.confirm)),
    path('filer/', login_required(views.filer)),
    # url(r'^filer.*', login_required(views.filer)),
    path('srcfiler/', login_required(views.srcfiler)),
    # url(r'^srcfiler.*', login_required(views.srcfiler)),
    path('logfiler/', login_required(views.logfiler)),
    # url(r'^logfiler.*', login_required(views.logfiler)),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    #only staff
    #url(r'^botsadmin/$', login_required(views.home)),  #do not show django admin root page
    #url(r'^botsadmin/$', login_required(views.home)),  #do not show django admin root page
    #url(r'^botsadmin/bots/$', login_required(views.home)),  #do not show django admin root page
    path('admin/', admin.site.urls),
    path('runengine/', run_permission(views.runengine)),
    #url(r'^runengine.+', run_permission(views.runengine)),
    
    #only superuser
    path('delete/', superuser_required(views.delete)),
    # url(r'^delete.*', superuser_required(views.delete)),
    path('plugin/index/', superuser_required(views.plugin_index)),
    # url(r'^plugin/index.*', superuser_required(views.plugin_index)),
    path('plugin/', superuser_required(views.plugin)),
    # url(r'^plugin.*', superuser_required(views.plugin)),
    path('plugout/index/', superuser_required(views.plugout_index)),
    # url(r'^plugout/index.*', superuser_required(views.plugout_index)),
    path('plugout/backup/', superuser_required(views.plugout_backup)),
    # url(r'^plugout/backup.*', superuser_required(views.plugout_backup)),
    path('plugout/', superuser_required(views.plugout)),
    # url(r'^plugout.*', superuser_required(views.plugout)),
    path('sendtestmail/', superuser_required(views.sendtestmailmanagers)),
    # url(r'^sendtestmail.*', superuser_required(views.sendtestmailmanagers)),

    
    #catch-all
    path('', views.index),
    #url(r'^.*', views.index),
    #path('__debug__/', include(debug_toolbar.urls)),
    path('grammar/', include('grammar.urls')),
]

handler500 = views.server_error
