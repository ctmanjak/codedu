import json
import falcon

from look.app import app

from . import client, admin_token, admin_token, admin_token

def test_create_category(client):
    doc = {
        "CreateCategory": {
            "category": {
                "title": "pytest_category-1",
                "subtitle": "pytest_category-1's subtitle",
            }
        },
        "CreateCategory2": {
            "category": {
                "title": "pytest_category-2",
                "subtitle": "pytest_category-2's subtitle",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                CreateCategory: createCategory(data: {title:"pytest_category-1"}) {
                    category {
                        title
                        subtitle
                    }
                }
                CreateCategory2: createCategory(data: {title:"pytest_category-2"}) {
                    category {
                        title
                        subtitle
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_create_board(client):
    doc = {
        "CreateBoard": {
            "board": {
                "title": "pytest_board-1",
                "subtitle": "pytest_board-1's subtitle",
            }
        },
        "CreateBoard2": {
            "board": {
                "title": "pytest_board-2",
                "subtitle": "pytest_board-2's subtitle",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                CreateBoard: createBoard(data: {title:"pytest_board-1"}) {
                    board {
                        title
                        subtitle
                    }
                }
                CreateBoard2: createBoard(data: {title:"pytest_board-2"}) {
                    board {
                        title
                        subtitle
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_create_board(client):
    doc = {
        "CreateBoard": {
            "board": {
                "title": "pytest_board-1",
                "subtitle": "pytest_board-1's subtitle",
            }
        },
        "CreateBoard2": {
            "board": {
                "title": "pytest_board-2",
                "subtitle": "pytest_board-2's subtitle",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                CreateBoard: createBoard(data: {title:"pytest_board-1"}) {
                    board {
                        title
                        subtitle
                    }
                }
                CreateBoard2: createBoard(data: {title:"pytest_board-2"}) {
                    board {
                        title
                        subtitle
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_connect_category_board(client):
    doc = {
        "CreateCategoryBoard": {
            "categoryBoard": {
                "categoryId": "1",
                "boardId": "1",
            }
        },
        "CreateCategoryBoard2": {
            "categoryBoard": {
                "categoryId": "2",
                "boardId": "1",
            }
        },
        "CreateCategoryBoard3": {
            "categoryBoard": {
                "categoryId": "2",
                "boardId": "2",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                CreateCategoryBoard: createCategoryBoard(data: {categoryId: 1, boardId: 1}) {
                    categoryBoard {
                        categoryId
                        boardId
                    }
                }
                CreateCategoryBoard2: createCategoryBoard(data: {categoryId: 2, boardId: 1}) {
                    categoryBoard {
                        categoryId
                        boardId
                    }
                }
                CreateCategoryBoard3: createCategoryBoard(data: {categoryId: 2, boardId: 2}) {
                    categoryBoard {
                        categoryId
                        boardId
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_create_chapter(client):
    doc = {
        "CreateChapter": {
            "chapter": {
                "title": "pytest_chapter-1",
                "subtitle": "pytest_chapter-1's subtitle",
            }
        },
        "CreateChapter2": {
            "chapter": {
                "title": "pytest_chapter-2",
                "subtitle": "pytest_chapter-2's subtitle",
            }
        },
        "CreateChapter3": {
            "chapter": {
                "title": "pytest_chapter-3",
                "subtitle": "pytest_chapter-3's subtitle",
            }
        },
        "CreateChapter4": {
            "chapter": {
                "title": "pytest_chapter-4",
                "subtitle": "pytest_chapter-4's subtitle",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                CreateChapter: createChapter(data: {boardId: 1, title:"pytest_chapter-1"}) {
                    chapter {
                        title
                        subtitle
                    }
                }
                CreateChapter2: createChapter(data: {boardId: 1, title:"pytest_chapter-2"}) {
                    chapter {
                        title
                        subtitle
                    }
                }
                CreateChapter3: createChapter(data: {boardId: 2, title:"pytest_chapter-3"}) {
                    chapter {
                        title
                        subtitle
                    }
                }
                CreateChapter4: createChapter(data: {boardId: 2, title:"pytest_chapter-4"}) {
                    chapter {
                        title
                        subtitle
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_create_subchapter(client):
    doc = {
        "CreateSubchapter": {
            "subchapter": {
                "title": "pytest_subchapter-1",
            }
        },
        "CreateSubchapter2": {
            "subchapter": {
                "title": "pytest_subchapter-2",
            }
        },
        "CreateSubchapter3": {
            "subchapter": {
                "title": "pytest_subchapter-3",
            }
        },
        "CreateSubchapter4": {
            "subchapter": {
                "title": "pytest_subchapter-4",
            }
        },
        "CreateSubchapter5": {
            "subchapter": {
                "title": "pytest_subchapter-5",
            }
        },
        "CreateSubchapter6": {
            "subchapter": {
                "title": "pytest_subchapter-6",
            }
        },
        "CreateSubchapter7": {
            "subchapter": {
                "title": "pytest_subchapter-7",
            }
        },
        "CreateSubchapter8": {
            "subchapter": {
                "title": "pytest_subchapter-8",
            }
        },
    }

    body = {
        "query": '''
            mutation {
                CreateSubchapter: createSubchapter(data: {chapterId: 1, title:"pytest_subchapter-1"}) {
                    subchapter {
                        title
                    }
                }
                CreateSubchapter2: createSubchapter(data: {chapterId: 1, title:"pytest_subchapter-2"}) {
                    subchapter {
                        title
                    }
                }
                CreateSubchapter3: createSubchapter(data: {chapterId: 2, title:"pytest_subchapter-3"}) {
                    subchapter {
                        title
                    }
                }
                CreateSubchapter4: createSubchapter(data: {chapterId: 2, title:"pytest_subchapter-4"}) {
                    subchapter {
                        title
                    }
                }
                CreateSubchapter5: createSubchapter(data: {chapterId: 3, title:"pytest_subchapter-5"}) {
                    subchapter {
                        title
                    }
                }
                CreateSubchapter6: createSubchapter(data: {chapterId: 3, title:"pytest_subchapter-6"}) {
                    subchapter {
                        title
                    }
                }
                CreateSubchapter7: createSubchapter(data: {chapterId: 4, title:"pytest_subchapter-7"}) {
                    subchapter {
                        title
                    }
                }
                CreateSubchapter8: createSubchapter(data: {chapterId: 4, title:"pytest_subchapter-8"}) {
                    subchapter {
                        title
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_update_category(client):
    doc = {
        "updateCategory": {
            "category": {
                "title": "pytest_updatedcategory-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updateCategory(data: {id: 1, title:"pytest_updatedcategory-1"}) {
                    category {
                        title
                    }
                }
            }
        '''
    }

    
    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_update_board(client):
    doc = {
        "updateBoard": {
            "board": {
                "title": "pytest_updatedboard-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updateBoard(data: {id: 1, title:"pytest_updatedboard-1"}) {
                    board {
                        title
                    }
                }
            }
        '''
    }

    
    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_update_chapter(client):
    doc = {
        "updateChapter": {
            "chapter": {
                "title": "pytest_updatedchapter-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updateChapter(data: {id: 1, title:"pytest_updatedchapter-1"}) {
                    chapter {
                        title
                    }
                }
            }
        '''
    }

    
    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_update_subchapter(client):
    doc = {
        "updateSubchapter": {
            "subchapter": {
                "title": "pytest_updatedsubchapter-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                updateSubchapter(data: {id: 1, title:"pytest_updatedsubchapter-1"}) {
                    subchapter {
                        title
                    }
                }
            }
        '''
    }

    
    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_delete_subchapter(client):
    doc = {
        "deleteSubchapter": {
            "subchapter": {
                "title": "pytest_updatedsubchapter-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteSubchapter(data: {id: 1}) {
                    subchapter {
                        title
                    }
                }
            }
        '''
    }

    
    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_delete_chapter(client):
    doc = {
        "deleteChapter": {
            "chapter": {
                "title": "pytest_updatedchapter-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteChapter(data: {id: 1, title:"pytest_updatedchapter-1"}) {
                    chapter {
                        title
                    }
                }
            }
        '''
    }

    
    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())
    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_delete_board(client):
    doc = {
        "deleteBoard": {
            "board": {
                "title": "pytest_updatedboard-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteBoard(data: {id: 1, title:"pytest_updatedboard-1"}) {
                    board {
                        title
                    }
                }
            }
        '''
    }

    
    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_delete_category(client):
    doc = {
        "deleteCategory": {
            "category": {
                "title": "pytest_updatedcategory-1"
            }
        }
    }

    body = {
        "query": '''
            mutation {
                deleteCategory(data: {id: 1, title:"pytest_updatedcategory-1"}) {
                    category {
                        title
                    }
                }
            }
        '''
    }

    
    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

def test_check_learn(client):
    doc = {"category": {"edges": [{"node": {"boards": {"edges": [{"node": {"chapters": {"edges": [{"node": {"subchapters": {"edges": [{"node": {"id": "c3ViY2hhcHRlck5vZGU6NQ=="}}, {"node": {"id": "c3ViY2hhcHRlck5vZGU6Ng=="}}]}}}, {"node": {"subchapters": {"edges": [{"node": {"id": "c3ViY2hhcHRlck5vZGU6Nw=="}}, {"node": {"id": "c3ViY2hhcHRlck5vZGU6OA=="}}]}}}]}}}]}}}]}}

    body = {
        "query": '''
            query {
                category {
                    edges {
                        node {
                            boards {
                                edges {
                                    node {
                                        chapters {
                                            edges {
                                                node {
                                                    subchapters {
                                                        edges {
                                                            node {
                                                                id
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        '''
    }

    response = client.simulate_post('/api/graphql', content_type='application/json', body=json.dumps(body), headers={
        "Authorization": admin_token,
    })
    result_doc = json.loads(response.content.decode())

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK

# def test_create_subchapter_with_image(client):
#     doc = {
#         "CreateSubchapter": {
#             "subchapter": {
#                 "title": "pytest_subchapter-1",
#                 "content": "pytest_subchapter-1's content",
#             }
#         },
#     }

#     body = {
#         "query": '''
#             mutation {
#                 CreateSubchapter: createSubchapter(data: {chapterId: 1, title:"pytest_subchapter-1", content:"pytest_subchapter-1's content"}) {
#                     subchapter {
#                         title
#                         content
#                     }
#                 }
#             }
#         ''',
#         "variables": {
#             "content": "content"
#         }
#     }

#     fake_image_byte = b"a" * (2 * 1024 * 1024)
    
#     m = MultipartEncoder(
#     fields={'data': ('data', json.dumps(body), 'application/json'),
#             'image': ('a.png', fake_image_byte, 'image/png')}
#     )
    
#     response = client.simulate_post('/api/graphql', content_type=m.content_type, body=m.to_string(), headers={
#         "Authorization": my_token,
#     })

#     result_doc = json.loads(response.content.decode())

#     assert v.validate(result_doc, schema)
#     assert response.status == falcon.HTTP_OK

#     with open(f"test/{result_doc['createPost']['post']['image']}", 'rb') as f:
#         assert f.read() == fake_image_byte