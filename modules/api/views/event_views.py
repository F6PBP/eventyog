from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from modules.main.models import Event

@csrf_exempt
def create_event_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        category = data.get("category"),
        image_urls = data.get('image_urls')
        start_time=data.get("start_time")
        end_time=data.get("end_time")

        if not image_urls.endswith(('.jpg', '.jpeg', '.png')):
            return JsonResponse({"error": "Thumbnail must be a valid image URL (.jpg, .jpeg, .png)."}, status=400)
        
        if not title or not category or not start_time:
            return JsonResponse({"error": 'Invalid input'}, status=400)
        
        if end_time and start_time >= end_time:
            return JsonResponse({"error": "Event berakhir sebelum dimulai"}, status=400)
        
        new_event = Event.objects.create(
            user=request.user,
            title=data["title"],
            description=data["description"],
            category=data["category"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            location=data["location"],
            image_urls=image_urls,
        )
        new_event.save()

        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status": "error"}, status=401)