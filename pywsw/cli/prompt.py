from typing import overload

from rich.console import Console
from rich.prompt import DefaultType, InvalidResponse, PromptBase, PromptType
from rich.text import Text, TextType


class WSWPromptBase(PromptBase[PromptType]):
    field_width: int

    @overload
    def __init__(
        self,
        prompt: TextType = "",
        *,
        field_width: int = 60,
        console: Console | None = None,
        password: bool = False,
        choices: list[str] | None = None,
        case_sensitive: bool = True,
        show_default: bool = True,
        show_choices: bool = True,
    ) -> None: ...
    def __init__(self, *args, field_width: int = 60, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_width = field_width

    def make_prompt(self, default: DefaultType) -> Text:
        txt = super().make_prompt(default)
        if len(txt) < self.field_width:
            txt.align("right", self.field_width)
        return txt


class Prompt(WSWPromptBase[str]):
    response_type = str

    @overload
    def __init__(
        self,
        prompt: TextType = "",
        *,
        field_width: int = 60,
        console: Console | None = None,
        password: bool = False,
        choices: list[str] | None = None,
        case_sensitive: bool = True,
        show_default: bool = True,
        show_choices: bool = True,
    ) -> None: ...
    def __init__(self, *args, **kwargs):
        kwargs["case_sensitive"] = False
        super().__init__(*args, **kwargs)

    @property
    def short_choices(self) -> dict[str, str]:
        out: dict[str, str] = {}
        if self.choices:
            for qi in self.choices:
                for n in range(len(qi)):
                    qqi = qi[: n + 1].lower()
                    if qqi not in [
                        j[: n + 1].lower() for j in self.choices if j != qi
                    ]:
                        out[qqi] = qi
                        break
        return out

    def make_prompt(self, default: DefaultType) -> Text:
        prompt = self.prompt.copy()
        prompt.end = ""

        if self.show_choices and self.choices:
            if short_choices := self.short_choices:
                choice_strs: list[str] = [
                    v.lower().replace(k, k.upper(), count=1)
                    for k, v in short_choices.items()
                ]
            else:
                choice_strs = [k.lower() for k in self.choices]

            if choice_strs:
                _choices = ",".join(choice_strs)
                choices = f"[{_choices}]"
                prompt.append(" ")
                prompt.append(choices, "prompt.choices")

        if (
            default != ...
            and self.show_default
            and isinstance(default, (str, self.response_type))
        ):
            prompt.append(" ")
            _default = self.render_default(default)
            prompt.append(_default)

        prompt.append(self.prompt_suffix)
        prompt.align("right", self.field_width)
        return prompt

    def process_response(self, value: str) -> PromptType:
        value = self.short_choices.get(value.strip().lower(), value)
        return super().process_response(value)


class FloatPrompt(WSWPromptBase[float]):
    response_type = float
    validate_error_message = "[prompt.invalid]Please enter a number"


class IntPrompt(WSWPromptBase[int]):
    response_type = int
    validate_error_message = (
        "[prompt.invalid]Please enter a valid integer number"
    )


class Confirm(WSWPromptBase[bool]):
    response_type = bool
    validate_error_message = "[prompt.invalid]Please enter Y or N"
    choices: list[str] = ("y", "n")

    def render_default(self, default: DefaultType) -> Text:
        """Render the default as (y) or (n) rather than True/False."""
        yes, no = self.choices
        return Text(
            f"({yes})" if default else f"({no})", style="prompt.default"
        )

    def process_response(self, value: str) -> bool:
        """Convert choices to a bool."""
        value = value.strip().lower()
        if value not in self.choices:
            raise InvalidResponse(self.validate_error_message)
        return value == self.choices[0]
