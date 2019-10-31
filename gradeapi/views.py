from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from mygrades.models import Student, Assignment, ExemptAssignment
from gradeapi.serializers import StudentModelSerializer, ExemptAssignmentModelSerializer


class ShowStudents(ModelViewSet):
    permission_classess = (IsAuthenticated,)
    serializer_class = StudentModelSerializer
    queryset = Student.objects.all()


class ExemptStudentsModelViewSet(ModelViewSet):
    serializer_class = ExemptAssignmentModelSerializer

    def retrieve(self, request, pk=None):
        if pk:
            student_id = pk
            assignments = self.request.query_params.get('checked').split(',')

            print(student_id)
            print(assignments)

            assignment_object = list()

            for i in assignments:
                assignment_object.append(Assignment.objects.get(id=i))
            print(assignment_object)

            student = Student.objects.get(id=student_id)
            assignment_objects = list()

            exempt_object, _ = ExemptAssignment.objects.get_or_create(student=student)

            for i in assignment_object:
                exempt_object.assignments.add(i)

            exempt_object.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
