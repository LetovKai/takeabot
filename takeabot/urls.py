from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

import core
from core import views
from core.views import MainView
from takeabot import settings
from takeabot.sitemap import ArticlesSitemap, IndexSitemap, BlogSitemap, TermsSitemap, PolicySitemap

sitemaps = {
    'index': IndexSitemap,
    'blog': BlogSitemap,
    'articles': ArticlesSitemap,
    'terms': TermsSitemap,
    'privacy_policy': PolicySitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('blank/', views.index, name='blank'),
    path('', include('lp.urls'), name='index'),
    path('dashboard/', MainView.as_view(), name='dashboard'),
    path('users/', include('users.urls', namespace='users')),
    path('mysales/', include('mysales.urls')),
    path('mybot/', include('mybot.urls')),
    path('myoffers/', include('myoffers.urls')),
    path('myprice/', include('myprice.urls')),
    path('blog/', include('blog.urls')),
    path('__debug__/', include('debug_toolbar.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = views.pages_error_404
