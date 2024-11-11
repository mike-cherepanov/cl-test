from typing import Any

from rest_framework import serializers

from .models import Choice, Question


class ChoiceSerializer(serializers.ModelSerializer[Choice]):
    class Meta:
        model = Choice
        fields = ['id', 'question', 'value']
        read_only_fields = ['question']  # Prevent updating question field after creation

    def update(self, instance: Choice, validated_data: Any) -> Choice:
        return super().update(instance, validated_data)

    def create(self, validated_data: Any) -> Choice:
        return super().create(validated_data)

    def validate(self, data: dict[str, Any]) -> Any:
        question = self.context.get('question')
        data['question'] = question
        return data


class QuestionSerializer(serializers.ModelSerializer[Question]):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        read_only_fields = ['id', 'choices']
        fields = ['id', 'value', 'choices']
