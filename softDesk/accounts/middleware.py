from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status
import json


class AgeValidationMiddleware(MiddlewareMixin):
    """
    Middleware pour valider l'âge RGPD lors de l'inscription
    """
    
    def process_request(self, request):
        # Ne s'applique que sur les endpoints d'inscription
        if (request.path in ['/api/auth/register/', '/api/users/'] and 
            request.method == 'POST'):
            
            try:
                # Lire le body de la requête
                if request.body:
                    data = json.loads(request.body.decode('utf-8'))
                    age = data.get('age')
                    
                    # Vérifier l'âge RGPD (minimum 15 ans)
                    if age is not None and age < 15:
                        return JsonResponse({
                            'error': 'RGPD Compliance Error',
                            'detail': 'L\'utilisateur doit avoir au moins 15 ans pour s\'inscrire (conformité RGPD).'
                        }, status=status.HTTP_400_BAD_REQUEST)
                        
            except (json.JSONDecodeError, ValueError):
                # Si on ne peut pas décoder le JSON, on laisse passer pour que Django gère l'erreur
                pass
        
        return None
