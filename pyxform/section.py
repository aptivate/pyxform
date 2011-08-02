from question import SurveyElement
from utils import node

class Section(SurveyElement):
    def validate(self):
        super(Section, self).validate()
        for element in self._children:
            element.validate()
        self._validate_uniqueness_of_element_names()

    # there's a stronger test of this when creating the xpath
    # dictionary for a survey.
    def _validate_uniqueness_of_element_names(self):
        element_slugs = []
        for element in self._children:
            if element.get_name() in element_slugs:
                raise Exception(
                    "Element with this name already exists.",
                    element_slugs, element.get_name()
                    )
            element_slugs.append(element.get_name())

    def xml_instance(self):
        if type(self) == RepeatingSection:
            kwargs = {"jr:template": ""}
        else:
            kwargs = {}

        result = None

        if not self.get(u"type") == u"group":
            result = node(self.get_name(), **kwargs)
        #print self.get_name()
        #print self.get(u"type")
        for child in self._children:
            if not result:
                result = child.xml_instance()
            else:
                result.appendChild(child.xml_instance())
        return result

    def xml_control(self):
        """
        Ideally, we'll have groups up and rolling soon, but for now
        let's just return a list of controls from all the children of
        this section.
        """
        return [e.xml_control() for e in self._children if e.xml_control() is not None]

class RepeatingSection(Section):
    def xml_control(self):
        """
        <group>
        <label>Fav Color</label>
        <repeat nodeset="fav-color">
          <select1 ref=".">
            <label ref="jr:itext('fav')" />
            <item><label ref="jr:itext('red')" /><value>red</value></item>
            <item><label ref="jr:itext('green')" /><value>green</value></item>
            <item><label ref="jr:itext('yellow')" /><value>yellow</value></item>
          </select1>
        </repeat>
        </group>
        """
        control_dict = self.get_control()
        if u"appearance" in control_dict:
            repeat_node = node(u"repeat", 
            nodeset=self.get_xpath(),
            appearance=control_dict[u"appearance"]
            )
        else:
            repeat_node = node(u"repeat", nodeset=self.get_xpath())
        for n in Section.xml_control(self):
            repeat_node.appendChild(n)
        return node(
            u"group",
            self.xml_label(),
            repeat_node
            )

class LogicalGroupedSection(Section):
    def xml_control(self):
        control_dict = self.get_control()
        if u"appearance" in control_dict:
            group_node = node(u"group",
                 self.xml_label(), 
                 nodeset=self.get_xpath(), 
                 appearance=control_dict[u"appearance"]
                 )
        else:
            group_node = node(u"group", self.xml_label(), nodeset=self.get_xpath())
        for n in Section.xml_control(self):
            group_node.appendChild(n)
        return group_node

    def to_dict(self):
        # This is quite hacky, might want to think about a smart way
        # to approach this problem.
        result = super(GroupedSection, self).to_dict()
        result[u"type"] = u"lgroup"
        return result

class GroupedSection(Section):
    def xml_control(self):
        control_dict = self.get_control()
        if u"appearance" in control_dict:
            group_node = node(u"group",
                 self.xml_label(), 
                 nodeset=self.get_xpath(), 
                 appearance=control_dict[u"appearance"]
                 )
        else:
            group_node = node(u"group", self.xml_label(), nodeset=self.get_xpath())
        for n in Section.xml_control(self):
            group_node.appendChild(n)
        return group_node

    def to_dict(self):
        # This is quite hacky, might want to think about a smart way
        # to approach this problem.
        result = super(GroupedSection, self).to_dict()
        result[u"type"] = u"group"
        return result
