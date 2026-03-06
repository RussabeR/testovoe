from unittest.mock import MagicMock, AsyncMock

import pytest
from src.exceptions.exceptions import PostNotFoundException, UserNotFoundException, PostAlreadyExistException, \
    ObjectNotFoundException
from src.schemas.post_schemas import PostOUT, PostCreateRequest




@pytest.mark.asyncio
async def test_get_all_posts(posts_service, mock_db):

    post = MagicMock()
    post.id = 1
    post.title = "First Post"
    post.content = "Test content"

    post2 = MagicMock()
    post2.id = 2
    post2.title = "Second Post"
    post2.content = "Second content"


    mock_db.posts.get_filtered = AsyncMock(return_value=[post, post2])

    result = await posts_service.get_all_posts()

    assert len(result) == 2
    assert all(isinstance(p, PostOUT) for p in result)

    assert result[0].title == "First Post"
    assert result[1].title == "Second Post"

    mock_db.posts.get_filtered.assert_called_once_with(skip=0, limit=20)


@pytest.mark.asyncio
async def test_get_user_posts_no_cache(posts_service, mock_db):
    posts_service.post_cache = None

    post1 = MagicMock()
    post1.id = 1
    post1.user_id = 1
    post1.title = "First Post"
    post1.content = "Content 1"

    post2 = MagicMock()
    post2.id = 2
    post2.user_id = 1
    post2.title = "Second Post"
    post2.content = "Content 2"

    mock_db.posts.get_filtered = AsyncMock(return_value=[post1, post2])

    result = await posts_service.get_user_posts(user_id=1)

    assert len(result) == 2
    assert all(isinstance(p, PostOUT) for p in result)
    assert result[0].title == "First Post"
    assert result[1].title == "Second Post"

    mock_db.posts.get_filtered.assert_called_once_with(user_id=1)


@pytest.mark.asyncio
async def test_get_user_posts_with_cache(posts_service, mock_db):
    posts_service.post_cache = AsyncMock()
    cached_data = [
        {"id": 1, "user_id": 1, "title": "Cached Post 1", "content": "Content 1"},
        {"id": 2, "user_id": 1, "title": "Cached Post 2", "content": "Content 2"},
    ]

    posts_service.post_cache.get_or_set_user_posts.return_value = cached_data

    result = await posts_service.get_user_posts(user_id=1)

    assert len(result) == 2
    assert all(isinstance(p, PostOUT) for p in result)
    assert result[0].title == "Cached Post 1"
    assert result[1].title == "Cached Post 2"

    posts_service.post_cache.get_or_set_user_posts.assert_awaited_once()



@pytest.mark.asyncio
async def test_get_user_post_by_id_no_cache_found(posts_service, mock_db):
    posts_service.post_cache = None

    post = MagicMock()
    post.id = 1
    post.user_id = 1
    post.title = "My Post"
    post.content = "Content"

    mock_db.posts.get_one = AsyncMock(return_value=post)

    result = await posts_service.get_user_post_by_id(user_id=1, post_id=1)

    assert isinstance(result, PostOUT)
    assert result.id == 1
    assert result.title == "My Post"

    mock_db.posts.get_one.assert_called_once_with(id=1, user_id=1)



@pytest.mark.asyncio
async def test_get_user_post_by_id_no_cache_not_found(posts_service, mock_db):
    posts_service.post_cache = None

    mock_db.posts.get_one = AsyncMock(side_effect=ObjectNotFoundException)

    import pytest
    from src.exceptions.exceptions import PostNotFoundException

    with pytest.raises(PostNotFoundException):
        await posts_service.get_user_post_by_id(user_id=1, post_id=1)

    mock_db.posts.get_one.assert_called_once_with(id=1, user_id=1)



@pytest.mark.asyncio
async def test_get_user_post_by_id_cache_hit(posts_service, mock_db):

    posts_service.post_cache = AsyncMock()

    cached_data = {"id": 1, "user_id": 1, "title": "Cached Post", "content": "Content"}

    posts_service.post_cache.get_or_set_user_post.return_value = cached_data

    result = await posts_service.get_user_post_by_id(user_id=1, post_id=1)

    assert isinstance(result, PostOUT)
    assert result.title == "Cached Post"


    posts_service.post_cache.get_or_set_user_post.assert_awaited_once()




@pytest.mark.asyncio
async def test_get_user_post_by_id_cache_miss_not_found(posts_service, mock_db):

    posts_service.post_cache = AsyncMock()

    async def get_one_raise(*args, **kwargs):
        raise ObjectNotFoundException()

    mock_db.posts.get_one = AsyncMock(side_effect=get_one_raise)

    async def side_effect(u_id, post_id, loader):
        return await loader()

    posts_service.post_cache.get_or_set_user_post.side_effect = side_effect

    with pytest.raises(PostNotFoundException):
        await posts_service.get_user_post_by_id(user_id=1, post_id=1)

    posts_service.post_cache.get_or_set_user_post.assert_awaited_once()




@pytest.mark.asyncio
async def test_add_post_user_not_found(posts_service, mock_db):
    mock_db.users.exists = AsyncMock(return_value=False)

    data = PostCreateRequest(title="Test", content="Content")

    with pytest.raises(UserNotFoundException):
        await posts_service.add_post(user_id=1, data=data)

    mock_db.users.exists.assert_awaited_once_with(id=1)


