from .models import AuditLog
from django.db.models import Model
from django.forms.models import model_to_dict
import json
from decimal import Decimal
from datetime import date, datetime

class AuditService:
    @staticmethod
    def _json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return str(obj)
        return str(obj)

    @staticmethod
    def log_action(user, action, instance: Model, before_state=None, after_state=None, entity_name=None):
        """
        Record an audit log entry.
        
        Args:
            user: User instance or None
            action: AuditLog.Action choice
            instance: The model instance being modified/accessed
            before_state: Dict representing state before change (optional)
            after_state: Dict representing state after change (optional)
            entity_name: Override entity name (optional)
        """
        
        # Serialize specific types safely
        def safe_serialize(data):
            if not data: return None
            # If it's a Django model, convert to dict
            if isinstance(data, Model):
                try:
                    data = model_to_dict(data)
                except:
                    pass
            
            # Clean dictionary
            if isinstance(data, dict):
                return json.loads(json.dumps(data, default=AuditService._json_serial))
            return data

        try:
            entity = entity_name or instance.__class__.__name__
            entity_id = str(instance.pk)
            
            before_clean = safe_serialize(before_state)
            after_clean = safe_serialize(after_state)

            AuditLog.objects.create(
                user=user if user and user.is_authenticated else None,
                action=action,
                entity=entity,
                entity_id=entity_id,
                before_state=before_clean,
                after_state=after_clean
            )
        except Exception as e:
            # Fallback logging to prevent transaction failure due to audit error
            # In a real system, you might want to force fail or log to file
            print(f"CRITICAL: Failed to create audit log: {str(e)}")
