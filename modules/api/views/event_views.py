from datetime import datetime
import uuid
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import HttpRequest, HttpResponse, JsonResponse
from modules.main.models import Event, UserProfile
from eventyog.decorators import check_user_profile
from django.core import serializers
from django.db.models import Q
from django.utils import timezone

@check_user_profile(is_redirect=False)
def main(request: HttpRequest) -> JsonResponse:
    try:
        data = {
            'show_navbar': True,
            'is_admin' : getattr(request, 'is_admin', False),
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def show_event_json(request):
    try:
        events = Event.objects.all()
        
        events_json = serializers.serialize("json", events)
        return HttpResponse(events_json, 
                          content_type="application/json", 
                          status=200)
                          
    except Event.DoesNotExist:
        return JsonResponse({
            'error': 'Events not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Internal server error'
        }, status=500)
        
        

def show_upcoming_events(request):
    try:
        now = timezone.now()
        events = Event.objects.all()
        
        upcoming_events = events.filter(start_time__lte=now)

        # Take top 6        
        upcoming_events = upcoming_events[:6]
        events_json = serializers.serialize("json", upcoming_events)
        
        
        return HttpResponse(events_json, 
                          content_type="application/json", 
                          status=200)        
                          
    except Event.DoesNotExist:
        return JsonResponse({
            'error': 'Events not found'
        }, status=404)
        
    except Exception as e:
        print(e)
        return JsonResponse({
            'error': 'Internal server error'
        }, status=500)

def show_event_by_id(request, event_id: uuid.UUID):
    try:
        event = Event.objects.get(uuid=event_id)
        ratings = event.user_rating.all()
        ratings_data = []
        
        for rating in ratings:
            user_profile = UserProfile.objects.get(user=rating.user.user)
            image_url = (
                    f'https://res.cloudinary.com/mxgpapp/image/upload/v1728721294/{user_profile.profile_picture}.jpg'
                    if user_profile.profile_picture
                    else 'https://res.cloudinary.com/mxgpapp/image/upload/v1729588463/ux6rsms8ownd5oxxuqjr.png'
                )
            
            ratings_data.append({
                'username': rating.user.user.username,
                'profile_picture': image_url,
                'rating': user_profile.profile_picture,
                'review': rating.review,
                'created_at': rating.created_at.isoformat(),
                'updated_at': rating.updated_at.isoformat()
            })
        
        # Format sesuai dengan model Event di Flutter
        context = {
            "model": "main.event",
            "pk": str(event.uuid),
            "fields": {
                'title': event.title,
                'description': event.description,
                'category': event.category,
                'start_time': event.start_time.isoformat(),
                'end_time': event.end_time.isoformat() if event.end_time else None,
                'location': event.location,
                'image_urls': event.image_urls,
                'created_at': event.created_at.isoformat(),
                'updated_at': event.updated_at.isoformat(),
                'user_rating': ratings_data,
            }
        }
        return JsonResponse(context, status=200)
    except Event.DoesNotExist:
        return JsonResponse({
            "status": "error", 
            "message": "Event not found"
        }, status=404)


@csrf_exempt
def create_event_flutter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            category = data.get("category")
            image_urls = data.get('image_urls')
            start_time = data.get("start_time")
            end_time = data.get("end_time")
            description = data.get("description")
            location = data.get("location")

            if image_urls and not image_urls.endswith(('.jpg', '.jpeg', '.png')):
                return JsonResponse({"error": "Thumbnail must be a valid image URL (.jpg, .jpeg, .png)."}, status=400)
            
            if not title or not category or not start_time:
                return JsonResponse({"error": 'Invalid input'}, status=400)
            
            if end_time and start_time >= end_time:
                return JsonResponse({"error": "Event berakhir sebelum dimulai"}, status=400)
            
            if not location:
                location =  None
            
            new_event = Event.objects.create(
                title=title,
                description=description,
                category=category,
                start_time=start_time,
                end_time=end_time,
                location=location,
                image_urls=image_urls,
            )
            new_event.save()
            return JsonResponse({"status": "success"}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def delete_event_flutter(request, event_id):
    if request.method in ['DELETE', 'POST']:
        try:
            event = Event.objects.get(pk=event_id)
            event.delete()
            return JsonResponse({'status': 'success', 'message': 'Event deleted successfully'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
@csrf_exempt
def edit_event_flutter(request, event_id):
    if request.method == 'POST': 
        try:
            event = Event.objects.get(uuid=event_id)
            data = json.loads(request.body)
            # Convert string dates to datetime objects if they exist
            start_time_str = data.get("start_time", event.start_time)
            end_time_str = data.get("end_time", event.end_time)

            # Parse datetime strings if they're not None
            if start_time_str:
                event.start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            if "end_time" in data:
                if data["end_time"] is None:
                    event.end_time = None
                else:
                    event.end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))

            # Handle other fields
            event.title = data.get("title", event.title)
            event.description = data.get("description", event.description)
            event.image_urls = data.get("image_urls", event.image_urls)
            event.location = data.get("location", event.location)
            event.category = data.get("category", event.category)

            if event.image_urls and not event.image_urls.endswith(('.jpg', '.jpeg', '.png')):
                return JsonResponse({"error": "Thumbnail must be a valid image URL (.jpg, .jpeg, .png)."}, status=400)
            if not event.title:
                return JsonResponse({"error": "Title is required"}, status=400)
            if not event.category:
                return JsonResponse({"error": "Category is required"}, status=400)
            if not event.start_time:
                return JsonResponse({"error": "Start time is required"}, status=400)   
            if event.end_time and event.start_time >= event.end_time:
                return JsonResponse({"error": "Event berakhir sebelum dimulai"}, status=400)
            if not event.location:
                event.location = None
            
            event.save()

            response = {
                "status": "success",
                "message": "Event updated successfully",
                "data": {
                    "uuid": str(event.uuid),
                    'title': event.title,
                    'description': event.description,
                    'start_time': event.start_time.isoformat() if isinstance(event.start_time, datetime) else event.start_time,
                    'end_time': event.end_time.isoformat() if isinstance(event.end_time, datetime) else event.end_time,
                    'image_urls': event.image_urls,
                    'location': event.location,
                    'category': event.category,
                }
            }
            return JsonResponse(response, status=200)
        except Event.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Event not found"}, status=404)
        except json.JSONDecodeError:
            print("JSON ERROR")
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({'status': 'error', 'error': 'Method not allowed'}, status=405)