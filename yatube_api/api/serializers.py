from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from posts.models import Comment, Follow, Group, Post, User


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'slug', 'title', 'description')
        model = Group


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all(),
                                              required=False)

    class Meta:
        fields = ('id', 'author', 'post', 'text', 'created')
        model = Comment


class PostSerializer(serializers.ModelSerializer):
    comment = CommentSerializer(many=True, required=False)
    author = SlugRelatedField(slug_field='username', read_only=True)
    publication_date = serializers.DateTimeField(
        source='pub_date', read_only=True
    )

    class Meta:
        fields = (
            'text', 'pub_date', 'author', 'group',
            'comment', 'publication_date', 'id'
        )
        model = Post

    def create(self, validated_data):
        if 'group' or 'comment' not in self.initial_data:
            return Post.objects.create(**validated_data)
        return Post.objects.create(**validated_data)


class FollowSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = SlugRelatedField(
        queryset=User.objects.all(), slug_field='username')

    class Meta:
        fields = ('user', 'following')
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            )
        ]

    def validate(self, data):
        if self.context.get('request').user == data['following']:
            raise serializers.ValidationError(
                'Невозможно подписаться на самого себя!')
        return data
