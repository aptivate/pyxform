from utils import node, SEP
from survey_element import SurveyElement

def _overlay(over, under):
    if type(under)==dict:
        result = under.copy()
        result.update(over)
        return result
    return over if over else under

class Question(SurveyElement):
    def get_type_definition(self):
        qtd = self.get_question_type_dictionary()
        question_type_str = self._dict[self.TYPE]
        return qtd.get_definition(question_type_str)

    def get(self, key):
        """
        Overlay this questions binding attributes on type of the
        attributes from this question type.
        """
        question_type_dict = self.get_type_definition()
        under = question_type_dict.get(key, None)
        over = SurveyElement.get(self, key)
        if not under: return over
        return _overlay(over, under)

    def xml_instance(self):
    
        if self.get(u"default"):
            return node(self.get_name(), unicode(self.get(u"default")))
        return node(self.get_name())
        
    def xml_control(self):
        return None


class InputQuestion(Question):
    """
    This control string is the same for: strings, integers, decimals,
    dates, geopoints, barcodes ...
    """
    def xml_control(self):
        control_dict = self.get_control()
        if u"appearance" in control_dict:
            return node(u"input", ref=self.get_xpath(), 
                appearance=control_dict[u"appearance"], 
                *self.xml_label_and_hint()
                )
        else:
            return node(u"input",
                ref=self.get_xpath(),
                *self.xml_label_and_hint()
                )

class TriggerQuestion(Question):

    def xml_control(self):
        control_dict = self.get_control()
        if u"appearance" in control_dict:
            return node(u"trigger", ref=self.get_xpath(), 
                appearance=control_dict[u"appearance"], 
                *self.xml_label_and_hint()
                )
        else:
            return node(u"trigger",
                ref=self.get_xpath(),
                *self.xml_label_and_hint()
                )

class UploadQuestion(Question):
    def _get_media_type(self):
        return self.get_control()[u"mediatype"]
        
    def xml_control(self):
        control_dict = self.get_control()
        if u"appearance" in control_dict:
            return node(
                u"upload",
                ref=self.get_xpath(),
                mediatype=self._get_media_type(),
                appearance=control_dict[u"appearance"],
                *self.xml_label_and_hint()
                )
        else:
            return node(
                u"upload",
                ref=self.get_xpath(),
                mediatype=self._get_media_type(),
                *self.xml_label_and_hint()
                )


class Option(SurveyElement):

    def __init__(self, *args, **kwargs):
        if kwargs.has_key(self.MEDIA):
            d = {
                self.LABEL : kwargs[self.LABEL],
                self.MEDIA : kwargs[self.MEDIA],
                self.NAME : unicode(kwargs[self.NAME]),
                }
        else:
            d = {
                self.LABEL : kwargs[self.LABEL],
                self.NAME : unicode(kwargs[self.NAME]),
                }
        SurveyElement.__init__(self, **d)

    def xml_value(self):
        return node(u"value", self.get_name())

    def xml(self):
        item = node(u"item")
        item.appendChild(self.xml_label())
        item.appendChild(self.xml_value())
        return item

    def validate(self):
        pass


class MultipleChoiceQuestion(Question):
    def __init__(self, *args, **kwargs):
        kwargs_copy = kwargs.copy()
        choices = kwargs_copy.pop(u"choices", []) + \
            kwargs_copy.pop(u"children", [])
        Question.__init__(self, *args, **kwargs_copy)
        for choice in choices:
            try:
                self.add_choice(**choice)
            except KeyError:
                raise KeyError("An option for this question is missing a name or a label.", kwargs)
        
    def validate(self):
        Question.validate(self)
        for choice in self.iter_children():
            if choice!=self: choice.validate()
        
    def add_choice(self, **kwargs):
        option = Option(**kwargs)
        self.add_child(option)

    def xml_control(self):
        assert self.get_bind()[u"type"] in [u"select", u"select1"]

        control_dict = self.get_control()
        if u"appearance" in control_dict:
            result = node(
                self.get_bind()[u"type"],
                ref=self.get_xpath(),
                appearance=control_dict[u"appearance"]
                )
        else:
            result = node(
                self.get_bind()[u"type"],
                ref=self.get_xpath()
                )
        for n in self.xml_label_and_hint():
            result.appendChild(n)
        for n in [o.xml() for o in self._children]:
            result.appendChild(n)                
        return result

class SelectOneQuestion(MultipleChoiceQuestion):
    def __init__(self, *args, **kwargs):
        super(SelectOneQuestion, self).__init__(*args, **kwargs)
        self._dict[self.TYPE] = u"select one"
