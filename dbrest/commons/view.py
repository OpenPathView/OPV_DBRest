#!/usr/bin/env python
# coding: utf-8

# View utils, comes from : https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/Views

from sqlalchemy import *
from sqlalchemy.schema import DDLElement
from sqlalchemy.sql import table
from sqlalchemy.ext import compiler

class CreateView(DDLElement):
    def __init__(self, name, selectable):
        self.name = name
        self.selectable = selectable
        self.selectableRawReqfilter = None


class DropView(DDLElement):
    def __init__(self, name):
        self.name = name


@compiler.compiles(CreateView)
def compile(element, compiler, **kw):
    selectReq = compiler.sql_compiler.process(element.selectable)

    if element.selectableRawReqfilter is not None:
        selectReq = element.selectableRawReqfilter(selectReq)

    return "CREATE VIEW %s AS %s" % (element.name, selectReq)


@compiler.compiles(DropView)
def compile(element, compiler, **kw):
    return "DROP VIEW %s" % (element.name)


def view(name, metadata, selectable, selectableRawReqfilter=None):
    t = table(name)

    for c in selectable.c:
        c._make_proxy(t)

    createView = CreateView(name, selectable)
    createView.selectableRawReqfilter = selectableRawReqfilter
    createView.execute_at('after-create', metadata)
    DropView(name).execute_at('before-drop', metadata)
    return t
