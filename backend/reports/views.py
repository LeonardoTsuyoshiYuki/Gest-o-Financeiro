from rest_framework import viewsets, permissions, views, decorators, status, serializers
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncMonth
from .models import Report, Category
from .serializers import ReportSerializer, CategorySerializer
from .filters import ReportFilter

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

from users.permissions import IsAdmin, IsGestor, IsAnalyst, IsViewer

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all().select_related('category')
    serializer_class = ReportSerializer
    # Default permission, overridden by get_permissions
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ReportFilter
    search_fields = ['title', 'category__name']
    ordering_fields = ['reference_date', 'total_value', 'created_at']

    def get_permissions(self):
        """
        RBAC Policies:
        - List/Retrieve: IsViewer+
        - Create/Update: IsAnalyst+
        - Transition (Approve): IsGestor+ (Handled in transition view? No, viewset level first)
        - Destroy: IsAdmin
        """
        if self.action in ['list', 'retrieve', 'history']:
            return [IsViewer()]
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAnalyst()]
        if self.action == 'destroy':
            return [IsAdmin()]
        if self.action == 'transition':
             # Transition logic might require specific checks inside, 
             # but generally mostly Analysis/Managers do this.
             # Let's say Gestor+ for status changes/approvals? 
             # Or Analyst for REVIEW->PENDING, etc.
             # We rely on IsAnalyst as baseline and refine inside transition if needed.
             # Prompt says GESTOR: Aprovação. ANALISTA: Operação.
             # So transition might need nuanced check.
             return [IsAnalyst()]
             
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        instance = serializer.save()
        from audit.services import AuditService
        from audit.models import AuditLog
        from django.forms.models import model_to_dict
        
        AuditService.log_action(
            user=self.request.user,
            action=AuditLog.Action.IMPORT if self.request.path.endswith('import/') else AuditLog.Action.UPDATE,
            instance=instance,
            after_state=model_to_dict(instance),
            entity_name="Report"
        )

    def perform_update(self, serializer):
        """
        Prevent direct status changes via standard Update.
        Status changes must go through /transition/ endpoint.
        """
        if 'status' in serializer.validated_data:
            instance = self.get_object()
            if serializer.validated_data['status'] != instance.status:
                raise serializers.ValidationError({"status": "Changes to status are not allowed here. Use the transition endpoint."})
        
        # Capture state before save (for non-status updates)
        from audit.services import AuditService
        from audit.models import AuditLog
        from django.forms.models import model_to_dict
        
        instance_pre = self.get_object()
        before_state = model_to_dict(instance_pre)
        
        instance = serializer.save()

        AuditService.log_action(
            user=self.request.user,
            action=AuditLog.Action.UPDATE,
            instance=instance,
            before_state=before_state,
            after_state=model_to_dict(instance),
            entity_name="Report"
        )

    def perform_destroy(self, instance):
        from audit.services import AuditService
        from audit.models import AuditLog
        from django.forms.models import model_to_dict

        before_state = model_to_dict(instance)
        
        AuditService.log_action(
            user=self.request.user,
            action=AuditLog.Action.DELETE,
            instance=instance,
            before_state=before_state,
            entity_name="Report"
        )
        instance.delete()

    @decorators.action(detail=True, methods=['post'], url_path='transition')
    def transition(self, request, pk=None):
        """
        Endpoint to change report status following FSM rules.
        Body: { "status": "APPROVED", "comment": "Optional" }
        """
        report = self.get_object()
        new_status = request.data.get('status')
        comment = request.data.get('comment')
        
        if not new_status:
            return Response({"error": "Status is required."}, status=status.HTTP_400_BAD_REQUEST)

        from .services import ReportWorkflowService
        from django.core.exceptions import ValidationError as DjangoValidationError
        
        try:
            ReportWorkflowService.transition_status(report, new_status, request.user, comment)
            return Response(ReportSerializer(report).data)
        except DjangoValidationError as e:
            return Response({"error": str(e.message)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @decorators.action(detail=True, methods=['get'], url_path='history')
    def history(self, request, pk=None):
        """
        Returns audit history for this report.
        """
        from audit.models import AuditLog
        
        logs = AuditLog.objects.filter(entity="Report", entity_id=str(pk)).order_by('-created_at')
        
        # Simple manual serialization for history
        history_data = []
        for log in logs:
            history_data.append({
                'id': log.id,
                'action': log.get_action_display(),
                'user': log.user.username if log.user else 'System',
                'created_at': log.created_at,
                'comment': log.after_state.get('_workflow_comment') if log.after_state else None,
                'changes': log.after_state # Could diff before/after here if needed
            })
            
        return Response(history_data)

class DashboardStatusSummaryView(views.APIView):
    """
    Retorna consolidação de relatórios por status e contagem de atrasados.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from datetime import date
        
        # 1. Agregação por Status
        # Retorna: <QuerySet [{'status': 'PENDING', 'count': 5, 'total': Decimal('100.00')}, ...]>
        by_status_qs = Report.objects.values('status').annotate(
            count=Count('id'),
            total=Sum('total_value')
        )

        # Formatar para dicionário amigável: { 'PENDING': {count, total}, ... }
        # Inicializa com todos os status zerados para garantir consistência no frontend
        summary = {
            status: {'count': 0, 'total': 0.0} 
            for status, _ in Report.Status.choices
        }
        
        for item in by_status_qs:
            st = item['status']
            summary[st] = {
                'count': item['count'],
                'total': float(item['total'] or 0)
            }

        # 2. Relatórios em Atraso (Overdue)
        # Considera atrasado se: due_date < hoje E status não for (APPROVED, CANCELED)
        # FAILED, REVIEW e PENDING contam como atraso se data passou.
        today = date.today()
        overdue_qs = Report.objects.filter(
            due_date__lt=today
        ).exclude(
            status__in=[Report.Status.APPROVED, Report.Status.CANCELED]
        )
        
        overdue_agg = overdue_qs.aggregate(
            count=Count('id'),
            total=Sum('total_value')
        )
        
        summary['OVERDUE'] = {
            'count': overdue_agg['count'],
            'total': float(overdue_agg['total'] or 0)
        }

        return Response(summary)

class DashboardTimelineView(views.APIView):
    """
    Retorna evolução temporal dos valores agrupados por mês e status.
    Formato otimizado para gráficos (Recharts).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Agrupa por Mês (reference_date) e Status
        qs = Report.objects.annotate(
            month=TruncMonth('reference_date')
        ).values('month', 'status').annotate(
            total=Sum('total_value')
        ).order_by('month')

        # Pivotar dados:
        # [ { month: '2025-01-01', 'APPROVED': 100, 'PENDING': 50 }, ... ]
        timeline_map = {}

        for item in qs:
            month_str = item['month'].strftime('%Y-%m-%d')
            if month_str not in timeline_map:
                timeline_map[month_str] = {'month': month_str}
            
            # Adiciona o valor do status específico
            timeline_map[month_str][item['status']] = float(item['total'] or 0)

        # Converte map para lista ordenada
        timeline_data = sorted(timeline_map.values(), key=lambda x: x['month'])
        
        # Preencher meses vazios? (Opcional, mas bom para gráfico contínuo). 
        # Por enquanto vamos retornar apenas meses com dados.
        
        return Response(timeline_data)

class DashboardCarrierView(views.APIView):
    """
    Retorna total por operadora (Categoria).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Agrupa por Nome da Categoria
        qs = Report.objects.values('category__name').annotate(
            count=Count('id'),
            total=Sum('total_value')
        ).order_by('-total') # Top spenders first

        data = []
        for item in qs:
            data.append({
                'name': item['category__name'] or 'Sem Categoria',
                'count': item['count'],
                'total': float(item['total'] or 0)
            })
            
        return Response(data)

class DashboardInsightsView(views.APIView):
    """
    KPIs Executivos e Insights Automáticos.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from datetime import date, timedelta
        from django.utils import timezone
        from invoices.models import InvoiceImport
        
        today = date.today()
        first_this_month = today.replace(day=1)
        next_month = (first_this_month + timedelta(days=32)).replace(day=1)
        last_month_end = first_this_month - timedelta(days=1)
        first_last_month = last_month_end.replace(day=1)
        
        # 1. Financeiro (Report)
        # Considera APPROVED e PENDING como "Volume Faturado"
        reports_qs = Report.objects.exclude(status__in=[Report.Status.CANCELED, Report.Status.FAILED])
        
        current_data = reports_qs.filter(
            reference_date__gte=first_this_month,
            reference_date__lt=next_month
        ).aggregate(total=Sum('total_value'), count=Count('id'))
        
        last_data = reports_qs.filter(
            reference_date__gte=first_last_month,
            reference_date__lt=first_this_month
        ).aggregate(total=Sum('total_value'))
        
        current_total = float(current_data['total'] or 0)
        last_total = float(last_data['total'] or 0)
        
        # Variation
        variation = 0.0
        if last_total > 0:
            variation = ((current_total - last_total) / last_total) * 100.0
        elif current_total > 0:
            variation = 100.0 # From 0 to something
            
        # 2. Operacional (Invoices) - Mês Atual
        # InvoiceImport usa created_at (DateTime)
        invoices_qs = InvoiceImport.objects.filter(
            created_at__gte=timezone.make_aware(timezone.datetime.combine(first_this_month, timezone.datetime.min.time())),
            created_at__lt=timezone.make_aware(timezone.datetime.combine(next_month, timezone.datetime.min.time()))
        )
        
        errors_count = invoices_qs.filter(status=InvoiceImport.Status.FAILED).count()
        skipped_count = invoices_qs.filter(status=InvoiceImport.Status.SKIPPED).count()
        
        # 3. Insights Generation
        insights = []
        if variation > 10:
            insights.append(f"Aumento de {variation:.1f}% em relação ao mês anterior.")
        elif variation < -10:
            insights.append(f"Redução de {abs(variation):.1f}% em relação ao mês anterior.")
            
        if errors_count > 0:
            insights.append(f"{errors_count} faturas com erro de importação exigem atenção.")
            
        if skipped_count > 0:
            insights.append(f"{skipped_count} faturas duplicadas foram ignoradas.")

        return Response({
            'current_month_total': current_total,
            'last_month_total': last_total,
            'variation_percent': round(variation, 1),
            'import_errors_count': errors_count,
            'skipped_count': skipped_count,
            'report_count': current_data['count'],
            'insights_list': insights
        })
