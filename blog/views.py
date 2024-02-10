from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView, DetailView, ListView, CreateView, UpdateView

from blog.forms import AddPostForm
from blog.models import Articles
from blog.utils import DataMixin


class BlogView(DataMixin, ListView):
    template_name = 'blog/blog.html'
    context_object_name = 'posts'
    title_page = 'Blog TAKEABOT ADD INFORMATION'
    cat_selected = 0

    def get_queryset(self):
        return Articles.published.all().select_related('cat')


class ShowPost(DataMixin, DetailView):
    template_name = 'blog/blog-details.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        return get_object_or_404(Articles.published, slug=self.kwargs[self.slug_url_kwarg])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_content = context['post'].content
        context['formatted_content'] = mark_safe(post_content)
        return self.get_mixin_context(context, title=context['post'].title)


class AddPage(PermissionRequiredMixin, LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'blog/add_article.html'
    title_page = 'Blog TAKEABOT ADD INFORMATION'
    permission_required = 'blog.add_blog_blog'  # <приложение>.<действие>_<таблица>

    def form_valid(self, form):
        w = form.save(commit=False)
        w.author = self.request.user
        return super().form_valid(form)


class UpdatePage(PermissionRequiredMixin, DataMixin, UpdateView):
    model = Articles
    fields = ['title', 'content', 'photo', 'is_published', 'cat']
    template_name = 'blog/add_article.html'
    success_url = reverse_lazy('blog')
    title_page = 'Blog TAKEABOT ADD INFORMATION'

    def get_object(self, queryset=None):
        return Articles.objects.get(slug=self.kwargs['post_slug'])
    permission_required = 'blog.add_blog_blog'


# @permission_required(perm='women.add_women', raise_exception=True)
# def contact(request):
#     return HttpResponse("Обратная связь")


# class WomenCategory(DataMixin, ListView):
#     template_name = 'women/index.html'
#     context_object_name = 'posts'
#     allow_empty = False
#
#     def get_queryset(self):
#         return Women.published.filter(cat__slug=self.kwargs['cat_slug']).select_related("cat")
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         cat = context['posts'][0].cat
#         return self.get_mixin_context(context,
#                                       title='Категория - ' + cat.name,
#                                       cat_selected=cat.pk,
#                                       )

# class TagPostList(DataMixin, ListView):
#     template_name = 'women/index.html'
#     context_object_name = 'posts'
#     allow_empty = False
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         tag = TagPost.objects.get(slug=self.kwargs['tag_slug'])
#         return self.get_mixin_context(context, title='Тег: ' + tag.tag)
#
#     def get_queryset(self):
#         return Women.published.filter(tags__slug=self.kwargs['tag_slug']).select_related('cat')
