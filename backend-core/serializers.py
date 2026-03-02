from rest_framework import serializers
from .models import User, VideoResource

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the Custom User model. 
    Includes role-based data and subscription status for the member dashboard.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_premium', 'stripe_customer_id']
        read_only_fields = ['is_premium', 'stripe_customer_id']

class VideoResourceSerializer(serializers.ModelSerializer):
    """
    Serializer for the 80+ proprietary medical recordings.
    Includes transcription status for the AI Semantic Search pipeline.
    """
    # Custom field to show if the video has been processed by AI Whisper
    is_transcribed = serializers.SerializerMethodField()

    class Meta:
        model = VideoResource
        fields = [
            'id', 'title', 'video_url', 'category', 
            'transcript', 'is_transcribed', 'created_at'
        ]
        extra_kwargs = {
            'transcript': {'write_only': True} # Keep raw transcript out of the list view for performance
        }

    def get_is_transcribed(self, obj):
        return bool(obj.transcript)

class SpaceSerializer(serializers.Serializer):
    """
    A lightweight serializer to mirror Circle.so 'Spaces'.
    Used for organizing content categories like 'Journal Club' or 'Nutrition Tips'.
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    is_premium_only = serializers.BooleanField(default=True)
    member_count = serializers.IntegerField(default=0)

class PostSerializer(serializers.Serializer):
    """
    Handles community discussions. 
    Demonstrates nested serialization for the Author (User).
    """
    id = serializers.IntegerField(read_only=True)
    author = UserSerializer(read_only=True)
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()
    space_id = serializers.IntegerField()
    created_at = serializers.DateTimeField(read_only=True)
    reactions_count = serializers.IntegerField(default=0)

class CommentSerializer(serializers.Serializer):
    """
    Flat serializer for post comments with moderation flags.
    """
    id = serializers.IntegerField(read_only=True)
    post_id = serializers.IntegerField()
    author_name = serializers.CharField(source='author.username', read_only=True)
    body = serializers.TextField()
    is_flagged = serializers.BooleanField(default=False)