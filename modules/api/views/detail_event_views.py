import json
from  django.http import JsonResponse
from modules.main.models import Rating

def create_rating_flutter(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        new_rating = Rating.objects.create(
            user=request.user,
            title=data["rating"],
            description=data["review"],
        )
        new_rating.save()

        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status": "error"}, status=401)
    
def create_ticket_flutter(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        new_ticket = Rating.objects.create(
            user=request.user,
            title=data["name"],
            description=data["price"],
        )
        new_ticket.save()

        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status": "error"}, status=401)
      