from rest_framework.routers import DefaultRouter
from .views import ReceiptViewSet, ExpenseViewSet

router = DefaultRouter()
router.register(r"expenses", ExpenseViewSet, basename="expenses")
router.register(r"receipts", ReceiptViewSet, basename="receipts")

urlpatterns = router.urls
