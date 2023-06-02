from webargs import fields, validate
Signup_args = {
    "name": fields.Str(required=True),
    "gender": fields.Str(required=True),
    "mail": fields.Email(required=True),
    "password": fields.Str(required=True, validate=validate.Length(min=6)),
}

Login_args={
    "mail":fields.Email(required=True),
    "password": fields.Str(required=True, validate=validate.Length(min=6)),
}

Edit_args={
    "prompt":fields.Str(required=True),
    "content":fields.Str(required=True)
}

Access_token_args={
    "access_token":fields.Str(required=True),
    "AES_key":fields.Str(required=True)
}

Api_key_args={
    "api_key":fields.Str(required=True),
    "AES_key":fields.Str(required=True)
}

Email_args={
    "mail":fields.Str(required=True)
}