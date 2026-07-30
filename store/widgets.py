from django import forms


class RichTextEditorWidget(forms.Textarea):
    """
    A dependency-free rich text editor for the Django admin.

    Renders the normal <textarea> (kept in the DOM but hidden) plus a
    toolbar + contenteditable surface. The contenteditable's HTML is
    synced back into the textarea on every change and right before the
    form submits, so nothing extra is needed server-side — Django just
    sees a normal TextField value.
    """

    template_name = "admin/widgets/richtext_editor.html"

    class Media:
        css = {"all": ("store/admin/richtext.css",)}
        js = ("store/admin/richtext.js",)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["richtext_id"] = f"richtext-{name}"
        return context
