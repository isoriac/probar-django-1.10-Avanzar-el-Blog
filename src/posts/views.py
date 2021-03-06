try:
    from urllib import quote_plus #Python 2
except:
    pass

try:
    from urllib.parse import quote_plus #Python 3
except: 
    pass

from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone


from .models import Post
from .forms import PostForm
from .utils import get_read_time

from comments.models import Comment 
from comments.forms import CommentForm
from .utils import get_read_time

# Create your views here.
def post_create(request):
	if not request.user.is_authenticated():
		response = HttpResponse("No tienes permiso para hacer eso.")
		response.status_code = 403
		return response
	form = PostForm(request.POST or None, request.FILES or None)
	if form.is_valid() and request.user.is_authenticated():
		instance = form.save(commit=False)
		instance.user = request.user 
		instance.save()
		messages.success(request, "Tu post ha sido creado correctamente. Yuju!")
		return HttpResponseRedirect(instance.get_absolute_url())
	context = {
		"form": form
	}
	return render(request, "post_form.html", context)


def post_detail(request, slug=None):
	instance = get_object_or_404(Post, slug=slug)
	if instance.publish > timezone.now().date() or instance.draft:
		if not request.user.is_staff or not request.user.is_superuser:
			raise Http404
	share_string = quote_plus(instance.titulo)
	print(get_read_time(instance.get_markdown()))
	initial_data = {
		"content_type": instance.get_content_type,
		"object_id": instance.id,
	}
	form = CommentForm(request.POST or None, initial=initial_data)
	if form.is_valid():
		c_type = form.cleaned_data.get("content_type")
		content_type = ContentType.objects.get(model=c_type)
		obj_id = form.cleaned_data.get("object_id")
		content_data = form.cleaned_data.get("content")
		parent_obj = None
		try:
			parent_id = int(request.POST.get("parent_id"))
		except:
			parent_id = None
		if parent_id:
			parent_qs = Comment.objects.filter(id=parent_id)
			if parent_qs.exists() and parent_qs.count() == 1:
				parent_obj = parent_qs.first()
		new_comment, created = Comment.objects.get_or_create(
								user=request.user,
								content_type=content_type,
								object_id=obj_id,
								content=content_data,
								parent=parent_obj,
								)
		return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

	#Post.objects.get(id=instance.id)
	comments = instance.comments #Comment.objects.filter_by_instance(instance)
	context = {
		"titulo": instance.titulo,
		"instance": instance,
		"share_string": share_string,
		"comments": comments,
		"comment_form": form,
	}
	return render(request, "post_detail.html", context)


def post_list(request):
	hoy = timezone.now().date()
	queryset_list = Post.objects.active() #filter(draft=False).filter(publish__lte=timezone.now()) #all() #.order_by("-timestamp")
	if request.user.is_staff or request.user.is_superuser:
		queryset_list = Post.objects.all()
		
	query = request.GET.get("q")
	if query:
		queryset_list = queryset_list.filter(
			Q(titulo__icontains=query)|
			Q(contenido__icontains=query)|
			Q(user__first_name__icontains=query)|
			Q(user__last_name__icontains=query)
			).distinct()
	paginator = Paginator(queryset_list, 2) # Show 25 contacts per page
	page_request_var = "list"
	page = request.GET.get(page_request_var)
	try:
		queryset = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		queryset = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		queryset = paginator.page(paginator.num_pages)

	context = {
	"titulo": "MI BLOG SUPERMEGACHULO",
	"object_list": queryset,
	"page_request_var": page_request_var,
	"hoy": hoy,
	}

	return render(request, "post_list.html", context)

def post_update(request, slug=None):
	if not request.user.is_authenticated():
		raise Http404
	instance = get_object_or_404(Post, slug=slug)
	form = PostForm(request.POST or None, request.FILES or None, instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "Tu <a href='#'>post</a> ha sido modificado.", extra_tags="html_safe")
		# messages.success(request, "Bien hecho.")
		# messages.success(request, "Me encantas.")
		return HttpResponseRedirect(instance.get_absolute_url())

	context = {
		"titulo": instance.titulo,
		"instance": instance,
		"form": form,
	}
	return render(request, "post_form.html", context)


def post_delete(request, slug=None):
	if not request.user.is_authenticated():
		raise Http404
	instance = get_object_or_404(Post, slug=slug)
	instance.delete()
	messages.success(request, "Tu post ha sido eliminado.")
	return redirect("posts:list")