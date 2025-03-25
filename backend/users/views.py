from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer
from projects.permissions import IsProjectAdmin


class Me(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)


class Users(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ("username",)


class UserCreation(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated & IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        return user


from rest_framework.generics import DestroyAPIView, UpdateAPIView

class UserDeletion(DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated & IsAdminUser]
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get('id')  # Pega o ID diretamente da URL
        if not user_id:
            return Response({"error": "ID do usuário não fornecido"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            username = user.username
            user.delete()
            return Response({"success": f"Usuário {username} excluído com sucesso"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Erro ao excluir usuário: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserUpdate(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated & IsAdminUser]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        user_id = self.kwargs.get('id')
        if not user_id:
            return Response({"error": "ID do usuário não fornecido"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
            
            # Atualizar nome de usuário se fornecido
            if 'username' in request.data:
                user.username = request.data['username']
            
            # Atualizar status de administrador se fornecido
            if 'is_staff' in request.data:
                user.is_staff = request.data['is_staff']
            
            # Atualizar senha se fornecida
            if 'password1' in request.data and 'password2' in request.data:
                if request.data['password1'] != request.data['password2']:
                    return Response({"error": "As senhas não coincidem"}, status=status.HTTP_400_BAD_REQUEST)
                user.set_password(request.data['password1'])
            
            user.save()
            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Erro ao atualizar usuário: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
