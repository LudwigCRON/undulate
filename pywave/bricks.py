#!/usr/bin/env python3
# spell-checker: disable

"""
bricks.py declare the basic building block
to generate a waveform
"""

import pywave
from enum import Enum, unique


@unique
class BRICKS(Enum):
    """
    BRICKS enumerate the different allowed block
    and symbol to describe a waveform

    It defines the mapping between symbols and their
    character representation inside the input file
    """
    repeat = '.'#: repeat the previous character
    nclk = "n"  #: falling edge clock without arrow
    pclk = "p"  #: rising edge clock without arrow
    Nclk = "N"  #: falling edge clock with arrow
    Pclk = "P"  #: rising edge clock with arrow
    low = "l"   #: forced low value in sync with clock edge
    Low = "L"   #: forced low value in sync with clock edge and with arrow
    high = "h"  #: forced high value in sync with clock edge
    High = "H"  #: forced high value in sync with clock edge and arrow
    zero = "0"  #: data set to 0
    one = "1"   #: data set to 1
    gap = "|"   #: single line time compression
    highz = "z" #: high impedance signal
    x = "x"     #: unknown bit
    X = "X"     #: unknown data
    data = "="  #: data
    up = "u"    #: rc settling to 1
    down = "d"  #: rc settling to 0
    meta = "m"  #: metastable state settling to 0
    Meta = "M"  #: metastable state settling to 1
    ana = "a"   #: analogue signal based on equation
    step = "s"  #: analogue signal stepping
    cap = "c"   #: analogue signal charging (rc)
    imp = "i"   #: impulse down or glitch
    Imp = "I"   #: impulse up or glitch
    space = ' ' #: make a blank in the wavelane
    field_start = "[" #: new field internal representation of a register
    field_end = "]"   #: end of field internal representation
    field_mid = ":"   #: bit seperation
    field_bit = "b"   #: single bit field internal represention

    @staticmethod
    def transform_y(y: float, height: float = 20):
        """
        change y coordinate to represente voltage between VSSA and VDDA
        if current VSSA <-> ISSA / VDDA <-> IDDA

        Args:
            y: y-coordinate between VSSA and VDDA
            height: height of a brick in the wavelane
        Returns:
            the new y-coordinate between 0 and height
        """
        scaled_value = (y - pywave.CONTEXT["VSSA"]) / (
            pywave.CONTEXT["VDDA"] - pywave.CONTEXT["VSSA"]
        )
        return height - height * scaled_value

    @staticmethod
    def from_char(c: str):
        """
        Give the corresponding enumeration from a char
        Args:
            c: character representing the symbol
        Returns:
            the enumeration corresponding to c
            or None
        """
        if c in "23456789":
            return BRICKS.data
        a = [b for b in BRICKS if b.value == c]
        return a[0] if a else None

    @staticmethod
    def ignore_transition(from_symb, to_symb) -> bool:
        """
        define special case when transition are skipped to prevent
        glitches by default

        Args:
            from_symb (pywave.BRICKS): symbol from which start the transition
            to_symb (pywave.BRICKS): target symbol of the transition
        Returns:
            boolean result corresponding to the statement
            'transition should be skipped'
        """
        if (from_symb, to_symb) in [
            (BRICKS.low, BRICKS.Low),
            (BRICKS.high, BRICKS.High),
            (BRICKS.Low, BRICKS.low),
            (BRICKS.High, BRICKS.high),
            (BRICKS.one, BRICKS.Pclk),
            (BRICKS.zero, BRICKS.Nclk),
            (BRICKS.High, BRICKS.Pclk),
            (BRICKS.high, BRICKS.Pclk),
            (BRICKS.high, BRICKS.pclk),
            (BRICKS.High, BRICKS.pclk),
            (BRICKS.Low, BRICKS.Nclk),
            (BRICKS.low, BRICKS.Nclk),
            (BRICKS.low, BRICKS.nclk),
            (BRICKS.Low, BRICKS.nclk)
        ]:
            return True
        if (to_symb in [pywave.BRICKS.zero, pywave.BRICKS.one] or BRICKS.is_forced_signal(to_symb)) and \
           from_symb in [pywave.BRICKS.data, pywave.BRICKS.x, pywave.BRICKS.X]:
            return True
        if BRICKS.is_forced_signal(to_symb) and BRICKS.is_clock(from_symb):
            if from_symb.value.lower() == 'n' and to_symb.value.lower() == 'h':
                return True
            if from_symb.value.lower() == 'p' and to_symb.value.lower() == 'l':
                return True
            if from_symb.value.lower() == 'h' and to_symb.value.lower() == 'p':
                return True
            if from_symb.value.lower() == 'l' and to_symb.value.lower() == 'n':
                return True
        return False

    @staticmethod
    def need_equation(symb) -> bool:
        """
        Args:
            symb (pywave.BRICKS) : symbol potentially needing an equation
        Returns:
            bool
                boolean result asserting the symb need an equation
        """
        return symb in [BRICKS.ana, BRICKS.step, BRICKS.cap]

    @staticmethod
    def need_data(symb) -> bool:
        """
        Args:
            symb (pywave.BRICKS) : symbol potentially needing a data
        Returns:
            bool
                boolean result asserting the symb need a data
        """
        return symb in [BRICKS.data,
                        BRICKS.field_start, BRICKS.field_mid,
                        BRICKS.field_end, BRICKS.field_bit]

    @staticmethod
    def need_attribute(symb) -> bool:
        """
        Args:
            symb (pywave.BRICKS) : symbol potentially needing an attribute
        Returns:
            bool
                boolean result asserting the symb need an attribute
        """
        return symb in [BRICKS.field_start, BRICKS.field_bit]

    @staticmethod
    def need_position(symb) -> bool:
        """
        Args:
            symb (pywave.BRICKS) : symbol potentially needing a position
        Returns:
            bool
                boolean result asserting the symb need a position
        """
        return symb in [pywave.BRICKS.field_start, pywave.BRICKS.field_end, pywave.BRICKS.field_bit]

    @staticmethod
    def need_type(symb) -> bool:
        """
        Args:
            symb (pywave.BRICKS) : symbol potentially needing a type
        Returns:
            bool
                boolean result asserting the symb need a type
        """
        return symb in [pywave.BRICKS.field_start, pywave.BRICKS.field_bit]

    @staticmethod
    def is_repeating_symbol(symb) -> bool:
        """
        Args:
            symb (pywave.BRICKS) : symbol potentially repeating the last valid brick
        Returns:
            bool
                boolean result asserting the symb repeat the last valid one
        """
        return symb in [BRICKS.repeat, BRICKS.gap]

    @staticmethod
    def is_clock(symb) -> bool:
        """
        Args:
            symb (pywave.BRICKS) : symbol potentially a clock signal
        Returns:
            bool
                boolean result asserting the symb is a clock signal
        """
        return symb in [BRICKS.Pclk,
                        BRICKS.Nclk,
                        BRICKS.pclk,
                        BRICKS.nclk]

    @staticmethod
    def is_forced_signal(symb) -> bool:
        """
        Args:
            symb (pywave.BRICKS) : symbol potentially forced to a value
        Returns:
            bool
                boolean result asserting the symb is forced
        """
        return symb in [pywave.BRICKS.high, pywave.BRICKS.High,
            pywave.BRICKS.low, pywave.BRICKS.Low]
