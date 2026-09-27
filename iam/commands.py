import dataclasses


@dataclasses.dataclass(frozen=True)
class SignupCommand:
    username: str
    password: str
