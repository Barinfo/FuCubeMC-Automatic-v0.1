# Example Usages

```
GET http://<Your Panel Address>
Content-Type: application/json; charset=utf-8
```

## User registration

```http
POST /api/reg
```

### Query Param

支持json传入或form-data

```js
{
    password: string,
    confirmPassword: string, //确认密码
    email: string
}
```

### Response

#### HTTP 200

```json
{
    "message": "注册成功，请前往邮箱验证"
}
```

#### Other

```json
{
    "error": "缺少传参"
}
```

## User Login

```http
POST /api/login
```

### Query Param

支持json传入或form-data

```js
{
    password: string,
    email: string
}
```

### Response

#### HTTP 200

```json
{
    "message": "登录成功",
    "points": 114514, //当前积分(签到后)
    "token": "da84b654-a6dc-4c3b-8448-7b4acf9c3bdc"
}
```

#### Other

```json
{
    "error": "缺少用户名或密码"
}
```

## User Login

```http
POST /api/login
```

### Query Param

支持json传入或form-data

```js
{
    token: string,
    email: string
}
```

### Response

#### HTTP 200

```json
{
    "message": "签到成功",
    "points": 1002, //当前积分(签到后)
    "add": 2 //获得积分
}
```

#### Other

```json
{
    "error": "身份验证失败"
}
```