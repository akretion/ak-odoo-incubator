from odoo.tools.float_utils import float_repr, float_round


def json_float_round(value, precision_digits, rounding_method="HALF-UP"):
    """Not suitable for float calculations! Similar to float_repr except that it
    returns a float suitable for json dump

    This may be necessary to produce "exact" representations of rounded float
    values during serialization, such as what is done by `json.dumps()`.
    Unfortunately `json.dumps` does not allow any form of custom float representation,
    nor any custom types, everything is serialized from the basic JSON types.

    :param int precision_digits: number of fractional digits to round to.
    :param rounding_method: the rounding method used: 'HALF-UP', 'UP' or 'DOWN',
           the first one rounding up to the closest number with the rule that
           number>=0.5 is rounded up to 1, the second always rounding up and the
           latest one always rounding down.
    :return: a rounded float value that must not be used for calculations, but
             is ready to be serialized in JSON with minimal chances of
             representation errors.
    """
    rounded_value = float_round(
        value, precision_digits=precision_digits, rounding_method=rounding_method
    )
    rounded_repr = float_repr(rounded_value, precision_digits=precision_digits)
    # As of Python 3.1, rounded_repr should be the shortest representation for our
    # rounded float, so we create a new float whose repr is expected
    # to be the same value, or a value that is semantically identical
    # and will be used in the json serialization.
    # e.g. if rounded_repr is '3.1750', the new float repr could be 3.175
    # but not 3.174999999999322452.
    # Cfr. bpo-1580: https://bugs.python.org/issue1580
    return float(rounded_repr)
