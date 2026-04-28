# prompts/api_views.py

from rest_framework.views       import APIView
from rest_framework.response    import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework             import status
from django.shortcuts           import get_object_or_404
from django.db                  import transaction
from django.db.models           import F
from .models                    import Prompt, SavedPrompt
from .serializers               import PromptDetailSerializer


# ─── Prompt Detail ────────────────────────────────────────────────────────────
class PromptDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        # 1. Query DB — optimized
        prompt = get_object_or_404(
            Prompt.objects.select_related(
                'category'
            ).prefetch_related('tags'),
            pk=pk
        )

        # 2. Serialize — pass request for is_saved context
        serializer = PromptDetailSerializer(
            prompt,
            context={'request': request}
        )

        # 3. Return JSON
        return Response(serializer.data)


# ─── Copy Prompt ──────────────────────────────────────────────────────────────
class CopyPromptAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        prompt = get_object_or_404(Prompt, pk=pk)

        with transaction.atomic():
            Prompt.objects.filter(pk=pk).update(
                copy_count=F('copy_count') + 1
            )
            prompt.refresh_from_db()

        return Response({
            'message'   : 'Copied!',
            'copy_count': prompt.copy_count,
        })


# ─── Save Prompt ──────────────────────────────────────────────────────────────
class SavePromptAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt_id = request.data.get('prompt_id')

        if not prompt_id:
            return Response(
                {'error': 'prompt_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        prompt = get_object_or_404(Prompt, pk=prompt_id)

        saved, created = SavedPrompt.objects.get_or_create(
            user=request.user,
            prompt=prompt
        )

        if created:
            return Response({
                'message': 'Prompt saved!',
                'saved'  : True,
                'id'     : saved.id,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Already saved',
                'saved'  : True,
                'id'     : saved.id,
            }, status=status.HTTP_200_OK)


# ─── Unsave Prompt ────────────────────────────────────────────────────────────
class UnsavePromptAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        saved = get_object_or_404(
            SavedPrompt,
            pk=pk,
            user=request.user
        )
        saved.delete()

        return Response({
            'message': 'Removed from saved',
            'saved'  : False,
        }, status=status.HTTP_200_OK)