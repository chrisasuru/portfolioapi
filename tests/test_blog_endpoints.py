from fastapi import status
from ..models.blog.post import BlogPost, PublishingStatus
from ..models.blog.comment import BlogComment
from ..models.blog.tag import BlogTag
from sqlmodel import select
from slugify import slugify
from random import choice

def test_unauthenticated_cannot_create_blog(client):

    blog_post_data = {
        "title": "I am a Proud Misogynist",
        "body": "I hate my life.",
        "tags": ["Dance", "Hate"]
    }

    response = client.post("/v1/blog_posts", json = blog_post_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_authenticated_basic_user_cannot_create_blog(authenticated_client):

    blog_post_data = {
        "title": "I am a Proud Misogynist Uh",
        "body": "I hate my life.",
        "tags": ["Forever", "Hate"]
    }

    response = authenticated_client.post("/v1/blog_posts", json = blog_post_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_authenticated_publisher_user_can_create_blog(publisher_authenticated_client):

    blog_post_data = {
        "title": "Publisher Authenticated Client",
        "body": "I hate my life.",
        "tags": ["Forever", "Hate"]
    }

    response = publisher_authenticated_client.post(f"/v1/blog_posts", json = blog_post_data)

    assert response.status_code == status.HTTP_201_CREATED

def test_authenticated_editor_user_can_create_blog(editor_authenticated_client):

    blog_post_data = {
        "title": "Editor Authenticated Client",
        "body": "I hate my life.",
        "tags": ["Forever", "Hate"]
    }

    response = editor_authenticated_client.post(f"/v1/blog_posts", json = blog_post_data)

    assert response.status_code == status.HTTP_201_CREATED

def test_unauthenticated_cannot_update_blog_post(client, session):

    blog_post_data = {
        "title":"New title for my blog unauth"
    }

    blog_posts = session.exec(select(BlogPost)).all()


    blog = choice(blog_posts)

    response = client.put(f"/v1/blog_posts/{blog.id}", json = blog_post_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_authenticated_basic_user_cannot_update_blog_post(authenticated_client, session):

    blog_post_data = {
        "title":"New title for my blog fail"
    }

    blog_posts = session.exec(select(BlogPost)).all()

    blog = choice(blog_posts)


    response = authenticated_client.put(f"/v1/blog_posts/{blog.id}", json = blog_post_data)


    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_authenticated_admin_user_can_update_blog_post(admin_authenticated_client, session):

    blog_post_data = {
        "title":"New title for my blog Admin Update"
    }

    blog_posts = session.exec(select(BlogPost)).all()

    blog = choice(blog_posts)

    response = admin_authenticated_client.put(f"/v1/blog_posts/{blog.id}", json = blog_post_data)

    assert response.status_code == status.HTTP_200_OK

def test_authenticated_super_admin_can_update_blog_post(super_admin_authenticated_client, session):

    blog_post_data = {
        "title":"New title for my blog Super User Update"
    }

    blog_posts = session.exec(select(BlogPost)).all()

    blog = choice(blog_posts)

    response = super_admin_authenticated_client.put(f"/v1/blog_posts/{blog.id}", json = blog_post_data)

    assert response.status_code == status.HTTP_200_OK

    
def test_authenticated_publisher_user_can_update_blog_post(publisher_authenticated_client, session):

    blog_post_data = {
        "title":"New title for my blog Publisher Update"
    }

    blog_posts = session.exec(select(BlogPost)).all()

    blog = choice(blog_posts)

    response = publisher_authenticated_client.put(f"/v1/blog_posts/{blog.id}", json = blog_post_data)

    assert response.status_code == status.HTTP_200_OK

def test_authenticated_editor_user_can_update_blog_post(editor_authenticated_client, session):

    blog_post_data = {
        "title":"New title for my blog Editor Update"
    }

    blog_posts = session.exec(select(BlogPost)).all()

    blog = choice(blog_posts)

    response = editor_authenticated_client.put(f"/v1/blog_posts/{blog.id}", json = blog_post_data)

    assert response.status_code == status.HTTP_200_OK    

def test_unauthenticated_user_cannot_delete_blog_post(client, session):


    blog_posts = session.exec(select(BlogPost)).all()

    blog = choice(blog_posts)

    response = client.delete(f"/v1/blog_posts/{blog.id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_authenticated_user_cannot_delete_blog_post(authenticated_client, session):


    blog_posts = session.exec(select(BlogPost)).all()

    blog = choice(blog_posts)

    response = authenticated_client.delete(f"/v1/blog_posts/{blog.id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_super_user_can_delete_blog_post(super_admin_authenticated_client, session):

    blog_posts = session.exec(select(BlogPost)).all()

    blog = choice(blog_posts)

    response = super_admin_authenticated_client.delete(f"/v1/blog_posts/{blog.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT 

def test_admin_can_delete_blog_post(admin_authenticated_client, session):

    blog_posts = session.exec(select(BlogPost)).all()

    blog = choice(blog_posts)

    response = admin_authenticated_client.delete(f"/v1/blog_posts/{blog.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_editor_can_delete_blog_post(editor_authenticated_client, session):

    blog_posts = session.exec(select(BlogPost)).all()

    blog = choice(blog_posts)

    response = editor_authenticated_client.delete(f"/v1/blog_posts/{blog.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_publisher_can_delete_blog_post(publisher_authenticated_client, session):

    blog_posts = session.exec(select(BlogPost)).all()

    blog = choice(blog_posts)

    response = publisher_authenticated_client.delete(f"/v1/blog_posts/{blog.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_unauthenticated_cannot_read_draft(client, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)

    response = client.get(f"/v1/blog_posts/{blog.id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_authenticated_cannot_read_draft(client, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)

    response = client.get(f"/v1/blog_posts/{blog.id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_editor_can_read_draft(editor_authenticated_client, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)

    response = editor_authenticated_client.get(f"/v1/blog_posts/{blog.id}")

    assert response.status_code == status.HTTP_200_OK

def test_publisher_can_read_draft(publisher_authenticated_client, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)

    response = publisher_authenticated_client.get(f"/v1/blog_posts/{blog.id}")

    assert response.status_code == status.HTTP_200_OK

def test_admin_can_read_draft(admin_authenticated_client, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)

    response = admin_authenticated_client.get(f"/v1/blog_posts/{blog.id}")

    assert response.status_code == status.HTTP_200_OK

def test_super_admin_can_read_draft(super_admin_authenticated_client, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)

    response = super_admin_authenticated_client.get(f"/v1/blog_posts/{blog.id}")

    assert response.status_code == status.HTTP_200_OK

def test_unauthenticated_user_cannot_publish_blog(client, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)

    blog_post_data = {
        "publishing_status": PublishingStatus.PUBLISHED
    }
    
    response = client.put(f"/v1/blog_posts/{blog.id}/publish", json = blog_post_data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_authenticated_user_cannot_publish_blog(authenticated_client, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)

    blog_post_data = {
        "publishing_status": PublishingStatus.PUBLISHED
    }
    
    response = authenticated_client.put(f"/v1/blog_posts/{blog.id}/publish", json = blog_post_data)

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_editor_user_can_publish_blog(editor_authenticated_client, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)

    blog_post_data = {
        "publishing_status": PublishingStatus.PUBLISHED
    }
    
    response = editor_authenticated_client.put(f"/v1/blog_posts/{blog.id}/publish", json = blog_post_data)

    assert response.status_code == status.HTTP_200_OK


def test_publisher_user_can_publish_blog(publisher_authenticated_client, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)

    blog_post_data = {
        "publishing_status": PublishingStatus.PUBLISHED
    }
    
    response = publisher_authenticated_client.put(f"/v1/blog_posts/{blog.id}/publish", json = blog_post_data)

    assert response.status_code == status.HTTP_200_OK

def test_admin_user_can_publish_blog(admin_authenticated_client, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)

    blog_post_data = {
        "publishing_status": PublishingStatus.PUBLISHED
    }
    
    response = admin_authenticated_client.put(f"/v1/blog_posts/{blog.id}/publish", json = blog_post_data)

    assert response.status_code == status.HTTP_200_OK


def test_super_admin_user_can_publish_blog(super_admin_authenticated_client, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)

    blog_post_data = {
        "publishing_status": PublishingStatus.PUBLISHED
    }
    
    response = super_admin_authenticated_client.put(f"/v1/blog_posts/{blog.id}/publish", json = blog_post_data)

    assert response.status_code == status.HTTP_200_OK


def test_can_list_blog_comments(client, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)
    blog.publishing_status = PublishingStatus.PUBLISHED
    session.add(blog)
    session.commit()
    session.refresh(blog)
    
    response = client.get(f"/v1/blog_posts/{blog.id}/comments")
    
    assert response.status_code == status.HTTP_200_OK

def test_unauthenticated_cannot_create_blog_comment(client, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)
    blog.publishing_status = PublishingStatus.PUBLISHED
    session.add(blog)
    session.commit()
    session.refresh(blog)
    
    response = client.post(f"/v1/blog_posts/{blog.id}/comments", json = {"body":"Cool blog post."})
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_authenticated_can_create_blog_comment(authenticated_client, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)
    blog.publishing_status = PublishingStatus.PUBLISHED
    session.add(blog)
    session.commit()
    session.refresh(blog)
    
    response = authenticated_client.post(f"/v1/blog_posts/{blog.id}/comments", json = {"body":"Cool blog post."})
    
    assert response.status_code == status.HTTP_201_CREATED
    
def test_unauthenticated_cannot_delete_blog_comment(client, test_user, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)
    blog.publishing_status = PublishingStatus.PUBLISHED
    session.add(blog)
    session.commit()
    session.refresh(blog)

    comment = BlogComment(
        body = "Fuck",
        author_id = test_user.id,
        blog_post_id = blog.id
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)

    response = client.delete(f"/v1/blog_posts/{blog.id}/comments/{comment.id}")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_user_can_delete_own_blog_comment(authenticated_client, test_user, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)
    blog.publishing_status = PublishingStatus.PUBLISHED
    session.add(blog)
    session.commit()
    session.refresh(blog)

    comment = BlogComment(
        body = "Fuck",
        author_id = test_user.id,
        blog_post_id = blog.id
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)

    response = authenticated_client.delete(f"/v1/blog_posts/{blog.id}/comments/{comment.id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_user_can_delete_own_blog_comment(authenticated_client, test_user, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)
    blog.publishing_status = PublishingStatus.PUBLISHED
    session.add(blog)
    session.commit()
    session.refresh(blog)

    comment = BlogComment(
        body = "Fuck",
        author_id = test_user.id,
        blog_post_id = blog.id
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)

    response = authenticated_client.delete(f"/v1/blog_posts/{blog.id}/comments/{comment.id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_user_cannot_delete_other_user_blog_comment(authenticated_client, test_other_user, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)
    blog.publishing_status = PublishingStatus.PUBLISHED
    session.add(blog)
    session.commit()
    session.refresh(blog)

    comment = BlogComment(
        body = "Fuck",
        author_id = test_other_user.id,
        blog_post_id = blog.id
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)

    response = authenticated_client.delete(f"/v1/blog_posts/{blog.id}/comments/{comment.id}")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_super_admin_user_can_delete_blog_comment(super_admin_authenticated_client, test_user, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)
    blog.publishing_status = PublishingStatus.PUBLISHED
    session.add(blog)
    session.commit()
    session.refresh(blog)

    comment = BlogComment(
        body = "Fuck",
        author_id = test_user.id,
        blog_post_id = blog.id
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)

    response = super_admin_authenticated_client.delete(f"/v1/blog_posts/{blog.id}/comments/{comment.id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_admin_user_can_delete_blog_comment(admin_authenticated_client, test_user, session):

    blog_posts = session.exec(select(BlogPost).where(BlogPost.publishing_status == PublishingStatus.DRAFT)).all()

    blog = choice(blog_posts)
    blog.publishing_status = PublishingStatus.PUBLISHED
    session.add(blog)
    session.commit()
    session.refresh(blog)

    comment = BlogComment(
        body = "Fuck",
        author_id = test_user.id,
        blog_post_id = blog.id
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)

    response = admin_authenticated_client.delete(f"/v1/blog_posts/{blog.id}/comments/{comment.id}")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_unauthenticated_cannot_create_tags(client):

    response = client.post("/v1/tags", json = {
        "name": "Hate Life"
    })

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_basic_user_cannot_create_tags(authenticated_client):

    response = authenticated_client.post("/v1/tags", json = {
        "name": "Hate Life"
    })

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_admin_user_can_create_tags(admin_authenticated_client):

    response = admin_authenticated_client.post("/v1/tags", json = {
        "name": "Hate Life"
    })

    assert response.status_code == status.HTTP_201_CREATED


def test_super_admin_user_can_create_tags(super_admin_authenticated_client):

    response = super_admin_authenticated_client.post("/v1/tags", json = {
        "name": "Hate Living"
    })

    assert response.status_code == status.HTTP_201_CREATED      

def test_unauthenticated_cannot_delete_tag(client, session):

    tags = session.exec(select(BlogTag)).all()
    
    tag = choice(tags)

    response = client.delete(f"/v1/tags/{tag.slug}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_basic_user_cannot_delete_tag(authenticated_client, session):

    tags = session.exec(select(BlogTag)).all()
    
    tag = choice(tags)

    response = authenticated_client.delete(f"/v1/tags/{tag.slug}")

    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_admin_user_can_delete_tag(admin_authenticated_client, session):

    tags = session.exec(select(BlogTag)).all()
    
    tag = choice(tags)

    response = admin_authenticated_client.delete(f"/v1/tags/{tag.slug}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_super_admin_user_can_delete(super_admin_authenticated_client, session):

    tags = session.exec(select(BlogTag)).all()
    
    tag = choice(tags)

    response = super_admin_authenticated_client.delete(f"/v1/tags/{tag.slug}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

      

def test_create_blog(admin_authenticated_client):

    blog_post_data = {
        "title": "Satanic power up",
        "body": "No",
        "tags": ["Power Ups", "Puma"]
    }

    response = admin_authenticated_client.post("/v1/blog_posts", json = blog_post_data)

    assert response.status_code == status.HTTP_201_CREATED


def test_update_blog(admin_authenticated_client, session):

    blog_post = BlogPost(
        title = "I hate my life.",
        slug = slugify("I hate my life."),
        body = "You don't listen.",
        author_id = 1,
    )

    session.add(blog_post)
    session.commit()

    updated_data = {
        "title": "New title."
    }

    response = admin_authenticated_client.put(f"/v1/blog_posts/{blog_post.id}", json = updated_data)

    assert response.status_code == status.HTTP_200_OK


