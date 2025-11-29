from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from .models import Listing, Booking, Review
from django.contrib.auth.models import User
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer, UserInfoSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserInfoSerializer

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    def get_permissions(self):
        """ Require authenticaion only whe creating/updating listings
            Anyone can view listing
        """
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)
    
    def perform_destroy(self, instance):
        """Only the owner of the listing can delete it"""
        user = self.request.user
        if instance.host != user:
            raise PermissionDenied("You can only delete your own listings.")
        instance.delete()


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    # Displays all bookings for a specific listing
    filterset_fields = ['listing']  # Add the filter for: GET /api/bookings/?listing=<listing_id>

    """Adds the filter by listing in Swagger documentation"""
    # Overrides list method only to attach Swagger metadata
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter(
            'listing',                 # name of the query param
            openapi.IN_QUERY,          # it's in the URL query string
            description="Filter bookings by listing ID",
            type=openapi.TYPE_STRING   # String ID 
        )
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        # When connected to the auth service, make sure to use user.role
        # if hasattr(user, 'role') and user.role == 'host':
        if user.is_staff:
            # Host sees bookings for their listings only
            return Booking.objects.filter(listing__host=user)
        # Guest sees their own bookings
        return Booking.objects.filter(user=user)

    def perform_create(self, serializer):
        # Permission makes sure only the guest can create
        user = self.request.user
        listing = serializer.validated_data['listing']
        days = (serializer.validated_data['end_date'] - serializer.validated_data['start_date']).days + 1
        serializer.save(
            user=user,
            total_price=listing.price_per_night * days,
            status='pending'
        )
    
    def perform_destroy(self, instance):
        user = self.request.user
        if instance.user != user:
            raise PermissionDenied("You can only delete your own booking.")
        if instance.status == "confirmed":
            raise PermissionDenied("Cannot delete a confirmed booking. Set status to canceled instead.")
        instance.delete()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer

    def get_permissions(self):
        """ Require authenticaion only whe creating/updating reviews
            Anyone can view reviews
        """
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """Reviews is nested in listings: api/listings/<listing_pk>/reviews/"""
        listing_id = self.kwargs.get('listing_pk')
        if listing_id:
            return Review.objects.filter(listing_id=listing_id)
        return Review.objects.all()

    def perform_create(self, serializer):
        listing_id = self.kwargs.get('listing_pk')
        serializer.save(user=self.request.user, listing_id=listing_id)
    
    def perform_destroy(self, instance):
        user = self.request.user
        if instance.user != user:
            raise PermissionDenied("You can only delete your own review.")
        instance.delete()
