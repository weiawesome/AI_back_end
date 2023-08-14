from webargs import fields, validate
def validate_password(value):
    if len(value) < 8 or len(value) > 30:
        raise validate.ValidationError("Password must be between 8 and 30 characters.")
    if value.strip() == "":
        raise validate.ValidationError("Password cannot contain only whitespace.")
    return value
def validate_name(value):
    if not value.strip():
        raise validate.ValidationError("Name cannot be empty or contain only whitespace.")
    if len(value) > 50:
        raise validate.ValidationError("Name cannot exceed 50 characters.")
    if value.startswith(' ') or value.endswith(' '):
        raise validate.ValidationError("Name cannot start or end with whitespace.")
    return value.strip()
def validate_empty(value):
    if not value.strip():
        raise validate.ValidationError("Content cannot be empty or contain only whitespace.")
    return value
def validate_gender(value):
    valid_genders = ["male", "female", "other"]
    if value not in valid_genders:
        raise validate.ValidationError("Gender must be one of 'male', 'female', or 'other'.")
    return value

Signup_args = {
    "name": fields.Str(required=True, validate=validate_name),
    "gender": fields.Str(required=True, validate=validate_gender),
    "mail": fields.Email(required=True),
    "password": fields.Str(required=True, validate=validate_password),
}

Login_args={
    "mail":fields.Email(required=True),
    "password": fields.Str(required=True,validate=validate_password)
}

Edit_args={
    "prompt":fields.Str(required=True),
    "content":fields.Str(required=True,validate=validate_empty)
}

Access_token_args={
    "access_token":fields.Str(required=True,validate=validate_empty),
    "aes_key":fields.Str(required=True,validate=validate_empty)
}

Api_key_args={
    "api_key":fields.Str(required=True, validate=validate_empty),
    "aes_key":fields.Str(required=True,validate=validate_empty)
}

Email_args={
    "mail":fields.Str(required=True)
}

Information_args={
    "name": fields.Str(required=True, validate=validate_name),
    "gender": fields.Str(required=True, validate=validate_gender)
}
Password_Edit_args={
    "current_password":fields.Str(required=True,validate=validate_password),
    "edit_password":fields.Str(required=True,validate=validate_password)
}
OCR_Text_args={
    "prompt":fields.Str(required=True),
    "content":fields.Str(required=True,validate=validate_empty)
}