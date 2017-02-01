import collections
from astropy.units import Quantity
import warnings

from astromodels.utils.io import display
from astromodels.utils.valid_variable import is_valid_variable_name


class DuplicatedNode(Exception):
    pass


class ProtectedAttribute(RuntimeError):
    pass


class NonExistingAttribute(RuntimeWarning):
    pass


class Node(object):

    def __init__(self, name):

        self._children = collections.OrderedDict()
        self._parent = None

        assert is_valid_variable_name(name), "Illegal characters in name %s. You can only use letters and numbers, " \
                                             "and _" % name

        self._name = name

    # def __setattr__(self, key, value):
    #
    #     print("%s -> %s" % (key,value))
    #
    #     if hasattr(self, "_children"):
    #
    #         # After construction, the object has always a _children attribute and a _parameters attribute
    #
    #         # Process parameters first (they are the most important ones)
    #         if key in self._children:
    #
    #             raise ProtectedAttribute("You cannot assign to a node")
    #
    #         else:
    #
    #             # Attributes which start with "_" are created by children classes
    #
    #             if not key[0] == '_' and not hasattr(self, key):
    #
    #                 warnings.warn("Attribute %s does not exist. Check for typos." % key, NonExistingAttribute)
    #
    #             object.__setattr__(self, key, value)
    #
    #     else:
    #
    #         # We are here during construction
    #         object.__setattr__(self, key, value)

    @property
    def name(self):
        """
        Returns the name of the node

        :return: a string containing the name
        """
        return self._name

    @property
    def path(self):

        return ".".join(self._get_path())

    def _reset_node(self):

        # We need to use directly the __setattr__ method because the normal self._children = ... will trigger
        # an exception, because of the __setattr__ method of the DualAccessClass which forbids changing
        # nodes

        object.__setattr__(self, "_children", collections.OrderedDict())

        object.__setattr__(self, "_parent", None)

    def _add_children(self, children):

        for child in children:

            self._add_child(child)

    def _add_child(self, new_child, name=None, add_attribute=True):

        new_child._set_parent(self)

        if name is None:

            name = new_child.name

        if name in self._children:

            raise DuplicatedNode("You cannot use the same name (%s) for different nodes" % name)

        self._children[name] = new_child

        if add_attribute:

            # Add also an attribute with the name of the new child, to allow access with a syntax like
            # node.child

            object.__setattr__(self, name, new_child)

    def _get_child(self, child_name):

        return self._children[child_name]

    def _remove_child(self, child_name):

        object.__delattr__(self, child_name)

        return self._children.pop(child_name)

    def _set_parent(self, parent):

        # We need to use directly the __setattr__ method because the normal self._children = ... will trigger
        # an exception, because of the __setattr__ method of the DualAccessClass which forbids changing
        # nodes. However, this might reassign the parent to a class

        object.__setattr__(self, "_parent", parent)

    def _get_parent(self):

        return self._parent

    def _get_child_from_path(self, path):
        """
        Return a children below this level, starting from a path of the kind "this_level.something.something.name"

        :param path: the key
        :return: the child
        """

        keys = path.split(".")

        this_child = self

        for key in keys:

            try:

                this_child = this_child._get_child(key)

            except KeyError:

                raise KeyError("Child %s not found" % path)

        return this_child

    def _get_path(self):

        parent_names = []

        current_node = self

        while True:

            this_parent = current_node._get_parent()

            if this_parent is None:

                break

            else:

                parent_names.append(current_node.name)

                current_node = this_parent

        return parent_names[::-1]

    def to_dict(self, minimal=False):

        this_dict = collections.OrderedDict()

        for key, val in self._children.iteritems():

            this_dict[key] = val.to_dict(minimal)

        return this_dict

    def _repr__base(self, rich_output):

        raise NotImplementedError("You should implement the __repr__base method for each class")

    def __repr__(self):
        """
        Textual representation for console

        :return: representation
        """

        return self._repr__base(rich_output=False)

    def _repr_html_(self):
        """
        HTML representation for the IPython notebook

        :return: HTML representation
        """

        return self._repr__base(rich_output=True)

    def display(self):
        """
        Display information about the point source.

        :return: (none)
        """

        # This will automatically choose the best representation among repr and repr_html

        display(self)

    def _find_instances(self, cls):
        """
        Find all the instances of cls below this node.

        :return: a dictionary of instances of cls
        """

        instances = collections.OrderedDict()

        for child_name, child in self._children.iteritems():

            if isinstance(child, cls):

                key_name = ".".join(child._get_path())

                instances[key_name] = child

                # Now check if the instance has children,
                # and if it does go deeper in the tree

                # NOTE: an empty dictionary evaluate as False

                if child._children:

                    instances.update(child._find_instances(cls))

            else:

                instances.update(child._find_instances(cls))

        return instances
