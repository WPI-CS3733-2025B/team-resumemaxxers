#### 2.2.2.1 \<Blueprint1> Routes auth.routes

|    | Methods           | URL Path   | Description               |
|:---|:------------------|:-----------|:--------------------------|
| 4. |  'GET', 'POST'  | faculty/login   | faculty login page        |
| 5. | 'GET'  | faculty/logout | faculty logout            |
| 6. | 'GET'  | faculty/verify/<token> | faculty verifies email          |
| 7. | 'GET'  | faculty/login/sso | faculty login with Auth0 SSO          |


#### 2.2.2.2 \<Blueprint2> Routes  main.student.routes -- student

|   | Methods      | URL Path                          | Description                              |
|:--|:-------------|:----------------------------------|:-----------------------------------------|
|1. | 'GET'        | student/<student_id>/profile/view | students or faculty view student profile |
|2. | 'GET', 'POST' | student/<student_id>/profile/edit              | student edits their profile              |
|3. | 'GET'        | student/positions | students views positions |
|4. | 'GET'        | student/positions/recommended | students views recommended positions |
| 5. | 'GET', 'POST' | student                 | main route for student |


#### 2.2.2.3 \<Blueprint3> Routes main.faculty.routes -- faculty

|   | Methods           | URL Path                          | Description  |
|:--|:------------------|:----------------------------------|:-------------|
|1. | 'GET' | faculty/<faculty_id>/profile/view | faculty view their profile |
|2. | 'GET', 'POST' | faculty/editlists                 | faculty edit the predefined lists |
| 3. | 'GET', 'POST' | faculty/recommendations           | faculty viewing reference requests from students |
| 4. | 'GET', 'POST' | faculty/positions           | faculty viewing their own positions |
| 5. | 'GET', 'POST' | faculty                 | main route for faculty |

#### 2.2.2.4 \<Blueprint4> Routes main.application.routes -- application

|   | Methods | URL Path                            | Description                                   |
|:--|:--------|:------------------------------------|:----------------------------------------------|
|1. | 'POST'  | application/<application_id>/reject | faculty reject students' application          |
|2. | 'POST'  | application/<application_id>/approve                 | faculty approve students' application         |
|3. | 'POST'  | application/<application_id>/withdraw                | student withdraw their 'pending' applications |
|3. | 'POST'  | application/<application_id>                | page for viewing application details |
|4. | 'GET'   | application                         | page to view all the applications             |

#### 2.2.2.5 \<Blueprint5> Routes main.position.routes -- position

|    | Methods     | URL Path                     | Description                                    |
|:---|:------------|:-----------------------------|:-----------------------------------------------|
| 1. | 'POST'      | position/create              | faculty-only method for creating positions     |
| 2. | 'GET', 'POST' | position/<position_id>/edit                | faculty-only page for editing positions        |
| 3. | 'GET', 'POST' | position/<position_id>/delete              | faculty-only method for deleting a position    |
| 4. | 'GET'       | position/<position_id>/view                | page for viewing position info                 |
| 5. | 'GET', 'POST' | position/<position_id>/apply | student-only method for applying to a position |



#### 2.2.2.6 \<Blueprint6> Routes main.recommendation.routes -- recommendation

|   | Methods | URL Path                                   | Description                                                    |
|:--|:--------|:-------------------------------------------|:---------------------------------------------------------------|
|1. | 'POST'  | recommendation/request | student-only method for requesting a faculty recommendation    |
|2. | 'POST'  | recommendation/<recommendation_id>/reject                      | faculty-only method for rejecting a student rec. request       |
|3. | 'POST'  | recommendation/<recommendation_id>/accept                      | faculty-only method for accepting a student rec. request       |
|4. | 'GET'   | recommendation                             | view incoming (faculty) or sent (student) rec. requests (page) |
