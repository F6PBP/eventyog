from  django.http import HttpRequest, JsonResponse
from modules.api.ApiResponse import ApiResponse

def main(request: HttpRequest) -> ApiResponse:
    return ApiResponse(status=200, content="Hello, World!")