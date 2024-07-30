### `Auth` 类使用教程

#### 介绍
`Auth` 类提供了多种静态方法来处理用户认证和信息检索。这些方法可以用于验证用户凭据、获取用户信息以及管理会话令牌。

#### 方法说明

##### `get_id_by_reg_email(email: str) -> str`
- **用途**: 根据注册时使用的电子邮件地址获取用户ID。
- **参数**: 
  - `email`: 注册时使用的电子邮件地址。
- **返回**: 用户ID。

##### `get_name_by_email(email: str) -> str`
- **用途**: 根据电子邮件地址获取用户名。
- **参数**: 
  - `email`: 当前用户的电子邮件地址。
- **返回**: 用户名。

##### `get_name_by_id(id: int) -> str`
- **用途**: 根据用户ID获取用户名。
- **参数**: 
  - `id`: 用户ID。
- **返回**: 用户名。

##### `get_info(id: int) -> dict`
- **用途**: 根据用户ID获取详细的用户信息。
- **参数**: 
  - `id`: 用户ID。
- **返回**: 包含用户详细信息的字典。

##### `is_email(email: str) -> bool`
- **用途**: 验证给定的字符串是否为有效的电子邮件地址。
- **参数**: 
  - `email`: 待验证的电子邮件地址。
- **返回**: 如果电子邮件地址有效则返回`True`，否则返回`False`。

##### `load_salt() -> bytes`
- **用途**: 加载或生成用于密码哈希的盐值。
- **返回**: 盐值。

##### `is_token_valid(token: str, id: str) -> bool`
- **用途**: 验证给定的令牌是否有效。
- **参数**: 
  - `token`: 待验证的令牌。
  - `id`: 对应的用户ID。
- **返回**: 如果令牌有效则返回`True`，否则返回`False`。

##### `get_token() -> str`
- **用途**: 从请求中获取令牌。
- **返回**: 令牌值，如果没有找到则返回`None`。

##### `set_cookies_and_return_body(cookie_dict: dict, body) -> object`
- **用途**: 设置cookie并返回响应体。
- **参数**: 
  - `cookie_dict`: 包含要设置为cookie的键值对的字典。
  - `body`: 要作为响应体返回的内容。
- **返回**: 设置了cookie并携带响应体的Flask响应对象。

##### `get_hash_password(password: str) -> bytes`
- **用途**: 使用bcrypt生成密码的哈希值。
- **参数**: 
  - `password`: 明文密码。
- **返回**: 密码的哈希值。

#### 使用示例

```python
# 获取用户ID
user_id = Auth.get_id_by_reg_email('example@domain.com')

# 获取用户名
username = Auth.get_name_by_email('example@domain.com')

# 验证电子邮件格式
is_valid_email = Auth.is_email('invalid-email.com')

# 验证令牌
token_valid = Auth.is_token_valid('token-string', 'user-id')

# 生成密码哈希
hashed_password = Auth().get_hash_password('my-secret-password')