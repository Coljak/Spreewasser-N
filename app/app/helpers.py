"""
In django 4 the function is_ajax() was dropped.
Therefore this function is implemented with the difference, that the request needs to be passed.
"""

def is_ajax(request):
     return request.headers.get('x-requested-with') == 'XMLHttpRequest'