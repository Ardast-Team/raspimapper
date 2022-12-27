#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..engine import _grammarcheck as grammarcheck

if __name__ == '__main__':
    grammarcheck.start()
    #~ grammarcheck.startmulti('bots/usersys/grammars/edifact/*','edifact')     #for bulk check of grammars
