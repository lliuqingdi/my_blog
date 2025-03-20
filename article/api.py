from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from asgiref.sync import sync_to_async
import asyncio
from .models import ArticlePost
from ollama import AsyncClient


class ChatView(View):
    async def get(self, request):
        return await sync_to_async(render)(request, 'article/chat.html')

    async def post(self, request):
        try:
            prompt = request.POST.get('prompt', '')

            async def generate():
                response = ""
                async for part in await AsyncClient().chat(
                        model='deepseek-r1',
                        messages=[{'role': 'user', 'content': prompt}],
                        stream=True,
                        options={'temperature': 0}
                ):
                    response += part['message']['content']
                return response

            result = await generate()
            return JsonResponse({'response': result})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class AIChatView(View):
    async def post(self, request):
        try:
            prompt = request.POST.get('prompt', '')
            if not prompt:
                return JsonResponse({'error': '请输入问题'}, status=400)

            articles = ArticlePost.objects.filter(title__icontains=prompt)[:5]
            context = "\n".join([f"{a.title}: {a.content[:200]}..." for a in articles])

            ai_prompt = f"用户问：{prompt}\n以下是相关的文章：\n{context}\n请基于这些文章回答用户问题："

            async def generate():
                response = ""
                async for part in await AsyncClient().chat(
                        model='deepseek-r1',
                        messages=[{'role': 'user', 'content': ai_prompt}],
                        stream=True,
                        options={'temperature': 0}
                ):
                    response += part['message']['content']
                return response

            result = await generate()
            return JsonResponse({'response': result})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

