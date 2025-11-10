from django.contrib.auth.base_user import BaseUserManager


class MyUserManager(BaseUserManager):
    def create_user(self, login, email, phone, password=None, **extra_fields):
        if not login:
            raise ValueError("Login is required.")
        if not email:
            raise ValueError("Email is required.")
        if not phone:
            raise ValueError("Phone number is required.")

        email = self.normalize_email(email)

        user = self.model(login=login, email=email, phone=phone, **extra_fields)

        user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self, login, email="1337", phone=1337, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(
            login=login,
            email=email,
            phone=phone,
            password=password,
            **extra_fields,
        )
