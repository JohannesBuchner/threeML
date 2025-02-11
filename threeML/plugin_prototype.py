"""
Define the interface for a plugin class.
"""

import abc
from typing import Dict

from astromodels import IndependentVariable, Model
from astromodels.core.parameter import Parameter

from threeML.io.logging import invalid_plugin_name, setup_logger

log = setup_logger(__name__)
# def set_external_property(method):
#     """
#     Sets external property values if they exist
#
#
#     :param method:
#     :return:
#     """
#
#     @functools.wraps(method)
#     def wrapper(instance, *args, **kwargs):
#
#         if instance._external_properties:
#
#             for property, value in instance._external_properties:
#                 property.value = value
#
#         return method(instance, *args, **kwargs)
#
#     return wrapper


class PluginPrototype(metaclass=abc.ABCMeta):
    def __init__(self, name: str, nuisance_parameters: Dict[str, Parameter]):

        invalid_plugin_name(name, log)

        # Make sure total is not used as a name (need to use it for other things, like the total value of the statistic)

        if name.lower() == "total":

            log.error("Sorry, you cannot use 'total' as name for a plugin.")

            raise AssertionError(
                "Sorry, you cannot use 'total' as name for a plugin."
            )

        self._name: str = name

        # This is just to make sure that the plugin is legal

        if not isinstance(nuisance_parameters, dict):

            log.error("nuisance_parameters are not a dict and are invalid!")

            raise AssertionError(
                "nuisance_parameters are not a dict and are invalid!"
            )

        self._nuisance_parameters: Dict[str, Parameter] = nuisance_parameters

        # These are the external properties (time, polarization, etc.)
        # self._external_properties = []

        self._tag = None

    def get_name(self) -> str:
        log.warning(
            "Do not use get_name() for plugins, use the .name property",
        )

        return self.name

    @property
    def name(self) -> str:
        """
        Returns the name of this instance

        :return: a string (this is enforced to be a valid python identifier)
        """
        return self._name

    @property
    def nuisance_parameters(self) -> Dict[str, Parameter]:
        """
        Returns a dictionary containing the nuisance parameters for this dataset

        :return: a dictionary
        """

        return self._nuisance_parameters

    def update_nuisance_parameters(
        self, new_nuisance_parameters: Dict[str, Parameter]
    ) -> None:

        if not isinstance(new_nuisance_parameters, dict):

            log.error("nuisance_parameters are not a dict and are invalid!")

            raise AssertionError(
                "nuisance_parameters are not a dict and are invalid!"
            )

        self._nuisance_parameters = new_nuisance_parameters

    # def external_property(self, property, value):
    #     """
    #     Set external/auxiliary properties and their value
    #     :param property: an astromodels auxiliary variable
    #     :param value: the value of the auxiliary variable for this plugin
    #     :return:
    #     """
    #
    #     self._external_properties.append((property, value))

    def get_number_of_data_points(self) -> int:
        """
        This returns the number of data points that are used to evaluate the likelihood.
        For binned measurements, this is the number of active bins used in the fit. For
        unbinned measurements, this would be the number of photons/particles that are
        evaluated on the likelihood
        """

        log.warning(
            "get_number_of_data_points not implemented, values for statistical measurements such as AIC or BIC are "
            "unreliable",
        )

        return 1.0

    def _get_tag(self):

        return self._tag

    def _set_tag(self, spec):
        """
        Tag this plugin with the provided independent variable and a start and end value.

        This can be used for example to fit a time-varying model. In this case the independent variable will be the
        time and the start and end will be the start and stop time of the exposure for this plugin. These values will
        be used to average the model over the provided time interval when fitting.

        :param independent_variable: an IndependentVariable instance
        :param start: start value for this plugin
        :param end: end value for this plugin. If this is not provided, instead of integrating the model between
        start and end, the model will be evaluate at start. Default: None (i.e., not provided)
        :return: none
        """

        if len(spec) == 2:

            independent_variable, start = spec
            end = None

        elif len(spec) == 3:

            independent_variable, start, end = spec

        else:

            raise ValueError(
                "Tag specification should be (independent_variable, start[, end])"
            )

        # Let's do a lazy check

        if not isinstance(independent_variable, IndependentVariable):

            log.warning(
                "When tagging a plugin, you should use an IndependentVariable instance. You used instead "
                "an instance of a %s object. This might lead to crashes or "
                "other problems." % type(independent_variable)
            )

        self._tag = (independent_variable, start, end)

    tag = property(
        _get_tag,
        _set_tag,
        doc="Gets/sets the tag for this instance, as (independent variable, start, "
        "[end])",
    )

    ######################################################################
    # The following methods must be implemented by each plugin
    ######################################################################

    @abc.abstractmethod
    def set_model(self, likelihood_model_instance: Model):
        """
        Set the model to be used in the joint minimization. Must be a LikelihoodModel instance.
        """
        pass

    @abc.abstractmethod
    def get_log_like(self) -> float:
        """
        Return the value of the log-likelihood with the current values for the
        parameters
        """
        pass

    @abc.abstractmethod
    def inner_fit(self):
        """
        This is used for the profile likelihood. Keeping fixed all parameters in the
        LikelihoodModel, this method minimize the logLike over the remaining nuisance
        parameters, i.e., the parameters belonging only to the model for this
        particular detector. If there are no nuisance parameters, simply return the
        logLike value.
        """
        pass
