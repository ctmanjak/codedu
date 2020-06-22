# import json
# import falcon

# from look.app import app

# from . import client, my_token, others_token, admin_token

# def test_create_quiz(client):
#     doc = {
#         "CreateQuiz": {
#             "quiz": {
#                 "question": "quiz_test_answer_is-1",
#             }
#         },
#         "CreateQuiz2": {
#             "quiz": {
#                 "question": "quiz_test_answer_is-2",
#             }
#         },
#         "CreateQuiz3": {
#             "quiz": {
#                 "question": "quiz_test_answer_is-3",
#             }
#         },
#     }

#     body = {
#         "query": '''
#             mutation ($choice1: String!, $choice2: String!, $choice3: String!){
#                 CreateQuiz: createQuiz(data: {subchapterId: 2, question:"quiz_test_answer_is-1", choice:$choice1, answer:0}) {
#                     quiz {
#                         question
#                     }
#                 }
#                 CreateQuiz2: createQuiz(data: {subchapterId: 2, question:"quiz_test_answer_is-2", choice:$choice2, answer:1}) {
#                     quiz {
#                         question
#                     }
#                 }
#                 CreateQuiz3: createQuiz(data: {subchapterId: 2, question:"quiz_test_answer_is-3", choice:$choice3, answer:2}) {
#                     quiz {
#                         question
#                     }
#                 }
#             }
#         ''',
#         "variables": {
#             "choice1": [
#                 "choice 1",
#                 "choice 2",
#                 "choice 3",
#             ],
#             "choice2": [
#                 "choice 1",
#                 "choice 2",
#             ],
#             "choice3": [
#                 "choice 1",
#                 "choice 2",
#                 "choice 3",
#                 "choice 4",
#             ],
#         }
#     }

#     response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
#         "Authorization": my_token,
#     })
#     result_doc = json.loads(response.content.decode())

#     assert result_doc == doc
#     assert response.status == falcon.HTTP_OK

# def test_check_quiz(client):
#     doc = {
#         "subchapter": {
#             "edges": [{
#                 "node": {
#                     "quizzes": {
#                         "edges": [
#                             {
#                                 "node": {
#                                     "question": "quiz_test_answer_is-1"
#                                 }
#                             },
#                             {
#                                 "node": {
#                                     "question": "quiz_test_answer_is-2"
#                                 }
#                             },
#                             {
#                                 "node": {
#                                     "question": "quiz_test_answer_is-3"
#                                 }
#                             },
#                         ]
#                     }
#                 }
#             }]
#         }
#     }

#     body = {
#         "query": '''
#             query {
#                 subchapter(filters: {id: 2}) {
#                     edges {
#                         node {
#                             quizzes {
#                                 edges {
#                                     node {
#                                         question
#                                     }
#                                 }
#                             }
#                         }
#                     }
#                 }
#             }
#         '''
#     }

#     response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
#         "Authorization": my_token,
#     })
#     result_doc = json.loads(response.content.decode())

#     assert result_doc == doc
#     assert response.status == falcon.HTTP_OK