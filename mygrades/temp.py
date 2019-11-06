import collections

A = {'data': {0: {'first_name': 'Wesley', 'last_name': 'Brannon', 'epic_id': '61549', 'attendance': 'Present',
                  'class_title': 'US History Through Literature', 'date': 'Oct 22, 2019'},
              1: {'first_name': 'Wesley', 'last_name': 'Brannon', 'epic_id': '61549', 'attendance': 'Present',
                  'class_title': 'US History Through Literature', 'date': 'Oct 22, 2019'},
              2: {'first_name': 'Kylie', 'last_name': 'Garner', 'epic_id': '32622', 'attendance': 'Present',
                  'class_title': '2nd Grade ELA', 'date': 'Oct 25, 2019'},
              3: {'first_name': 'Kylie', 'last_name': 'Garner', 'epic_id': '32622', 'attendance': 'Present',
                  'class_title': '2nd Grade ELA/Reading', 'date': 'Oct 23, 2019'},
              4: {'first_name': 'Kylie', 'last_name': 'Garner', 'epic_id': '32622', 'attendance': 'Present',
                  'class_title': '2nd grade Math', 'date': 'Oct 21, 2019'},
              5: {'first_name': 'Carson', 'last_name': 'Kissire', 'epic_id': '40789', 'attendance': 'Present',
                  'class_title': 'Of Mice and Men Novella Study', 'date': 'Oct 21, 2019'},
              6: {'first_name': 'Carson', 'last_name': 'Kissire', 'epic_id': '40789', 'attendance': 'Present',
                  'class_title': 'Geometry A', 'date': 'Oct 21, 2019'},
              7: {'first_name': 'Carson', 'last_name': 'Kissire', 'epic_id': '40789', 'attendance': 'Absent',
                  'class_title': 'Biology 1', 'date': 'Oct 25, 2019'},
              8: {'first_name': 'Lainey', 'last_name': 'Lovett', 'epic_id': '72709', 'attendance': 'Absent',
                  'class_title': 'PK Math', 'date': 'Oct 22, 2019'},
              9: {'first_name': 'Lainey', 'last_name': 'Lovett', 'epic_id': '72709', 'attendance': 'Absent',
                  'class_title': 'Prek Story Time', 'date': 'Oct 21, 2019'},
              10: {'first_name': 'Kaytlin', 'last_name': 'Foutch', 'epic_id': '66049', 'attendance': 'Present',
                   'class_title': 'Of Mice and Men Novella Study', 'date': 'Oct 21, 2019'},
              11: {'first_name': 'Kaytlin', 'last_name': 'Foutch', 'epic_id': '66049', 'attendance': 'Present',
                   'class_title': 'Algebra II A - TI Nspire  ', 'date': 'Oct 21, 2019'},
              12: {'first_name': 'Kaytlin', 'last_name': 'Foutch', 'epic_id': '66049', 'attendance': 'Absent',
                   'class_title': 'Biology 1', 'date': 'Oct 25, 2019'},
              13: {'first_name': 'Kaytlin', 'last_name': 'Foutch', 'epic_id': '66049', 'attendance': 'Present',
                   'class_title': 'US History', 'date': 'Oct 25, 2019'},
              14: {'first_name': 'Kaytlin', 'last_name': 'Foutch', 'epic_id': '66049', 'attendance': 'Present',
                   'class_title': 'Geometry A', 'date': 'Oct 21, 2019'},
              15: {'first_name': 'Claire', 'last_name': 'Garner', 'epic_id': '46702', 'attendance': 'Present',
                   'class_title': 'Math: First Grade', 'date': 'Oct 21, 2019'},
              16: {'first_name': 'Claire', 'last_name': 'Garner', 'epic_id': '46702', 'attendance': 'Present',
                   'class_title': 'K ELA (Rockin’ K ELA 2019-2020 Class)', 'date': 'Oct 23, 2019'},
              17: {'first_name': 'Zurri', 'last_name': 'Knight', 'epic_id': '70898', 'attendance': 'Present',
                   'class_title': '5th Grade Science', 'date': 'Oct 22, 2019'},
              18: {'first_name': 'Zurri', 'last_name': 'Knight', 'epic_id': '70898', 'attendance': 'Present',
                   'class_title': "Carole Keffer's  ELA Class", 'date': 'Oct 23, 2019'},
              19: {'first_name': 'Alexis', 'last_name': 'Rietman', 'epic_id': '31813', 'attendance': 'Present',
                   'class_title': 'ACT Prep – English and Writing', 'date': 'Oct 22, 2019'},
              20: {'first_name': 'Dylan', 'last_name': 'Smith', 'epic_id': '61485', 'attendance': 'Absent',
                   'class_title': 'Algebra II A - TI Nspire  ', 'date': 'Oct 21, 2019'},
              21: {'first_name': 'Cody', 'last_name': 'Whitlock', 'epic_id': '50356', 'attendance': 'Present',
                   'class_title': '6th Grade English', 'date': 'Oct 21, 2019'},
              22: {'first_name': 'Cody', 'last_name': 'Whitlock', 'epic_id': '50356', 'attendance': 'Present',
                   'class_title': '7th grade ELA', 'date': 'Oct 24, 2019'},
              23: {'first_name': 'Cody', 'last_name': 'Whitlock', 'epic_id': '50356', 'attendance': 'Absent',
                   'class_title': '6th & 7th grade writing--IEW', 'date': 'Oct 23, 2019'},
              24: {'first_name': 'Cameron', 'last_name': 'Vann', 'epic_id': '202099', 'attendance': 'Absent',
                   'class_title': 'English II', 'date': 'Oct 22, 2019'}}, 'status_code': '100',
     'message': 'Records pulled successfully', 'site': 'Epic Live Attendance',
     }

# print({i['epic_id']: 1 if i['attendance'] == 'Present' else 0 for i in A['data'].values()})
#
# print({i['epic_id']: sum(i['attendance'] == 'Present') for i in A['data'].values()})


def get_registrar():
    presents = []
    for i in A['data'].values():
        if i['attendance'] == 'Present':
            presents.append(i['epic_id'])
    return collections.Counter(presents)


print(get_registrar())
