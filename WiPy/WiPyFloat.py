# WiPyFloat.py
# Last modified: 27 Aug 2016

# J.G.Davies, Jacobus Systems Ltd., Brighton & Hove, UK.
# This code is hereby released as Public Domain.  I would appreciate an acknowledgement if you find it useful.


class Float():

    mantissa = 0
    exponent = 0


    def __init__(self, f=None):
        if f:
            if (type(f).__name__ == "Float"):
                self.mantissa = f.mantissa
                self.exponent = f.exponent
            elif (type(f).__name__ == "int"):
                self.mantissa = int(f)
                self.exponent = 0
            elif (type(f).__name__ == "str"):
                self.load(str(f))

            self.normalise()

        return

    # Operator overloads.

    def __abs__(self):
        result = Float(self)
        result.mantissa = abs(result.mantissa)
        return result

    def __add__(self, other):
        return Float.add(self, other)

    def __eq__(self, other):
        self.normalise()
        other.normalise()
        return (self.mantissa == other.mantissa) and (self.exponent == other.exponent)

    def __mul__(self, other):
        return Float.multiply(self, other)

    def __neg__(self):
        result = Float(self)
        result.mantissa = -result.mantissa
        return result

    def __pos__(self):
        return Float(self)

    def __str__(self):
        return self.str()

    def __sub__(self, other):
        return Float.subtract(self, other)

    def __truediv__(self, other):
        return Float.divide(self, other)


    # Static methods.

    @staticmethod
    def add(f1, f2):
        # Return a new Float holding (f1 + f2).
        result = Float(f1)
        result.add_float(f2)
        return result

    @staticmethod
    def divide(f1, f2):
        # Return a new Float holding (f1 / f2).
        result = Float(f1)
        result.divide_float(f2)
        return result

    @staticmethod
    def multiply(f1, f2):
        # Return a new Float holding (f1 * f2).
        result = Float(f1)
        result.multiply_float(f2)
        return result

    @staticmethod
    def subtract(f1, f2):
        # Return a new Float holding (f1 - f2).
        result = Float(f1)
        result.subtract_float(f2)
        return result


    # Methods.
    def add_float(self, f, add=True):
        # Add Float 'f' to this Float.

        # Align the exponents.
        self_mantissa = self.mantissa
        self_exponent = self.exponent
        f_mantissa = f.mantissa
        f_exponent = f.exponent

        if (f_exponent < self_exponent):
            shift = self_exponent - f_exponent
            self_mantissa *= 10 ** shift
            self_exponent -= shift
        elif (f_exponent > self_exponent):
            shift = f_exponent - self_exponent
            f_mantissa *= 10 ** shift
            f_exponent -= shift

        if add:
            self.mantissa = self_mantissa + f_mantissa
        else:
            self.mantissa = self_mantissa - f_mantissa

        self.exponent = self_exponent
        self.normalise()

        return self

    def debug(self):
        s = "Float: {0}, {1}".format(self.mantissa, self.exponent)
        return s

    def divide_float(self, f):
        # Divide this Float by 'f'.
        self.mantissa *= 100000000
        self.exponent -= 8

        self.mantissa //= f.mantissa
        self.exponent -= f.exponent
        self.normalise()

        return self

    def int(self):
        result = 0
        return result

    def load(self, s):
        s = s.strip().lower()
        pos = True

        if (s[0] == "+"):
            s = s[1:]
        elif (s[0] == "-"):
            s = s[1:]
            pos = False

        if "e" in s:
            return self.load_scientific(s, pos)

        if "." in s:
            whole, decimal = s.split(".")

            if not decimal:
                # There is no decimal part.
                # TODO: if 'whole' ends in zeros, could scale the number and set self.exponent.
                # This would help keep 'mantissa' a simple 31-bit int on the WiPy.
                self.mantissa = int(whole)
                if not pos: self.mantissa = -self.mantissa
                self.exponent = 0
                self.normalise()
                return True

            # There is a decimal part.
            if whole and (int(whole) == 0):
                whole = None

            if not whole:
                # There is no whole part.
                value, nleading = self.parse_decimal(decimal)
                if value:
                    self.mantissa = int(value)
                    if not pos: self.mantissa = -self.mantissa
                    self.exponent = -nleading - len(value)
                    self.normalise()
                else:
                    self.mantissa = 0
                    self.exponent = 0
                return True

            # There is a whole part and a decimal part.
            whole = whole.lstrip("0")
            decimal = decimal.rstrip('0')
            self.mantissa = int(whole + decimal)
            if not pos: self.mantissa = -self.mantissa
            self.exponent = -len(str(decimal))
            self.normalise()
        else:
            # TODO: if 'whole' ends in zeros, could scale the number and set self.exponent.
            # This would help keep 'mantissa' a simple 31-bit int on the WiPy.
            self.mantissa = int(s)
            if not pos: self.mantissa = -self.mantissa
            self.exponent = 0
            self.normalise()

        return True

    def multiply_float(self, f):
        # Multiply this Float by 'f'.
        self.mantissa *= f.mantissa
        self.exponent += f.exponent
        self.normalise()
        return self

    def normalise(self):
        # Normalise where possible.
        if (self.mantissa != 0):
            s = str(self.mantissa)
            stripped = s.rstrip("0")
            diff = len(s) - len(stripped)

            if (diff > 0):
                self.mantissa = int(stripped)
                self.exponent += diff

        return True

    def str(self, format="F"):
        if ("E" in format):
            return self.str_scientific()

        # Use format "F".
        pos = (self.mantissa >= 0)
        result = str(abs(self.mantissa))

        if (self.exponent > 0):
            result += "0" * self.exponent
        elif (self.exponent < 0):
            if (-self.exponent < len(result)):
                cut = len(result) + self.exponent
                result = result[:cut] + "." + result[cut:]
            else:
                n_zeros = -self.exponent - len(result)
                result = "0." + ("0" * n_zeros) + result

        if not pos: result = "-" + result

        return result

    def subtract_float(self, f):
        # Subtract Float 'f' from this Float.
        return self.add_float(f, False)


    # Helper methods.

    def load_scientific(self, s, pos):
        mant, exp = s.split("e")
        self.load(mant)
        self.exponent += int(exp)
        self.normalise()

        return False

    def parse_decimal(self, s):
        nleading = 0

        for c in s:
            if (c != "0"): break
            nleading += 1

        if (nleading == 0):
            value = s
        else:
            value = s[nleading:]

        return value, nleading

    def str_scientific(self):
        pos = (self.mantissa >= 0)
        result = str(abs(self.mantissa))
        len_mantissa = len(result)

        if (len(result) > 1):
            result = result[:1] + "." + result[1:]
            result = result.rstrip("0")
            result = result.rstrip(".")

        result += "e" + str(self.exponent + len_mantissa - 1)

        if not pos: result = "-" + result

        return result


if (__name__ == "__main__" ):
    import Float_tests
