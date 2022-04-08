from django import forms


class FormFieldsController:
    fields = {}
    class_name = None
    classes_excluded = []
    more_classes = {}
    placeholders = {}
    validators = []
    validators_excluded = []
    more_validators = {}
    remove_labels = []
    widgets_attrs = {}
    disable_fields = False

    def __init__(self):
        if self.disable_fields:
            self.__disable_fields()

        if self.class_name is not None:
            self._add_class()

        self._add_classes()
        self._add_placeholders()
        self._remove_labels()
        self._add_validators()
        self.__add_widgets_attrs()

    def _add_class(self):
        for field_name, field in self.fields.items():
            if field_name not in self.classes_excluded:
                if "class" not in field.widget.attrs:
                    field.widget.attrs["class"] = ""
                field.widget.attrs["class"] += f" {self.class_name} "

    def _add_classes(self):
        for field, class_name in self.more_classes.items():
            if "class" not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs["class"] = ""
            self.fields[field].widget.attrs["class"] += f" {class_name}"

    def _add_placeholders(self):
        for field, placeholder_name in self.placeholders.items():
            self.fields[field].widget.attrs["placeholder"] = placeholder_name

    def _add_validators(self):
        for field_name, field in self.fields.items():
            if not field.validators:
                field.validators = []

            if field_name not in self.validators_excluded:
                field.validators.extend(self.validators)

        for field, validators in self.more_validators.items():
            if not self.fields[field].validators:
                self.fields[field].validators = []
            self.fields[field].validators.extend(validators)

    def _remove_labels(self):
        if self.remove_labels == "__all__":
            self.remove_labels = self.fields.keys()

        for field in self.remove_labels:
            self.fields[field].label = ""

    def __disable_fields(self):
        for field in self.fields.values():
            field.disabled = True

    def __add_widgets_attrs(self):
        for field, attrs in self.widgets_attrs.items():
            if not getattr(self.fields[field].widget, "attrs"):
                self.fields[field].widget.attrs = {}

            self.fields[field].widget.attrs.update(attrs)


class FitnessCalculatorModelForm(forms.ModelForm, FormFieldsController):
    def __init__(self, *args, disable_fields=False, **kwargs):
        super(FitnessCalculatorModelForm, self).__init__(*args, **kwargs)
        self.disable_fields = disable_fields
        FormFieldsController.__init__(self)