@pytest.mark.asyncio
async def test_add_post_already_exists(posts_service, mock_db):
    mock_db.users.exists = AsyncMock(return_value=True)
    mock_db.posts.exists = AsyncMock(return_value=True)

    data = PostCreateRequest(title="Test", content="Content")

    with pytest.raises(PostAlreadyExistException):
        await posts_service.add_post(user_id=1, data=data)

    mock_db.users.exists.assert_awaited_once_with(id=1)
    mock_db.posts.exists.assert_awaited_once_with(user_id=1, title="Test")



@pytest.mark.asyncio
async def test_add_post_success_no_cache(posts_service, mock_db):
    posts_service.post_cache = None

    mock_db.users.exists = AsyncMock(return_value=True)
    mock_db.posts.exists = AsyncMock(return_value=False)

    post_mock = MagicMock()
    post_mock.id = 1
    post_mock.user_id = 1
    post_mock.title = "New Post"
    post_mock.content = "Content"
    mock_db.posts.add = AsyncMock(return_value=post_mock)

    mock_db.commit = AsyncMock()

    from src.schemas.post_schemas import PostCreateRequest

    data = PostCreateRequest(title="New Post", content="Content")
    result = await posts_service.add_post(user_id=1, data=data)

    assert isinstance(result, PostOUT)
    assert result.id == 1
    assert result.title == "New Post"

    mock_db.users.exists.assert_awaited_once_with(id=1)
    mock_db.posts.exists.assert_awaited_once_with(user_id=1, title="New Post")
    mock_db.posts.add.assert_awaited_once()
    mock_db.commit.assert_awaited_once()



@pytest.mark.asyncio
async def test_add_post_success_with_cache(posts_service, mock_db):
    posts_service.post_cache = AsyncMock()

    mock_db.users.exists = AsyncMock(return_value=True)
    mock_db.posts.exists = AsyncMock(return_value=False)

    post_mock = MagicMock()
    post_mock.id = 1
    post_mock.user_id = 1
    post_mock.title = "New Post"
    post_mock.content = "Content"
    mock_db.posts.add = AsyncMock(return_value=post_mock)
    mock_db.commit = AsyncMock()

    from src.schemas.post_schemas import PostCreateRequest

    data = PostCreateRequest(title="New Post", content="Content")
    result = await posts_service.add_post(user_id=1, data=data)

    assert isinstance(result, PostOUT)
    assert result.title == "New Post"

    mock_db.users.exists.assert_awaited_once_with(id=1)
    mock_db.posts.exists.assert_awaited_once_with(user_id=1, title="New Post")
    mock_db.posts.add.assert_awaited_once()
    mock_db.commit.assert_awaited_once()

    posts_service.post_cache.invalidate_user_posts.assert_awaited_once_with(1)



@pytest.mark.asyncio
async def test_delete_post_not_found(posts_service, mock_db):
    mock_db.posts.get_one_or_none = AsyncMock(return_value=None)

    from src.exceptions.exceptions import PostNotFoundException
    import pytest

    with pytest.raises(PostNotFoundException):
        await posts_service.delete_post(user_id=1, post_id=1)

    mock_db.posts.get_one_or_none.assert_awaited_once_with(id=1)



@pytest.mark.asyncio
async def test_delete_post_permission_error(posts_service, mock_db):
    post_mock = MagicMock()
    post_mock.id = 1
    post_mock.user_id = 2
    mock_db.posts.get_one_or_none = AsyncMock(return_value=post_mock)

    from src.exceptions.exceptions import PermissionErrorException
    import pytest

    with pytest.raises(PermissionErrorException):
        await posts_service.delete_post(user_id=1, post_id=1)

    mock_db.posts.get_one_or_none.assert_awaited_once_with(id=1)



@pytest.mark.asyncio
async def test_delete_post_success_no_cache(posts_service, mock_db):
    posts_service.post_cache = None

    post_mock = MagicMock()
    post_mock.id = 1
    post_mock.user_id = 1
    mock_db.posts.get_one_or_none = AsyncMock(return_value=post_mock)
    mock_db.posts.delete = AsyncMock()
    mock_db.commit = AsyncMock()

    result = await posts_service.delete_post(user_id=1, post_id=1)

    assert result == {"status": "ok", "message": "Пост 1 удален"}
    mock_db.posts.get_one_or_none.assert_awaited_once_with(id=1)
    mock_db.posts.delete.assert_awaited_once_with(id=1)
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_post_success_with_cache(posts_service, mock_db):
    posts_service.post_cache = AsyncMock()

    post_mock = MagicMock()
    post_mock.id = 1
    post_mock.user_id = 1
    mock_db.posts.get_one_or_none = AsyncMock(return_value=post_mock)
    mock_db.posts.delete = AsyncMock()
    mock_db.commit = AsyncMock()

    result = await posts_service.delete_post(user_id=1, post_id=1)

    assert result == {"status": "ok", "message": "Пост 1 удален"}


    mock_db.posts.get_one_or_none.assert_awaited_once_with(id=1)
    mock_db.posts.delete.assert_awaited_once_with(id=1)
    mock_db.commit.assert_awaited_once()
    posts_service.post_cache.invalidate_post.assert_awaited_once_with(1, 1)