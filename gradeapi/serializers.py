from rest_framework.serializers import ModelSerializer, SerializerMethodField
from mygrades.models import Student, Curriculum, ExemptAssignment, Assignment


class StudentModelSerializer(ModelSerializer):
    subject = SerializerMethodField('get_curriculum_subject')
    curriculum = SerializerMethodField('get_curriculum_name')
    status = SerializerMethodField('get_assignment_status')

    def get_assignment_status(self, instance):
        assignment = Assignment.objects.filter(curriculum=instance.curriculum)
        assignment_statuses = list()
        for i in assignment:
            assignment_statuses.append(i.status)

        return assignment_statuses

    def get_curriculum_name(self, instance):
        return Curriculum.objects.get(id=instance.curriculum.id).name

    def get_curriculum_subject(self, instance):
        return Curriculum.objects.get(id=instance.curriculum.id).subject

    class Meta:
        model = Student
        fields = ('id', 'first_name', 'last_name', 'curriculum', 'subject', 'status')


class ExemptAssignmentModelSerializer(ModelSerializer):
    class Meta:
        model = ExemptAssignment
        fields = ('student', 'assignments')
