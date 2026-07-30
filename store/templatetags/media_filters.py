from django import template

register = template.Library()


@register.filter
def video_mime_type(file_field):
    """Return the correct <source type="..."> for a product video based on
    its file extension, so both .mp4 and .webm uploads render correctly."""

    if not file_field:
        return "video/mp4"

    name = getattr(file_field, "name", "") or ""
    name = name.lower()

    if name.endswith(".webm"):
        return "video/webm"

    return "video/mp4"
