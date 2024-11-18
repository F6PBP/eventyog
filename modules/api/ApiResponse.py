from django.http import JsonResponse

class ApiResponse(JsonResponse):
    def __init__(self, status, content=None, message=None, *args, **kwargs):
        # Enforce the structure: {"status": ..., "content": ...}
        data = {
            "status": status,
            "content": content,
            "message": message,
            "error": None if status == 200 else content
        }
        # Initialize the parent class with structured data
        super().__init__(data, *args, **kwargs)
