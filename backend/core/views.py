from rest_framework import viewsets, generics, permissions
from .models import User, IncidentReport
from .serializers import UserRegistrationSerializer, IncidentReportSerializer

class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class IncidentReportViewSet(viewsets.ModelViewSet):
    # Solo mostramos los reportes activos por defecto
    queryset = IncidentReport.objects.filter(state=IncidentReport.State.ACTIVE).order_by('-created_at')
    serializer_class = IncidentReportSerializer
    
    # Por ahora permitimos que cualquiera los vea y los cree para facilitar las pruebas
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        # Si el usuario inició sesión, lo asociamos como autor del reporte
        author = self.request.user if self.request.user.is_authenticated else None
        serializer.save(author=author)