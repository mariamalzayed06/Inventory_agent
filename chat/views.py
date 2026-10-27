from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .agent import run_agent
# Create your views here.

def chat_page(request):
    return render(request, "chat.html")


@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST is allowed."}, status=405)

    data = json.loads(request.body)
    user_message = data.get("message", "")

    if not user_message:
        return JsonResponse({"error": "No message provided."}, status=400)

    reply = run_agent(user_message)
    return JsonResponse({"reply": reply})