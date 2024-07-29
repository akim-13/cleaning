from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def check_groups(user, group_names):
    return user.is_authenticated and user.groups.filter(name__in=group_names).exists()

def groups_required(*group_names):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not check_groups(request.user, group_names):
                return redirect('main')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
